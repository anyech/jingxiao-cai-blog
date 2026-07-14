# A Cold-Start Canary Is Not a Serving SLA

URL: https://anyech.github.io/jingxiao-cai-blog/cold-start-canary-not-serving-sla.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/cold-start-canary-not-serving-sla.html.md
Date: 2026-07-10
Tags: ai-agents, local-llm, agent-ops, reliability, kubernetes, self-hosted-ai

Summary: One successful cold start proves a path. It does not prove concurrent safety, cache independence, recovery, cleanup, or a production serving SLA.

---

[← Back to Blog](/jingxiao-cai-blog/)

# A Cold-Start Canary Is Not a Serving SLA


 **July 10, 2026** | By Jingxiao Cai

 Tags: ai-agents, local-llm, agent-ops, reliability, kubernetes, self-hosted-ai



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a bounded local-serving experiment into a public proof ladder while keeping private topology, model identities, routes, resource figures, and operational artifacts out of the article.



 **Boundary:** this is a sanitized on-demand-serving pattern, not a benchmark or a description of a specific live cluster. The examples explain what a canary can and cannot prove.


 A local model that scales from idle, answers correctly, and returns to its baseline feels like a finished feature.

 It is not. It is the first useful proof.

 The distinction matters because on-demand serving combines several different systems: storage, scheduling, process startup, readiness, request coordination, failure recovery, idle cleanup, and the client-facing latency contract. A single successful request exercises one path through that graph. It does not prove the graph.


 **A cold-start canary proves that the path can work once. A serving SLA needs evidence about what happens when the path is concurrent, interrupted, stale, and slow.**



 This post gives self-hosted AI operators a small proof ladder for deciding when an on-demand model is still a canary, when it is ready for broader experiments, and when it might be eligible for production promotion.


 **Conceptual scope:** the safe proof unit below preserves state transitions and failure semantics. It intentionally omits private model names, node labels, storage paths, ports, exact timings, and live configuration values.



## The Pressure: Idle Capacity Is Expensive

 Large local models create an obvious incentive to scale down when unused. The promise sounds simple:



- a request arrives;

- an activator brings the model online;

- the request waits for readiness;

- later, an idle controller scales the model down again.


 The first working request makes that design look complete. But the difficult questions start immediately afterward:



- Did the test actually start from a cold client-side cache?

- Would two simultaneous requests trigger two competing activations?

- What happens if the activation owner dies?

- Can a disconnected waiter leave durable state behind?

- Can the idle reaper race with an active request or a restoring baseline?

- Does a restarted controller remember what it was warming?


 If those questions are unanswered, the feature is not “done but slow.” It is a canary with a larger proof surface still ahead.


## The Proof Ladder



| Stage | What it asks | What passing earns |
| --- | --- | --- |
| **0. Baseline** | Is the target state known, healthy, and free of stale ownership or helper residue? | Permission to run a bounded canary. |
| **1. Cold path** | Can one request activate, become ready, answer correctly, and restore the declared end state? | Evidence that the happy path exists. |
| **2. Concurrency** | Do simultaneous requests elect one owner while waiters reuse the same activation? | Evidence against double-scale and duplicate ownership. |
| **3. Failure recovery** | Can ownership expire or transfer safely, and do disconnects clean up waiter state? | Evidence that one dead actor does not wedge the path. |
| **4. Controller durability** | Are warm requests idempotent, restart-reconciled, cancellable, and bounded in history? | Eligibility for broader controlled trials. |
| **5. Service contract** | Are latency, observability, desired-warm semantics, rollout, rollback, and capacity limits explicit? | Eligibility for a production promotion decision, not automatic promotion. |


 **Promotion rule:** each stage earns the next test. None of the early stages silently grants a production SLA.



## Concurrency Is a Semantic Test

 A concurrent cold start is not just a load test. It asks whether the system has one coherent meaning for “activation in progress.”

 The expected result is not merely two successful responses. It is one activation owner plus one or more waiters that observe the same transition:



```
request_a:
  role: activation_owner
  transition: idle -> starting -> ready

request_b:
  role: waiter
  transition: observe_starting -> reuse_ready

shared_result:
  scale_requests: one semantic activation
  responses: successful
  ownership_residue: absent
  end_state: declared baseline restored
```

 Without that ownership proof, two green responses may hide duplicate scale requests, conflicting timers, or a race that appears only when one request disconnects.

 A coordination primitive such as a lease can help, but the object itself is not the proof. A bounded canary can observe one owner, bounded waiters, expiry, takeover after failure, and cleanup. That still does not prove stale-owner fencing against a delayed former owner. A production design needs an explicit fencing or generation rule, or equivalent evidence that an expired actor can no longer mutate the target. Kubernetes documents [Lease objects](https://kubernetes.io/docs/concepts/architecture/leases/) as coordination primitives; the application still has to define the ownership contract correctly.


## Cleanup Is Part of the Result

 Canary reports often stop when the response arrives. On-demand serving cannot.

 The test result includes the state after the response:



- the activator returns to its declared idle state;

- no stale owner or waiter record remains;

- the model target is left in the intended baseline state;

- an idle controller cannot race a still-active ownership lease;

- a cleanup failure is reported as a failure, not hidden behind a correct model answer.


 This is the same reason readiness probes and startup probes are different concepts in Kubernetes: “the process exists,” “the process has started,” and “the process should receive traffic” are separate claims. The [probe documentation](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) is a useful reminder not to collapse them.


## Cache Honesty Changes the Claim

 Cold-start measurements are easy to overstate because “cold” has layers:



- the model process may be absent;

- the client node's file pages may be nonresident;

- the storage server may still have hot pages;

- container images, metadata, or shared libraries may still be warm;

- the scheduler may already have the right placement information cached.


 A useful canary names the layer it controlled and the layers it did not. “Client page cache was cold; upstream caches were not characterized” is more valuable than a dramatic “true cold start” label that the test cannot defend.


 **Measurement rule:** if a cache layer was not reset or observed, record it as unknown. Unknown is a boundary, not an embarrassment.



## The Public-Safe Evidence Card



```
on_demand_serving_canary:
  boundary: controlled_canary
  scope: one_bounded_observation_set
  baseline:
    target_health: observed_healthy
    stale_ownership: absent
  cold_claim:
    controlled_layer: client_page_cache_residency
    upstream_cache_state: unknown
  happy_path:
    activation_to_semantic_answer: observed
    declared_end_state_restored: observed
  concurrency:
    single_owner: observed_in_bounded_test
    waiter_reuse: observed_in_bounded_test
  recovery:
    lease_expiry_and_takeover: observed_in_bounded_test
    stale_owner_fencing: not_claimed
    waiter_disconnect_cleanup: observed_in_bounded_test
  durable_controller:
    implemented: mock_or_staged_only
  production_contract:
    latency_slo: not_claimed
    rollout_and_rollback: separate_gate
  verdict: canary_only
```

 The card teaches more than a screenshot of a successful response. It shows exactly which claim moved and which claim did not.


## When Not To Use On-Demand Serving

 Scale-to-zero is not a universal win. Keep a model warm, or use a different serving shape, when:



- interactive latency cannot absorb model load time;

- request bursts make repeated warm-up more expensive than steady capacity;

- the storage path cannot deliver predictable startup behavior;

- coordination or observability is too weak to distinguish waiting from wedging;

- cleanup races would be more dangerous than the saved idle capacity;

- a simpler scheduled warm window fits the workload better.


 On-demand serving is an operating policy, not merely an implementation trick. It should be chosen against workload shape and failure cost.


## Conclusion

 A correct cold-start response is worth celebrating. It proves the system has a real path from idle to useful output.

 The disciplined next step is not to rename that path “production.” It is to test ownership, waiters, failure recovery, cleanup, cache boundaries, controller durability, and the service contract one gate at a time.

 That is how on-demand local LLM serving becomes trustworthy: not through one impressive cold start, but through a ladder of claims that remain honest under concurrency and failure.



### Related Posts



- [A Local LLM Router Is Not a Panel Lane Yet](/jingxiao-cai-blog/local-llm-router-not-panel-lane-yet.html)

- [Reachable Is Not Ready](/jingxiao-cai-blog/reachable-is-not-ready-agent-runtime-offload.html)

- [Synthetic Fanout Is Not Production Approval](/jingxiao-cai-blog/synthetic-fanout-not-production-approval-agent-probes.html)

- [Before Raising Reindex Concurrency, Prove the Memory Lane](/jingxiao-cai-blog/before-raising-reindex-concurrency-prove-memory-lane.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted AI, agent operations, and evidence-driven promotion boundaries.

 A canary earns the next question, not the final label.





### Feedback

 Questions, critiques, or examples of cold-start proof ladders? Open an issue in the [blog repository](https://github.com/anyech/jingxiao-cai-blog) or leave a comment below.



 Published on July 10, 2026 • Part of my ongoing self-hosted AI and agent operations series

 [← Back to Blog](/jingxiao-cai-blog/)
