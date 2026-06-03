# When Your Tunnel Watchdog Lies: Fixing False SSH Alarms Without Hiding Real Failures

URL: https://anyech.github.io/jingxiao-cai-blog/when-your-tunnel-watchdog-lies.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/when-your-tunnel-watchdog-lies.html.md
Date: 2026-06-02
Tags: devops, networking, monitoring, ai-agents, openclaw, reliability

Summary: A real transient SSH failure plus a wrapper contract bug turned one tunnel watchdog alert into a lesson: keep degraded alerts visible, but do not label them as monitor crashes.

---

← Back to Blog

# When Your Tunnel Watchdog Lies: Fixing False SSH Alarms Without Hiding Real Failures


 June 2, 2026 | By Jingxiao Cai

 Tags: devops, networking, monitoring, ai-agents, openclaw, reliability



 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped separate a private reverse-SSH incident into the public-safe parts: transient transport noise, wrapper semantics, and alert honesty.



 Short version: a watchdog can be right about a transient failure and wrong about the operational headline. The fix is not to silence the watchdog; it is to make the alert contract say exactly what happened.


 A tunnel watchdog fired on a reverse-SSH lane with a scary-looking connection-close signature.

 At first glance, that sounds simple: SSH failed, so the tunnel is broken. But the investigation found two different failures stacked on top of each other:



- A real transient transport failure. A burst-shaped probe could make one lane briefly reject a handshake while the same lane passed an immediate focused recheck.

- A wrapper contract bug. In this wrapper, nonzero meant command/runtime failure, but the watchdog used that same channel for ordinary degraded alert text. The host wrapper therefore labeled the alert as a wrapper failure instead of a normal degraded condition.



 The alert was not fake. The headline was wrong.




 Conceptual scope: this is a sanitized operations story. I am omitting hostnames, lane names, exact topology, file paths, schedule details, thread identifiers, script names, and private wrapper names. The reusable lesson is the monitor contract, not my deployment fingerprint.



## The Failure Shape

 The original symptom looked like a hard tunnel failure: one SSH probe saw a connection-close error during key exchange. That is a real failure signature. It should not be ignored.

 But the shape mattered. The error appeared during a topology-wide burst probe, where multiple lanes were checked at the same time. A focused single-lane recheck immediately afterward succeeded. That changed the read from “the lane is definitely dead” to “this lane can produce transient failures under burst pressure.”

 That distinction is easy to lose in an alert stream. Humans do not read every alert as a nuanced diagnosis; they read the headline first. If the headline says the wrapper crashed, the operator starts debugging the monitor. If the headline says a monitored lane degraded and then recovered, the operator investigates the lane with a very different posture.


## The Contract Bug

 The second problem was quieter but more damaging. The watchdog had two jobs:



- Detect and print a degraded tunnel condition when one exists.

- Use the wrapper's failure channel when the watchdog itself cannot run correctly.


 Those jobs were blurred. Normal degraded alert output used the same binary failure channel as actual wrapper/runtime failure. That meant the upstream wrapper could not tell the difference between “the monitor successfully found a degraded lane” and “the monitor command failed.”




 Observed event
 What it should mean
 Bad contract read





 Transient SSH close during burst probe
 Transport warning; recheck before escalating
 Hard tunnel failure



 Watchdog prints degraded alert text
 Monitor succeeded and found something worth reporting
 Wrapper crashed or command failed



 Immediate focused recheck succeeds
 Transient class confirmed; keep evidence and soak
 Contradictory noise





 The monitor was trying to be helpful. The contract made it sound less trustworthy than it was.


## The Fix Was Not “Stop Alerting”

 The wrong fix would have been to suppress the warning entirely. That would make the dashboard quieter, but it would also hide real transport evidence.

 The better fix had three parts:



- Add a short grace recheck. If a lane fails during a burst probe, recheck the specific problem lane before paging the operator.

- Separate degraded output from command failure. A watchdog that successfully emits a degraded alert should encode that as monitored-system state, not as monitor-runtime failure. In a binary wrapper where nonzero means “the command failed,” that means success plus alert text. In a typed-status monitor, it may mean distinct warning/critical/unknown statuses.

- Keep real wrapper failures distinct. Reserve the wrapper/runtime failure channel for cases where the watchdog itself cannot run, parse, connect to prerequisites, or produce a trustworthy report.



 Healthy contract: “I successfully ran and found a degraded monitored condition” is not the same as “I failed to run.” Treat those as separate states in whatever status channel your supervisor actually understands.



## Why This Matters for Agent Operations

 Self-hosted agents accumulate monitors quickly: tunnel checks, cron delivery checks, storage checks, queue checks, model-route checks, and state-store checks. Each monitor is small. The alert surface is not.

 When wrapper contracts are sloppy, operators learn the wrong lesson. They either distrust the alert channel because it cries “wrapper failure” too often, or they overreact to transient transport noise because the alert lacks recheck context. Both outcomes are bad.

 An agent runtime needs monitors that are honest enough to preserve weak signals and precise enough not to convert every weak signal into an incident.


## The Pattern I Would Reuse

 For any watchdog that wraps a lower-level probe, I would now force the states into separate buckets:




 State
 Status behavior
 Operator meaning





 All monitored lanes healthy
 Healthy status, usually silent
 No action



 Degraded monitored condition found
 Degraded monitored-state status; in binary wrappers, success plus alert text
 Monitor worked; investigate the reported condition



 Transient failure clears on focused recheck
 Recovered/transient status, with evidence or telemetry note
 Record and watch; do not page as a hard failure by default



 Watchdog cannot run or cannot trust its own result
 Runtime/unknown failure status
 Debug the monitor or wrapper first





 The exact mechanics vary by system. Some supervisors intentionally use nonzero check states for warning or critical monitored conditions. That is fine when the states are typed and unambiguous. The stable principle is narrower: do not let the same status mean both monitored-system degradation and monitor-runtime failure.


## A Small Checklist for Watchdog Design



- Name the monitored condition separately from wrapper health. Do not let one word like “failed” cover both.

- Recheck burst-sensitive failures before paging. A topology-wide probe can create a failure shape that a focused probe does not reproduce.

- Preserve the first failure signature. A cleared recheck does not mean the original event was imaginary.

- Reserve the wrapper-runtime failure state for wrapper/runtime failure. Normal degraded alert text should not masquerade as command failure; if your monitor supports typed warning/critical states, use them explicitly.

- Write reopen criteria. Decide what recurrence turns a transient class into a real infrastructure investigation.



## Conclusion

 This incident was useful because it resisted the easy labels. It was not “just a false alarm,” because the SSH close signature was real. It was not “the tunnel is broken,” because the immediate focused recheck succeeded. It was not “the monitor crashed,” because the monitor had actually done its job and emitted alert text.

 The real bug was the contract between the monitor and the wrapper.

 That is the lesson I am keeping: do not make watchdogs quieter by hiding degraded conditions. Make them more precise by separating monitored-system state from watchdog-runtime state. Quiet systems are nice. Honest systems are better.



### Related Posts



- Gateway Restart Behavior: What OpenClaw Users Need to Know About Config Changes

- When a True Alert Is Still the Wrong Page

- When the Report Exists but Delivery Failed

- The Monitor Is Not the Contract






### About the Author

 Jingxiao Cai works on AI/ML infrastructure and writes about self-hosted agents, automation reliability, and the operational boundaries that keep small systems understandable.

 A monitor contract should separate monitored-system degradation from monitor-runtime failure.




## Comments

 Found this useful? Leave a comment below, or send it to someone whose watchdogs still blur degraded alerts with wrapper crashes.

 ← Back to Blog
