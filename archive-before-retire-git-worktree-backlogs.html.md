# Archive Before You Retire: A Transaction Model for Git Worktree Backlogs

URL: https://anyech.github.io/jingxiao-cai-blog/archive-before-retire-git-worktree-backlogs.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/archive-before-retire-git-worktree-backlogs.html.md
Date: 2026-08-15
Tags: git, devops, agent-ops, recovery, automation, reliability

Summary: Stale worktrees are not safe to delete just because they look old. Archive-preserve transactions make recovery requirements and protected-tip drift checks explicit.

---

[← Back to Blog](/jingxiao-cai-blog/)

# Archive Before You Retire: A Transaction Model for Git Worktree Backlogs


 **August 15, 2026** | By Jingxiao Cai

 Tags: git, devops, agent-ops, recovery, automation, reliability



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a completed cleanup into a public-safe transaction model and separate recoverability evidence from private paths, branch names, identifiers, and archive topology.



 **Short version:** a stale worktree is not safe to remove merely because its branch looks old. Preserve and read back the exact tip, preserve dirty and untracked state through the right mechanism, retire the checkout before its ref, and treat an observed protected-tip mismatch as a stop rather than a change this transaction can prevent.


 Git worktrees make parallel work cheap. They also make stale state easy to accumulate.

 Eventually the repository contains a mix of clean checkouts, dirty experiments, branches that were integrated another way, branches that were superseded, and directories whose original owner is no longer active. At that point, “delete the old worktrees” is not a cleanup plan. It is a request to classify history, preserve recovery options, and perform a batch of conditional state transitions.


 **Retirement should be an archive-preserve transaction, not a sequence of optimistic delete commands.**




 **Conceptual scope:** this is a sanitized Git and agent-operations pattern. The proof unit models one clean candidate, one dirty candidate, and a protected branch. It omits real paths, branch names, commit hashes, session identities, batch size, private archive layout, and operational transcripts.



## Three Decisions That Look Like One

 A worktree backlog mixes three different decisions:



- **Semantic disposition:** should this candidate be integrated, rejected, superseded, or retained for review?

- **Recovery preservation:** what exact state must remain reachable if the retirement decision is wrong?

- **Physical retirement:** when may the branch name, worktree registration, and checkout directory be removed?


 Those decisions should not collapse into one heuristic such as “merged,” “old,” or “clean.” Patch equivalence can require human judgment. A clean index does not prove the branch tip is safely anchored elsewhere. A commit snapshot does not preserve untracked or ignored bytes. An archive ref does not prove a physical checkout can be restored.

 The safe sequence is therefore conservative: classify first, preserve second, retire last.


## The Transaction State Machine



| State | Required evidence | Stop condition |
| --- | --- | --- |
| **Discover** | Exact worktree registration, branch tip, index/worktree status, and ownership signals. | Candidate identity is incomplete or changes during inventory. |
| **Classify** | Explicit semantic disposition and the recovery material required for that class. | Integration, supersession, or ownership is ambiguous. |
| **Anchor** | Create-only archive reference for the exact tip; durably reachable anchors for tracked/index dirt; sensitivity-reviewed physical payload plus per-path digests for included untracked or ignored bytes. | Archive destination conflicts or the source object changed. |
| **Read back** | Archive references resolve to the expected objects and physical artifacts match manifest identities and content digests within the declared storage and retention boundary. | Any anchor is missing, mismatched, or unreadable. |
| **Retire** | No active owner or in-progress Git operation remains; retire the registered checkout first, then delete the branch ref only if its object ID still matches inventory. | Source drift, active ownership, lock, or unexpected filesystem state. |
| **Verify** | Original names/registrations are absent as intended, recovery anchors remain reachable, and the protected tip still matches the recorded observation. | Any protected invariant or recovery read-back fails. |

 This is not a distributed transaction in the database sense. Git references and filesystem moves do not magically share one atomic commit. The value of the model is that it makes the ordering and stop rules explicit.


## A Safe Proof Unit: One Clean and One Dirty Candidate

 The smallest useful reproduction needs only three logical branches:



- a protected branch that must never move;

- a clean candidate whose exact tip must remain reachable;

- a dirty candidate whose tip and tracked/index changes require separate recovery anchors.




```
expected_protected_tip = protected_branch.tip

for candidate in inventory:
    expected_tip = candidate.tip

    disposition = human_review(candidate)
    anchors = create_required_anchors(candidate, disposition)
    assert read_back(anchors)

    assert candidate.tip == expected_tip          # source did not drift
    assert protected_branch.tip == expected_protected_tip
    assert no_active_owner(candidate)

    retire_registered_checkout(candidate)
    retire_original_name_compare_and_swap(candidate, expected_tip)

    assert read_back(anchors)
    assert protected_branch.tip == expected_protected_tip
```

 That order is deliberate. Git porcelain refuses to delete a branch that a linked worktree still uses. A ref-level expected-object deletion can bypass that refusal but leave a broken registration. After anchors have read back, the safer interruption is therefore “the branch still exists without a registered checkout,” followed by a ref-level delete conditioned on the expected object ID.

 Compare-and-swap applies only to the reference transition. It does not atomically include linked-worktree registration or filesystem removal. A concrete implementation must document and test its ordering, honor checked-out-branch protections, and keep every intermediate state recoverable and reportable. A porcelain refusal is a safety signal, not an obstacle to bypass silently.

 The pre-retirement reads are observations, not leases. Without an external exclusion mechanism, another writer can race the interval between the last tip and ownership checks, checkout removal, and expected-object ref deletion. Checkout-before-ref ordering deliberately makes the safe late-race result “anchors verified, checkout retired, branch retained.” Expected-object deletion protects the ref value at deletion time; it does not guarantee that every drift after inventory leaves the checkout intact, and equality checks do not reveal an out-and-back change.

 Registered-checkout removal refuses by default when a worktree is modified, untracked, or locked. Treat that refusal as the transaction's last honest stop. Forced removal deletes the working directory, including excluded untracked or ignored bytes. Escalate only after required anchors and per-path digests read back, and only after recording which excluded paths will be destroyed intentionally and cannot be recovered from the archive.

 The proof should inject at least two failures:



- **Source-object drift:** inject a mismatch before the final pre-retirement gate; the original branch and checkout must remain. Inject a second mismatch after that gate but before expected-object ref deletion; the checkout may already be retired, but the branch ref must remain and the partial result must stop for reconciliation.

- **Archive collision:** pre-create the intended archive destination with a different object. The item must stop rather than overwrite or silently choose another identity.


 Those negative tests matter more than a happy-path deletion count. They prove the process knows when it is no longer executing the reviewed transaction.


## Dirty State Has More Than One Shape

 “Dirty” is not a complete recovery instruction. Different state needs different preservation:



| State | Recovery anchor | Important boundary |
| --- | --- | --- |
| Clean tracked checkout | Exact tip archive ref. | Still verify the ref before removing the original name. |
| Tracked or index changes | One or more durably reachable snapshot anchors plus the original tip. | Test staged and unstaged content, deletions, modes, and submodule state; route an unmerged index with conflict stages to stop-and-inspect. An unreferenced object is not a durable anchor. |
| Untracked or ignored files | Sensitivity-reviewed physical payload archive and manifest with per-path content digests. | Git refs cannot preserve untracked bytes; record intentional exclusions and stop if an exclusion defeats the restore claim. |
| In-progress Git operation | Stop and inspect. | Do not snapshot or retire through a merge, rebase, bisect, or other unresolved operation. |

 A restore guide should say exactly which mechanism preserves which class. “Everything was archived” is too vague if some bytes live only in a physical payload while other state is reachable through Git objects. A path-only manifest proves presence, not integrity; record and verify a content digest for every preserved path.

 Ignored files are also a sensitivity boundary. Credentials, tokens, generated data, special files, links, and mounts often live there. Decide exclusions, destination access, retention, and expiry before creating a payload archive, and never turn “preserve untracked state” into “copy secrets blindly.” An intentional exclusion narrows the restore claim; removing the checkout destroys that excluded local byte unless another reviewed copy exists.


## Protected-Tip Equality Is a Detector, Not a Lock

 A backlog cleanup should not intend to rewrite the protected branch. If candidates are obsolete or already integrated, retirement can preserve their exact tips under archive-qualified references without merging them into the protected line.

 Record the protected tip before the batch. Check it before each risky transition if the environment is highly concurrent, and always check it again at closeout. Also verify any protected config or policy files whose bytes must remain unchanged.

 This check detects a net mismatch at an observation point; it does not prevent movement, attribute causality, or reveal every transient out-and-back change. Git provides no cross-ref transaction that binds one branch's retirement to another branch staying still. If the closeout observation differs, stop the batch and reconcile rather than silently re-baselining. Recovery anchors make that partial state diagnosable.


 **Completion claim:** the backlog is retired only when recovery anchors read back, original state is absent by design, and the protected-tip observation still matches. A smaller worktree count by itself is not proof.



## What Compare-and-Swap Buys You

 The inventory is a point-in-time claim. Between discovery and retirement, another process can move a branch, create an archive destination, or acquire the checkout. Ref-level compare-and-swap means creating an archive ref with create-only semantics when its destination must be absent and deleting an original ref only when it still names the expected object. Those preconditions turn observed source-ref mismatch into per-item stops instead of silent deletion.

 Deleting the original branch ref also removes that branch's reflog. Recovery cannot depend on the deleted name's prior-tip history; every required tip or pre-rewrite state must be carried by an anchor that survives independently.

 The important behavior is not “retry until it works.” It is “the reviewed precondition no longer holds, so leave this candidate untouched and return it to review.” A large batch may therefore complete partially: safe items retire, drifted items remain, and the report names both outcomes honestly.


## Session and Process Ownership Come Before Filesystem Cleanup

 Agent-managed worktrees add another recovery surface: a paused session or live process may still assume its old working directory exists. A clean Git status does not prove the path is unowned.

 Before physical retirement, inspect:



- live processes whose current working directory or open files point into the checkout;

- paused or resumable sessions that persist the path as their work root;

- worktree administrative pointers and back-references;

- symlinks, hardlinks, mounts, or external references that make a move non-local;

- in-progress Git operations, locks, and unreviewed changes since inventory.


 If ownership is ambiguous, preserve the candidate and stop. Cleanup is not improved by turning a recoverable stale checkout into a broken active session.

 An ownership check narrows a race; it does not close one. A paused session can resume between the check and retirement. Where tooling supports it, hold an administrative lock across that window; otherwise treat ownership inspection as evidence of diligence, not proof of exclusivity.


## When Not to Use This Pattern Blindly

 The transaction model teaches ordering; it is not a universal deletion script. Add implementation-specific checks for submodules, sparse checkouts, alternate object databases, cross-filesystem moves, linked worktree metadata, network filesystems, and external backup media.

 An archive ref is a reachability anchor inside the same repository, not an independent backup. “Durably reachable” here means retained and read-back-verifiable within the declared repository storage and retention boundary; it does not establish backup durability or physical-checkout restoration. Garbage-collection protection, repository loss, and restore testing are separate concerns. Read-back proves presence and identity; claim successful recovery only after a representative restore rehearsal.

 Do not use archive-preserve retirement as a substitute for semantic review. If a candidate may contain valuable unintegrated work, determine that first. Do not call two branches equivalent merely because a patch looks similar. Do not remove an active checkout to satisfy a cleanliness metric.


## The Checklist I Would Reuse



- Freeze a point-in-time inventory with exact object identities.

- Classify semantic disposition separately from physical retirement.

- Identify tracked, index, untracked, ignored, and in-progress state.

- Create archive destinations with create-only, no-overwrite semantics.

- Read back every required Git anchor and every physical payload digest.

- Check process, session, pointer, and filesystem ownership; hold an administrative lock where available.

- Revalidate source and protected-branch identities.

- Retire each registered checkout first, then its original ref under an expected-object compare-and-swap precondition.

- Verify anchors again, rehearse a representative restore, compare the protected-tip observation, and write a restore guide.

- Report stopped items as stopped; do not hide them behind a batch success count.



 **Falsifier:** this pattern has failed if branch-ref deletion proceeds after an observed source mismatch or expected-object failure, a late-race partial state is hidden instead of reconciled, an archive destination is overwritten or silently renamed, included untracked bytes lack verified manifest digests, a recovery anchor cannot be read back after retirement, a stopped candidate is hidden inside a batch success count, or the protected tip at closeout differs from the recorded observation without stopping reconciliation.



## Conclusion

 Worktree cleanup becomes dangerous when it is framed as deleting directories and branch names. The real job is preserving exact recovery state while changing which names and checkouts remain active.

 Archive first. Read it back. Stop on an observed mismatch. Retire the checkout before its ref, and make the ref transition conditional on the expected object. Then compare the protected-tip observation, reconcile any movement or partial result, and ensure a future operator can understand and restore what was preserved.

 That is the difference between a smaller worktree list and a defensible cleanup.



### Related Posts



- [Thread Affinity Is a Safety Boundary for Agent Work](/jingxiao-cai-blog/thread-affinity-safety-boundary-agent-ops.html)

- [When Multiple Agents Share the Same Proof Surface](/jingxiao-cai-blog/multi-agent-proof-surface-coordination.html)

- [When a Dirty-Tree Alert Is Correct](/jingxiao-cai-blog/dirty-tree-alert-review-artifact-agent-ops.html)

- [Proof Without Touching Production](/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, automation reliability, and the operational boundaries that keep small systems understandable.

 A cleanup is complete when recovery anchors and closeout checks read back—not when the list merely gets shorter.




## Comments

 How do you make stale worktree retirement recoverable without turning cleanup into a permanent platform?

 [← Back to Blog](/jingxiao-cai-blog/)
