# Proof Expires: Why Agent PR Evidence Needs a Refresh Window

URL: https://anyech.github.io/jingxiao-cai-blog/agent-pr-proof-expiration-refresh-window.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/agent-pr-proof-expiration-refresh-window.html.md
Date: 2026-05-18
Tags: ai-agents, github, pull-requests, proof, staging, reliability, openclaw, agent-ops

Summary: Agent PR proof can be true and stale at the same time; cite old evidence with freshness labels, target revisions, and refresh triggers.

---

← Back to Blog

# Proof Expires: Why Agent PR Evidence Needs a Refresh Window


 May 18, 2026 | By Jingxiao Cai

 Tags: ai-agents, github, pull-requests, proof, staging, reliability, openclaw, agent-ops



 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped extend a proof-boundary discussion into a reusable freshness rule while keeping examples generic and removing PR identifiers, branch names, raw logs, local paths, and live deployment details.



 Short version: behavior proof for an agent-authored PR can expire. A proof packet should say when it was captured, what revision it covered, what changed since then, and which events require refresh.





 The previous rule was about blast radius: if an agent-authored pull request needs behavior proof, start with isolated or staged evidence before touching production.

 That rule is necessary, but it is not enough. A proof packet can be safe, accurate, and still become stale.

 The subtle failure mode is not that the old proof was fake. It may have been perfectly honest when it was captured. The failure is treating that old evidence as if it still describes the current code, current review concern, current integration contract, or current staged harness.


 A green check can become historical evidence without becoming a lie.




 Conceptual scope: this is a sanitized agent-operations write-up and part 1 of a proof-boundary mini-series. I am intentionally omitting exact PR numbers, branch names, commit hashes, check-run counts, bot labels, local worktree paths, session identifiers, channel identifiers, raw terminal transcripts, and live deployment details. The examples are generalized patterns, not transcripts from any single review thread. The public lesson is proof freshness.



## Old Proof Is Not Always Current Proof

 Agents are good at producing artifacts: a test transcript, a focused regression run, a staged harness result, a fake integration trace, a short comment saying what passed. Once that artifact exists, it is tempting to keep pointing at it.

 But PRs move. Review concerns move. The target branch moves. The harness can move too.

 That means proof has two separate properties:



- truth at capture time: did the evidence honestly exercise the behavior it claimed to exercise?

- freshness at review time: does that evidence still apply to the code and concern being reviewed now?


 A proof packet can pass the first test and fail the second. That is not a reason to discard it. It is a reason to downgrade it from current proof to historical evidence.


## What Makes Proof Expire?

 The refresh trigger should be explicit. These are the common ones I want agents to notice:




 Refresh trigger
 Why old proof may no longer apply
 Safer response





 Target branch changed
 The patch may now sit on different surrounding code, dependencies, or defaults.
 Re-run the focused gate after rebase or merge-base change.



 Patch changed
 The proof may cover the old diff but not the latest review surface.
 Re-state what changed and re-run the affected proof level.



 Integration contract changed
 A fake provider, chat surface, webhook, or gateway harness may no longer match the real contract it represents.
 Check the fixture shape or contract stub before reusing the result.



 Reviewer concern changed
 The original proof answered one claim, while the new review is asking a different question.
 Map the new concern to a new proof surface instead of repeating the old result.



 Time window elapsed
 Long-lived PRs can drift even without obvious source changes: dependencies, CI images, generated baselines, and external assumptions age.
 Treat old evidence as a baseline and refresh the smallest meaningful check.



 Harness drift suspected
 The staged runtime or synthetic fixture may have evolved separately from the code under review.
 Verify the harness first; do not use it as proof until its shape is known.





 The key is not to re-run everything all the time. The key is to know which event invalidates which claim.


## Refresh the Claim, Not Just the Command

 A common agent mistake is to answer staleness with a blind rerun:

 old command passed before
same command passed again
therefore proof refreshed

 Sometimes that is enough. Often it is not. The agent first needs to restate the claim:



- What behavior is this PR claiming to fix or protect?

- What environment did the proof exercise?

- What changed since the evidence was captured?

- Does the old proof surface still exercise the disputed behavior?

- What does the proof still not prove?


 Only then does the agent know whether to re-run the same check, adjust the synthetic fixture, update the fake integration harness, or ask whether a different proof surface is required.


 The useful invariant: proof freshness is measured against the claim under review, not against the agent's memory that some command once passed.



## The Proof Packet Needs a Freshness Boundary

 By proof packet, I mean the public-safe evidence summary that travels with a PR: the behavior claim, the proof surface, the environment boundary, the commands or checks, the result, the limits, and the next review action. It is not raw logs. It is the reviewer-facing map of what was proven and what was not.

 The original proof packet already named the proof surface, environment boundary, side effects, approval, cleanup, and limits. I would add one more block:

 freshness boundary:
 proof captured at: date / revision / staged run label
 target revision: branch or commit class, generalized if public
 refresh trigger: rebase / patch changed / contract changed / reviewer concern changed / time window expired
 changed since proof: short summary
 still valid because: short reason, or "not current; refresh needed"

 That last line is the discipline. If the agent cannot explain why the proof is still valid, the proof should be treated as stale until refreshed.

 This also helps reviewers. Instead of reading a vague “proof supplied” comment and wondering whether it covers the current PR state, they can see the proof's target and its freshness boundary.


## When Stale Proof Blocks vs. Downgrades

 Stale proof does not always mean “block everything.” The decision depends on whether the stale proof is the only evidence for a claim that still matters.




 State
 How to label it
 Action





 Old proof covers unchanged code and unchanged reviewer concern
 Current enough, with freshness note
 Keep it, but state why it still applies.



 Old proof covers the old diff, but the changed claim is elsewhere
 Historical evidence
 Keep it as context and refresh only the affected proof surface.



 Old proof is the only evidence for a behavior that changed
 Stale / not current
 Block the proof claim until refreshed or explicitly scoped down.



 Harness, fixture, dependency, CI image, permission shape, or config shape may have drifted
 Proof environment uncertain
 Verify the proof environment before trusting the behavior result.



 Time passed but no relevant surface changed
 Freshness review needed
 Use time as a prompt to check, not automatic invalidation.





 If a team needs a default time rule, I would keep it deliberately soft: refresh before asking for final review or merge if meaningful evidence is more than a few days old, and always refresh after a rebase, merge-conflict resolution, material patch change, harness/config change, or changed reviewer concern. Time alone is a smell; changed claim coverage is the blocker.


## Historical Evidence Still Has Value

 Stale proof is not worthless. It can still be useful in several ways:



- it shows that the agent understood the original behavior claim;

- it gives a known-good command or harness shape to rerun;

- it helps isolate whether a later failure came from the patch, the target branch, or the proof environment;

- it documents why a reviewer previously accepted or rejected a claim; and

- it gives future agents a starting point instead of a blank page.


 The mistake is not keeping old evidence. The mistake is keeping it unlabeled.


## A Lightweight Refresh Policy

 I do not want agents to turn every PR update into a full proof rebuild. The policy should be small:



- Before citing proof, check freshness. Compare the proof packet against the current target, current diff, and current reviewer concern.

- After rebase, merge-conflict resolution, or meaningful patch change, rerun the smallest proof surface that exercises the changed claim. Smallest does not mean shallow: if the changed claim crosses layers, the refreshed proof must cross those layers too.

- When the reviewer asks a new question, map it to a new proof claim. Do not keep repeating an old answer.

- When the harness may have drifted, verify the harness before trusting the result. Include fixture data, dependency versions, CI images, generated baselines, permission scopes, config shapes, and external contract assumptions.

- If the proof is stale and cannot be refreshed safely, say so. Mark it historical and block or escalate honestly.


 This is not bureaucracy. It is what keeps proof from becoming a cargo-cult artifact.


## What Agents Should Stop Saying by Default

 There are a few phrases I want agents to avoid as defaults:



- “Proof already supplied.” Supplied when, against what revision, and for which claim?

- “CI was green.” Which check exercised the behavior? Was it after the latest change?

- “The staged run passed.” What did the staged run simulate, and has the harness drifted?

- “No need to rerun.” Why not? What refresh trigger did you check?


 Better phrasing is more precise:

 The prior proof is historical evidence for the old diff.
After the rebase, I reran the focused staged harness that exercises the changed delivery path.
The refreshed proof covers the current patch, but it still does not prove live production behavior.

 That is longer, but it tells the truth.


## Conclusion

 Agent PR proof needs a freshness boundary. Without one, old evidence can quietly become a stale credential for trust.

 The durable rule is simple: keep the proof, label the proof, refresh the proof when the claim or target changes, and downgrade old proof to historical evidence when it no longer covers the current review surface.

 Proof should age visibly. If it does, reviewers can trust it more, not less.



### Related Posts



- Proof Without Touching Production

- Before Opening Another Agent PR, Reduce the Queue First

- Building Fail-Closed Stage Environments for AI Agents on a Small VPS

- When a Coding-Agent Route Drifts






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, automation reliability, and the operational boundaries that keep small systems understandable.

 A proof packet can be true and stale at the same time.







## Comments

 Found this useful? Leave a comment below, or send it to someone whose agent is still citing proof from three rebases ago.

 ← Back to Blog
