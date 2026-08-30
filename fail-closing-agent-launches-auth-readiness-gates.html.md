# The Worker Path Skipped the Launch Gate

URL: https://anyech.github.io/jingxiao-cai-blog/fail-closing-agent-launches-auth-readiness-gates.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/fail-closing-agent-launches-auth-readiness-gates.html.md
Date: 2026-04-29
Updated: 2026-08-30
Tags: ai-agents, security, tooling, reliability, openclaw, auth

Summary: The ordinary agent path consulted its launch policy. An alternate worker path reached the raw executor. The repair needs policy parity and later authority fences.

---

[← Back to Blog](/jingxiao-cai-blog/)

# The Worker Path Skipped the Launch Gate


 **April 29, 2026** · Updated August 30, 2026 | By Jingxiao Cai

 Tags: ai-agents, security, tooling, reliability, openclaw, auth



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped connect a general launch-gate rule to a public alternate-worker-path reproduction without importing private runtime fingerprints.



 **What changed:** the original article described auth and readiness gates in general. Public [issue #131661](https://github.com/openclaw/openclaw/issues/131661) supplied a sharper case: two paths to the same session-tool effect did not consult the same policy. The companion [PR #131669](https://github.com/openclaw/openclaw/pull/131669) is open and unmerged as of August 30, 2026.



## One Effect, Two Request Paths

 The configured test policy was straightforward: block `sessions_spawn` before it creates a child session. The ordinary agent-tool path runs inside the Gateway, consults the Gateway's `before_tool_call` policy, and only then reaches the core session tool.

 A cloud worker uses a different transport. It sends a session-tool request back to the Gateway over worker RPC. The worker-session executor still reaches the same core `sessions_spawn` or `sessions_send` implementation—but the public issue showed that this alternate path called the raw executor without first consulting the policy.



- **Ordinary path:** request → `before_tool_call` → core tool → child or message effect.

- **Worker path before the proposed fix:** request → worker RPC executor → raw core tool → child or message effect.


 The same requested effect therefore had different admission behavior depending on how it arrived. The policy did not disagree with itself on the worker path; it never received the worker call.


 **An alternate transport is not an alternate policy contract.**




## The Decisive Proof Was an Absent Effect

 The useful test was not “did the hook log something?” It was whether a blocked call left the downstream effect absent.



| Test | Observed result | Evidence class |
| --- | --- | --- |
| Block worker-hosted `sessions_spawn` | No child session appeared | Isolated Gateway/worker protocol boundary |
| Block worker-hosted `sessions_send` | The target transcript length and marker stayed unchanged | Isolated Gateway/worker protocol boundary |
| Send concurrent retries with one operation identity | One terminal policy result was stored and replayed; no message effect appeared | Focused executor-boundary regression |
| Revoke delegated authority after policy admission | Send dispatch, child commit, provider allocation, and deferred enrollment stopped at their named fences | Focused authority-fence regressions |

 The PR body binds its published isolated run to [the exact tested snapshot](https://github.com/openclaw/openclaw/commit/251b15669a8e0645e979b93fb0f7bdb221786b2c). The live PR head has advanced since that run. This article attributes the proof to the linked snapshot; it does not claim that every later revision has independently repeated the same boundary test.


## Decide Once, Then Fence Each Effect

 The proposed repair reuses the existing `before_tool_call` engine rather than inventing a worker-only policy system. The lifecycle is intentionally small:



- **Elect one durable operation owner.** Concurrent retries first converge on one operation identity.

- **Run the existing policy.** The owner calls `before_tool_call` before target resolution can become child creation or message delivery.

- **Store the terminal decision.** A blocked or allowed result belongs to the operation. Replay reuses it instead of rerunning policy or creating another effect.

- **Recheck authority at the effect.** If delegated authority closes after admission, the send dispatch, child commit, provider allocation, or deferred enrollment must stop before its mutation begins.


 “Durable owner” does not mean the worker owns the right to act forever. It means one operation owns the decision record. The authority fence answers a different question: is that operation still authorized at the moment this particular effect would start?


## Why the Early Policy Check Is Not Enough

 A policy can allow a request at time A while the delegated run is still active. The operation may then wait for placement, provisioning, or dispatch. If the initiating authority closes during that wait, an unfenced implementation can begin the effect at time B using a decision whose authority has expired.

 That is why the design uses both:



- **policy parity** before either request path reaches the effect; and

- **fresh authority** immediately before each later mutation boundary.


 A single early check would close the original bypass but leave a time-of-check/time-of-use window. A separate worker-only hook would close the bypass by creating two policy languages that could drift again. I prefer one policy engine plus cheap, local effect fences.


## This Is a Launch-Gate Case, Not an Auth-Fallback Proof

 The original version of this article came from a different failure: a tool adapter could discover an unintended ambient credential when the intended auth path was incomplete. That incident and the worker bypass share one design invariant—preconditions must be proved before side effects—but they are not the same mechanism.



- **Auth-path failure:** the launch may use the wrong identity or credential class.

- **Worker-policy bypass:** the launch reaches the right core tool without the policy decision that the ordinary path would receive.


 PR #131669 addresses the second case. It does not prove the broader auth-intent, credential-isolation, route-health, capability, or delivery-readiness framework. Those remain separate launch-gate checks.

 The distinction also explains why silent fallback is dangerous. Capacity fallback may be valid when an authorized alternate preserves the contract. An auth mismatch or skipped policy is not capacity degradation; it changes who may act or which decision governs the effect.


## What the Published Proof Does Not Show

 PR #131669 is proposed, unreleased behavior. Its published proof used disposable state, an isolated Gateway/worker protocol boundary, and a loopback mock provider. It did not use a production Gateway, external channel delivery, a real model provider, a remote VM, or a managed worker fleet.

 The article's later-fence claim is intentionally limited to the focused regressions named above. Worker operations with separate authority/effect contracts do not automatically inherit this exact repair. Their policy owner, durable operation identity, and actual mutation boundary must be identified independently.

 The claim would fail if the base worker path already ran the same policy before effects; if a blocked spawn still created a child; if a blocked send changed the target transcript; if concurrent retries reran policy or duplicated an effect; or if authority revocation could still begin one of the fenced mutations.


## How I Audit an Alternate Execution Path Now



- List every transport that can reach the same effect.

- Locate the shared admission policy and prove that each path calls it.

- Place the policy after durable owner election but before the first effect.

- Persist one terminal decision for concurrent and replayed attempts.

- Recheck delegated authority immediately before each later mutation.

- Test blocked behavior by proving the child, message, allocation, or enrollment effect stayed absent.

- Bind mutable proof to the exact tested snapshot.


 The authorial decision I want to preserve is simple: do not solve path asymmetry with another path-specific policy. Make equivalent effects converge on one decision owner, then make every delayed effect prove that authority is still alive.



### Related Posts



- [Agent Dispatch Should Be Parent-Owned](/jingxiao-cai-blog/parent-owned-agent-dispatch-router-contracts.html)

- [Prepared Is Not Authorized](/jingxiao-cai-blog/prepared-is-not-authorized-agent-activation-packet.html)

- [Approval Is Not Execution](/jingxiao-cai-blog/approval-is-not-execution-deferred-side-effects.html)

- [VPS OAuth Survival Guide](/jingxiao-cai-blog/vps-oauth-survival-guide.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and self-hosted AI-agent operations. He likes alternate execution paths that converge on the same policy and recheck authority before delayed effects.

 If two paths can create the same effect, they should not disagree about who gets to say no.



 Originally published April 29, 2026 · Substantially updated August 30, 2026

 [← Back to Blog](/jingxiao-cai-blog/)
