# High Draft Acceptance Does Not Guarantee a Throughput Gain: A Lean CPU Speculative-Decoding Test

URL: https://anyech.github.io/jingxiao-cai-blog/high-draft-acceptance-no-throughput-gain-speculative-decoding.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/high-draft-acceptance-no-throughput-gain-speculative-decoding.html.md
Date: 2026-08-12
Tags: llm-inference, speculative-decoding, benchmarking, performance, cpu, measurement

Summary: Across two output lengths, every tested draft depth accepted many proposed tokens but still lost on both runtime-reported generation throughput and request wall time.

---

[← Back to Blog](/jingxiao-cai-blog/)

# High Draft Acceptance Does Not Guarantee a Throughput Gain: A Lean CPU Speculative-Decoding Test


 **August 12, 2026** | By Jingxiao Cai

 Tags: llm-inference, speculative-decoding, benchmarking, performance, cpu, measurement



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a private benchmark into a recomputable public-safe evidence unit while removing model identities, host labels, paths, hashes, and deployment details.



 **Boundary:** this is one CPU-only target/drafter pair, one fixed prompt, two forced output lengths, and three runs per cell. It is a local enablement decision, not a general verdict on speculative decoding, other models, other quantizations, or accelerator-backed serving.


 The draft model was working. It proposed tokens, the target accepted many of them, and the acceptance counter looked healthy.

 The request still got slower.

 That is the trap in speculative-decoding evaluation: acceptance is easy to celebrate because it proves that some target work was skipped. But the skipped work is only one side of the ledger. The drafter also consumes compute and memory bandwidth, and the target still has to verify its proposals. The operational question is not “Were tokens accepted?” It is “Did the complete request finish faster?”


 **Draft acceptance is a mechanism metric. Throughput and wall time are outcome metrics.**




 **Reader promise:** by the end of this post, you will have a small measurement protocol, the public-safe recomputable values from one N=3 test, and a bounded decision rule for enabling or rejecting a speculative path.



## The Bounded Result

 I compared speculative drafting disabled with draft depths `n=1`, `n=2`, and `n=3` at two decode-heavy output lengths. Every cell contains three serial runs with the same fixed prompt, generated-token count, sampling controls, target/drafter pair, runtime, and CPU host class.

 The runs used a fixed variant order. No dedicated warm-up, interleaving, or randomization was recorded, so cache, thermal, background-load, and order drift remain possible confounders. That makes this a bounded local enablement test rather than a production-grade benchmark.

 Every tested draft depth lost on both outcome metrics. Mean runtime-reported generation throughput fell by 5.7% to 18.3%, while mean request wall time increased by 5.7% to 18.8%. Yet pooled draft acceptance ranged from 48.6% to 80.4%.



| Draft depth | Output tokens | Draft acceptance | Mean generation tokens/s | Change vs off | Mean wall time (s) | Change vs off |
| --- | --- | --- | --- | --- | --- | --- |
| off | 512 | — | 24.033 | — | 26.522 | — |
| n=1 | 512 | 75.9% | 22.655 | -5.7% | 28.041 | +5.7% |
| n=2 | 512 | 59.0% | 21.597 | -10.1% | 29.085 | +9.7% |
| n=3 | 512 | 48.6% | 19.626 | -18.3% | 31.497 | +18.8% |
| off | 2,048 | — | 23.023 | — | 94.165 | — |
| n=1 | 2,048 | 80.4% | 21.403 | -7.0% | 101.050 | +7.3% |
| n=2 | 2,048 | 65.8% | 21.436 | -6.9% | 100.953 | +7.2% |
| n=3 | 2,048 | 53.1% | 19.449 | -15.5% | 110.705 | +17.6% |

 The bounded decision was straightforward: keep drafting disabled on this runtime. The result does not say speculative decoding is ineffective. It says this target/drafter/runtime combination did not earn enablement under this workload.


## Define the Metrics Before Comparing Them

 **Draft acceptance** here is the pooled number of accepted draft tokens divided by the pooled number of proposed draft tokens across all three runs in a cell. It is not the arithmetic mean of three per-run percentages.

 **Generation tokens/s** is the runtime's backend-specific generation-rate field; it was not independently instrumented. **Wall time** is measured separately around the request, so the conclusion does not depend on treating the runtime metric as an end-to-end timer.

 The generated-token count was fixed within each output-length comparison. The same requests underpin both generation rate and wall time, so those metrics are two differently scoped views of each run, not independent replications.

 Keeping those surfaces separate prevents two common mistakes:



- using a high acceptance ratio as a proxy for speedup; and

- using an internal decode metric as though it captured every request cost.



## The Acceptance Arithmetic Is Publicly Recomputable



| Draft depth | Output tokens | Accepted / proposed, runs 1 / 2 / 3 | Pooled total | Pooled acceptance |
| --- | --- | --- | --- | --- |
| n=1 | 512 | 220/290 &middot; 220/290 &middot; 220/290 | 660/870 | 75.8621% |
| n=1 | 2,048 | 911/1,135 &middot; 912/1,134 &middot; 912/1,134 | 2,735/3,403 | 80.3703% |
| n=2 | 512 | 276/468 &middot; 276/468 &middot; 276/468 | 828/1,404 | 58.9744% |
| n=2 | 2,048 | 1,163/1,767 &middot; 1,163/1,767 &middot; 1,163/1,767 | 3,489/5,301 | 65.8178% |
| n=3 | 512 | 303/623 &middot; 303/623 &middot; 303/623 | 909/1,869 | 48.6356% |
| n=3 | 2,048 | 1,257/2,367 &middot; 1,257/2,367 &middot; 1,257/2,367 | 3,771/7,101 | 53.1052% |

 The exact percentages matter less than the contradiction they expose: the highest observed pooled acceptance, 80.4%, still came with 7.0% lower reported generation throughput and 7.3% higher wall time.


## The Means Are Not Hiding One Bad Run

 Here are all three per-run timing values in every cell, shown to six decimal places. The means and deltas above were calculated from the full-precision source measurements rather than from these displayed values.



| Draft depth | Output tokens | Generation tokens/s, runs 1 / 2 / 3 | Wall time seconds, runs 1 / 2 / 3 |
| --- | --- | --- | --- |
| off | 512 | 24.032745 / 24.031547 / 24.033537 | 26.517395 / 26.553268 / 26.493878 |
| n=1 | 512 | 22.645722 / 22.641171 / 22.677490 | 28.072329 / 28.085832 / 27.963858 |
| n=2 | 512 | 21.598684 / 21.591714 / 21.600749 | 29.078755 / 29.109895 / 29.066425 |
| n=3 | 512 | 19.615974 / 19.602590 / 19.659833 | 31.514876 / 31.551388 / 31.424818 |
| off | 2,048 | 23.030269 / 23.015419 / 23.023529 | 94.106198 / 94.224299 / 94.164788 |
| n=1 | 2,048 | 21.401632 / 21.415856 / 21.391437 | 101.044526 / 100.996842 / 101.109659 |
| n=2 | 2,048 | 21.427522 / 21.418181 / 21.461086 | 100.980612 / 101.088023 / 100.791037 |
| n=3 | 2,048 | 19.464551 / 19.444808 / 19.439072 | 110.711190 / 110.661473 / 110.742313 |

 Every drafting run was slower than every corresponding drafting-off run in this sample on both reported generation rate and wall time. With only three runs per cell, this is still not a population estimate or a tail-latency study. It does show that the arithmetic means were not flipped by one isolated outlier.


## Why Acceptance Can Lose

 Speculative decoding trades target-model work for a different bundle of work:



- run the draft model;

- materialize proposed tokens;

- verify them with the target;

- discard or repair rejected proposals; and

- coordinate the extra state and memory traffic.


 Accepted tokens are the benefit side. Drafting and verification are the cost side. A high acceptance rate can coexist with a net loss when the drafter is too expensive relative to the target work it saves, especially on a CPU path with a comparatively heavy draft artifact.

 This test did not separately instrument compute, verification, cache, or memory-bandwidth attribution. The result is consistent with draft overhead exceeding saved target work; it does not identify one microarchitectural bottleneck as the proven cause.


## A Small Enablement Scorecard

 For a lean first pass, I would record at least these five fields per cell:



| Metric | Role | Decision use |
| --- | --- | --- |
| Accepted / proposed tokens | Mechanism diagnostic | Confirms that drafting is active and shows proposal quality |
| Runtime-reported generation tokens/s | Engine outcome | Measures reported decode-rate change |
| End-to-end request wall time | User-visible outcome | Checks whether the complete request actually gets faster |
| All per-run timing values | Stability evidence | Shows spread and whether a mean hides an outlier |
| Fixed controls | Comparison integrity | Keeps target, draft, prompt, runtime, host class, and execution mode aligned |


 **Practical rule:** enable drafting only when the outcome metric that matters to your workload improves reproducibly. Use acceptance to explain and tune the mechanism, not to overrule a slower request.



## When Not to Use This Test as a Final Answer



- **Interactive traffic:** test time-to-first-token and tail latency, not only forced long outputs.

- **Concurrent serving:** test queueing, batch shape, throughput under load, and interference.

- **Accelerators:** remeasure on the actual GPU or other backend; CPU cost balance does not transfer automatically.

- **Quality-sensitive workloads:** add output-quality and task-success checks where the decoding configuration can change behavior.

- **Capacity decisions:** include memory use, energy, concurrency, and cost per completed request.


 Also do not compare a new drafter against an unmatched baseline with different prompts, token caps, sampling, cache state, runtime build, or host pressure. The cleaner the claimed delta, the stricter the control surface should be.


## Limitations and Falsification

 This evidence covers one target/drafter pair on one CPU runtime and host class, with a fixed prompt, forced-length generation, two output lengths, and N=3. The fixed serial variant order and absence of a recorded warm-up, interleaving, or randomization leave order and system-drift confounders unresolved. It does not establish a general result for other models, quantizations, backends, accelerators, prompts, concurrency levels, or workloads.

 This is a sanitized reproduction: exact runtime/build identity, model artifacts, host label and specification, private paths, and hashes are deliberately withheld. The published arithmetic is independently checkable, but reproducing the environment requires an internal same-class run rather than a reader-runnable public package.

 The transcription claim fails if recomputing the published per-run values at their stated precision does not reproduce the displayed means, deltas, and pooled acceptance percentages. The bounded operational decision would be weakened by a same-protocol replication on the same target/drafter/runtime class in which one draft depth reproducibly improves both runtime-reported generation throughput and wall time by more than 5%.

 A smaller or cheaper draft artifact, a backend optimization, or materially different hardware would be a new hypothesis, not a contradiction by itself.


## Conclusion

 The draft path was active. It accepted many proposals. It still made every tested request slower.

 That is why speculative-decoding qualification needs both mechanism and outcome metrics. Publish the accepted/proposed counts. Publish the per-run timing values. Define pooled arithmetic. Keep an end-to-end timer beside the engine's throughput counter. Then make the decision from the workload outcome, not from the most flattering internal ratio.


 **High draft acceptance can explain a speculative path. It cannot, by itself, justify enabling one.**





### Related Posts



- [The Harness Passed. The Claim Did Not](/jingxiao-cai-blog/harness-passed-claim-did-not-independent-evidence.html)

- [When Reasoning Eats the Answer](/jingxiao-cai-blog/when-reasoning-eats-the-answer-empty-llm-completions.html)

- [Reachable Is Not Ready](/jingxiao-cai-blog/reachable-is-not-ready-agent-runtime-offload.html)

- [An Idea Miner Should Be Allowed to Find Nothing](/jingxiao-cai-blog/idea-miner-allowed-find-nothing.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about inference measurement, self-hosted agents, and evidence-driven automation.

 A mechanism earns deployment through workload outcomes, not through one attractive counter.





### Feedback

 Which metric has overturned an apparently promising inference optimization in your own tests? Open an issue in the [blog repository](https://github.com/anyech/jingxiao-cai-blog) or leave a comment below.



 Published on August 12, 2026 • Part of my ongoing distributed-runtime and evidence-driven performance series

 [← Back to Blog](/jingxiao-cai-blog/)
