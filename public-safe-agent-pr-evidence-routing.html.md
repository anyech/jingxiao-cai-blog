# Public-Safe Evidence Beats Private Debugging Dumps in Agent PRs

URL: https://anyech.github.io/jingxiao-cai-blog/public-safe-agent-pr-evidence-routing.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/public-safe-agent-pr-evidence-routing.html.md
Date: 2026-06-21
Tags: ai-agents, agent-ops, open-source, debugging, opsec, automation

Summary: When an agent hits a real production-flavored failure, the useful upstream contribution is not a raw log dump. It is a small, public-safe evidence unit that names the failure class, the observed state shape, the proof boundary, and the next verification step.

---

[← Back to Blog](/jingxiao-cai-blog/)

# Public-Safe Evidence Beats Private Debugging Dumps in Agent PRs


 **June 21, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, open-source, debugging, opsec, automation



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a private auth/session debugging episode into a generalized public pattern and remove emails, session IDs, channel IDs, hostnames, local paths, tokens, private logs, and deployment-specific context.



 **Boundary:** this is an agent-operations pattern, not a raw incident report. The upstream thread was public, but the private runtime context behind the observation is intentionally generalized.


 The easiest way to make an upstream bug report useless is to remove all evidence.

 The easiest way to make it dangerous is to paste the whole private debugging session.

 Agent systems make this trade-off sharper because the raw evidence is often full of things that should not become public: auth profile names, session identifiers, channel context, local file paths, hostnames, provider fallbacks, command transcripts, and operational habits. But upstream maintainers still need something concrete. They do not need vibes. They need a small, reproducible-looking signal that explains the failure class without leaking the operator.


 **The useful unit is not the log dump. The useful unit is a public-safe evidence slice: observed state shape, failure class, proof boundary, and next verification step.**




## The Situation

 A public OpenClaw pull request was repairing a stale runtime auth-selection class. The short version: transient fallback state can get persisted in a place where future runs treat it as if it were still the intended selection.

 I had a matching current-release failure signal from a real agent deployment. That signal was useful to the PR because it showed the bug class was not only a synthetic fixture and not only a cross-provider fallback corner. It also appeared in a same-provider auth-profile shape where an automatic emergency profile had become sticky after the primary profile was healthy again.

 That evidence was relevant. It was also not publishable raw.

 The raw local context included the usual private mess: exact auth profile identities, session-store entries, channel surfaces, timestamps, local recovery scripts, and deployment shape. None of that belonged in a public GitHub comment.


## The Evidence Slice That Was Safe to Share

 The public-safe comment kept the parts maintainers could reason about:



- the failure was seen on the current release, not on the PR branch

- the setup shape involved same-provider auth profiles, with one configured primary and fallback/emergency profiles

- the affected sessions did not have a user-auth-profile lock

- the persisted state was marked as `auto`, not as a deliberate user override

- the primary profile was available at scan time

- a dry-run recovery would clear older automatic fallback pins while skipping very recent ones

- the comment explicitly said it was failing evidence, not after-fix proof for the PR branch


 That is enough for an upstream maintainer to evaluate relevance without receiving a private transcript.


 **Public reference:** the sanitized evidence comment is on OpenClaw PR [#87893](https://github.com/openclaw/openclaw/pull/87893#issuecomment-4665323033). The blog post you are reading deliberately keeps the lesson more general than the comment itself.



## The Pattern

 When an agent produces upstream evidence from private runtime state, I now use this translation table.



| Private raw evidence | Public-safe replacement | Why it is better |
| --- | --- | --- |
| Exact account, profile, or email values | Role-level shape: primary profile, fallback profile, emergency profile, user override, automatic override | Preserves the state-machine meaning without exposing identity. |
| Session IDs, channel IDs, and local store paths | Counted observations and affected surface class | Gives maintainers scale and scope without leaking routing metadata. |
| Full logs or transcripts | Minimal state predicates and sanitized counters | Turns noisy logs into a checkable bug shape. |
| Private recovery command output | Dry-run recovery behavior: what would be cleared, skipped, or left untouched | Shows operational consequence without publishing local tools. |
| “This PR probably fixes it” | Explicit proof boundary: current-release failing evidence, not after-fix proof | Prevents evidence inflation. The maintainer knows exactly what claim is being made. |


## Route Evidence to the Right Upstream Surface

 Another easy mistake is posting good evidence in the wrong place.

 In this case there were multiple related upstream threads: stale issues, adjacent fixes, broader architecture trackers, and an active maintainer PR. The evidence belonged on the active PR because it matched the precise stale-auto-runtime-auth class being repaired. Posting it on an older general issue would have created more triage work and less signal.

 That routing decision matters. A good evidence slice in the wrong thread becomes archaeology. A good evidence slice in the active repair thread becomes maintainer leverage.


 **Rule of thumb:** route evidence to the narrowest active upstream surface where it can change a maintainer decision. If the evidence is only background, say that. If it is not after-fix proof, say that too.



## Name the Proof Boundary

 The most important sentence in the public comment was the caveat: this was current-release failing evidence, not verified after-fix proof for the PR branch.

 That caveat is not weakness. It is what keeps the evidence honest.

 Agent systems are especially prone to proof inflation because they can produce confident summaries from partial evidence. A real production-flavored failure signal is valuable, but it does not automatically prove that a proposed branch fixes the problem. Those are different claims:



- **Failure-class evidence:** this bug shape is real outside the test fixture.

- **Patch relevance evidence:** the proposed change appears to target the right state transition.

- **After-fix proof:** the patched branch was run against a representative before/after scenario and the failure disappeared.


 It is fine to contribute the first one. Just do not label it as the third.


## Why This Is an Agent-Operations Habit

 This is not only a GitHub etiquette point. It is an operations habit for agentic systems.

 As agents read private state, run local validators, summarize incidents, and talk to public systems, they need a default evidence discipline:



- sanitize before publication

- separate raw observation from public claim

- preserve the bug-shape predicates maintainers need

- remove identities, paths, IDs, tokens, and local topology

- state the proof boundary instead of upgrading weak evidence into strong evidence


 The agent should be helpful enough to produce a useful upstream signal and paranoid enough not to export the user’s life as a debugging artifact.


 **Public-posting check:** if the post needs exact private identifiers to be convincing, it is not ready to post. First convert identifiers into roles, counters, state predicates, or a reproducible minimal case.



## The Reusable Checklist

 Before posting private-runtime evidence to a public PR or issue, I want this checklist to pass:



- **Target:** is this the narrow active thread where the evidence can help?

- **Claim:** what exactly does the evidence prove, and what does it not prove?

- **Shape:** did I preserve the state predicates maintainers need?

- **Privacy:** did I remove exact people, emails, IDs, paths, hostnames, secrets, channels, and raw logs?

- **Boundary:** did I distinguish failing evidence from after-fix proof?

- **Next step:** did I say what would turn this into stronger proof?


 That is the difference between an agent that merely has access and an agent that can participate safely in an open-source maintenance loop.



### Related Posts



- [The Screenshot Was Green. The Page Was Wrong: Semantic Validation for Agent Artifacts](/jingxiao-cai-blog/screenshot-green-page-wrong-agent-artifact-validation.html)

- [When the Report Exists but the User Never Sees It](/jingxiao-cai-blog/when-report-exists-but-delivery-failed-agent-ops.html)

- [Troubleshooting AI Agent Skills: Why “Installed” Is Not the Same as “Usable”](/jingxiao-cai-blog/troubleshooting-ai-agent-skills.html)

- [Local Semantic Memory on a 4-Core ARM VPS](/jingxiao-cai-blog/local-semantic-memory-openclaw-arm-vps.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and uses OpenClaw as a personal agent operations lab. He is interested in the boring habits that let autonomous tools touch real systems without turning every useful observation into an accidental leak.

 The best debugging artifact is small enough to share, specific enough to help, and boring enough not to leak anything exciting.



 Found this useful? Send it to someone whose “evidence” folder is one unsanitized log dump away from becoming a security incident.

 [← Back to Blog](/jingxiao-cai-blog/)
