# The Timeout Was Honest. The Active State Was Not.

URL: https://anyech.github.io/jingxiao-cai-blog/timeout-honest-active-state-was-not.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/timeout-honest-active-state-was-not.html.md
Date: 2026-08-25
Tags: ai-agents, agent-ops, debugging, lifecycles, timeouts, tool-calls

Summary: When an adapter exposes tool items only at completion, a watchdog can see zero active work during a real upstream continuation. Fix the missing lifecycle fact first.

---

[← Back to Blog](/jingxiao-cai-blog/)

# The Timeout Was Honest. The Active State Was Not.


 **August 25, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, debugging, lifecycles, timeouts, tool-calls



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped separate a private incident trace from a public-safe lifecycle reproduction, verify the producer/consumer boundary, and keep unreleased implementation evidence out of production claims.



 **Boundary:** this post combines public upstream reports with a sanitized local reproduction and isolated source tests. It omits private prompts, logs, identifiers, paths, routes, model details, and deployment fingerprints. The paired implementation described below is not merged, released, or production-canary evidence.


 A coding-agent turn entered a failure mode in which it went quiet after several normal reasoning and tool cycles. The downstream watchdog waited for terminal completion, saw no active item, and eventually interrupted the turn.

 The obvious fix was to increase the timeout. That would have reduced the chance that this particular watchdog fired first. It would not have repaired the state that made the timeout decision.


 **A watchdog can make a correct decision from an incomplete lifecycle.**




 **Reader promise:** by the end of this post, you will have a small diagnostic test for distinguishing slow continuation from missing lifecycle projection, a paired producer/consumer repair pattern, and explicit conditions that keep timeout tuning in the containment lane.



## The False Zero

 The upstream provider had already added a custom tool item. Its arguments were not complete, so the tool had not been dispatched. The adapter exposed completed raw items, but it did not expose this nonterminal start as an active downstream item.

 That created two simultaneously true views:



| Layer | What it knew | State |
| --- | --- | --- |
| Provider/core | A tool item had been added and was still incomplete. | Nonterminal work exists |
| Downstream client | No projected item was active and no terminal event had arrived. | Active item count is zero |

 The downstream counter was not stale. It accurately counted the lifecycle events it had received. The defect was that the producer-owned start fact never crossed the adapter boundary.

 This distinction matters because the same visible timeout can come from very different mechanisms:



- a genuinely slow but observable continuation;

- a provider stream that stalled between item start and completion;

- a projected item whose completion was lost;

- a terminal event that was emitted but dropped downstream; or

- a local watchdog whose budget is simply too short.


 Changing a timer before separating those cases turns diagnosis into policy guesswork.


## The Smallest Useful Reproduction

 A public-safe reproduction does not need the private transcript. It needs only two projections with identical completion behavior and one stable correlation key:



```javascript
const activeItems = new Set();

function completeTool(event) {
  activeItems.delete(event.callId);
  persistAndDispatch(event);          // completion-owned effect
}

function completionOnly(event) {
  if (event.kind === "item_done") {
    completeTool(event);
  }
}

function pairedLifecycle(event) {
  if (event.kind === "item_added") {
    activeItems.add(event.callId);      // observational only
  }
  if (event.kind === "item_done") {
    completeTool(event);
  }
}
```

 The reproduction checks three boundaries:



| Boundary | Completion-only projection | Paired projection |
| --- | --- | --- |
| Provider adds tool item | Active count remains zero | Stable call ID becomes active |
| Before item completion | Completion watch may fire | Completion watch is blocked |
| Provider completes item | No active item to clear | Blocker clears; persistence and dispatch may proceed |


 **Core invariant:** start is observational; completion owns persistence and dispatch. The signal makes work visible without pretending that partial arguments are executable.



## The Repair Must Be Paired

 A producer-only change can emit a start event that nobody uses. A consumer-only change can wait for a signal that its bundled producer never emits. The repair therefore has an explicit landing order.



- **Producer:** emit a nonterminal raw-item start for provider-added function and custom-tool items.

- **Identity:** preserve a stable correlation key across start and completion, even if provider item shapes or fallback IDs differ.

- **Consumer:** count that item as a completion blocker while it is active.

- **Cleanup:** clear it on matching raw completion and on terminal/error cleanup.

- **Effects:** keep persistence, dispatch, assistant-content projection, and completion semantics owned by later authoritative events.


 The isolated producer tests covered start/completion identity reuse and a dynamic-tool round trip. The isolated consumer tests covered start/completion correlation, waiting while a start is present, and an explicit no-start timeout control. Broader source checks passed in those isolated trees.


 **Release boundary:** the current bundled producer does not emit the new start signal. That makes the consumer half intentionally dormant until a released producer provides the contract. A tested local pair is implementation evidence, not a production fix.


 The falsification checks below assume that a future producer first satisfies that start-event contract. They test the behavior of the pair under that precondition; they do not claim that the currently bundled producer already does so.


## Why a Larger Timeout Is Still Useful

 Timeout containment is not useless. When an inner stream has its own retry or failure classification, a larger outer budget can let that inner mechanism act first. That can produce a more precise error and reduce premature interruption.

 But containment and repair answer different questions:



| Change | What it improves | What it does not prove |
| --- | --- | --- |
| Increase outer quiet window | Changes which bounded watchdog gets to classify the silence first | That downstream state now includes the active provider item |
| Project item start | Restores visibility of nonterminal provider work | That the provider will eventually complete successfully |
| Track start through completion | Prevents false-zero completion timeout while the item is active | That unbounded waiting is safe |

 Keep a terminal backstop. A visible active item can still hang forever. The point is not to remove timeouts; it is to make their inputs truthful.


## A Diagnostic Ladder for Silent Turns



- **Reconcile effects first.** Determine whether a tool was dispatched, completed, or never left the provider stream before retrying anything.

- **Locate the last authoritative lifecycle event.** Separate provider item-added, item-completed, assistant output, and terminal turn events.

- **Compare layer views.** Did the producer know about an item the downstream client could not count?

- **Prove the projection path.** Check whether an app-server or adapter notification actually existed before blaming forwarding or the host.

- **Classify deadline coupling.** Which watchdog fired first, and which progress anchor reset each budget?

- **Test start, done, and no-start controls.** A useful regression must prove both correct waiting and bounded failure.

- **Preserve landing order.** Do not ship a consumer contract against a producer version that cannot emit it.


 Public reports such as [openai/codex#32659](https://github.com/openai/codex/issues/32659) and [openclaw/openclaw#125287](https://github.com/openclaw/openclaw/issues/125287) establish the broader incomplete-turn failure family. The open timeout-only mitigation in [openclaw/openclaw#111646](https://github.com/openclaw/openclaw/pull/111646) illustrates the containment lane. None of those public records alone proves this paired implementation; the bounded reproduction and isolated tests supply that narrower evidence.


## When Not to Use This Pattern



- Do not synthesize fake activity from a local timer or heartbeat when the producer owns the real lifecycle fact.

- Do not treat reasoning progress, partial tool arguments, or a start signal as a final answer.

- Do not persist or dispatch a tool from an incomplete start event.

- Do not replay uncertain side effects merely because the outer turn timed out.

- Do not remove the terminal backstop after making active work visible.

- Do not claim a paired fix is live when one released side of the contract is still missing.



 **Falsifier:** this claim fails if a provider-added tool item still leaves downstream active count at zero under the paired contract; a start event persists or dispatches the tool; stable call-ID correlation fails; completion or terminal cleanup leaks a blocker; or the no-start control cannot reach the bounded timeout path.



## Conclusion

 In the investigated incident, the timeout was not the diagnosed root cause. It was the layer that finally made an invisible state disagreement user-visible.

 The durable lesson is broader than one coding-agent adapter: if a downstream controller makes lifecycle decisions, every producer-owned nonterminal state that blocks completion needs a truthful, correlated projection. Tune timers for containment, but repair missing facts at the boundary that owns them.



### Related Posts



- [When a Coding-Agent Route Drifts](/jingxiao-cai-blog/coding-agent-route-drift-without-premature-fixes.html)

- [Why AI Cron Jobs Need Exact-Exec Drivers](/jingxiao-cai-blog/ai-cron-jobs-exact-exec-drivers.html)

- [A Visible Message Does Not Prove an Agent Wake](/jingxiao-cai-blog/visible-message-does-not-prove-agent-wake.html)

- [When the Report Exists but Delivery Failed](/jingxiao-cai-blog/when-report-exists-but-delivery-failed-agent-ops.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, technical debugging, and evidence-driven engineering workflows.

 A timeout is only as truthful as the lifecycle state it can observe.




## Comments

 Which lifecycle facts does your agent watchdog actually observe—and which ones are still implicit upstream?

 [← Back to Blog](/jingxiao-cai-blog/)
