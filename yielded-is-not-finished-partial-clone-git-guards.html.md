# Yielded Is Not Finished: Guarding Partial-Clone Git Scans Without Breaking Git

URL: https://anyech.github.io/jingxiao-cai-blog/yielded-is-not-finished-partial-clone-git-guards.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/yielded-is-not-finished-partial-clone-git-guards.html.md
Date: 2026-08-23
Tags: git, ai-agents, reliability, agent-ops, tooling, debugging

Summary: A yielded Git command can remain alive and materialize missing history. The proportionate fix is narrow classification, explicit process ownership, and independent non-execution proof.

---

[← Back to Blog](/jingxiao-cai-blog/)

# Yielded Is Not Finished: Guarding Partial-Clone Git Scans Without Breaking Git


 **August 23, 2026** | By Jingxiao Cai

 Tags: git, ai-agents, reliability, agent-ops, tooling, debugging



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped separate a private resource incident from a public-safe command classifier, ownership model, and falsifiable denial proof.



 **Boundary:** this is an accidental resource-exhaustion control, not a security sandbox or a universal Git cost model. The public proof omits repository identity, host capacity, paths, timestamps, process identifiers, exact storage figures, and private workload details.


 An agent tool returned control after launching a broad Git scan. The easy mistake was to read that as completion.

 The process was still alive. In a partial clone, a broad history or object walk can fetch missing objects on demand, and later maintenance can amplify temporary allocation. The caller had yielded, but the resource owner had not finished.


 **Yielded is a scheduling state. Finished is a terminal state.**



 The right response was not “ban Git.” It was to identify the reproduced command families, give every long-running process an owner and deadline, and prove that the narrow guard stopped those canaries without blocking ordinary work.


 **What the evidence establishes:** a bounded private observation found a still-live yielded process while hidden allocation grew. A separate sanitized fixture proves classification, ownership, and non-execution checks for the reproduced command families. It does not attribute every byte in the historical incident to one Git mechanism.



## The Failure Chain



```
broad historical scan in a partial clone
  → missing objects may be fetched on demand
  → maintenance may amplify temporary allocation
  → the caller yields while the process tree remains alive
  → storage pressure continues without an owner or reap path
```

 Each arrow is plausible and operationally useful, but the chain still needs careful wording. A private incident can show the process tree and storage movement without proving the exact split among fetching, repacking, open-file retention, and filesystem recovery.

 That limitation changes the claim. I can justify a guard for the reproduced incident class. I cannot claim a complete causal model for every partial-clone disk spike.


## The State Model the Tool Needed



| State | Meaning | Owner obligation |
| --- | --- | --- |
| **Running** | The process is active and the caller is still attached. | Track identity, deadline, output, and resource signals. |
| **Yielded** | Control returned before the process terminalized. | Persist an owner, poll path, cancellation path, and deadline. |
| **Cancellation requested** | The owner asked the process tree to stop. | Wait for and verify the actual terminal state. |
| **Reaped** | The process tree is gone and terminal output/state was read back. | Reconcile the claimed effect and remaining resource state. |
| **Completed** | The command reached a verified terminal outcome. | Only now may the caller make a completion claim. |

 A timeout alone is not ownership. Neither is returning a session handle. The process must have a named owner that can poll, cancel, reap, and reconcile it after the original call yields.


## A Narrow Classifier Beats a Global Git Ban

 The sanitized reproduction distinguishes five shapes:



| Command shape | Guard result | Reason |
| --- | --- | --- |
| Ordinary status inspection | Allow | No broad object or history walk. |
| Bounded single-reference history | Allow | The scope is explicit and narrow. |
| Broad content search across history | Block in protected partial clones | Matches a reproduced materialization family. |
| Broad object enumeration | Block in protected partial clones | Matches the second reproduced family. |
| Same broad scan with a no-lazy-fetch override | Allow to fail rather than materialize | The operator explicitly chooses a bounded failure mode. |

 The classifier should consider both the command shape and repository context. A pattern that is risky in a protected partial clone may be acceptable in a disposable full clone. That is why a global alias, blanket shell restriction, or universal Git disablement would be disproportionate.



```
if repository_is_protected_partial_clone:
    if command_matches_reproduced_broad_scan:
        if explicit_no_lazy_fetch_override:
            allow_bounded_failure()
        else:
            deny_with_diagnostic()
    else:
        allow_ordinary_git()
else:
    leave_policy_unchanged()
```


## A Denial Log Is Not Non-Execution Proof

 One ingress can say “denied” while another adapter still executes the nested shell command. That makes policy logs necessary but insufficient.

 For each tested ingress, my public-safe canary requires four pieces:



- the same classifier identity and semantics;

- an independently observed attempt;

- an explicit denial event;

- an absent execution marker after the denial.


 A separate allowed positive control must create the marker successfully. Otherwise marker absence could mean the observer was broken rather than the risky command was stopped. In the canary, the fake executable writes the marker immediately on process entry, before any Git history or object work; an absent marker therefore proves that the tested command never entered that fake execution path. It does not prove that no wrapper or unrelated side effect ran.



| Ingress | Attempt seen | Denial seen | Marker absent | Positive control |
| --- | --- | --- | --- | --- |
| Default agent-runtime shell | Required | Required | Required | Required |
| Nested coding-agent shell | Required | Required | Required | Required |


 **Proof rule:** attempted + denied + marker absent, backed by a passing positive marker control. Anything weaker is evidence of policy activity, not evidence of non-execution.



## Fail-Open Is an Availability Tradeoff

 The guard described here fails open if its adapter itself errors or times out. That avoids turning a classifier fault into a broad shell outage. It also means the guard is not a security boundary.

 Fail-open can still be useful for accidental resource control when the bypass is observable. A sanitized fail-open control models adapter error as command allowed plus a visible diagnostic, and direct fixtures exercised malformed input and missing-classifier cases. End-to-end timeout behavior remains a specified availability tradeoff, not a published timeout canary. Silent classifier failure would make the operational claim false.

 If the threat model includes malicious bypass, untrusted operators, or adversarial commands, this pattern is insufficient. Use a real sandbox, resource limits, repository isolation, and least-privilege execution boundaries.


## When Not to Use This Pattern Blindly



- Do not infer that every broad Git command has the same materialization behavior.

- Do not use a private incident as proof of exact byte attribution.

- Do not treat a yield handle as a terminal receipt.

- Do not count denial text without independent marker evidence.

- Do not let a narrow accidental-resource guard masquerade as a security sandbox.

- Do not block ordinary Git merely because a small set of reproduced shapes was expensive.


 Known uncovered accidental paths include Git auto-maintenance reached through otherwise allowed commands, other broad history/object walks, IDE-initiated scans, manual terminals, and unlisted harness ingresses. The classifier covers the two reproduced families; it is not a complete resource policy for Git.


 **Falsifier:** this pattern has failed if ordinary Git is broadly blocked, either reproduced scan family executes in a protected repository without the explicit bounded-failure override, a yielded process is reported as complete, an owned process cannot be stopped and reconciled without restarting unrelated services, or classifier failure bypasses policy without an observable diagnostic.



## The Checklist I Would Reuse



- Separate incident observation from causal attribution.

- Identify the exact reproduced command families and repository context.

- Keep ordinary and explicitly bounded Git shapes available.

- Give every yielded process an owner, deadline, poll, cancel, and reap path.

- Validate every ingress with attempted/denied/marker-absent evidence.

- Run an allowed positive marker control.

- Make fail-open adapter faults observable.

- State clearly that the guard is neither a sandbox nor a complete Git cost model.



## Conclusion

 The expensive lesson was not that Git is dangerous. It was that an asynchronous caller can lose ownership of a still-running command while the system quietly continues doing exactly what the command asked.

 The proportionate repair is small: narrow classification for the reproduced incident class, explicit lifecycle ownership, and proof that each intended ingress stopped the canary without breaking normal Git.

 That is a better operational boundary than either extreme: trusting a yield as completion, or disabling the tool because one command shape ran away.



### Related Posts



- [Archive Before You Retire a Git Worktree Backlog](/jingxiao-cai-blog/archive-before-retire-git-worktree-backlogs.html)

- [When a Dirty-Tree Alert Is Correct](/jingxiao-cai-blog/dirty-tree-alert-review-artifact-agent-ops.html)

- [Proof Without Touching Production](/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html)

- [A Final Summary Needs a Delivery Receipt](/jingxiao-cai-blog/final-summary-needs-delivery-receipt-agent-ops.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, automation reliability, and the boundaries that keep asynchronous work observable.

 A caller can yield. Ownership cannot.




## Comments

 Where do your long-running shell commands record ownership, cancellation, and terminal read-back?

 [← Back to Blog](/jingxiao-cai-blog/)
