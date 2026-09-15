# The Snapshot Moved. The SQLite Integrity Scan Did Not.

URL: https://anyech.github.io/jingxiao-cai-blog/sqlite-snapshot-cache-not-integrity-scan.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/sqlite-snapshot-cache-not-integrity-scan.html.md
Date: 2026-09-15
Tags: sqlite, debugging, performance, agent-ops

Summary: A cache-placement change can leave a separate source-database scan untouched. Small cold/warm controls show why startup diagnosis must follow the opened file.

---

[← Back to Blog](/jingxiao-cai-blog/)

# The Snapshot Moved. The SQLite Integrity Scan Did Not.

**September 15, 2026** | By Jingxiao Cai

Co-created with **Clawsistant**, my OpenClaw AI agent, using a bounded synthetic experiment and a sanitized numerical extract.

I moved a startup snapshot cache to memory-backed storage. Startup stayed slow, and the integrity check was still a suspect. The misleading assumption was that moving “the database cache” moved every database read.

It did not. In the inspected startup path, snapshot creation and physical database admission were separate operations. The integrity worker opened the *source database*, not the snapshot cache.

**Before optimizing a slow read, identify the file the slow reader actually opens.**

## A small experiment separated two costs

The following measurements came from synthetic indexed databases, not private database contents. The tested OpenClaw 2026.9.3 admission path ran on Node 24.20.0 with SQLite 3.53.4. Source-page residency was measured before each run: zero for cold-source conditions and complete for warm-source conditions. This is not a cold-boot experiment: installed-code pages were not deliberately evicted. Only experiment-owned files were evicted from the page cache; no system-wide cache clearing was used.

| Allocated fixture | Cold full admission | Warm full admission |
| --- | --- | --- |
| 16.21 MiB | 2.550–2.579 s | 0.259–0.265 s |
| 32.38 MiB | 4.674–4.775 s | 0.271–0.275 s |

Each range contains only two repetitions. [Download the eight sanitized samples](/jingxiao-cai-blog/assets/data/sqlite-integrity-synthetic-samples.json), including the fixture size, initial residency and measured admission time. They are an extract of recorded observations, not a portable performance guarantee or a complete reproduction package.

Disposable instrumented worker copies placed timestamps around the full integrity SQL. On the smaller fixture, that phase took roughly 2.34 seconds cold and 14 milliseconds warm; on the larger one, roughly 4.5 seconds cold and 28 milliseconds warm. A minimal native child running the same full checks retained the cold cost. Removing the larger import path did not make the source reads free.

The full experiment comprised 35 serial child runs, including five expected rejections. Corruption, foreign-key failure, stale input identity, cancellation and post-result file replacement were exercised. All seven recorded control groups passed, including source preservation and child closure. Those controls matter: a faster path that omits a check is not an equivalent optimization.

## Two paths, one misleading cache label

```
source database → stable snapshot copy → snapshot cache
source database → read-only integrity worker → admission decision
```

Changing the destination on the first line does not change the open pathname on the second. The integrity worker still performs a full `integrity_check` and `foreign_key_check`; the parent also waits for child closure and revalidates file identity.

This explains a trap in startup profiling. A parent event loop can look idle while its child waits on file I/O. A warm cached handle can also avoid a physical open that a fresh process must perform. Neither observation tells you that a fresh database admission no longer scans the source.

SQLite's [integrity-check documentation](https://www.sqlite.org/pragma.html#pragma_integrity_check) also distinguishes integrity checking from foreign-key checking. Treating one successful check as proof that both ran would change the correctness contract.

## The decision I changed

I stopped treating snapshot placement as the explanation for the remaining startup time. The next useful measurement was a phase trace tying the slow worker to its opened file, CPU time, physical reads and final admission—not another cache-placement change.

That choice trades a quick-looking optimization for a more specific diagnosis. An import reduction might remove a small fixed cost. It cannot, by itself, eliminate a multi-second read of cold source pages. Conversely, a source-page effect in a small test is not evidence that adding a warmer is the right operational remedy.

A compact diagnostic sequence is enough: identify each open pathname; time copy, integrity and settlement separately; compare wall time with child CPU and reads; then repeat on a disposable fixture while keeping the checks unchanged. Keep the production decision separate from the experimental result.

## What this does not establish

The experiment shows source-page sensitivity in these small fixtures. It does **not** establish the cause of a particular production startup, predict large-database behavior, or validate a faster replacement admission path. Instrumentation perturbs execution, the schema is synthetic, and two repetitions do not establish tail latency. The result is a reason to follow the actual read path, not to weaken integrity checks.

### Related Posts

- [Before Raising Reindex Concurrency, Prove the Memory Lane](/jingxiao-cai-blog/before-raising-reindex-concurrency-prove-memory-lane.html)

- [Bound Before You Serialize](/jingxiao-cai-blog/bound-before-serialize-oversized-child-result.html)

### About the Author
Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents and technical debugging.

## Comments
Have you optimized one file path while the expensive reader was opening another?
