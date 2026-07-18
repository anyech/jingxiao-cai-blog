# A Default Is Not Caller Intent: Preserve Provenance in Agent Settings

URL: https://anyech.github.io/jingxiao-cai-blog/default-is-not-caller-intent-agent-setting-provenance.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/default-is-not-caller-intent-agent-setting-provenance.html.md
Date: 2026-07-18
Tags: ai-agents, agent-ops, configuration, routing, provenance, testing

Summary: A resolved value is not enough. Agent runtimes must preserve request provenance, selection authority, constraints, and rejection reasons across every adapter.

---

[← Back to Blog](/jingxiao-cai-blog/)

# A Default Is Not Caller Intent: Preserve Provenance in Agent Settings


 **July 18, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, configuration, routing, provenance, testing



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn an isolated integration failure into a reusable configuration pattern while removing private routes, model names, source paths, test counts, and deployment fingerprints.



 **Boundary:** this is a composite, conceptual runtime-integration pattern, not a description of a named or current deployment. The examples use a generic response-mode preference because the bug class applies equally to timeouts, tool permissions, output modes, retry policies, and other layered defaults.


 Consider a composite example: an agent runtime receives a request with no explicit response-mode setting. An early integration layer fills the missing field with the system default: `compact`. A later advisory policy selects `detailed` for the task. The final runner still uses `compact`.

 Every individual value looked valid. The defect lived in the missing provenance. By the time the request reached the runner, it carried a scalar but no longer carried the fact that the scalar had been defaulted. The runner interpreted the value as caller authority and correctly refused to override it.


 **A resolved value tells you what the value is. It does not tell you who chose it.**




 **Reader promise:** by the end of this post, you will have a compact representation for explicitness, a precedence rule for layered agent settings, and a small test matrix that catches defaults masquerading as caller intent.



## The Bug Is Not the Default

 `compact` can be a sensible conservative default. The mistake is treating a defaulted value as if a caller explicitly requested it.

 These two inputs are semantically different:



```javascript
// Caller explicitly chose the compact response mode.
{ responseMode: "compact", responseModeExplicit: true }

// No caller choice; an earlier layer supplied a fallback.
{ responseMode: "compact", responseModeExplicit: false }
```

 If a transport, request normalizer, or direct-execution path drops `responseModeExplicit`, both requests collapse to the same object. No downstream precedence rule can reconstruct the lost intent reliably. The boolean form illustrates the minimum distinction; the structured envelope below is the stronger representation used by the proof matrix.


## Carry a Value Envelope, Not Just a Scalar

 A useful setting contract preserves the original request separately from the final selection:



| Field group | Question answered | Example |
| --- | --- | --- |
| `requested` | What did the caller or operator explicitly request, if anything? | `{ value: "compact", source: "caller" }` |
| `selected` | What final value will the runtime use, and which authority selected it? | `{ value: "detailed", source: "advisory-policy" }` |
| `constraints` | Which mandatory safety, capability, budget, or operator limits were applied? | `["capability-limit"]` |
| `validation` | Was the request accepted, rejected, or replaced—and why? | `{ status: "passed" }` |

 The exact schema can vary. A structured envelope makes the authority tiers explicit:



```typescript
type ResolvedSetting<T> = {
  requested?: {
    value: T;
    source: "caller" | "operator";
    explicit: true;
  };
  selected: {
    value: T;
    source: "mandatory-constraint" | "operator-mandate"
      | "caller" | "advisory-policy" | "system-default";
  };
  constraints: string[];
  validation: {
    status: "passed" | "rejected" | "replaced";
    reason?: string;
  };
};
```

 The important property is not the field name. It is that an early resolver cannot erase the distinction between “the caller chose this” and “the system needed a temporary value.”


## Make Precedence About Authority

 A naïve preference-resolution rule compares only whether a value exists:



```javascript
const finalMode = request.responseMode
  ?? advisoryPolicy.responseMode
  ?? systemDefault;
```

 That is safe only when presence implies authority. In layered agent systems, it often does not.

 A stronger rule evaluates source, explicitness, and authority. Mandatory safety, legal, capability, budget, and operator constraints are a higher tier than caller preference. The table below describes preference resolution only after those constraints have admitted the request.



| Incoming state | Competing authority | Disposition | Why |
| --- | --- | --- | --- |
| Mandatory constraint or operator mandate | Any caller preference | Enforce the constraint or reject | Hard boundaries outrank preference |
| Validated explicit caller preference | Different advisory preference | Preserve caller value | Advisory policy must not silently override admitted intent |
| System default | Valid advisory preference | Use advisory value | The default is fallback, not authority |
| No value | No advisory value | Use system default | The fallback is now the best available choice |
| Unsupported execution-affecting value | Any value | Reject before dispatch | The caller receives an observable error; no silent clamp or fallback occurs |


 **Authority invariant:** enforce mandatory constraints first; preserve valid explicit caller preference over advisory policy; let advisory policy replace defaults; and reject unsupported execution-affecting input before dispatch.



## Test the Cross-Product, Not the Happy Path

 A unit test of the advisory function can prove that it returns `detailed`. It cannot prove that the integration path carries that choice to the runner. The useful proof unit covers four semantic cases, then repeats them across transport and serialization boundaries:



| Case | Input | Expected runner state | Failure caught |
| --- | --- | --- | --- |
| Explicit preserve | Caller sets a valid value | Caller value + caller provenance | Advisory-policy overreach |
| Default replace | Earlier layer fills a default | Advisory value + advisory provenance | Default mistaken for intent |
| Default retain | No applicable policy decision | Default value + default provenance | Uninitialized setting |
| Constraint or invalid-input reject | Caller conflicts with a hard constraint or supplies an unsupported value | Observable pre-dispatch rejection | Safety bypass or fail-open normalization |

 Run those four cases through every relevant entry path and serialization hop: interactive sessions, direct execution, scheduled work, delegated workers, network payloads, retries, caches, or test harnesses. Shared policy code does not guarantee shared request semantics. Every adapter must schema-validate and preserve the same authority envelope.


## Observe Provenance at the Runner Boundary

 Do not stop verification at the policy result. Capture a sanitized runner-boundary record that can answer:



- what final value was used;

- which layer selected it;

- whether the originating input was explicit;

- whether validation happened before dispatch; and

- whether the execution path received the same semantics the policy produced.


 This does not require logging private prompts, model names, or full request payloads. A small typed record is enough:



```json
{
  "setting": "response-mode",
  "requestedClass": "omitted",
  "selectedClass": "expanded",
  "sourceClass": "advisory-policy",
  "constraintsApplied": 0,
  "validation": "passed",
  "dispatch": "allowed"
}
```

 For public artifacts, even those classes may be more detail than necessary. For local qualification, however, the record turns “the router chose correctly” into a checkable integration claim.


## Stop Rerunning After a Real Integration Failure

 A failing isolated integration check is useful evidence. It is not an invitation to keep rerunning until the expected value appears.

 When a narrow integration check shows that policy output and runner state diverge:



- preserve the failing test result;

- classify whether the defect is policy, transport, precedence, validation, or observation;

- fix the smallest source seam;

- run focused regression tests in isolation; and

- do not repeat the integration check until those regressions pass.


 The same stop rule applies after repeated equivalent test failures. At that point, prove which fixture, adapter, compiled artifact, or test project actually owns the observed behavior before trying again. Otherwise the workflow starts optimizing for a green rerun instead of understanding the live code path.


## When a Plain Scalar Is Fine

 Provenance envelopes have a cost. They add types, serialization rules, migration work, and tests. Do not add them mechanically to every local variable.

 A plain scalar is usually enough when:



- one authority owns the value from input to use;

- the value is resolved exactly once;

- presence and explicit intent are genuinely equivalent;

- no adapter, advisory policy, constraint layer, or fallback may replace it; and

- invalid input cannot cross an execution boundary.


 Use a provenance-bearing setting when multiple authorities can act, a default may later be replaced, or the value controls a meaningful execution decision.


## Conclusion

 Layered agent systems do not merely resolve values. They reconcile authority.

 If an early layer converts “missing” into `compact` and discards the fact that it was a default, a later layer cannot distinguish fallback from caller intent. The runtime may faithfully preserve the wrong authority.

 Carry the original request, selection source, constraints, validation, and replacement reason across every adapter. Define precedence in terms of authority. Reject unsupported execution-affecting input before dispatch. Test semantic cases across every transport boundary. And when integration evidence diverges from policy output, stop rerunning until the owning seam is understood.


 **Defaults should keep a request safe. They should not impersonate the caller.**





### Related Posts



- [Fallback Is Not Preference](/jingxiao-cai-blog/fallback-is-not-preference-agent-auth-recovery.html)

- [Patch the Thing You Changed](/jingxiao-cai-blog/patch-the-thing-you-changed-narrow-config-validation.html)

- [The Harness Passed. The Claim Did Not](/jingxiao-cai-blog/harness-passed-claim-did-not-independent-evidence.html)

- [Prove the Change Without Touching Production](/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, evidence-driven workflows, and operational decision boundaries.

 Configuration precedence is an authority problem disguised as a value problem.





### Feedback

 Where has a default been mistaken for explicit intent in your systems? Open an issue in the [blog repository](https://github.com/anyech/jingxiao-cai-blog) or leave a comment below.



 Published on July 18, 2026 • Part of my ongoing AI-agent operations and reliability series

 [← Back to Blog](/jingxiao-cai-blog/)
