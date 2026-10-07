# One Client, Two Module Copies: Who Owns the State?

URL: https://anyech.github.io/jingxiao-cai-blog/one-client-two-module-copies-runtime-ownership.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/one-client-two-module-copies-runtime-ownership.html.md
Date: 2026-10-07
Tags: openclaw, codex, typescript, reliability, agent-ops

Summary: Two module evaluations can see one in-memory client but separate owner state. A merged OpenClaw change shares that owner within one build; reported regressions are not deployment reliability.

---

[← Back to Blog](/jingxiao-cai-blog/)

# One Client, Two Module Copies: Who Owns the State?


 **October 7, 2026** | By Jingxiao Cai

 Tags: openclaw, codex, typescript, reliability, agent-ops



 This post was co-created with **Clawsistant**, my OpenClaw AI agent.
 It helped separate public source and reported regression evidence from deployment claims.



 **Scope:** This note covers merged public PR #160949 and its public implementation and tests. It does not claim that a particular production incident was fixed or that every deployed version has this behavior.


**Relationship disclosure:** `anyech`, this site’s GitHub identity, authored PR #160949 with AI assistance. Reported execution results are contribution-author reports, not an independent rerun. The article analyzes the October 1 merge, not an assertion that today’s release or main branch is unchanged.

Here, a *physical client* means the same in-memory app-server client instance, not merely two connections to the same server. A *module copy* is a separate evaluation of the plugin code. Two copies of the same plugin build can receive the same long-lived app-server client. The client is one object, but if each module evaluation keeps its own registry for that object, the runtime state splits: a second copy can add another callback or fail to see ownership recorded by the first. The symptom looks like a protocol problem even though the broken boundary is local state ownership.

 **Early bounded proof — PR-reported, with pinned assertion source:** after the test loads a second same-build module copy around the same client, the close-handler count remains one; the second copy can see and release the retained owner exactly once. Separate regressions exercise native-child retirement through the original monitor and visibility of the same rate-limit notification snapshot through both copies.

## The client is shared; the module registries were not

The affected Codex app-server runtime associates callbacks, retained-thread release tokens, monitor state, and rate-limit observations with a physical client. Module-level maps normally make that association cheap and clear. The trap appears when the same build is evaluated twice: each copy creates a separate map, while both copies are handed the same client.

That gives the system two answers to “what state belongs to this client?” Copy A may own the close handler and retained-thread release function; copy B sees the same transport but not the same bookkeeping. Registering another handler does not repair the missing ownership relationship. Nor does an extra unsubscribe fallback explain which copy is responsible for releasing the original custody.

## Share ownership at the same boundary as the client

Merged [OpenClaw PR #160949](https://github.com/openclaw/openclaw/pull/160949) moves those client-owned registries under the existing build-scoped state owner. Same-build module copies can then consult one runtime record for the physical client. The claim here is the shared owner at that boundary, not an independently established claim about every identity or generation check.

The practical design rule is narrow: state tied to one physical client should have one owner across copies of the same build. That does not mean making every cache global. Keeping unrelated builds isolated is a design requirement, not a cross-build negative-test result established here.

## What the public tests cover

The public description reports same-build-copy regressions for one close-handler registration, retained-owner visibility and release, original native-child custody retirement, and rate-limit snapshot visibility. The claim is the state/owner boundary those controls describe—not a deployed-system success rate. Three commit-pinned sources are [client runtime](https://github.com/openclaw/openclaw/blob/7f60f5f7e51dfa5bb72078e9583c19646e934381/extensions/codex/src/app-server/client-runtime.test.ts), [native-child close](https://github.com/openclaw/openclaw/blob/7f60f5f7e51dfa5bb72078e9583c19646e934381/extensions/codex/src/app-server/native-subagent-monitor.close.test.ts), and [rate-limit cache](https://github.com/openclaw/openclaw/blob/7f60f5f7e51dfa5bb72078e9583c19646e934381/extensions/codex/src/app-server/rate-limit-cache.test.ts). The complete pinned client-runtime file declares *“keeps the exact retained owner when a same-build plugin module copy resumes the client”*: after `vi.resetModules()` and re-import it asserts one close-handler registration, visibility of the retained owner, and exactly-once release. Reading those assertions confirms what the test checks, not that we executed it. No test was rerun for this article.

The PR description reports 119 tests across eight files and two routed projects, plus a paired native-protocol comparison. Those counts and the comparison remain PR-reported results, not an experiment independently executed for this article. Source inspection is not test execution. The merged revision is [7f60f5f](https://github.com/openclaw/openclaw/commit/7f60f5f7e51dfa5bb72078e9583c19646e934381), merged October 1, 2026.

## Keep the claim at the tested boundary

These artifacts support the same-build module-copy/client ownership path. They are not a full Gateway or Control UI end-to-end reliability estimate, and they do not establish the cause or resolution of any individual production event. A deployment's live behavior still depends on its actual version and runtime; this article makes no claim about a local installation.

The useful takeaway is not “make every registry global.” It is to put shared state at the narrowest owner that actually survives module duplication: the build-scoped runtime for the physical client.


### Related Posts



- [The Old Owner Was Still There: Why Agent Cutovers Need Ownership Proof](/jingxiao-cai-blog/old-owner-agent-cutovers.html)

- [Thread Affinity Is a Safety Boundary for Agent Work](/jingxiao-cai-blog/thread-affinity-safety-boundary-agent-ops.html)

- [Proof Without Touching Production: A Safer PR Boundary for Agents](/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html)



### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, automation reliability, and the operational boundaries that keep small systems understandable.

 One physical client should not acquire a second owner just because its module was evaluated twice.


## Comments

 Found this useful? Leave a comment below, or send it to someone debugging state shared across plugin module copies.

 [← Back to Blog](/jingxiao-cai-blog/)
