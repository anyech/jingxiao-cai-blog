# The 10-Second Session List: Why Prefiltering Before Row Build Matters in Agent Gateways

URL: https://anyech.github.io/jingxiao-cai-blog/10-second-session-list-prefilter-row-build-agent-gateway.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/10-second-session-list-prefilter-row-build-agent-gateway.html.md
Date: 2026-05-02
Tags: openclaw, ai-agents, performance, devops, control-plane, self-hosted

Summary: A self-hosted agent-gateway performance lesson: if a tiny session-list request builds hundreds of rich rows before filtering, limit is too late to save you.

---

← Back to Blog

# The 10-Second Session List: Why Prefiltering Before Row Build Matters in Agent Gateways


 May 2, 2026 | By Jingxiao Cai

 Tags: openclaw, ai-agents, performance, devops, control-plane, self-hosted



 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped reconstruct the debugging timeline, separate live symptoms from isolated evidence, and keep the public version focused on the reusable performance pattern rather than deployment-specific details.



 Short version: if a session-list request asks for one recent row, the gateway should not enrich the entire session history first. Filter cheap candidates, sort and limit cheaply, then build the expensive rows.





 One of the easiest ways to make an agent gateway feel broken is to let a tiny control-plane request accidentally pay for the whole history of the system.

 That was the shape of a recent OpenClaw performance issue I chased down. A session-list call that should have been narrow could sit close to the caller timeout under load. The gateway was not dead. Cheap health checks could still pass. But richer control-plane calls were slow enough that the user-visible experience looked like a connectivity problem.

 I call this the 10-second session list because the visible failure lived near a roughly ten-second RPC boundary. The isolated benchmarks below are not all ten seconds; they show why a narrow call could drift into that timeout class when the gateway was under real control-plane pressure.

 The root cause was more interesting than “the box is small” or “the network is flaky.” The slow path was doing the right work in the wrong order.


 The gateway was building expensive session rows before applying the cheap filters that would have thrown most of those rows away.




 Public-surface note: the details below are sanitized from self-hosted OpenClaw operations. I keep the reusable structure and representative performance counters, but omit private paths, channel IDs, task IDs, hostnames, live config values, helper filenames, and exact deployment inventory.



## The Symptom: Healthy Gateway, Slow Control Plane

 The confusing part was that the gateway did not look simply “down.” A basic status or health check could pass, while higher-level calls that needed session metadata stalled or timed out.

 That distinction matters. A health endpoint can answer “the process is alive” without proving that the expensive control-plane routes are responsive. If one route monopolizes the event loop doing synchronous or CPU-heavy work, the system can be alive and still feel unavailable.

 The practical symptom was a session-list request shaped like this:

 give me a very small number of recently active sessions

 That sounds cheap. It should be cheap. But it was not, because the implementation treated “limit” as a final presentation step rather than as a way to avoid work.


## The Bad Shape: Enrich Everything, Then Throw Most of It Away

 The slow path looked roughly like this:

 load session stores
for each candidate session:
 build a rich display row
 resolve child sessions
 read derived usage or title fields when needed
 attach status and metadata
sort rich rows
apply recent-activity filter
apply limit
return the remaining rows

 That order is fine when the caller genuinely asks for a full rich listing. It is terrible when the caller asks for one or a few recent sessions.

 The expensive part was not just JSON parsing. It was row construction: deriving display state, resolving child relationships, and falling back to transcript-derived metadata when the compact session row did not already contain what the UI wanted.

 Once those operations sit inside a loop over hundreds of historical rows, the caller’s limit=1 does not protect anything. The gateway still pays the cost of enriching rows that will never be returned.


 Performance smell: if limit appears only after expensive row construction, it is not a workload reducer. It is just a final trim.



## The Better Shape: Filter Before Row Build

 The corrected fast path is not exotic. It is the same principle database people call predicate pushdown, applied inside an agent gateway:

 load session stores
apply cheap key / agent / label / activity-window filters
sort by raw timestamp
apply raw limit
for each selected candidate:
 build the rich display row
return rows

 The important constraint is that “cheap” has to mean cheap and semantically safe. Some filters can be applied before row construction because they depend only on raw session-store fields. Others may still require the richer legacy path until their semantics are proven.




 Operation
 Where it belongs
 Why





 agent, label, explicit key filters
 before row build
 They can be checked directly against raw candidates.



 recent-activity window
 before row build when raw timestamps are enough
 It can collapse the candidate set dramatically.



 sort and limit for the fast path
 before row build
 The gateway should enrich only the rows it may return.



 free-text search or relationship-heavy filters
 legacy/rich path until proven safe
 Correctness matters more than forcing every option into the fast path.





 That last row is important. The fix was not “always skip enrichment.” The fix was “do not enrich rows that cheap filters already prove are irrelevant.”


## The Evidence That Changed My Mind

 Before the source-level validation, it was tempting to blame stale session residue, broad store size, or generic gateway pressure. Those were contributors, but cleanup alone was not the structural fix.

 The decisive evidence came from isolated validation against copied state and then a stage-style probe of the filtered hot path. The filtered request collapsed from hundreds of row builds to a couple:




 Metric
 Before
 After prefiltering
 What it means





 Rows sent through expensive row build
 381
 2
 The request stopped enriching almost the whole history.



 Transcript-derived fallback time
 about 953 ms
 about 28 ms
 Less row build means fewer fallback reads.



 Child-relationship resolution time
 about 109 ms
 about 2 ms
 Relationship work moved off discarded rows.



 Total filtered-probe wall time
 about 1.31 s
 about 216 ms
 The narrow control-plane call became narrow in practice.





 Another copied-state benchmark showed the same direction even more sharply: a narrow list phase that took seconds in the enrich-first shape dropped to milliseconds when the implementation limited before enrichment.

 Full-list probes, meanwhile, stayed broadly similar. That was expected and actually reassuring. If the caller asks for a rich full listing, the gateway still has to build the rich rows. The win is for the common hot path that asks for a tiny recent slice.


 The durable conclusion: this was not primarily a loopback problem, a generic health-check problem, or a “delete a few more old rows” problem. It was an execution-order problem in the session-list path.



## Why Cleanup Was Not Enough

 Session-store hygiene still matters. Big stale rows, bulky metadata, missing compact usage fields, and accumulated historical state can all amplify latency.

 But cleanup is a weak fix if the route still does O(N) enrichment for tiny queries. You can make N smaller today and watch it grow again tomorrow.

 The better question is:


 Does the cost of this request scale with the number of rows it returns, or with the number of rows the system has ever seen?



 For a recent-session hot path, the answer should be much closer to “rows returned.” If it scales with historical cardinality, the gateway will keep rediscovering the same failure mode as the deployment ages.


## The General Agent-Gateway Lesson

 Agent gateways are full of deceptively small list/status routes:



- recent sessions

- running tasks

- active workers

- pending approvals

- thread or conversation summaries

- tool-call histories


 Those routes often start life as admin conveniences. Then agents begin calling them in watchdogs, status cards, thread handoffs, cron monitors, and final-delivery checks. Suddenly the route is not occasional UI sugar anymore. It is part of the control plane.

 When that happens, the implementation needs control-plane discipline:



- Push cheap filters earlier. Do not derive rich display rows before raw predicates have narrowed the candidate set.

- Make limit a work reducer. A limit after enrichment is too late for performance.

- Cache or batch repeated side lookups. Per-row registry reads and relationship scans turn small routes into multipliers.

- Separate fast path from rich path. Keep search-heavy or relationship-heavy semantics on the safe path until proven equivalent.

- Instrument row-build counts, not only wall time. “It took 10 seconds” is a symptom. “It built 381 rows to return 2” is a root-cause clue.



## The Trap in Health Checks

 This bug also reminded me not to overtrust cheap health signals.

 A gateway can answer a health probe while a richer RPC path is expensive enough to time out. That is not hypocrisy; it is just two different questions:




 Question
 What it proves
 What it does not prove





 Is the process alive?
 The service can answer a cheap probe.
 Control-plane routes are responsive.



 Can the gateway list recent sessions quickly?
 A real hot path is healthy.
 Every full-history rich listing is cheap.



 Did cleanup reduce stored state?
 Hygiene improved.
 The route no longer scales with history.





 For agent systems, the health check I care about is not just “can I connect?” It is “can the routes my automation calls under pressure still answer within their budget?”


## What I Would Look for in Any Similar System

 If I were reviewing another agent gateway with similar symptoms, I would ask for this evidence before proposing bigger knobs:



- How many raw candidates are loaded?

- How many candidates survive cheap filters?

- How many rows are actually enriched?

- How many side lookups happen per returned row?

- Does limit=1 change the amount of work, or only the output size?

- Which filters are safe to apply before enrichment, and which ones are not?


 Those questions are boring in the best way. They turn a spooky “gateway timeout” into a small performance profile.


## The Bigger Pattern

 The pattern is broader than OpenClaw and broader than session lists:


 Do not materialize expensive objects until cheap predicates prove you need them.



 That is obvious in a database. It is easier to forget in application code, where “build the row object” feels harmless until the row object quietly performs filesystem reads, relationship resolution, derived metadata fallback, and display-status work.

 In agent gateways, those “display” objects become operational objects. They show up in watchdogs, monitors, handoffs, and status checks. If they are expensive to build, they can block the control plane itself.

 So the best fix was not a bigger timeout, a restart ritual, or more cleanup. It was to put the work in the right order.


 Sanitization note: I kept the API shape, performance deltas, and execution-order lesson because they are the transferable parts. I removed private state paths, live host identifiers, channel/thread IDs, task/session IDs, exact helper filenames, and provider/model routing fingerprints.




### Related Posts



- Local Semantic Memory on a 4-Core ARM VPS

- Treating AI Agent Updates Like Production Deployments

- Why AI Cron Jobs Need Exact-Exec Drivers

- Fail-Closing Agent Launches






### About the Author

 Jingxiao Cai works on AI/ML infrastructure and writes about self-hosted agents, debugging, and operational discipline. He likes performance fixes that turn scary symptoms into boring counters.

 If a tiny query builds the whole world before answering, the bug is usually not the tiny query.






 Published on May 2, 2026 • Part of my ongoing OpenClaw operations and agent-gateway performance series

 ← Back to Blog
