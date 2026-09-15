"""Single source-pass verifier for a single-file age/tar wrapper.

No upload, source deletion, receipt mutation, or live-state restoration. Caller
retains original-file hash/metadata and runtime gates before retirement.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import time


def progress_record(stage, **fields):
    """Reserved terminal fields cannot collide with a result's time/pid keys."""
    return {**fields, 'stage': stage, 'time': time.time(), 'pid': os.getpid()}


def write_json_atomic(path, value):
    path = Path(path)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as target:
            json.dump(value, target, indent=2)
            target.write('\n')
            target.flush()
            os.fsync(target.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def restore_archive(cipher, expected_digest, identity, restore, member, log):
    """Traverse the ciphertext file exactly once, hashing while age decrypts to private tar.

    Authenticate and check the ciphertext digest before unpacking. Local staging
    avoids a second network read and prevents unauthenticated tar extraction.
    A failed/interrupted attempt never accepts an existing restore destination;
    retry uses new staging after caller reconciliation. This function does not
    declare source retirement safe: caller must compare restored original bytes
    and metadata, including xattrs/ACLs, against its approved source manifest.
    """
    cipher, restore = Path(cipher), Path(restore)
    if not member or Path(member).name != member or member in {'.', '..'}:
        raise ValueError('expected one plain basename')
    if os.path.lexists(restore):
        raise FileExistsError('reconcile existing restore destination first')
    if len(expected_digest) != 64 or any(c not in '0123456789abcdef' for c in expected_digest):
        raise ValueError('expected SHA256 must be lowercase hex')
    digest = hashlib.sha256()
    read_bytes = 0
    with tempfile.TemporaryDirectory(prefix='.readback-', dir=restore.parent) as scratch:
        tar_path = Path(scratch) / 'verified.tar'
        with tar_path.open('xb') as plain:
            child = subprocess.Popen(['age', '-d', '-i', str(identity)],
                                     stdin=subprocess.PIPE, stdout=plain, stderr=log)
            try:
                with cipher.open('rb') as source:
                    while chunk := source.read(1024 * 1024):
                        digest.update(chunk)
                        read_bytes += len(chunk)
                        child.stdin.write(chunk)
                child.stdin.close()
                code = child.wait()
            except BaseException:
                child.kill()
                child.wait()
                child.stdin.close()
                raise
        if code != 0:
            raise RuntimeError('age authentication/decryption failed')
        if digest.hexdigest() != expected_digest:
            raise ValueError('ciphertext SHA256 mismatch')
        with tarfile.open(tar_path, 'r:') as archive:
            entries = archive.getmembers()
            if len(entries) != 1 or entries[0].name != member or not entries[0].isreg():
                raise ValueError('unexpected wrapper members or types')
            # PAX xattrs/ACLs are preserved by GNU tar below, not Python extraction.
        restore.mkdir(mode=0o700)
        subprocess.run(['tar', '--acls', '--xattrs', '--same-permissions',
                        '--numeric-owner', '--delay-directory-restore',
                        '-xf', str(tar_path), '-C', str(restore)],
                       stdout=log, stderr=log, check=True)
    return {'cipher_sha256': digest.hexdigest(), 'source_passes': 1,
            'source_bytes': read_bytes, 'authenticated': True}
