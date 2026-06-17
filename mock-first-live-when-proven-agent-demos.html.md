# Mock First, Live When Proven: How to Keep Agent Demos Honest

URL: https://anyech.github.io/jingxiao-cai-blog/mock-first-live-when-proven-agent-demos.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/mock-first-live-when-proven-agent-demos.html.md
Date: 2026-06-17
Tags: ai-agents, agent-ops, tooling, demo-safety, reliability, openclaw

Summary: Mock paths make agent demos safe to build, but they should never pretend to be live. Keep demo modes explicit, prove the live connector with cheap checks, and fail closed when evidence is missing.

---

← Back to Blog

# Mock First, Live When Proven: How to Keep Agent Demos Honest


 June 17, 2026 | By Jingxiao Cai

 Tags: ai-agents, agent-ops, tooling, demo-safety, reliability, openclaw



 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped turn a search-demo hardening pass into a generalized public pattern and remove deployment-specific names, identifiers, paths, prompts, and logs.



 Boundary: this is a demo-safety pattern, not a transcript of a live system. The examples below are intentionally generic so the useful lesson survives without exposing deployment fingerprints that are not needed for the lesson.


 A mock-backed demo is not dishonest by itself. It is often the safest way to build a user interface, exercise error states, and keep a prototype moving while the real connector is still unstable.

 The dishonesty starts when the demo stops saying which lane it is using.

 That distinction matters even more for AI-agent systems. A normal application can usually label a feature as “demo data.” An agent demo has more moving parts: model output, tool calls, cached examples, retrieval snippets, retry behavior, timeouts, and final natural-language synthesis. If those layers are not labeled clearly, a mock can accidentally inherit the credibility of a live run.


 Mock mode is a valid engineering tool. Unlabeled mock mode is a product risk.




## The Pattern: Mock First, Live When Proven

 The pattern I now prefer is simple:



- Build the demo around a deterministic mock path first.

- Label the mode visibly in the UI, logs, and final report.

- Add a live connector behind an explicit gate.

- Probe the live path with a cheap, non-destructive request before showing it as real.

- If the live proof is missing, fall back to mock only when the result is still labeled as mock.


 That flow is less flashy than “just wire the API and hope.” It also prevents a much worse failure: a user seeing a beautiful answer and assuming the system actually queried the live source when it only replayed canned data.


 Conceptual example: imagine a search-backed assistant demo with two lanes: a mock lane that returns fixed examples, and a live lane that calls a real search service. The public lesson is the control boundary between those lanes, not any specific service, endpoint, account, or deployment.



## Why This Gets Tricky in Agent Demos

 Agent demos blur boundaries because the final answer is a story. A model can summarize mock results with the same confidence and polish it uses for live results. If the surrounding system does not preserve provenance, the final text will not save you.

 The common failure modes are predictable:




 Failure
 What it looks like
 Safer behavior





 Mode ambiguity
 The UI says “search result” without saying mock or live.
 Show a mode badge and include the mode in exported reports.



 Cached proof drift
 A stale successful live response keeps making the demo look healthy.
 Attach timestamps and freshness windows to live evidence.



 Timeout laundering
 The live path times out, then the demo silently uses mock data.
 Return “live unavailable; showing mock example” instead of pretending success.



 Prompt-level overclaim
 The model says “I found” even though the tool did not run.
 Pass provenance into synthesis and forbid unsupported live claims.



 Operator blind spot
 The demo works on-screen, but logs cannot explain which lane ran.
 Record mode, probe result, freshness, and fallback reason as first-class fields.






## A Good Demo Has a Mode Ledger

 I like a tiny mode ledger because it makes the demo state hard to hand-wave:

 {
 "mode": "live",
 "live_probe": "passed",
 "probe_checked_at": "recent",
 "source_freshness": "within_window",
 "fallback_used": false,
 "user_visible_label": "Live data"
}

 When live proof is missing, the ledger should look different:

 {
 "mode": "mock",
 "live_probe": "timeout",
 "source_freshness": "not_proven",
 "fallback_used": true,
 "user_visible_label": "Mock example; live source unavailable"
}

 The exact field names do not matter. The invariant does: the final experience should not be able to claim more liveness than the system proved.


## Mock Is for Product Shape; Live Is for Trust

 Mock paths are excellent for product work:



- the page loads reliably during design reviews,

- edge cases can be forced without breaking real accounts,

- screenshots and docs stay deterministic,

- front-end and agent-synthesis work can proceed before the live backend is ready, and

- public demos can avoid exposing private or sensitive data.


 But mock paths cannot prove that the real integration works. Only a live path can do that, and only if the proof is recent enough, narrow enough, and visible enough.

 This is why I do not like a single “demo mode” toggle that hides everything behind one boolean. The better design separates three states:




 State
 Meaning
 User-visible claim





 Mock
 Deterministic sample data; no live source proof.
 “Example response.”



 Live-proven
 Recent cheap probe passed and the request used the live connector.
 “Live response.”



 Degraded
 Live source was attempted or expected but proof failed.
 “Live unavailable; showing mock or cached example.”






## Feature-Flag Lessons Apply Here

 This is basically feature-flag discipline applied to agent demos. LaunchDarkly's testing guidance notes that feature flags can target test contexts, expose functionality to narrow audiences, and use fallback values when a flag cannot be evaluated. That same shape maps well to demos: target the risky live behavior deliberately, keep fallback behavior explicit, and do not pretend a fallback is the primary path.

 Google's SRE book also draws a useful monitoring distinction between internal metrics and externally visible behavior. A live agent demo needs both: internal evidence that the connector was healthy, and external behavior that tells the viewer what they are actually seeing.

 A green internal probe without a visible label is not enough. A visible label without a real probe is not enough either.


## The Fail-Closed Rule

 For demos that influence decisions, I prefer this rule:


 If the system cannot prove live mode, it must not describe the result as live.



 That does not mean the demo has to stop. It means the claim changes. A degraded demo can still be useful if it says what happened:



- “Live search timed out; showing a mock example.”

- “Live connector is disabled for this public demo.”

- “Cached example from a previous successful run; freshness not guaranteed.”

- “Tool call was not executed; this is a UI-only preview.”


 Those labels are not embarrassing. They are trust-preserving.


## The Checklist I Use

 Before I treat an agent demo as live, I want answers to these questions:



- Mode: is the current run mock, live, cached, or degraded?

- Label: does the user-facing screen say that plainly?

- Probe: did the live connector pass a cheap, non-destructive check recently?

- Freshness: is the live proof inside a documented freshness window?

- Fallback: if fallback occurred, is it visible in the UI and final report?

- Synthesis: does the model receive the mode/provenance fields before writing the answer?

- Audit: can logs reconstruct which lane ran without exposing private details?

- Public safety: can the mock path demonstrate the idea without leaking real data, accounts, paths, or identifiers?


 If the answer to any of those is fuzzy, the demo can still be shown as a mock. It should not be sold as live.


## My Final Read

 The safest agent demos are not the ones that avoid mocks. They are the ones that make mocks boringly obvious and make live claims earn their label.

 Mock first so you can design safely. Go live only when the connector proves itself. If the proof disappears, fail closed on the claim, not necessarily on the whole demo.


 A good demo does not need to be live all the time. It needs to be honest every time.





### Related Posts



- Fail-Closing Agent Launches: Why Auth and Readiness Gates Should Block Before Tooling Starts

- Agent Dispatch Should Be Parent-Owned: Let Routers Produce Contracts, Not Side Effects

- When Live State Moves, Agent Validators Need to Follow

- When a Reviewer Demands Live Proof: Escalation Paths for Agent PRs






### References



- LaunchDarkly: Testing code that uses feature flags

- Google SRE Book: Monitoring Distributed Systems






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability. This blog captures lessons from building, debugging, and operating self-hosted AI-agent workflows.





### Feedback

 Questions, critiques, or war stories about mock/live demo boundaries? Open an issue in the blog repository or reach out through the linked channels.
