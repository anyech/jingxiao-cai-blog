# Recovery Is a State Decision, Not an Undo Button

URL: https://anyech.github.io/jingxiao-cai-blog/recovery-problem-ai-agent-undo.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/recovery-problem-ai-agent-undo.html.md
Date: 2026-03-07
Updated: 2026-08-30
Tags: ai-agents, devops, recovery, openclaw, automation, safety

Summary: A failed command is not yet a retry decision. Recovery becomes safer when independent evidence axes choose the state before any remediation begins.

---

[← Back to Blog](/jingxiao-cai-blog/)

# Recovery Is a State Decision, Not an Undo Button


 **March 7, 2026** · Updated August 30, 2026 | By Jingxiao Cai

 Tags: ai-agents, devops, recovery, openclaw, automation, safety



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped replace the original future-tense recovery checklist with a sanitized, executable state-machine proof.



 **What changed:** the original article treated recovery mostly as snapshots, rollback commands, and safe retries. The tested update below starts one step earlier: it decides whether recovery is allowed at all.



## A Transient Error Is Not Permission to Retry

 Consider an unattended backup command that times out after it may already have written an archive. Calling the error `transient` makes a retry sound reasonable. But the process error does not answer the questions that matter most:



- Did the task emit the receipt that proves which attempt ran?

- Did cleanup finish, or is an old effect still active?

- Did the privacy checks complete?

- Is the semantic result known, or merely the process exit?

- Does this controller still own the right to act?


 If any required answer is missing, “retry the transient failure” is no longer a recovery policy. It is a guess that may duplicate an effect, hide incomplete cleanup, or let a stale owner act.


 **Recovery disposition should come from independent evidence axes before the controller interprets the execution error.**



 This does *not* mean every failure needs a human. It means automatic remediation is reserved for the smaller set of failures whose required evidence is complete and whose transient class has a named, bounded handler.


## Five Evidence Questions, Then One Decision



| What the controller can prove | Resulting state | What may happen next |
| --- | --- | --- |
| Successful result and every required evidence axis is present | `completed` | Record completion; no recovery action |
| Verified transient class and every required axis is present | `recovered` after a successful handler | One named handler, bounded attempts, pre-effect reservation |
| Receipt, cleanup, privacy, result, or ownership evidence is missing | `manual_review` or circuit-open | No automatic remediation |
| An external delivery may or may not have happened | Delivery remains ambiguous | Reconcile through read-back; do not blindly resend |

 `manual_review` is a disposition for one run whose evidence needs human judgment. Circuit-open is the policy-level refusal to start more automatic attempts until the unsafe condition is cleared. Both stop remediation, but they describe different scopes.

 The concrete objects matter here. A *receipt gap*, a *cleanup gap*, and an *ownership gap* are not interchangeable “boundaries.” Each removes a different fact the controller would need before acting.


## What the Offline Reproduction Actually Showed

 I exercised the rule in a disposable SQLite-backed reproduction with three terminal observations. An adapter translates one task type's terminal record into the controller's generic observation shape. Two observations belonged to a generic backup adapter: one clean success and one verified transient dependency failure. A different task type omitted evidence required by its policy and therefore stopped for review. No live external delivery or production state was involved.



| Pass | Observation | Why it matters |
| --- | --- | --- |
| First | Three observations ingested; four offline outbox records created | Success and manual review emitted one notice each; the remediated case emitted one when remediation became pending and one when it recovered |
| First | Generic backup states ended as `completed` and `recovered` | A verified transient could use its named recovery handler |
| First | The separate case ended as `manual_review` | A tempting transient label did not override the missing proof required by its policy |
| Replay | All three observations classified as duplicates; zero new delivery records | Replay reused the existing lineage instead of creating another transition or notification |

 The four records are transition notifications captured by an effect-free offline handler, not four remote messages. The replay result is narrow but useful: these three replayed observations produced no second transition notification inside this controller. It does not turn an arbitrary external API into an exactly-once system.


## The State Machine Replaced My Pile of Undo Commands

 The original version of this article proposed a standard collection of `--undo`, `--replay`, and `--rollback` flags. Those can be useful interfaces, but they do not decide whether an operation is safe to perform. The controller now makes that decision first:



```python
def decide(observation, policy):
    gaps = required_evidence_gaps(observation, policy)
    if gaps:
        return manual_review(reason=gaps)

    if observation.result == "success":
        return completed()

    handler = policy.named_handler_for(observation.failure_class)
    if handler and handler.is_verified_transient:
        reserve_effect_once(observation.operation_key)
        return run_with_attempt_cap(handler, policy.max_attempts)

    return circuit_open(reason="no safe automatic handler")
```

 The important order is evidence, disposition, reservation, then effect. An error classifier cannot jump directly to the final line.


## State, Transition, and Notification Move Together

 A recovery decision is not durable if the database says `recovered` but the transition event is missing, or if a notification can be produced twice after a crash. The implementation writes three things in the same transaction:



- the current run state;

- the transition event that explains how it changed;

- an owned outbox record for the notification that still needs delivery.


 A stable operation key is the durable identity used to find the already-recorded decision on replay. In this reproduction, a duplicate observation found the existing state and outbox lineage instead of inventing a second recovery attempt.

 The outbox does not make a remote receiver transactional with SQLite. If a send times out after the receiver may have accepted it, the correct state is still “ambiguous.” The controller reconciles with a supported read-back or waits for a human decision; it does not manufacture certainty by sending again.


## The Tradeoff I Chose

 I would rather route an unusual task to manual review than broaden the automatic-remediation set around an attractive error label. That choice gives up some unattended recovery rate. In return, missing receipts, incomplete cleanup, privacy failures, unknown results, and stale ownership cannot borrow the word `transient` as permission to act.

 Automatic recovery earns its place one handler at a time:



- the failure class is explicit and tested;

- the policy names the handler rather than discovering it dynamically;

- an attempt cap is part of the policy;

- the remediation action is reserved before that handler executes;

- replay of the covered observations produces no duplicate action.



## What This Proof Does Not Establish

 This is a sanitized offline implementation, not an upstream OpenClaw feature or a universal recovery standard. It does not prove live external delivery, hostile same-user integrity, crash safety for arbitrary side-effect handlers, production load behavior, or that every transient failure is safe to remediate.

 It would also fail its own claim if a required evidence gap could enter automatic remediation; if replay created another state transition, handler attempt, or notice; if ambiguous delivery triggered an automatic resend; or if a handler could run without its named policy, attempt cap, and pre-effect reservation.


## A More Useful Recovery Checklist

 I still want snapshots, reversible operations, dry runs, and restore procedures. I now ask these questions first:



- Which evidence axes are required for this task?

- Which missing axis forces manual review or circuit-open?

- Which exact transient classes have named remediation handlers?

- Where is the pre-effect reservation made?

- Did the bounded replay test create another transition, handler attempt, or notification?

- How is an ambiguous external effect reconciled without blind retry?


 An undo command answers “how could I reverse this?” A recovery controller must answer the earlier question: “given what I can prove, am I allowed to do anything at all?”



### Related Posts



- [The Timeout Was Honest. The Active State Was Not.](/jingxiao-cai-blog/timeout-honest-active-state-was-not.html)

- [A Green Scheduled Run Can Still Hide a Broken Inner Producer](/jingxiao-cai-blog/green-scheduled-run-broken-inner-producer.html)

- [Append, Don't Rewrite: The Guardrail That Saved My Agent's Memory](/jingxiao-cai-blog/append-only-memory-guardrails-agent-ops.html)

- [A Durable Agent Task Needs a Lifecycle, Not Just a Queue](/jingxiao-cai-blog/turn-item-lifecycle-durable-agent-work.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and self-hosted AI-agent operations. He prefers recovery controllers that can explain why they are allowed to act—and stop when the evidence is incomplete.

 The safest retry is sometimes a state transition to “do not retry.”



 Originally published March 7, 2026 · Substantially updated August 30, 2026

 [← Back to Blog](/jingxiao-cai-blog/)
