# When SQLite Looks Empty but Isn’t: Reproducing Corrupt Task Registries Without Touching Prod

URL: https://anyech.github.io/jingxiao-cai-blog/sqlite-empty-corrupt-task-registries-without-touching-prod.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/sqlite-empty-corrupt-task-registries-without-touching-prod.html.md
Date: 2026-05-06
Tags: sqlite, openclaw, ai-agents, incident-response, debugging, self-hosted

Summary: A self-hosted agent-ops debugging story: raw SQLite can still see rows while the runtime registry restore fails, so reproduce on copies before touching production.

---

← Back to Blog

# When SQLite Looks Empty but Isn’t: Reproducing Corrupt Task Registries Without Touching Prod


 May 6, 2026 | By Jingxiao Cai

 Tags: sqlite, openclaw, ai-agents, incident-response, debugging, self-hosted



 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped separate raw database evidence from runtime restore behavior, then kept the public version focused on the transferable repair pattern instead of deployment-specific artifacts.



 Short version: a SQLite-backed task registry can look non-empty under raw inspection while the application still sees an unusable or effectively empty registry view. Do not debug that by poking production. Preserve copies, compare query paths, reproduce in isolation, and only cut over after the repair path is proven.





 Small self-hosted agent systems often lean on SQLite for exactly the right reasons: it is simple, local, fast, and easy to back up. That simplicity can make corruption incidents feel more surprising than they should.

 The tricky case I hit was not the cartoon version where every read explodes immediately. The confusing symptom was more subtle: raw SQLite inspection could still see task-history rows, while the agent runtime behaved as if the task registry could not be restored correctly.


 “The rows exist” and “the runtime can safely use this registry” are not the same claim.




 Public-surface note: this write-up is sanitized from self-hosted OpenClaw operations. It keeps the reusable debugging structure and SQLite concepts, but omits private paths, task IDs, channel IDs, hostnames, exact schedules, live counts, helper filenames, and deployment-specific topology.



## The Symptom: History Exists, Registry Restore Still Fails

 The user-visible failure looked like an agent control-plane problem: task tracking, delivery state, or maintenance probes started acting unreliable. Raw database checks made the situation look less catastrophic because the database file still contained historical task rows.

 That led to a dangerous temptation:

 SQLite can count rows,
so the registry is probably fine,
so maybe I can repair this in place.

 That would have been the wrong conclusion. A task registry is not just a bag of rows. The runtime depends on a particular schema, indexes, uniqueness assumptions, WAL sidecar state, and query paths. If any of those are inconsistent, the database can still answer some direct SQL while the application restore path fails or silently sees the wrong subset of state.


## Why “Looks Empty” Happens

 There were two useful failure classes to keep separate.




 Failure class
 What raw inspection may show
 What the runtime may experience





 Index drift or index corruption
 Base-table scans still reveal rows; indexed scans may disagree.
 Queries that rely on indexes or uniqueness invariants can return the wrong view.



 Table or overflow-page damage
 Some rows remain readable; specific payload reads fail or return mixed/corrupt fields.
 The restore path may abort, quarantine state, or treat the registry as unavailable.



 Sidecar mismatch
 The main database file looks plausible by itself.
 The application sees a different state once WAL/SHM behavior and checkpoint timing enter the picture.





 That is why one-liner diagnostics are not enough. PRAGMA quick_check is a useful gate, but it should not be the only evidence. A full PRAGMA integrity_check, indexed-vs-NOT INDEXED comparisons, schema inspection, and a runtime restore probe answer different questions.


 Operational smell: if raw SQL and the application disagree, do not immediately choose the answer you prefer. Treat the disagreement itself as evidence.



## The Safe Reproduction Ladder

 The repair workflow that actually held up was copy-first. Production was evidence, not a workbench.



- Freeze evidence first. Preserve the database and its sidecar files before running tools that might checkpoint, truncate, or rewrite them.

- Work on disposable copies. Put each hypothesis in a scratch directory, stage clone, container, or other throwaway environment.

- Ask multiple SQLite questions. Compare quick_check, integrity_check, ordinary counts, NOT INDEXED counts, and representative row scans.

- Run the application restore path separately. A database can satisfy a direct SQL query and still fail the runtime’s actual startup or restore code.

- Try repairs only on copies. Test REINDEX, logical backup, or CLI recovery on preserved snapshots before deciding whether any production cutover is justified.

- Cut over only during an explicit maintenance window. If the gateway has to be offline, that action needs a human-owned or pre-approved offline execution plan with logs that survive the outage.


 The key move is step four. Many incidents stop at “SQLite says there are rows.” Agent systems need a second gate: “the runtime can restore those rows through the same path it uses in real life.”


## Three Lenses Beat One Query

 I ended up thinking about the registry through three lenses:




 Lens
 Question
 Useful signal





 Base-table lens
 What rows are physically readable without trusting indexes?
 NOT INDEXED scans, selected payload reads, logical export attempts.



 Index/invariant lens
 Do indexed paths agree with raw scans?
 Count mismatches, uniqueness failures, integrity_check output, post-REINDEX comparisons.



 Runtime lens
 Can the application restore and use the registry safely?
 Isolated startup/restore probes, task-list parsing, and control-plane smoke checks.





 When all three lenses agree, you can start trusting the result. When they disagree, the mismatch is the incident.


## What Repairs Mapped to Which Failure

 SQLite gives you several tools, but they are not interchangeable.



- REINDEX is attractive when the base table is readable and the strongest evidence points to index drift. SQLite documents it as rebuilding indexes from scratch, which is exactly the shape you want for an index-only hypothesis.

- Logical backup or dump is useful when ordinary reads are still reliable enough to export a coherent database image.

- CLI recovery is the “the file is damaged, salvage what can be salvaged” lane. It belongs on copies, not casually on the live registry.

- Restore from a known-good candidate is sometimes safer than clever repair, especially when the runtime registry is already unreliable and recent history loss is bounded.


 The important part is not picking the flashiest tool. It is matching the tool to the evidence. If the evidence says index drift, a copy-tested REINDEX can be a small repair. If the evidence says table payload contamination, pretending it is “just an index” is wishful thinking.


## The Production Boundary

 The cleanest operational rule from this incident is simple:


 Do not let production be your reproduction harness.


 That rule has two parts.


### 1. No live mutation while you are still learning

 Before the repair path is proven, production should be read-only evidence. Take snapshots. Preserve sidecars. Run checks that do not mutate state. Move experiments elsewhere.


### 2. No self-cutting maintenance window

 If the repair requires stopping the gateway, do not rely on the same gateway-backed chat session to supervise the full stop/repair/start sequence. Either the human runs the window manually, or a pre-approved host-detached one-shot runner writes durable phase and result markers before it takes the gateway down.

 That second rule matters because database repair and service lifecycle are coupled. A script that stops the service may also cut off the very control channel that was supposed to report whether the script finished.


## The Mistakes This Prevents



- Trusting mtime over viability. The newest backup is not necessarily the best backup if it is empty, partial, or unreadable.

- Trusting the main database file alone. WAL-backed systems need sidecar-aware evidence capture.

- Trusting row counts as health. Counts can hide index drift, payload damage, or runtime restore failures.

- Running repairs from the wrong control plane. If stopping the gateway kills your supervisor, you need a different execution model.

- Conflating “recovered enough for SQL” with “safe for the application.” The runtime restore path is its own test.



## A Reusable Checklist



- Preserve the database plus WAL/SHM sidecars before any tool can rewrite them.

- Record which checks are read-only and which are mutating.

- Compare indexed scans with NOT INDEXED scans for key tables.

- Run both quick and full integrity checks on copies where possible.

- Probe the application restore path in an isolated harness.

- Test REINDEX, recovery, or restore candidates on copies first.

- Choose the smallest repair that explains the evidence.

- Use an explicit maintenance window for production cutover.

- After cutover, verify both SQLite health and the application’s control-plane behavior.



## My Take

 SQLite was not the villain here. The dangerous part was the human temptation to collapse several questions into one: “does the file still contain rows?”

 For an agent gateway, the better question is stricter:


 Can the live runtime restore, query, and update this registry through its real paths without contradicting the lower-level evidence?



 If the answer is no, treat the system as degraded even when raw SQL can still find history. Debug on copies. Repair with evidence. Keep production boring.


## References



- SQLite documentation: PRAGMA integrity_check and related checks

- SQLite documentation: REINDEX

- SQLite CLI documentation: recovering data from a corrupted database




### Related Posts



- Gateway Restart Behavior: What OpenClaw Users Need to Know About Config Changes

- Building Fail-Closed Stage Environments for AI Agents on a Small VPS

- The 10-Second Session List: Why Prefiltering Before Row Build Matters in Agent Gateways

- Treating AI Agent Updates Like Production Deployments: The Runbook Keeps Paying Off






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and self-hosted AI-agent operations. He writes about the debugging and reliability lessons that are easier to learn on copies than in production.

 This post intentionally avoids deployment-specific IDs, private paths, hostnames, exact schedules, and live registry counts. The repair pattern is the point.






 Found this useful? Send it to someone who says “the rows are still there” a little too confidently.

 ← Back to Blog
