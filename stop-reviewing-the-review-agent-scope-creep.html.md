# Stop Reviewing the Review: How Agent Workflows Drift Out of Scope

URL: https://anyech.github.io/jingxiao-cai-blog/stop-reviewing-the-review-agent-scope-creep.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/stop-reviewing-the-review-agent-scope-creep.html.md
Date: 2026-07-15
Tags: ai-agents, agent-ops, scope-creep, review, reliability, automation

Summary: Agent work can drift when every review finding creates another validator, receipt, schema, and review cycle. Freeze the target, classify objections, and budget assurance.

---

[← Back to Blog](/jingxiao-cai-blog/)

# Stop Reviewing the Review: How Agent Workflows Drift Out of Scope


 **July 15, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, scope-creep, review, reliability, automation



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped compare several sanitized review cycles, separate reusable workflow lessons from private operational details, and pressure-test the stop rules in this article.



 **Boundary:** this is a conceptual pattern for self-hosted agent operations. The examples are deliberately abstracted; they do not describe a current employer project, a live deployment topology, or a specific provider/model lineup.


 Consider a composite agent-workflow pattern. The task begins with a useful, bounded objective: prove one behavior safely enough to decide whether a small next step is reasonable.

 A reviewer found a real gap. The workflow added a validator. The validator needed a schema. The schema needed fixtures. The fixtures needed a receipt. The receipt needed its own parser. Then the next review focused on the proof system rather than the original behavior.

 Every local change looked defensible. The overall trajectory was not.


 **Scope creep becomes hard to see when each extra layer is individually reasonable.**




 **Reader promise:** by the end of this post, you will have a compact way to detect an assurance-boundary expansion loop, classify review findings, and stop hardening the proof machinery when it no longer changes the user-facing decision.



## The Failure Mode: Assurance-Boundary Expansion

 Ordinary scope creep adds features. Assurance-boundary expansion adds proof obligations. It often follows this sequence:



- A workflow defines a behavior and a safety boundary.

- A review finds a gap in the implementation or evidence.

- The revision adds machinery to prove the gap is closed.

- The next review evaluates that machinery and finds another gap.

- The proof boundary expands again while the original user outcome remains unchanged.


 This is not proof that review is bad. The first objection may be essential. The dangerous move is allowing every new concern to inherit blocking authority merely because it appeared later in the review chain.



| Cycle stage | What changed | Did the user-facing decision improve? |
| --- | --- | --- |
| Initial target | One bounded behavior and explicit stop condition | Yes: the decision is concrete |
| First substantive review | A real safety or evidence defect is identified | Usually yes |
| Coherent revision | The frozen defect set is addressed | Yes, if the revision stays inside the target |
| Meta-assurance expansion | New schemas, parsers, receipts, and fixtures prove the proof process | Often unclear |
| Review recursion | The new machinery creates another blocking review cycle | No evidence of added decision value |

 The transition from revision to recursion is the moment to stop and re-anchor.


## Freeze a Target That Fits on One Screen

 A useful review target should be small enough that a reviewer can tell whether a finding changes the decision. I use a target card with six fields:



```
Objective: the one user-visible behavior under review
Safety invariant: what must never happen
Permitted delta: files, interfaces, or behaviors allowed to change
Evidence gate: what observation would support the decision
Review budget: initial review plus at most one confirmation
Stop condition: the exact state that ends this cycle
```

 The card is not a magic specification. Its job is to make expansion visible. If a proposed fix needs a new authority model, new proof subsystem, or broader effect surface, that may be a valid next project—but it is not silently the same project.


 **Target-lock rule:** a reviewer can discover a new risk without automatically expanding the current cycle. Findings need classification, not automatic inheritance.



## Classify Objections by Causality

 The most useful question is not “is this concern technically valid?” Many concerns are valid. The question is “does this concern causally invalidate the frozen behavior, safety invariant, or evidence gate?”



| Finding type | Disposition | Why |
| --- | --- | --- |
| Breaks the declared behavior | Fix in the current cycle | The target does not work as specified |
| Violates the frozen safety invariant | Fix or block | The proposed decision is unsafe |
| Makes the named evidence gate unreadable or false | Repair the evidence path | The decision cannot be supported |
| Improves generic hardening but does not affect the target | Nonblocking backlog | Useful work, wrong cycle |
| Changes the authority, topology, or effect boundary | Explicit re-anchor | The decision object changed |
| Concerns the reviewer, runner, or parser rather than the system under review | Separate operational defect | Review infrastructure failure is not automatically system failure |

 This causality test prevents a common category error: treating an operational review failure as new evidence that the product behavior is wrong. A timed-out critic, malformed verdict heading, or missing review metadata may invalidate that review result. It does not automatically invalidate the frozen implementation.


## Use One Coherent Revision

 When an initial review returns several related objections, fix them as one declared delta. Do not open a fresh mini-cycle for each comment.



- Freeze the accepted objection set.

- Map each objection to one revision or explicit rationale.

- Verify the revised artifact deterministically where possible.

- Ask one confirmation question: did this frozen delta resolve the accepted objections without creating a decision-changing regression?


 The confirmation should not redesign the validator, invent a new receipt format, or expand the fixture matrix. If it does, it is no longer confirming the same delta.


## Budget Assurance Before the Cycle Starts

 Review budgets sound arbitrary until a workflow has spent hours improving its own acceptance machinery. The budget creates a forced decision point:



- **Initial review:** discover decision-changing defects.

- **One coherent revision:** address the accepted set.

- **One confirmation:** verify that frozen delta and check for decision-changing regressions introduced by the revision.

- **Then stop:** accept, block, or explicitly re-anchor as a new cycle.


 A stop does not mean every possible concern is solved. It means the current decision has reached its declared evidence boundary. Remaining hardening becomes backlog with a reopen trigger.


 **Reopen trigger:** new credible evidence—including runtime observations, static analysis, or changed authority/topology facts—shows the declared behavior, safety invariant, or evidence gate is wrong or incomplete. Reviewer curiosity without such evidence is not a reopen trigger.



## Track Outcome Readiness Separately from Assurance Depth

 A workflow can be highly verified and still far from its user outcome. Track both dimensions:



| Dimension | Question | Bad proxy |
| --- | --- | --- |
| Outcome readiness | Can the bounded useful action now be attempted or decided? | Number of validators written |
| Safety readiness | Are the declared failure modes contained? | Panel unanimity without evidence |
| Evidence readiness | Can an operator inspect what happened? | Receipt complexity |
| Review readiness | Is the exact frozen target available to reviewers? | More review rounds |

 If assurance depth rises while outcome readiness stays flat, investigate scope drift before adding another layer.


## When More Assurance Is Worth It

 Do not use this pattern to dismiss hard safety work. Additional proof is justified when:



- the next step has irreversible or broad external effects;

- a new finding directly breaks the frozen safety invariant;

- the evidence path cannot distinguish success from a dangerous false positive;

- the workflow will become standing automation rather than a one-time bounded action; or

- the target has explicitly changed and the user approves a re-anchor.


 In those cases, expand deliberately. Name the new target, reset the evidence contract, and avoid pretending the old review cycle simply continued.


## When Not To Use This Pattern

 A review budget is not a shortcut around:



- unresolved evidence that the system can cause harm;

- missing authorization for a protected action;

- unknown rollback behavior for a destructive change;

- current runtime drift that makes the frozen target stale; or

- a reviewer objection that directly falsifies the central claim.


 The purpose is to constrain irrelevant expansion, not to cap truth-seeking.


## Conclusion

 Agent workflows need review. They also need a definition of done for the review itself.

 Freeze the target. Classify objections by whether they causally change the behavior, safety invariant, or evidence gate. Repair one coherent delta. Confirm it once. Then accept, block, or re-anchor—without allowing the proof system to quietly become the product.


 **The right stop rule is not “no reviewer can imagine another concern.” It is “the frozen decision has the evidence it declared.”**





### Related Posts



- [Stop Points Are Deliverables in Agent Operations](/jingxiao-cai-blog/stop-points-are-agent-operations-deliverables.html)

- [Panel Results Need Panelist Evaluation](/jingxiao-cai-blog/panel-results-need-panelist-evaluation.html)

- [Prepared Is Not Authorized](/jingxiao-cai-blog/prepared-is-not-authorized-agent-activation-packet.html)

- [Ready Is Not a Label](/jingxiao-cai-blog/ready-is-not-a-label-pr-readiness-vector.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, evidence-driven workflows, and operational decision boundaries.

 Review should reduce decision uncertainty, not manufacture an infinite project.





### Feedback

 Where have you seen verification work become the product? Open an issue in the [blog repository](https://github.com/anyech/jingxiao-cai-blog) or leave a comment below.



 Published on July 15, 2026 • Part of my ongoing AI-agent operations and reliability series

 [← Back to Blog](/jingxiao-cai-blog/)
