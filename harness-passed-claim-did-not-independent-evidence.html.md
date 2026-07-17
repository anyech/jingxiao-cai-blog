# The Harness Passed. The Claim Did Not: Why Independent Evidence Matters

URL: https://anyech.github.io/jingxiao-cai-blog/harness-passed-claim-did-not-independent-evidence.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/harness-passed-claim-did-not-independent-evidence.html.md
Date: 2026-07-17
Tags: ai-agents, agent-ops, testing, evidence, review, reliability

Summary: A green harness is not enough when its “observation” merely repeats the input. Runtime claims need an independent evidence path and a real stop rule.

---

[← Back to Blog](/jingxiao-cai-blog/)

# The Harness Passed. The Claim Did Not: Why Independent Evidence Matters


 **July 17, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, testing, evidence, review, reliability



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a bounded final-review stop into a public evidence pattern while removing private implementation details, operational identifiers, and provider-specific fingerprints.



 **Boundary:** this is a conceptual agent-testing pattern, not a description of a live deployment or a specific model-routing implementation. The problem is not that a harness is synthetic; it is that a self-referential measurement cannot support a stronger runtime claim. The examples are deliberately small.


 A synthetic qualification harness passed its tests. Its snapshot was stable. Its validator rejected malformed inputs. Its result record was well-typed. The local evidence looked impressively complete.

 Then final review asked a narrower question: where did the claimed runtime observation come from?

 The answer changed the verdict. The field labeled as an observation was derived from the same scripted input that expressed the intended result. The harness had proved that it could preserve and compare its own data. It had not proved that a runtime independently attempted or observed the claimed behavior.


 **A test can be internally consistent and still lack an independent measurement.**




 **Reader promise:** by the end of this post, you will have a compact way to distinguish intended, attempted, and observed behavior; test whether the evidence path is independent; and stop a review cycle when the central claim remains unproven.



## The Three-Layer Claim

 Many agent-runtime claims quietly combine three different facts:



| Layer | Question | Typical evidence owner |
| --- | --- | --- |
| **Intended** | What did policy, configuration, or the test case request? | Fixture, router decision, or control-plane record |
| **Attempted** | What action did the runtime actually try to perform? | Dispatch boundary, adapter, or invocation event |
| **Observed** | What independently measured outcome occurred? | Runtime-owned event, response provenance, or external readback |

 A policy unit test may establish *intended*. A mocked adapter may establish the shape of *attempted*. Neither automatically establishes *observed*.


 **Claim invariant:** when the public or operational claim is “the runtime selected and used the intended path,” the evidence must connect intended, attempted, and observed values without deriving all three from one source.



## How a Harness Accidentally Observes Itself

 Consider this simplified anti-pattern:



```javascript
const expected = testCase.requestedRoute;
const decision = chooseRoute(testCase);

return {
  intended: expected,
  attempted: decision.route,
  observed: testCase.requestedRoute
};
```

 The result may satisfy `intended === attempted === observed`. But the equality is circular. The “observed” value came from the fixture, not from a runtime-owned observation boundary.

 A stronger shape keeps the sources separate:



```javascript
const intended = policyDecision(testCase);
const attempt = await dispatchBoundary.invoke(intended);
const observed = await observationBoundary.read(attempt.id);

assertEqual(intended.route, attempt.route);
assertEqual(attempt.route, observed.route);
```

 This pseudocode is a design sketch, not a universal implementation recipe. The important property is source independence: mutating the fixture alone must not be able to manufacture the runtime observation.

 An attempt ID is a correlation handle, not proof of independence. If the observation store merely copies the dispatch envelope, the second interface still reads the same claim-producing data path. A stronger measurement is produced by the downstream component that performed—or failed to perform—the behavior, then correlated to the specific attempt with freshness and request-identity checks. A mock can preserve that producer separation, but a mock that returns the fixture value proves only the simulated contract.


## Use an Evidence-Independence Matrix

 Before trusting a polished qualification packet, map each claim to its producer and ask what would falsify it.



| Claim | Evidence producer | Independent? | Falsification test |
| --- | --- | --- | --- |
| The policy chose route B | Policy result | Yes for policy behavior | Change eligibility input; decision should change predictably |
| The runtime attempted route B | Dispatch event | Only if runtime-owned and attempt-correlated | Break the dispatch seam; attempt evidence should fail or differ |
| The runtime observed route B | Response or runtime readback | Only if downstream-owned, fresh, and not copied from intent or dispatch | Fail downstream behavior while intent and dispatch metadata remain intact; the observation must differ, disappear, or report failure |
| Disabled mode restores the fixed route | Negative control | Useful only if it uses the same runtime seam and an independent producer | Disable routing; the fixed path must be observed |

 The last row matters. A test suite that proves only the enabled path may miss restoration defects. A negative control shows whether the system can distinguish “the feature selected this path” from “the fixture always says this path.”

 Mismatch injection and disabled-mode controls are necessary falsification checks, not sufficient proof of independent provenance. Two interfaces over one underlying envelope can pass both. The evidence still needs a trustworthy producer, correct attempt correlation, and a freshness boundary that rejects stale, replayed, or cross-request readback.


## Validate the Measurement, Not Just the Result

 Agent workflows often spend most of their effort validating artifacts:



- snapshot hashes;

- file-set and mode checks;

- schema validation;

- symlink and path protections;

- negative fixtures; and

- non-interference tests.


 Those controls can be valuable. They establish integrity of the qualification machinery. They do not establish that the machinery observes the system under test.

 Add four measurement questions to the review:



- **Producer:** which component produced this field?

- **Independence:** can the test input or dispatch envelope directly determine it without the claimed downstream behavior occurring?

- **Correlation and freshness:** does the readback belong to this exact attempt, or could it be stale, replayed, or attached to another request?

- **Mismatch:** has the harness demonstrated that it can detect intended, attempted, and observed values diverging?


 If the answer to the mismatch question is no, a green equality check may be a tautology.


## Let Final Review Produce a Real Stop

 The clean response to an unproven central claim is not always another harness revision. Sometimes the workflow already promised:



```
one final independent review
at most one bounded execution if accepted
any decision-changing review failure => terminal stop
```

 That rule changes incentives. The reviewer can say no without automatically creating a successor phase. The builder cannot keep adding proof machinery until the packet becomes too expensive to reject. The operator receives an honest outcome: useful offline evidence exists, but the runtime claim did not cross its evidence boundary.

 A terminal stop record should contain:



- the exact claim that remained unproven;

- the decision-changing findings and their evidence;

- what the completed harness still proves;

- what was explicitly not executed or changed;

- the authority boundary that prevents automatic continuation; and

- the separate decisions available later: accept the narrower evidence, pause, or authorize a clean-sheet design.


 This is not failure theater. It preserves both the value of the completed work and the truth about its limits.


## When To Repair, Re-Anchor, or Stop



| Finding | Disposition | Reason |
| --- | --- | --- |
| Formatting or metadata defect | Repair in place | The evidence claim is unchanged |
| Missing negative case inside the declared harness scope | Repair only if the review budget permits | The target may still be the same |
| Observation is derived from the fixture | Block the runtime claim | The measurement is not independent |
| Real observation requires a new runtime path or new authority | Explicit re-anchor | The decision object and risk surface changed |
| Final-review stop condition is triggered | Stop the cycle | Continuing would violate the agreed review contract |


## When Not To Demand Runtime Evidence

 Not every useful claim needs a live or end-to-end runtime observation. Keep the proof proportional:



- a pure policy function can be proven with deterministic unit tests;

- a parser contract may need fixtures, not a live service;

- a schema migration may be adequately tested against an isolated copy;

- an exploratory prototype may explicitly claim only structural feasibility; and

- a high-risk live probe may be unjustified when the narrower offline evidence is enough for the current decision.


 The mistake is not using synthetic evidence. A synthetic harness can preserve independent seams and detect a downstream mismatch. The mistake is attaching a stronger runtime claim to evidence that never crossed the relevant behavior boundary or came back through an independent producer.


## Conclusion

 A disciplined harness can prove many important things: deterministic policy behavior, artifact integrity, negative-input handling, non-interference, and a bounded execution contract.

 It cannot prove an independent runtime observation by copying the intended value into an observation field.

 Separate intended, attempted, and observed evidence. Name the producer of each field. Prove attempt correlation and freshness. Demonstrate that the measurement catches downstream mismatches while intent and dispatch metadata remain intact. And when final review falsifies the central claim, let the stop rule stop the workflow.


 **A green harness is evidence. It is not permission to claim more than the harness observed.**





### Related Posts



- [Stop Reviewing the Review](/jingxiao-cai-blog/stop-reviewing-the-review-agent-scope-creep.html)

- [Prove the Change Without Touching Production](/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html)

- [The Screenshot Was Green. The Page Was Wrong](/jingxiao-cai-blog/screenshot-green-page-wrong-agent-artifact-validation.html)

- [Agent PR Proof Expires](/jingxiao-cai-blog/agent-pr-proof-expiration-refresh-window.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, evidence-driven workflows, and operational decision boundaries.

 A passing test is only as strong as the independence of its measurement.





### Feedback

 Where have you seen a test accidentally observe its own fixture? Open an issue in the [blog repository](https://github.com/anyech/jingxiao-cai-blog) or leave a comment below.



 Published on July 17, 2026 • Part of my ongoing AI-agent operations and reliability series

 [← Back to Blog](/jingxiao-cai-blog/)
