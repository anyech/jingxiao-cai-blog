# When a Dirty-Tree Alert Is Correct: Classify the Artifact Before You Commit

URL: https://anyech.github.io/jingxiao-cai-blog/dirty-tree-alert-review-artifact-agent-ops.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/dirty-tree-alert-review-artifact-agent-ops.html.md
Date: 2026-05-25
Tags: ai-agents, git, automation, debugging, reliability, openclaw, agent-ops

Summary: An automated repository-health alert exposed a boundary problem: classify disposable review scaffolding, retained evidence, and intentional source changes before acting.

---

← Back to Blog
 
# When a Dirty-Tree Alert Is Correct: Classify the Artifact Before You Commit

 
 May 25, 2026 | By Jingxiao Cai

 Tags: ai-agents, git, automation, debugging, reliability, openclaw, agent-ops
 

 
 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped turn a repository-health recovery into a reusable agent-ops pattern while removing thread identifiers, local paths, branch names, raw alerts, commit hashes, and deployment-specific details.
 

 
 Short version: a dirty-tree alert is not automatically noise. Treat it as a classification prompt: decide what is durable evidence, what is disposable workspace state, and what policy gap let the artifact appear.
 

 The alert was annoying because it arrived from an automated maintenance workflow that is supposed to be boring. A repository-health check found unexpected workspace changes, and the tempting response was to make the tree clean as quickly as possible.

 That would have been the wrong first move. The alert was not a false positive. It was pointing at a real boundary problem: review-local artifacts had landed in a place where automated git hygiene could see them.

 
 Do not answer a dirty-tree alert with blind cleanup. Answer it with artifact classification.

 

 
 Conceptual scope: this is a sanitized OpenClaw agent-operations story. I am intentionally leaving out exact thread identifiers, channel identifiers, branch names, review directory names, commit hashes, local filesystem paths, raw terminal output, schedules, and live deployment details. The public lesson is the recovery pattern, not my local fingerprint.
 

 
## The Failure Shape

 The maintenance alert looked like a simple dirty repository. Underneath it were three different kinds of material:

 
 
 
 Material
 What it meant
 Correct handling
 

 
 
 
 Review-local source checkout
 A disposable copy of source code used for analysis appeared under the automation-visible workspace. In some workflows a review checkout can be the work product itself; here the important question is whether it is intentional source, retained evidence, or scratch scaffolding.
 Do not commit it. Add narrow ignore coverage or move it outside the watched area.
 

 
 Completed evidence bundle
 Small result files captured useful proof from completed work.
 Preserve the durable evidence only if it is safe, intended to be retained, and small enough to justify keeping.
 

 
 Recovery notes
 The incident itself taught a recurring workflow boundary.
 Record the lesson in a durable, sanitized checkpoint or protocol note.
 

 
 

 One alert, three categories. If an agent collapses those categories into “dirty tree,” it will either commit too much or delete useful evidence.

 
## Why the Alert Was Correct

 The automated guard was doing its job. A broad source checkout under a review workspace can contain generated files, local dependency state, copied configuration, test output, or other material that does not belong in the main repository history.

 Ignoring the alert would make the guard useless. Committing everything would make the repository worse. Deleting everything would risk losing the evidence that explained why the alert happened.

 The right conclusion was narrower: the guard had found a real artifact-shape gap. The fix was not “turn off the guard.” The fix was to teach the workspace policy that disposable source checkouts are different from retained result bundles.

 
## The Recovery Ladder

 The recovery path I want agents to use is intentionally mechanical:

 
 
- Freeze the situation. Stop adding unrelated changes until the dirty-tree shape is understood.
 
- Classify each path. Label every changed or untracked path as source change, durable evidence, disposable workspace state, generated output, or unknown.
 
- Preserve before pruning. If evidence is useful, keep a small retained artifact or checkpoint before deleting bulky scratch state; if it contains sensitive material, sanitize, truncate, or reject retention fail-closed.
 
- Patch the policy narrowly. Add narrow `.gitignore` or equivalent ignore coverage for the disposable shape, not a broad pattern that hides future real changes.
 
- Verify the clean state. Run the smallest meaningful gate: status, ahead/behind check, secret scan if new text was retained, and the maintenance dry run when available. If the secret scan fails, retention stops until the artifact is sanitized, truncated, or removed.
 
- Record the reopen criteria. Make it clear what future alert should reopen the incident versus what is now expected behavior.
 

 
 The useful invariant: a repository-health bot should never be trained to ignore “dirty.” It should be given better categories for why a path is dirty.
 

 
## Durable Evidence Is Not the Same as Scratch State

 This distinction matters more as agents do more review work.

 A disposable checkout is operational scaffolding, not automatically trash. It may be large, transient, branch-specific, and full of files that only exist because a reviewer needed a local reproduction. A retained evidence bundle is different: it is the small proof packet that says what happened, what passed, what failed, and what should happen next. Useful evidence still needs a retention decision; do not preserve bulky or sensitive artifacts just because they explain the alert.

 Both can appear during the same incident. The cleanup plan should not treat them the same way.

 
 
 
 Question
 If yes
 If no
 

 
 
 
 Is this the actual source change the agent meant to make?
 Review, test, and commit intentionally.
 Do not sweep it into a generic cleanup commit.
 

 
 Is this small, sanitized evidence that future agents need?
 Preserve it with a clear manifest or checkpoint.
 Archive or remove after confirming nothing durable is lost.
 

 
 Is this a full source checkout, dependency cache, build output, or scratch reproduction?
 Ignore or relocate it using a narrow pattern, such as a specific scratch-workspace path rather than a broad source-tree wildcard.
 Keep investigating before deleting or committing.
 

 
 Does this path contain secrets, credentials, private identifiers, or deployment fingerprints?
 Stop and sanitize fail-closed before any public or durable write.
 It may still be private; lack of obvious secrets is not enough.
 

 
 

 
## The Concurrency Trap

 There was one more agent-specific wrinkle: multiple workers can touch the same repository close together. During recovery, one worker may stage evidence while another is trying to prove that the tree is clean. A human operator can usually notice this social context. An unattended agent needs an explicit habit.

 The habit is simple: avoid history rewrites and broad resets during shared-agent cleanup unless the scope is absolutely clear. Prefer small follow-up commits, explicit status checks, and written handoffs over “make it clean” commands that erase another worker’s partial evidence.

 For agent systems, a dirty tree can be a technical signal and a coordination signal at the same time.

 
## What I Would Encode as Policy

 The policy I would carry forward is:

 
 
- Review workspaces may contain source checkouts, but each checkout needs classification: intentional work product, retained evidence, or disposable scaffolding.
 
- Durable result bundles are allowed, but they need manifests, sanitization, and clear ownership.
 
- Ignore rules should be narrow, tied to specific artifact shapes rather than broad “review/**” erasure.
 
- Secret scans should run on retained text, especially when evidence is promoted from scratch space to durable memory; a failed scan means sanitize, truncate, or discard before retention.
 
- Final verification should include both cleanliness and synchronization, because a clean local tree that is still ahead, behind, or unpushed is not the same operational state.
 

 This is not glamorous infrastructure. It is the boring line between a repository that stays trustworthy and one that slowly fills with accidental reviewer leftovers.

 
## Conclusion

 The lesson from the alert is not “dirty-tree jobs are noisy.” The lesson is that a dirty tree is a request for classification. This example is git-native, but the habit transfers to any version-control workflow where scratch artifacts and intentional changes can share a workspace.

 If the artifact is disposable scaffolding, keep it out of history. If it is durable evidence, preserve it deliberately only after a retention and sanitization decision. If it is a policy gap, patch the policy narrowly. If another worker may be involved, coordinate through status and follow-up commits instead of rewriting the ground underneath them.

 A good repository-health guard should make agents slower for a few minutes and safer for months. That is a trade I will take.

 
 
### Related Posts

 
 
- Proof Without Touching Production: A Safer PR Boundary for Agents
 
- When a Reviewer Demands Live Proof: An Agent Escalation Pattern
 
- When the Report Exists but Delivery Failed: An Agent-Ops Triage Pattern
 
- True Alert, Wrong Page: An Agent-Ops Triage Pattern
 

 

 
 
### About the Author

 Jingxiao Cai works on AI/ML infrastructure and writes about self-hosted agents, automation reliability, and the operational boundaries that keep small systems understandable.

 A dirty tree is not a verdict. It is a prompt to classify the artifacts before acting.

 

 
## Comments

 Have a similar cleanup rule for agent-maintained repositories? Leave a comment below, or send this to someone whose bots still treat every dirty tree as the same kind of problem.

 ← Back to Blog
