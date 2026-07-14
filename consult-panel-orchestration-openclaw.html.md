# LLM Panel Orchestration in OpenClaw: Config-Backed Routing, Timeout Classes, and Honest Dissent Without Chaos

URL: https://anyech.github.io/jingxiao-cai-blog/consult-panel-orchestration-openclaw.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/consult-panel-orchestration-openclaw.html.md
Date: 2026-04-03
Updated: 2026-07-04
Tags: openclaw, ai-agents, llm, orchestration, devops, multi-model-review

Summary: How I turned multi-model consultation into a config-backed OpenClaw workflow with launch guards, artifact-backed completion ledgers, local-lane promotion gates, bridge-back delivery contracts, and user-visible dissent.

---

[← Back to Blog](/jingxiao-cai-blog/)

# LLM Panel Orchestration in OpenClaw: Config-Backed Routing, Timeout Classes, and Honest Dissent Without Chaos


 **April 3, 2026** | By Jingxiao Cai | **Updated July 4, 2026**

 Tags: openclaw, ai-agents, llm, orchestration, devops, multi-model-review



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a messy internal evolution—manual mixed-panel runs, async handoff bugs, routing drift, and repeated hardening passes—into a cleaner operator memo that actually matches the live system.



 **April 8 follow-up:** I extended this write-up with the later watchdog-hardening pass: deduplicated progress updates, per-run duplicate-state checks, a full regression suite, and one remaining lifecycle edge case that still deserves future cleanup.



 **April 29 follow-up:** I added the final-delivery bridge-back lesson from long-running Discord work: detaching the work is only half the reliability story; the final answer still needs a contract-derived route back to the right conversation.



 **June 22 follow-up:** I added the context-pressure version of the pattern: panel results need artifact-backed completion and a finalizer ledger because a parent thread can be under context, compaction, or write-lock pressure even when the panelists themselves finished correctly.



 **July 4 follow-up:** a private local-model router can be available before it is eligible for the default panel. Local lanes still need soak, role assignment, timeout and weighting policy, and explicit config/Gateway approval before promotion. I expanded that boundary in [A Local LLM Router Is Not a Panel Lane Yet](/jingxiao-cai-blog/local-llm-router-not-panel-lane-yet.html).



 **Scope note:** this post is about the *orchestration pattern*, not about proving one model is universally best. The point is how to run a full panel, finish cleanly, surface dissent honestly, and keep routing policy in the right layer.



 **Another boundary up front:** a full jury panel is expensive and is **not** my default for routine queries. I use it for worthwhile ambiguity, higher-cost decisions, explicit panel requests, or cases where dissent is actually worth the latency.


 The same routing policy also supports lighter consultation modes. I am focusing on the full jury here because that is where orchestration bugs, weighting mistakes, and async handoff failures become easiest to see.





## The Hard Part Was Never “Ask More Models”

 Running a full panel of LLMs in parallel is not the interesting problem. Spawning the children is easy. Keeping the result coherent is the real work.

 The failures I kept hitting were never glamorous:



- one expected panelist quietly did not get launched

- an ACP-backed lane finished, but the answer did not auto-surface to the parent thread

- a partial result arrived, then the orchestrator went silent

- a slow non-core model held the whole panel hostage

- a wildcard dissent looked louder than it deserved because the weighting rules stayed implicit

- late completions arrived after the real answer was already delivered



 **The real unit of work is not “query 8 models.” It is “finish one user-visible review exactly once, with lineup integrity, visible weighting, and bounded latency.”**



 That is the problem the `consult-panel` workflow now solves inside my OpenClaw setup.


 **Current live full-jury shape:** the default active panel currently resolves to **7 voices** — a primary reasoning consultant, three additional stable-core critics, a diversity critic, a fixed experimental panelist, and a rotating wildcard endpoint — with explicit lineup resolution, timeout classes, dissent visibility, and degradation rules. The old Gemini ACP lane still exists as a dormant route definition, but it is no longer part of the default lineup.



## The Design Decision That Saved the Whole Thing

 The best decision was architectural, not prompt-related.

 The public invocation surface stays deliberately small. Natural requests like *consult the panel*, *panel review*, *have the consultants weigh in*, or *run jury mode* map into the same orchestration layer, while the routing truth stays in durable config and ops docs rather than inside the prompt wrapper.

 The canonical grounding for current behavior lives in three places: the routing config, the consult-panel skill, and the routing operations guide. That keeps the live policy inspectable without hardcoding model/version logic into the user-facing orchestration layer.


 **Keep the skill thin. Keep the routing truth in config and ops docs.**



 The user-facing skill exists to do orchestration:



- detect that the user wants a panel review

- resolve the configured lineup

- shape the review packet

- spawn the panel

- track completions and synthesize the result


 Every panelist gets the **same review packet**. That sounds trivial, but it is one of the most important fairness rules in the whole workflow: differences in output should come from the models, not from packet drift.

 What it does *not* do is hardcode model/version policy. That lives in durable config and the ops guide instead:



- `routing config`

- `operations guide`

- `lineup resolver`

- `packet-size gate`


 That split matters because it keeps model churn from leaking into workflow prose. If the primary lane changes, or the ACP secondary policy changes, or the fixed experimental lane gets replaced, I want to edit config—not rewrite orchestration logic in six places.


 **Naming lesson:** the skill is called `consult-panel`, not `jury`. “Jury” is a useful mode name, but it is a bad public skill name because it leaks internal taxonomy into the invocation surface.



## What the Current Panel Actually Looks Like

 The live jury lineup is not “eight random models.” The default active panel is currently seven voices with different jobs, different timeout leashes, and different interpretive weight.



| Panelist | Role | Class | Why it exists |
| --- | --- | --- | --- |
| **Primary reasoning consultant** | Primary consultant | `stable_core` | Main decision anchor for full-panel review. |
| **Compact-packet challenger** | Challenger consultant | `stable_core` | First stable-core challenger when the packet is compact enough. |
| **Stable core critic A** | Core critic | `stable_core` | Reliable large-context core voice and oversize fallback for the challenger. |
| **Stable core critic B** | Core critic | `stable_core` | Independent strong core voice. |
| **Diversity critic** | Diversity critic | `stable_core` | Semantic diversity lane without inventing a second wildcard slot. |
| **Fixed experimental panelist** | Fixed experimental panelist | `fixed_experimental` | Meaningful non-core lane with stable identity that can corroborate consensus or widen a real split. |
| **Rotating wildcard endpoint** | Rotating wildcard panelist | `rotating_wildcard` | Exploratory dissent / novelty lane, never decisive by itself. |

 The important thing is that **the current lineup is config-resolved**, not reconstructed from memory. That is how I stopped “full panel” from quietly meaning four models one week and seven the next.

 I also stopped pretending a dormant route definition was the same thing as an active default lane. The Gemini ACP path still exists in config, but it is intentionally **not** part of the default active jury lineup right now because that route became too finicky to treat as a routine full-weight core lane. If it comes back later, it returns explicitly as a nonblocking external lane rather than a hidden substitute.

 If the resolved lineup and the accepted spawn set do not match, the run is degraded immediately instead of being presented as a successful full panel. That one rule fixed a surprising amount of quiet orchestration dishonesty.



```
resolve_panel_shape(mode="jury")
```

 If the expected lineup and the actual spawn set differ, the run is degraded. I do not pretend it was a full panel.


 **Local-lane promotion note:** the same rule now applies to private local model routes. A local router can pass auth, model-list, chat, streaming, failover, and short-soak checks and still remain a candidate lane rather than a default panel voice. Promotion needs an explicit role, timeout class, weighting policy, rollback plan, and a reviewed config/Gateway activation step; the standalone follow-up is [here](/jingxiao-cai-blog/local-llm-router-not-panel-lane-yet.html).



## The Schema That Matters More Than the Prompt

 The routing config now carries three layers of truth:



- **role mapping** — what each semantic lane currently points to

- **mode shape** — which panelists belong to `standard`, `jury`, and compatibility aliases like `deepJury`

- **panel heuristics** — timeout classes, weight bands, checkpoint timing, and benchmark reference guidance


 A simplified shape looks like this:



```
{
  "roles": {
    "primary_consultant": { "preferred": "<primary-reasoning-model>" },
    "optional_external_lane": { "agentId": "<secondary-agent>", "modelAlias": "<stable-secondary-lane>" },
    "fixed_experimental_panelist": { "preferred": "<fixed-experimental-model>" },
    "rotating_wildcard_panelist": { "preferred": "<rotating-wildcard-endpoint>" }
  },
  "modes": {
    "jury": {
      "panelists": [
        "primary_consultant",
        "stable_core_challenger",
        "stable_core_critic_a",
        "stable_core_critic_b",
        "diversity_critic",
        "fixed_experimental_panelist",
        "rotating_wildcard_panelist"
      ]
    }
  },
  "panelHeuristics": {
    "classes": {
      "stable_core": { "nominalWeight": 1.0, "softTimeoutSeconds": 150 },
      "stable_external_nonblocking": { "nominalWeight": 1.0, "softTimeoutSeconds": 150 },
      "fixed_experimental": { "nominalWeight": 0.75, "softTimeoutSeconds": 120 },
      "rotating_wildcard": { "nominalWeight": 0.4, "softTimeoutSeconds": 90 }
    }
  }
}
```


 **Important boundary:** this is a sanitized explanatory sketch, not a byte-for-byte dump of the live file. I keep the reusable design, class logic, and role split; I leave out the local debris nobody else needs. The `diversity_critic` role shown in the schema resolves to the active diversity lane in the live panel.



## Why Timeout Policy Had To Change

 One of the most useful corrections was embarrassingly simple:


 **Parallel panel timeout is tail-latency control, not additive latency math.**



 That sounds obvious once you say it. But it matters operationally.

 If seven lanes are done and the only remaining holdout is a rotating wildcard endpoint, I should not keep acting as if the panel is “still incomplete” in the same way it would be if two stable-core critics were missing. Those are different situations.



| Class | Nominal weight | Soft timeout | Practical rule |
| --- | --- | --- | --- |
| `stable_core` | 1.0 | 150s | Default decision anchor. Keep the leash longest. |
| `stable_external_nonblocking` | 1.0 | 150s | Full interpretive weight if present, but do not block forever. |
| `fixed_experimental` | 0.75 | 120s | Useful corroboration or dissent, but non-core. |
| `rotating_wildcard` | 0.4 | 90s | Exploratory only. Drop aggressively when it becomes tail latency. |

 This was the shift from “wait for everyone because fairness” to “wait intelligently because the panel has structure.”


## Benchmark-Informed Weighting Helped, But Only After I Put It in Its Place

 I do use benchmark families as a rough reference band. I do *not* use them as a vote-counting formula.

 The live ops guide records a checked snapshot, but the useful signal is structural rather than brand-specific:



- the stable-core cluster is close enough to anchor the answer

- an external secondary lane can matter a lot when it is present, but it should remain operationally nonblocking instead of being silently required

- the fixed experimental lane is meaningful, but still non-core

- the rotating wildcard should not be benchmark-weighted like a fixed model at all because it is intentionally not stable enough to deserve that treatment



 **Important caution:** benchmark-informed weighting is helpful only when it stays advisory. The moment it becomes a mechanical vote tally, the system gets performatively rigorous and operationally dumb.



## The Async Rules Are Why the Workflow Finally Feels Trustworthy

 The strongest part of the current setup is no longer the model lineup. It is the coordination layer around it.

 The workflow now explicitly tracks:



- expected panelists

- pending vs completed lanes

- first substantive result arrival

- whether interim checkpoint updates have already been sent

- which panelists are eligible for timeout-drop

- whether ACP needs a targeted follow-up check

- whether the panel is merely closed or fully superseded


 The practical control loop looks more like this now:



```
resolve lineup from config
spawn all expected panelists
track expected vs completed lanes
send one bounded checkpoint when the first real result arrives
send one second checkpoint only if state changes meaningfully
if only ACP remains, inspect ACP directly before waiting blindly
after the second checkpoint, timeout-drop non-core stragglers
synthesize immediately once all expected lanes are complete or dropped
```

 That is not glamorous. It is also the part that stops the panel from becoming a reliability anti-feature.


## Final Delivery Needs a Bridge Back, Not Just a Background Thread

 The long-running-work version of this bug has the same shape as the panel bug: the worker can finish correctly while the user-facing conversation still never receives the final result. Moving a task into the background protects the main turn budget, but it does *not* automatically solve final delivery.

 The reliable pattern is a small delivery contract created before the detached work starts. It records the origin conversation, the work conversation, the single update target, and the delivery mode. Default detached work reports to its bound work thread. Bridge-back to an origin thread is explicit, not something the worker infers from memory or a nearby chat summary.


 **A background worker should never guess where its final answer belongs.**



 The practical loop now looks like this:



```
persist a delivery contract before launch
launch the worker with the contract reference and final-ready marker
wait for an explicit final-ready signal
dry-run the delivery plan against the persisted contract
send the final answer once through an idempotent ledger
split oversized finals deterministically instead of truncating them
record delivered message identifiers when the channel returns them
```

 That is deliberately boring distributed-systems hygiene: stable identity, explicit target selection, idempotent side effects, and observable delivery state. The agent-specific twist is that the final answer is prose, not a database row, so duplicate suppression and oversized-message handling need to preserve the user-visible text rather than silently summarize or drop it.


## June 2026 Follow-Up: Artifact-Backed Completion Beats Transcript Luck

 The later failure mode was subtler: panelists could finish and write useful results, but the parent thread was not always the healthiest place to notice, validate, synthesize, and deliver them. The failure was not “the panel had no answer.” It was “the answer existed in artifacts, while the user-facing orchestration path was under context and delivery pressure.”

 That pushed the design one step past status-line completion. A child saying “ready” is now provisional. The durable proof is an expected result artifact in the run directory, validated against the panel ledger. The finalizer reads the ledger, checks each expected lane, and only then decides whether the run is waiting, ready, blocked, or explicitly partial.



```
resolve expected panel lanes
write a panel-run ledger
record result paths before launch
accept compact child status lines as hints
validate authoritative result artifacts
finalize from the ledger, not from transcript vibes
deliver once through the recorded target
```

 This matters most when the parent conversation is already large. A huge thread can be slow, compacting, or temporarily write-locked. The panel should not lose functional quality just because the parent transcript is an overloaded coordination surface. The safer pattern is to promote the important state into a small artifact ledger and let the parent thread become one consumer of that ledger, not the only place the truth can live.


 **If a panel result is important, make it recoverable from artifacts before trusting the chat transcript to remember it.**




 **Important boundary:** this is a helper-level bridge-back pattern, not yet a native runtime event dispatcher. It is strong enough for local use because delivery targets come from a validated contract and retries are ledger-backed. A true Gateway/runtime event dispatcher would be a different risk class and deserves its own reviewed design.


 The general lesson is simple: if a task is long enough to detach, it is long enough to deserve an explicit final-delivery path. Otherwise “background work” just moves the failure from timeout to silence.


## Why Watchdog Coverage Had To Become a Launch Invariant

 The ugliest real failure was not “a model said something weird.” It was simpler: the panel could emit a clean *waiting on X* checkpoint and then never speak again.

 That is why I no longer treat “children launched” as a valid waiting state by itself. A multi-child run is only allowed to settle into waiting after two things are true:



- the resolved lineup matches the accepted spawn set

- real follow-up wakes exist to carry the panel to the next checkpoint or terminal synthesis


 In my implementation that means a small launch guard plus a watchdog planner. The planner defaults those wakes to **visible delivery** and rejects internal-only coverage by default, because a hidden watchdog is not much comfort if the user still experiences silence.

 Just as important: **generated plans are not proof.** I only count coverage as real once the follow-up jobs actually exist. When watchdog creation fails, the run is degraded immediately instead of being presented as a trustworthy “waiting” state.


 **Important boundary:** this is stronger orchestration hardening, not a formal guarantee. Real cron-backed visible-delivery watchdog wakes now carry the panel through to synthesis in my local repros, but I still describe the result as *best-effort fail-closed behavior*, not mathematical certainty.


 A second late bug was older queued checkpoints leaking out after a terminal answer. The local fix there was much smaller than the bug report made it sound: a tiny monotonic per-run delivery ledger that suppresses stale intermediate checkpoints while still allowing a legitimate retry of the final answer if delivery itself needs one more shot.


## Watchdog Hardening: The Bug Was Not Just Silence, It Was Repeated Almost-The-Same Progress

 The next reliability problem was more embarrassing than dramatic. The panel was no longer always going silent, but it could still emit *repeated user-facing checkpoint blocks* that looked meaningfully new only because they arrived on different async branches.

 The important diagnosis was that this was **not** a transport-duplication issue. The real bug lived in orchestration: child completions and later watchdog/finalization wakes could each recompute the same visible non-terminal state and both decide it was worth sending.

 The hardening rule that actually helped was small and specific:


 **For non-terminal updates, validate not only run identity and closure state, but also whether the same visible progress state for this panel run has already been delivered.**



 In plain English, the panel now remembers the *shape* of the last user-visible checkpoint for the current run. If a later async branch only regenerates the same visible progress state, the watchdog is supposed to do nothing and return quietly instead of spamming the thread with a cosmetically fresh duplicate.



- **duplicate same-state checkpoint** → suppress it

- **watchdog recomputes the same visible state** → suppress it

- **material state actually changes** → allow the next bounded checkpoint through


 I trust the fix more because it stopped being just a theory. The deterministic regression suite now passes the full targeted duplicate-state cases, including the same-state duplicate case, the watchdog-recomputation case, and the “state really changed, so the next checkpoint is legitimate” case.


 **What I would still not overclaim:** this hardening closes the duplicate-checkpoint class much more convincingly, but one stale lifecycle edge case still deserves a future cleanup pass. Right now it looks more like unnecessary probing/log noise than a user-facing synthesis corruption bug, but it is still not the kind of lifecycle ambiguity I want to leave permanent.



## The Two Delivery Bugs That Taught Me the Most


### 1. ACP completion is not the same as normal subagent completion

 One of the nastier failure modes was: Gemini finished, useful text existed, but the parent thread still looked silent. The fix was not “wait harder.” The fix was to treat ACP as a different completion surface and do targeted inspection when it is the last blocker.


### 2. Fresh user follow-up is not a late duplicate

 Another failure mode was subtle: after a final synthesis was already delivered, a true late completion and a fresh user-authored follow-up could land in the same general window. If the orchestrator treated the whole situation as late-result cleanup, it could accidentally suppress the new user instruction.

 That is why the current workflow keeps **panel-closed** and **superseded** as separate states.


 **Durable lesson:** multi-agent workflows fail less from “the model said something weird” than from lifecycle ambiguity. Most bugs live in the handoff layer.



## What I Learned About User-Facing Synthesis

 I used to think the final answer should hide as much orchestration detail as possible. That turned out to be half-right.

 The user does *not* need raw routing trivia. But they *do* need visible weighting.

 So the synthesis now tries to make one thing explicit:


 **Did the disagreement come from stable-core lanes, or only from non-core lanes?**



 That one distinction dramatically improves the trustworthiness of the result. “There was disagreement” is weak. “The stable-core lanes aligned; only the wildcard dissented” is actionable.


## What Other People Can Steal From This Pattern

 You do not need my exact stack to steal the shape.

 If you run any multi-model or multi-agent review workflow, the parts worth copying are:



- **semantic roles, not hardcoded versions**

- **config-resolved lineup before spawn**

- **same packet for fair comparison**

- **weight classes that are visible in synthesis**

- **watchdog coverage as a launch invariant, not a hopeful afterthought**

- **explicit final-delivery contracts for detached work**

- **timeout as tail-latency control**

- **explicit ACP / external-lane delivery handling**

- **clear distinction between closed, degraded, and superseded runs**


 What I would *not* copy is “always ask all models.” Full panel is expensive. It is worth it when the user explicitly asks, or when the decision is ambiguous/costly enough to justify the latency. Reduced modes are part of the design, not a fallback embarrassment.


 **In plain English:** the system got easier to trust the moment I stopped treating multi-model review as “fan out and pray” and started treating it like a first-class orchestration problem with schema, lifecycle, and delivery rules.



## The Design Rule I Trust Most Now

 If I had to compress the whole thing into one line, it would be this:


 **A good panel workflow does not just collect opinions. It defines which opinions count how much, how long they are allowed to block, and how the final answer reaches the user without ambiguity.**



 That is what changed the workflow from an interesting prompt trick into a reusable piece of operating infrastructure.


 **Sanitization note:** I kept the architecture, role taxonomy, class policy, and workflow lessons because those are the reusable parts. I intentionally left out local session keys, job IDs, run IDs, exact Discord thread IDs, and other runtime fingerprints that would expose the live environment without helping anyone copy the pattern.




### Related Posts



- [Handling Gemini Capacity Exhaustion: Fallback Lanes for Reliable Agent Workflows](/jingxiao-cai-blog/gemini-capacity-exhaustion-fallback-lanes.html)

- [Declarative Change Propagation: How I Built a Self-Documenting Cron System](/jingxiao-cai-blog/declarative-change-propagation-cron-system.html)

- [Why AI Cron Jobs Need Exact-Exec Drivers Instead of Freeform Agent Prompts](/jingxiao-cai-blog/ai-cron-jobs-exact-exec-drivers.html)

- [Why AI Agent Skills Break in Production (and How to Troubleshoot Them)](/jingxiao-cai-blog/troubleshooting-ai-agent-skills.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and likes orchestration systems that fail loudly, surface dissent honestly, and do not depend on one human remembering where all the asynchronous bodies are buried.

 If your panel workflow cannot explain why one model was allowed to block the answer and another one was not, it is still running on vibes.




 Found this useful? Send it to the person still calling eight parallel model calls a “simple jury prompt.”

 [← Back to Blog](/jingxiao-cai-blog/)
