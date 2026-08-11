# Approval Is Not Execution: Deferred Side Effects Without a Second Control Plane

URL: https://anyech.github.io/jingxiao-cai-blog/approval-is-not-execution-deferred-side-effects.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/approval-is-not-execution-deferred-side-effects.html.md
Date: 2026-08-11
Tags: ai-agents, agent-ops, approval-workflows, automation-safety, provenance, audit-logging

Summary: A deferred-effects manifest can preserve proposed intent, suspend dependency-bound work, and compile a review bundle while native action approval remains the only approval authority for the external effect.

---

[← Back to Blog](/jingxiao-cai-blog/)

# Approval Is Not Execution: Deferred Side Effects Without a Second Control Plane


 **August 11, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, approval-workflows, automation-safety, provenance, audit-logging



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a private implementation and test record into a public-safe design, while removing live routes, transport details, private paths, identifiers, review artifacts, and deployment fingerprints.



 **Short version:** a review bundle can preserve proposed work. It must not become approval or a dispatcher. Keep native action approval in charge, and let only preclassified, isolated, local, reversible preparation continue while an external effect is pending.


 Human approval creates an awkward pause in an agent workflow.

 The agent may already know how to prepare the next artifact, validate an unrelated branch, or assemble a review packet. But one action in the middle would send, publish, delete, mutate, or activate something outside the safe preparation lane.

 Two bad responses are common:



- stop the entire workflow even when useful independent work remains; or

- treat a provisional result, caller-supplied approval flag, or polished review bundle as permission to keep executing.


 I wanted a third option: defer the side effect, preserve exactly what was proposed, continue only the work that does not depend on the missing result, and leave execution authority where it already belongs.


 **Approval is an input to execution. It is not execution, and a record of intent is not approval.**




 **Reader promise:** by the end of this post, you will have a bounded manifest, dependency rule, journal model, and negative-test checklist for deferred side effects without installing a second agent runtime or control plane.



## This Is the Step After “Prepared Is Not Authorized”

 My earlier post, [Prepared Is Not Authorized](/jingxiao-cai-blog/prepared-is-not-authorized-agent-activation-packet.html), focused on the last boundary before a live action: assemble an activation packet, name the exact verb and target, and wait for valid authority.

 This post asks a different question:


 **What may the workflow safely do while it waits?**



 The answer cannot be “everything except the final API call.” A pending side effect can create dependencies. If a later step needs the actual issue number, published URL, deletion result, or live state produced by that action, the later step must suspend. If it only needs the proposed content, a digest, or an unrelated local artifact, preparation may continue.

 That distinction is the center of the design.


## The Borrowed Idea, and the Boundary I Kept

 Cloudflare OS describes early-access [Gatekeepers](https://github.com/cloudflare/cloudflare-os/blob/1cb5e3d9096589e38f3fcfaf3f2191aa95a4c592/README.md#gatekeepers-a-capability-based-security-layer) that place side-effecting actions behind later human approval and allow an agent to continue through simulated outcomes. Its pinned [Gatekeeper type definitions](https://github.com/cloudflare/cloudflare-os/blob/1cb5e3d9096589e38f3fcfaf3f2191aa95a4c592/packages/workshop-shared/src/gatekeeper.ts) make the review-and-apply separation inspectable.

 I borrowed the asynchronous review idea, not the runtime.



- I did not adopt Cloudflare OS.

- I did not add a second service that can approve or dispatch actions.

- I did not let simulated results stand in for materialized external state.

- I kept the existing workflow owner and native action-specific approval gate authoritative.


 The adaptation is deliberately smaller: a local, review-only manifest that can describe intent, dependencies, expiry, and continuation state, but cannot grant consent or commit a live action. The review compiler and verifier do not dispatch; the existing action owner and guarded execution path remain responsible for any later external call.


## A Review-Only Manifest

 The manifest is the safe proof unit. It records what the agent proposed without pretending the proposal happened.



```
protected_plan:
  schema: effect-review-plan.v1
  profile: review_only
  created_at: 2026-08-11T00:00:00Z
  expires_at: 2026-08-12T00:00:00Z
  approval_policy:
    native_action_approval: required
    caller_supplied_consent: forbidden
  actions:  # ordered
    - id: prepare_release_notes
      effect: local_artifact
      depends_on: []
      continuation: continue_preparation
    - id: publish_release
      effect: external_write
      depends_on: [prepare_release_notes]
      continuation: must_suspend
    - id: verify_public_url
      effect: external_readback
      depends_on: [publish_release]
      continuation: must_suspend

plan_digest: sha256(project_local_canonical_bytes(protected_plan))
runtime_state: review_only
```

 Everything that can change the external decision belongs inside `protected_plan`: schema/profile, target and payload hashes, effect class, ordered action graph, dependency and materialization rules, continuation class, expiry, and approval policy. Review commentary and observed runtime state stay outside. A native approval must identify the exact plan digest and selected action IDs; at dispatch time, the guarded owner must recompute that digest and recheck approval identity, expiry, dependencies, effect class, and current state. A mismatch, replay, or expired plan fails closed.

 The current adaptation stops before that dispatch boundary: its public claim is review-only, and its production-facing CLI cannot consent or apply. The dispatch rules above are requirements for any future integration, not a claim that this review compiler can execute.

 The exact field names are less important than the invariants:



| Invariant | Why it matters | Failure response |
| --- | --- | --- |
| The complete protected plan has a digest. | A later reviewer can tell whether the proposed bytes changed. | Invalidate the review and regenerate the packet. |
| Review-only state cannot become consent or commit state. | A polished packet remains evidence, not authority. | Reject the transition mechanically. |
| Materialized dependencies suspend. | A proposed URL, receipt, or deletion result is not the real result. | Stop dependent work until read-back exists. |
| Expiry is checked against trusted runtime time. | An old packet should not stay executable because the caller supplied a convenient clock. | Expire and rebuild from fresh state. |
| Native approval remains the only approval authority. | The manifest does not create a parallel authorization system; the existing guarded executor still owns dispatch. | Return a blocked execution state. |


## Canonicalize Before You Hash

 A digest is useful only if equivalent protected plans produce equivalent bytes. Hashing a pretty-printed file with unstable key order creates ceremony, not identity.



```
canonical_plan = json.dumps(
    protected_plan,
    sort_keys=True,
    separators=(",", ":"),
    ensure_ascii=False,
    allow_nan=False,
).encode("utf-8")

plan_digest = sha256(canonical_plan).hexdigest()
```

 This is a project-local deterministic serialization for one versioned, closed, validated Python object model. It is not RFC 8785 or a cross-language canonical JSON promise. The schema admits only defined JSON-shaped types, rejects floats and non-finite numbers, and treats the action list as ordered. An external JSON parser must also reject duplicate keys before creating the object. A port needs an agreed canonicalization form and shared test vectors before its digests are comparable.

 Keep mutable review commentary, runtime observations, and granted-approval state outside the protected plan. The digest should answer one question: *are these still the exact action and policy bytes the reviewer saw?* Approval state stays separate, but a valid approval must reference that digest.

 If target, content, action order, dependency, expiry, effect class, continuation, or approval policy changes, the digest changes and the prior review no longer applies. Preparation that changes eventual external content therefore creates a new protected plan; it cannot inherit approval from the earlier bytes.


## Continue Preparation, Not Fiction

 The continuation classifier should be conservative and policy-derived. A caller or plan generator cannot make an external action safe merely by writing `continue_preparation`; trusted validation must check the effect class, dependency graph, materialization rule, and allowed continuation. Unknown or malformed entries default to suspend. I use two outcomes:



| Outcome | Allowed | Examples |
| --- | --- | --- |
| `continue_preparation` | Preclassified, isolated, local, reversible, non-authoritative work that does not need the real side-effect result. | Format a draft, run a sanitizer, validate an unrelated file, assemble a review packet. |
| `must_suspend` | Anything that consumes materialized state from the pending action. | Verify a public URL, reply in a created thread, reference a new issue ID, confirm deletion. |

 Do not infer independence from step order alone. Declare dependencies, check their closure, reject cycles, and suspend when a required result does not exist.


 **Hard boundary:** a plausible simulated value is still provisional. If the next step would be wrong when the real service chooses a different identifier, timestamp, URL, ordering, or validation result, suspend it.



## The Journal Is Tamper-Evident Only Inside Its Threat Model

 I bind each retained journal record to the protected plan digest and the previous record hash. The record is a versioned closed object, so the hash input does not depend on ambiguous string concatenation:



```
record_without_hash = {
    "schema": "effect-journal-record.v1",
    "seq": sequence_number,
    "prev_hash": previous_record_hash_or_64_zero_genesis,
    "plan_digest": plan_digest,
    "event": transition_event,
}

record_hash = sha256(
    project_local_canonical_bytes(record_without_hash)
).hexdigest()
```

 Under a trusted verifier and retained plan baseline, this detects accidental or unrehashed corruption, broken linkage, and unrehashed reordering inside the retained record set. That is useful. It is not an immutable ledger, authorship proof, origin authentication, or non-repudiation mechanism.



- An actor controlling all local state can edit and coherently rehash the full history.

- A valid tail can be truncated unless something outside the journal anchors its latest hash.

- The verifier itself and the retained baseline remain trusted components.


 Those limits belong in the claim, not in fine print. The journal supports local consistency checks and recovery reasoning. It does not provide adversarial tamper proof or external non-repudiation.


## Compile for Review With Zero Dispatch

 A review compiler should be boring. It may render the proposed target, sanitized content, dependencies, expiry, digest, rollback limits, and the exact native approval still required. It must not contain a hidden “helpful” dispatch path, capability-bearing output, or authority-changing transition.

 The private implementation behind this sanitized reproduction passed 26 focused tests. The code and commands below describe the reviewed shape; they are not a published, reader-runnable package. The most important tests were negative:



| Falsifier | Expected test result |
| --- | --- |
| Mutate the protected plan. | The digest changes. |
| Supply consent through caller text or metadata. | Consent and commit remain unreachable. |
| Mutate or reorder retained journal records without recomputing their hashes. | Trusted verification fails. |
| Relabel or continue past an unmet materialized dependency. | Dependency closure fails and the action suspends. |
| Compile a review bundle. | Instrumented external dispatch count remains zero. |
| Reuse a digest-bound approval after plan mutation, action mismatch, replay, or expiry. | Validation rejects the transition before dispatch. |



```
inspected private harness
focused tests: 26
result: OK
```

 The count does not prove completeness or public reproducibility. It proves only that the enumerated invariants had focused executable coverage in the inspected private implementation.


## Interrupted Apply Must Become Uncertain

 There is one more dangerous shortcut: retrying after an ambiguous transport failure.

 If dispatch may have happened but read-back is missing, the state is not “pending” and not “failed.” It is `uncertain`. A guarded executor must durably record `applying` before the outbound call; otherwise a crash can erase the very ambiguity the journal needs to preserve. The workflow should reconcile with the external system, use an idempotency key when the service supports one, and obtain any required fresh native approval before sending again.



```
if dispatch_started and receipt_missing:
    state = "uncertain"
    auto_redispatch = False
```

 This is the same reason a delivery receipt matters after publication or messaging: an internal exception does not tell you whether the user-visible side effect occurred.


## When Not to Use This Pattern

 A deferred-effects manifest is not free. It adds schema, expiry, dependency, journal, and recovery obligations. Skip it when:



- the operation is local, reversible, and already inside an approved scope;

- the workflow can simply stop without wasting meaningful safe work;

- there is only one side effect and no useful independent continuation;

- the native platform already provides a trustworthy queued-approval contract; or

- the team cannot maintain trusted verification and a retained baseline.


 Also do not use the manifest to avoid a real synchronous approval. Some actions are too interdependent, ambiguous, or irreversible to simulate around. In those cases, waiting is the feature. Visible preparation can also create sunk-cost pressure on a human reviewer; technical separation of authority does not excuse rubber-stamping.


## What This Evidence Does Not Prove

 The implementation proves bounded local invariants. It does not prove that operators approve faster, that agents finish more work, or that errors decrease.



- No real operator canary has been run.

- Transport identity is not independently authenticated by the manifest layer.

- Zero-dispatch coverage reaches the instrumented review compiler and verifier surfaces, not every possible program on the host.

- The journal cannot defeat a coherent whole-history rewrite or valid-tail truncation by an actor controlling all local state.

- No second runtime or control plane was adopted, so this design does not reproduce every Gatekeeper behavior.


 The claim should be considered falsified if unverified metadata can unlock apply, protected-plan changes preserve the digest, stale or mismatched approval reaches dispatch, unrehashed retained-record mutation or reordering passes trusted verification, review compilation dispatches externally, or an action bypasses an unmet materialized dependency.


## A Compact Design Checklist



- Separate the protected proposed plan from mutable review, approval, and execution state.

- Use a closed schema and project-local deterministic serialization; bind review to the complete plan digest.

- Keep caller text, provisional metadata, and review bundles out of the authority path.

- Require the existing native approval for the exact digest, action, target, and payload; let the guarded owner dispatch.

- Policy-classify every downstream step as isolated preparation or a materialized dependency.

- Reject cycles, missing dependencies, stale packets, and caller-controlled time.

- Make review compilation provably zero-dispatch.

- Record retained transitions in a plan-bound hash chain, with encoding and threat-model limits stated.

- Use `uncertain` after interrupted apply; never blindly redispatch.

- Measure operator value in a bounded canary before adding more mechanism.



## Conclusion

 Deferred side effects do not require a second control plane.

 They require a smaller set of honest boundaries: the protected plan has identity; native approval is bound to exact bytes but remains external to the proposal; dependency-bound work suspends; preclassified isolated preparation may continue; review compilation cannot dispatch; the guarded owner remains responsible for execution; interrupted apply becomes uncertain; and journal claims stop where the local threat model stops.


 **Let the agent continue preparing. Do not let the preparation promote itself into authority.**





### Related Posts



- [Prepared Is Not Authorized](/jingxiao-cai-blog/prepared-is-not-authorized-agent-activation-packet.html)

- [A Default Is Not Caller Intent](/jingxiao-cai-blog/default-is-not-caller-intent-agent-setting-provenance.html)

- [Agent Dispatch Should Be Parent-Owned](/jingxiao-cai-blog/parent-owned-agent-dispatch-router-contracts.html)

- [A Final Summary Needs a Delivery Receipt](/jingxiao-cai-blog/final-summary-needs-delivery-receipt-agent-ops.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, evidence-driven automation, and operational boundaries that stay explicit under pressure.

 A useful plan can wait for approval without pretending the world already changed.





### Feedback

 Which deferred actions can your workflow safely prepare around, and which ones force a hard stop? Open an issue in the [blog repository](https://github.com/anyech/jingxiao-cai-blog) or leave a comment below.



 Published on August 11, 2026 • Part of my ongoing AI-agent operations and reliability series

 [← Back to Blog](/jingxiao-cai-blog/)
