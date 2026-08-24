# A Cheaper Agent Is Not a Cheaper Workflow: Delegate by Workload Class

URL: https://anyech.github.io/jingxiao-cai-blog/cheaper-agent-not-cheaper-workflow-delegate-by-class.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/cheaper-agent-not-cheaper-workflow-delegate-by-class.html.md
Date: 2026-08-24
Tags: ai-agents, agent-ops, delegation, routing, reliability, cost

Summary: Cheap agent delegation should be promoted by workload class, not model label. Tiny-task savings earned shadow expansion; a larger failure locked its class.

---

[← Back to Blog](/jingxiao-cai-blog/)

# A Cheaper Agent Is Not a Cheaper Workflow: Delegate by Workload Class


 **August 24, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, delegation, routing, reliability, cost



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a private shadow experiment into a public-safe comparison, a workload-class circuit breaker, and explicit falsification gates.



 **Boundary:** the measurements below are normalized, sanitized observations from one small shadow study. They omit provider and model identity, private prompts, routes, paths, subscription details, and deployment fingerprints. They do not authorize live automatic delegation.


 Five tiny tasks made a light worker look excellent.

 It matched the strong baseline on every exact result and used a small fraction of the normalized weighted cost. If I had stopped there, “delegate cheap work to the light lane” would have looked like an obvious optimization.

 Then I tried one larger deterministic aggregation task. The strong controls were exact. Both light configurations miscounted the same task instance.


 **A cheaper model can be a cheaper component and still be the wrong workflow decision.**




 **Reader promise:** by the end of this post, you will have a small promotion ladder for deciding when a cheaper delegated worker deserves broader shadow testing, when one workload class must be locked, and why neither result is permission for live routing.



## The Tiny-Task Win Was Real

 The shadow suite used five small, mechanically verifiable tasks. Every arm received the same semantic work contract and had to return strict structured output that an exact verifier could check.

 To keep the public comparison useful without publishing a live model mix, I normalized the strong single-worker arm to `1.00`:



| Shadow arm | Exact results | Normalized weighted cost | Normalized median wall clock | Decision |
| --- | --- | --- | --- | --- |
| Strong single worker | 5/5 | 1.00 | 1.00 | Decision-relevant comparator |
| Light single worker | 5/5 | ~0.05 | ~0.94 | Broader shadow observation |
| Strong two-worker fanout | 5/5 | ~2.14 | ~1.07 | No economic benefit |
| Light two-worker fanout | 5/5 | ~0.10 | ~0.99 | Cheap, but little wall-clock benefit |


 **Measurement boundary:** each of the five tasks ran once per arm; no attempt was excluded, censored, or rerun. The displayed cost index prices worker usage only, using a rate card captured with the experiment. It does not price parent-local execution and is neither a bill nor a model leaderboard. The wall-clock index is descriptive single-shot data, not a stable speed estimate.


 Within this five-task forced-shadow cohort, the light single-worker arm's displayed weighted-cost index was about `0.05` versus `1.00` for the strong single-worker comparator—roughly 95% lower on this proxy. Its median wall-time index was about `0.94` versus `1.00`, a single-digit difference across five single-shot tasks; I do not claim a stable latency advantage. Exact verification found no correction needed for these five results, but parent review and validation were not priced.

 That supports a narrow claim: **for these five tiny forced worker tasks, the light single-worker lane earned broader shadow collection.**

 It does not support “the light model is generally better,” “delegation always saves money,” or “turn on automatic routing.”


## Raw Tokens Are Not Cross-Model Cost

 One early temptation was to compare total token counts directly. That is not enough when the arms use different model classes, cache behavior, and output pricing.

 A useful cost record separates at least:



- ordinary input;

- cached input;

- cache writes when the pricing contract supports them;

- output;

- the runtime-actual model class; and

- the rate-card version and freshness.




```
weighted_cost =
    ordinary_input × ordinary_rate
  + cached_input   × cached_rate
  + cache_write    × cache_write_rate
  + output         × output_rate
```

 If any required usage bucket, runtime-actual attestation, or rate binding is missing, the economic comparison should become unknown—not zero, and not a guessed median.


 **Billing boundary:** weighted cost is an experiment-specific worker-side comparison proxy. It is not a promise about a subscription invoice, which may use credits, quotas, bundles, or other accounting rules.



## The Larger Task Changed the Decision

 The next workload was still deterministic: aggregate a larger set of structured records and return exact counts and a bounded maximum. It was not a judgment task, creative task, or open-ended synthesis.



| Workload class | Strong control | Light candidate | Disposition |
| --- | --- | --- | --- |
| Five tiny deterministic transforms | Exact | Exact | Expand shadow evidence |
| Larger deterministic record aggregation | Exact | Miscounts in both light configurations | Lock this class |

 Those are two correlated worker-level observations from one matched substantive smoke, not two independent task trials and not an estimate of failure prevalence. The important unit is the *workload class*, not the model label. Tiny text normalization and larger record aggregation can both look “mechanical,” yet they have different error surfaces, prompt amortization, context pressure, and verification cost.


 **Circuit-breaker rule:** for this aggregation contract, the two correlated light-configuration failures trigger a conservative local routing lock, not a capability conclusion. A materially different contract is a new class requiring its own preregistered calibration; it does not reopen this lock. Reopen the locked class only after a preregistered repair and exact rerun under unchanged gates.



## Use Two Gates, in This Order

 The router should answer safety before economics.


### Gate 1: Is This Work Delegable?



- **Mechanically verifiable:** can a deterministic checker decide whether the result is correct?

- **Bounded and non-sensitive:** are the input, output, time, tools, and effect boundary explicit?

- **Parent-owned judgment:** does the orchestrator retain synthesis, approval, and user-visible closeout?


 If any answer is no, do not enter the economy gate.


### Gate 2: Is Delegation Economically Better?



- Run a decision-relevant strong comparator.

- Require exact-quality parity on a matched cohort.

- Require complete requested → selected → runtime-actual attestation.

- Require complete, version-bound usage evidence.

- Measure parent review and rework, not only child inference.

- Reject material latency regression.

- Keep the result scoped to the tested workload class.




```
if not safe_to_delegate(task):
    return "keep with parent"

if workload_class_is_locked(task):
    return "hold"

result = shadow_compare(light_worker, strong_baseline)

if result.exact_quality_equal \
   and result.attestation_complete \
   and result.usage_complete \
   and result.parent_rework == 0 \
   and result.weighted_cost_materially_lower \
   and not result.material_latency_regression:
    return "broader shadow only"

return "hold"
```


## Fanout Is Usually a Coverage Decision

 Fanout can reduce wall clock when independent subtasks are large enough to amortize another worker. In this tiny suite, it mostly doubled worker and token volume.

 The strong fanout arm cost more than twice the strong single-worker comparator and was slower. The light fanout remained inexpensive because of unit price, but its roughly 1% wall-clock advantage versus the strong single-worker baseline did not justify doubling the worker count.

 That makes fanout a coverage or wall-clock tactic, not the default economic route. Ask whether parallelism changes the critical path enough to pay for duplicate startup, context, verification, and coordination.


## Parent Rework Belongs in the Cost Model

 A child result can be cheap to generate and expensive to repair. If the parent must re-read the source, reconstruct missing fields, correct counts, or rerun the task, the workflow did not preserve quality at a lower cost.

 A serious ledger therefore needs:



- child weighted cost;

- child wall clock;

- verification cost;

- parent review and correction time;

- retry or replacement cost; and

- the terminal disposition for that workload class.


 For the first true promotion gate, I would require zero parent rework on at least one genuinely auto-delegation-eligible, amortization-worthy class. Tiny forced tasks are calibration evidence, not that gate.


## The Promotion Ladder



| State | Evidence | Authority |
| --- | --- | --- |
| **Fixture only** | Gate and verifier behave deterministically. | No model claim. |
| **Forced shadow calibration** | Tiny matched tasks have complete attestation and exact output. | Collect broader shadow evidence. |
| **Workload-class candidate** | At least one representative class preserves quality, cost, latency, and zero rework. | Eligible for a separately reviewed live-routing decision. |
| **Live automatic route** | Policy, rollback, observability, authority, and class circuit breakers are all proven. | Requires explicit activation approval. |

 The current evidence reached only the second state for the tiny classes. The larger aggregation class moved in the opposite direction and was locked.


## When Not to Use Cheap Delegation



- Do not delegate judgment, synthesis, approval, or public voice merely because the child is cheaper.

- Do not route sensitive or effect-bearing work into a lane whose tool and data boundaries are not enforceable.

- Do not compare raw token counts as if they were cross-model cost.

- Do not compute medians from censored or partial cohorts that silently drop timed-out, failed, or missing rows.

- Do not generalize a tiny-task win to a larger workload class.

- Do not hide parent rework outside the economic ledger.

- Do not let a passing shadow gate activate live routing.



 **Falsifier:** the tiny-task claim weakens if a matched rerun loses exact parity or the material weighted-cost advantage, introduces material latency regression or parent rework, accepts missing usage or attestation, or changes the prompt and gate after seeing the result. The class lock can be reconsidered only after a preregistered exact rerun passes without that drift.



## Conclusion

 The light worker did not “win” or “lose.” It qualified for broader shadow collection on a few tiny classes and failed a larger class badly enough to trigger a stop rule.

 That is the useful outcome. A runtime-neutral delegation system should preserve the orchestrator's judgment while treating cheap execution as a class-scoped hypothesis with exact evidence, complete accounting, and reversible promotion gates.

 Promote the workload class, not the model label. And when a class produces a credible exactness failure, let the local lock hold until a preregistered repair earns another test.



### Related Posts



- [Agent Dispatch Should Be Parent-Owned](/jingxiao-cai-blog/parent-owned-agent-dispatch-router-contracts.html)

- [A Default Is Not Caller Intent](/jingxiao-cai-blog/default-is-not-caller-intent-agent-setting-provenance.html)

- [Synthetic Fanout Is Not Production Approval](/jingxiao-cai-blog/synthetic-fanout-not-production-approval-agent-probes.html)

- [A Local LLM Router Is Not a Panel Lane Yet](/jingxiao-cai-blog/local-llm-router-not-panel-lane-yet.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, evidence-driven routing, and the boundaries that keep automated execution honest.

 Cheap execution is useful only when the whole verified workflow stays cheap.




## Comments

 Which workload classes have actually earned cheap delegation in your system—and which ones are circuit-breaker locked?

 [← Back to Blog](/jingxiao-cai-blog/)
