import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import struct
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from archive_readback import restore_archive, progress_record, write_json_atomic

class ReadbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.key = self.root/'test.agekey'
        subprocess.run(['age-keygen','-o',str(self.key)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
        self.recipient = subprocess.check_output(['age-keygen','-y',str(self.key)],text=True).strip()
        self.src=self.root/'payload';self.src.write_bytes(os.urandom(2*1024*1024));self.src.chmod(0o640)
        os.utime(self.src,ns=(1700000000123456789,1700000000987654321))
        os.setxattr(self.src,'user.readback-test',b'value')
        acl=struct.pack('<I',2)+b''.join(struct.pack('<HHI',tag,perm,uid) for tag,perm,uid in [(1,6,0xffffffff),(2,4,65534),(4,4,0xffffffff),(16,4,0xffffffff),(32,0,0xffffffff)])
        os.setxattr(self.src,'system.posix_acl_access',acl)
        self.tar=self.root/'input.tar'
        subprocess.run(['tar','--format=pax','--acls','--xattrs','--numeric-owner','-cf',str(self.tar),'-C',str(self.root),'payload'],check=True)
        self.cipher=self.root/'cipher.age';self.encrypt()
    def encrypt(self):
        self.cipher.unlink(missing_ok=True)
        subprocess.run(['age','-r',self.recipient,'-o',str(self.cipher),str(self.tar)],check=True)
    def restore(self,digest=None):
        with (self.root/'log').open('wb') as log:
            return restore_archive(self.cipher,digest or hashlib.sha256(self.cipher.read_bytes()).hexdigest(),self.key,self.root/'restore','payload',log)
    def test_single_read_and_metadata(self):
        expected=hashlib.sha256(self.cipher.read_bytes()).hexdigest();original=Path.open;opens=[];bytecount=[]
        class Counted:
            def __init__(self,f):self.f=f
            def __enter__(self):return self
            def __exit__(self,*args):self.f.close()
            def read(self,n):
                value=self.f.read(n);bytecount.append(len(value));return value
        def tracked(path,*args,**kwargs):
            f=original(path,*args,**kwargs)
            if path==self.cipher:opens.append(1);return Counted(f)
            return f
        with patch.object(Path,'open',tracked):r=self.restore(expected)
        self.assertEqual(len(opens),1);self.assertEqual(sum(bytecount),self.cipher.stat().st_size)
        q=self.root/'restore/payload';self.assertEqual(q.read_bytes(),self.src.read_bytes())
        for attr in ['st_mode','st_uid','st_gid','st_mtime_ns']:self.assertEqual(getattr(q.stat(),attr),getattr(self.src.stat(),attr))
        self.assertEqual(set(os.listxattr(q)),set(os.listxattr(self.src)))
        for x in os.listxattr(self.src):self.assertEqual(os.getxattr(q,x),os.getxattr(self.src,x))
        self.assertEqual(r['source_passes'],1)
    def test_wrong_expected_hash_no_extraction(self):
        with self.assertRaises(ValueError):self.restore('0'*64)
        self.assertFalse((self.root/'restore').exists())
    def test_corrupt_authenticated_stream(self):
        data=bytearray(self.cipher.read_bytes());data[-100]^=1;self.cipher.write_bytes(data)
        with self.assertRaises((RuntimeError,BrokenPipeError)):self.restore()
        self.assertFalse((self.root/'restore').exists())
    def test_truncated_stream(self):
        self.cipher.write_bytes(self.cipher.read_bytes()[:-100])
        with self.assertRaises((RuntimeError,BrokenPipeError)):self.restore()
        self.assertFalse((self.root/'restore').exists())
    def test_path_escape_rejected(self):
        with tarfile.open(self.tar,'w') as t:
            i=tarfile.TarInfo('../escape');i.size=1;t.addfile(i,io.BytesIO(b'x'))
        self.encrypt()
        with self.assertRaises(ValueError):self.restore()
        self.assertFalse((self.root/'escape').exists());self.assertFalse((self.root/'restore').exists())
    def test_wrong_identity_no_extraction(self):
        subprocess.run(['age-keygen','-o',str(self.root/'wrong.key')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
        self.key=self.root/'wrong.key'
        with self.assertRaises((RuntimeError,BrokenPipeError)):self.restore()
        self.assertFalse((self.root/'restore').exists())
    def test_extraction_failure_requires_reconciliation(self):
        with patch('archive_readback.subprocess.run',side_effect=subprocess.CalledProcessError(1,'tar')):
            with self.assertRaises(subprocess.CalledProcessError):self.restore()
        self.assertTrue(self.src.exists())
        with self.assertRaises(FileExistsError):self.restore()
    def test_existing_staging_rejected(self):
        (self.root/'restore').mkdir();(self.root/'restore/keep').write_text('keep')
        with self.assertRaises(FileExistsError):self.restore()
        self.assertEqual((self.root/'restore/keep').read_text(),'keep')
    def test_interrupted_read_then_clean_retry(self):
        expected=hashlib.sha256(self.cipher.read_bytes()).hexdigest();original=Path.open
        class Interrupted:
            def __init__(self,f):self.f=f
            def __enter__(self):return self
            def __exit__(self,*args):self.f.close()
            def read(self,n):
                if self.f.tell():raise KeyboardInterrupt()
                return self.f.read(n)
        def interrupted(path,*args,**kwargs):
            f=original(path,*args,**kwargs);return Interrupted(f) if path==self.cipher else f
        with patch.object(Path,'open',interrupted):
            with self.assertRaises(KeyboardInterrupt):self.restore(expected)
        self.assertFalse(list(self.root.glob('.readback-*')));self.assertFalse((self.root/'restore').exists())
        self.restore(expected)
    def test_terminal_collision_and_atomic_failure(self):
        value=progress_record('complete',time=123,pid=456,result='pass');self.assertEqual(value['stage'],'complete');self.assertNotEqual(value['time'],123)
        path=self.root/'status.json';write_json_atomic(path,{'stage':'verified'})
        with patch('os.replace',side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):write_json_atomic(path,value)
        self.assertEqual(json.loads(path.read_text()),{'stage':'verified'});write_json_atomic(path,value)
        self.assertEqual(json.loads(path.read_text()),value)

if __name__=='__main__':unittest.main()
