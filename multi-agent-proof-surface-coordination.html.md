# When Multiple Agents Share the Same Proof Surface

URL: https://anyech.github.io/jingxiao-cai-blog/multi-agent-proof-surface-coordination.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/multi-agent-proof-surface-coordination.html.md
Date: 2026-05-20
Tags: ai-agents, github, pull-requests, proof, staging, coordination, reliability, openclaw, agent-ops

Summary: Staged proof is only low-risk when shared harnesses, fixtures, queues, and scratch state have owners, namespaces, collision checks, and cleanup rules.

---

← Back to Blog
 
# When Multiple Agents Share the Same Proof Surface

 
 May 20, 2026 | By Jingxiao Cai

 Tags: ai-agents, github, pull-requests, proof, staging, coordination, reliability, openclaw, agent-ops
 

 
 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped turn a multi-agent staging risk into a public coordination pattern while keeping examples generic and removing PR identifiers, branch names, raw logs, local paths, and live deployment details.
 

 
 Short version: staged proof is only low-risk if the proof surface is actually isolated. When multiple agents share a harness, fixture, runner, queue, or scratch state, proof needs ownership and collision rules.
 

 

 
 The first post in this mini-series drew the boundary between staged proof and production proof. The second post covered what to do when a reviewer still asks for live proof.

 There is a third trap: assuming that “non-production” automatically means “isolated.”

 This applies whether you are a solo developer running two agents, an open-source maintainer coordinating contributors, or a team operating a shared staging environment. The exact governance model can vary. The invariant is the same: if more than one actor can rely on the same proof surface, that surface needs coordination.

 It does not. A staged runtime can be shared. A fake provider can be shared. A scratch database, mock inbox, CI runner, branch, worktree, cache, or fixture namespace can be shared. If another agent is using the same surface, your proof can interfere with theirs, and theirs can invalidate yours.

 
 Staged proof is only low-risk when the proof surface has ownership.

 

 
 Conceptual scope: this is a sanitized agent-operations write-up and part 3 of a proof-boundary mini-series. I am intentionally omitting exact PR numbers, branch names, commit hashes, check-run counts, bot labels, local worktree paths, session identifiers, channel identifiers, raw terminal transcripts, and live deployment details. The examples are generalized patterns, not transcripts from any single review thread. The public lesson is multi-agent proof coordination.
 

 
## “Staged” Does Not Automatically Mean Isolated

 Agents often use the word “staged” as if it were a safety proof by itself. That is too vague. In this post, a staged runtime means a non-production environment that can execute behavior; a fixture namespace means the named slice of test data or mock responses for one proof run; and a lease window means the time-bound claim that one agent owns a shared surface for a specific proof.

 A staged proof surface can still be shared across multiple agents or humans:

 
 
- one fake service receives requests from several PR tests;
 
- one scratch database contains fixtures from multiple experiments;
 
- one CI queue runs proof jobs from unrelated branches;
 
- one mock inbox receives messages from several delivery tests;
 
- one staged runtime keeps state between runs; or
 
- one agent reuses a worktree that another agent still assumes is stable.
 

 None of those are production. All of them can still corrupt proof.

 
## The Collision Modes

 The collisions are usually boring, which is why they are easy to miss.

 
 
 
 Shared surface
 Failure mode
 What to check
 

 
 
 
 Fake service
 Another agent changes stub behavior or consumes queued responses.
 Service owner, fixture version, request namespace.
 

 
 Scratch database
 Rows from one proof make another proof pass or fail incorrectly.
 Schema namespace, seed manifest, cleanup owner.
 

 
 Mock inbox or outbound sink
 Messages from multiple proof runs look like one behavior trace.
 Run tag, recipient namespace, retention policy.
 

 
 Staged runtime
 State persists between jobs, or one agent restarts a service another agent is using.
 Lease window, restart policy, active users.
 

 
 CI runner or job queue
 Resource contention, cache reuse, or timing artifacts change results.
 Cache key, runner class, queue pressure, retry policy.
 

 
 Branch or worktree
 One agent rebases, cleans, or regenerates files while another proof references the old state.
 Owner, target revision, no-clean/no-rebase window.
 

 
 Shared capacity
 Agents stay in separate namespaces but exhaust the same connection pool, rate limit, disk budget, queue slots, or runner capacity.
 Capacity owner, quota budget, active jobs, backoff policy.
 

 
 

 The important point is that these failures do not require production access. They happen inside the “safe” zone when the safe zone is shared without a contract.

 
## The Coordination Contract

 Before an agent uses a shared proof surface, I want it to answer a short coordination contract:

 proof surface:
 staged runtime / fake service / CI runner / scratch DB / mock inbox / worktree

ownership:
 proof owner: agent or human role
 surface owner: agent, human, or shared service
 lease window: start, stop, timeout

scope:
 target revision: exact revision internally; public-safe revision class in public write-ups
 fixture namespace: name or generated run tag
 allowed operations: read / write / restart / cleanup / no-clean

collision check:
 active users: none / known / unknown
 shared state: yes/no
 collision risk: clear / blocked / needs coordination

cleanup:
 cleanup owner: agent or human role
 cleanup trigger: after proof / after review / manual approval
 retention reason: why anything remains

 This looks longer than it feels. In practice, the agent can fill it in with a few lines. The value is forcing the agent to notice whether it is standing on someone else’s proof surface.

 One important nuance: public write-ups should generalize revisions and surface names, but internal proof manifests should keep the exact revision and artifact identity needed for audit and rerun. Sanitization belongs at the publication boundary, not inside the private proof record.

 A point-in-time active-user check is also not enough for writable, restartable, or cleanup-capable shared surfaces. Before mutating shared state, the agent should acquire or confirm a lease, lock, owner note, or equivalent coordination token.

 
## The Artifact Manifest

 Every shared proof should also leave a small manifest. The manifest is not a transcript dump. It is a map of what was created and who owns it.

 
 
 
 Manifest field
 Purpose
 

 
 
 
 Proof artifact
 Names the generated report, fixture, run tag, staged job, or mock trace.
 

 
 Owner
 Identifies who can update, reuse, or delete it.
 

 
 Target revision
 Prevents reuse against the wrong code state.
 

 
 Input namespace
 Separates one proof run from another.
 

 
 Cleanup rule
 Explains when the artifact should be removed, archived, or preserved.
 

 
 Referenced by
 Links the artifact to the proof packet or review comment that depends on it.
 

 
 

 Without this manifest, future agents have to guess whether a file, fixture, or queue item is live evidence, stale evidence, scratch residue, or someone else’s active proof.

 
## Do Not Clean What You Do Not Own

 Cleanup is part of proof hygiene, but cleanup can also be destructive.

 An agent should not delete a shared fixture, mock trace, staged artifact, or scratch directory just because its own proof is done. It should first check ownership and active references.

 The safe cleanup rule is:

 
 Clean your namespace by default. Clean shared state only with ownership or explicit approval.

 

 This is the same reason agents should be careful with PR queues. The issue is not only whether the artifact is useful to this agent. The issue is whether another agent or reviewer still depends on it.

 There also needs to be a plan for orphaned state. If an agent crashes mid-proof, its namespace should have a time-to-live, lease expiry, or garbage-collection rule so a shared scratch database, mock inbox, or staged job does not become permanent mystery state. Cleanup automation should still respect ownership; it should remove expired namespaces, not sweep unrelated shared state.

 
## Proof Packets Need a Coordination Boundary

 The proof packet from the previous posts already had environment, freshness, approval, and cleanup fields. For shared surfaces, I would add a coordination boundary:

 coordination boundary:
 proof owner: agent or human role
 shared surface: yes/no
 active users checked: yes/no/unknown
 fixture namespace: run tag or isolated namespace
 collision check: clear / blocked / needs coordination
 cleanup owner: agent or human role
 retention reason: remove / keep until review / keep for audit

 The uncomfortable value is the “unknown” option. If the agent cannot determine whether other users exist, it should not pretend the surface is isolated.

 
## A Tiny Admission Gate

 Before running proof on a shared non-production surface, the agent should perform a tiny admission gate. This should be an automated or programmatic lease-and-namespace check where possible, not a human bureaucracy ritual for every small proof run:

 
 
- Identify the proof surface and whether it is shared.
 
- Check active users, active jobs, leases, owner notes, and shared capacity limits.
 
- Allocate a unique namespace or run tag.
 
- Record the target revision and fixture shape.
 
- Define cleanup ownership and retention.
 
- Only then run the proof.
 

 If any of those are blocked, the agent should say so. “I could not prove this safely because the staged surface is shared and ownership is unclear” is a valid outcome. If the surface reports active users as “unknown,” default to “needs coordination” rather than pretending the surface is isolated.

 
 The useful invariant: non-production proof should have the same ownership hygiene as public PR review surfaces.
 

 
## Conclusion

 Non-production proof is the right default. But non-production is not magic. A shared staged surface can still create false confidence, false failures, stale evidence, or accidental interference.

 The durable habit is simple: name the proof owner, isolate the fixture namespace, check for concurrent users, record the artifact manifest, and clean only what you own.

 Proof should reduce uncertainty. It should not become another agent’s hidden source of drift.

 
 
### Related Posts

 
 
- When Reviewers Still Ask for Live Proof
 
- Proof Expires
 
- Proof Without Touching Production
 
- Before Opening Another Agent PR, Reduce the Queue First
 

 

 
 
### About the Author

 Jingxiao Cai works on AI/ML infrastructure and writes about self-hosted agents, automation reliability, and the operational boundaries that keep systems understandable.

 A staged harness is private only if someone made it private.

 

 

 
 
## Comments

 Found this useful? Leave a comment below, or send it to someone whose agents all think the staging harness belongs to them.

 ← Back to Blog
