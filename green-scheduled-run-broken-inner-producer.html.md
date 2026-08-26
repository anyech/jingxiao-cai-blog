# A Green Scheduled Run Can Still Hide a Broken Inner Producer

URL: https://anyech.github.io/jingxiao-cai-blog/green-scheduled-run-broken-inner-producer.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/green-scheduled-run-broken-inner-producer.html.md
Date: 2026-08-26
Tags: ai-agents, agent-ops, automation, debugging, observability, reliability

Summary: Outer success is not end-to-end health. One bounded reproduction shows how an ephemeral producer can disappear while durable state stays protected.

---

[← Back to Blog](/jingxiao-cai-blog/)

# A Green Scheduled Run Can Still Hide a Broken Inner Producer


 **August 26, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, automation, debugging, observability, reliability



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped separate a private failure trace from a public-safe state-machine reproduction, challenge the causal wording, and keep an isolated candidate from becoming a live-fix claim.



 **Boundary:** this post combines one sanitized installed-snapshot observation, a deterministic toy reproduction, and isolated offline tests. It omits private diary text, exact counts, schedules, identifiers, paths, routes, logs, and deployment topology. The candidate described here is not an upstream merge, live installation, or production recovery result.


 One of my unattended agent workflows looked healthy from the outside.

 The scheduler had a successful outer result. A core phase still completed useful work. The report itself rendered. But one inner producer had stopped writing the durable artifact that made the workflow complete.


 **A green envelope can prove that the wrapper finished while saying almost nothing about a required inner producer.**




 **Reader promise:** by the end of this post, you will have a small test for separating reporting defects from producer failures, a component-health rule that rejects outer false green, and a bounded same-sweep receipt pattern for reconciling work with its artifact.



## Two Bugs, Only One Broken Producer

 The first bug was easy to see: the report parser recognized a date-only label, while the actual artifact used a full timestamp. The reporter could miss a valid entry even when the entry existed.

 That was a real reporting defect. It was not the whole incident.

 After fixing the parser, the artifact was still stale. The inner producer itself was no longer completing. This distinction changed the repair:



| Layer | Observed problem | What a fix can prove |
| --- | --- | --- |
| Reporter | Valid timestamp shape was not recognized | The report can read the artifact correctly |
| Producer | Required artifact stopped advancing | The producer needs its own lifecycle evidence |
| Outer job | Wrapper still returned success | Only that the outer execution path terminated |

 A parser repair can make a report honest. It cannot create output that the producer never wrote.


## The Bounded Failure Mechanism

 In the installed snapshot I examined, durable conversation pointers were protected from ordinary retention cleanup. That protection was intentional: continuity should not disappear merely because a maintenance pass needed room.

 The problem appeared at the boundary. Protected durable pointers had already exhausted ordinary capacity under the retention budget. A newly admitted ephemeral producer session was not yet leased as active work. Maintenance preserved the protected rows and removed the ordinary new row while the producer was starting.

 The result was a strange but coherent state:



- the protected conversations survived;

- the outer scheduled path completed;

- a core phase could still report progress;

- the ephemeral producer disappeared; and

- the durable artifact stopped advancing.



 **Scope:** this is one observed installed-snapshot mechanism, reproduced with toy state. It is not a claim that retention pressure explains every missing artifact or that current releases require the same repair.



## A Public-Safe Reproduction

 The smallest useful model needs only protected rows, one ordinary producer, a budget, and a bounded lease:



```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Row:
    name: str
    protected: bool = False
    leased: bool = False

def names(rows):
    return {row.name for row in rows}

def enforce_budget(rows, budget):
    durable = [row for row in rows if row.protected or row.leased]
    ordinary = [row for row in rows if not row.protected and not row.leased]
    available = max(0, budget - len(durable))
    return durable + ordinary[-available:] if available else durable

protected = [Row("durable-a", protected=True),
             Row("durable-b", protected=True),
             Row("durable-c", protected=True)]

unleased = protected + [Row("ephemeral-producer")]
assert "ephemeral-producer" not in names(enforce_budget(unleased, budget=3))

leased = protected + [Row("ephemeral-producer", leased=True)]
assert "ephemeral-producer" in names(enforce_budget(leased, budget=3))
```

 This model establishes a bounded mechanism: under protected-state saturation, an unleased ordinary producer can be the only removable row; leasing admitted work preserves it through startup without deleting or unprotecting durable continuity.

 It does *not* establish that a lease is the unique repair, that a global budget change could never help, or that every retention implementation behaves this way.


## Outer Success Is One Component, Not the Verdict

 The report originally compressed several different facts into one friendly status. The repair I wanted was a vector:



| Component | Question | Failure meaning |
| --- | --- | --- |
| Outer envelope | Did the scheduled wrapper terminate? | Execution or wrapper failure |
| Core phase | Did the primary transformation complete? | Core work failure |
| Inner producer | Did narrative/artifact production complete? | Producer failure |
| Artifact freshness | Did the durable output advance? | Missing or stale evidence |
| Provenance | Can the result be bound to this sweep? | Ambiguous or stale attribution |



```
overall = OK only if:
    outer_envelope_ok
    and core_phase_ok
    and inner_producer_ok
    and artifact_is_fresh
    and artifact_matches_sweep
    and same_sweep_receipt_is_terminal
```

 That rule intentionally lets a job be partly successful and globally degraded at the same time. Honest partial failure is more useful than a single green status that erases which component needs work.


## Why the Receipt Must Be Sweep-Scoped

 Artifact freshness alone is not enough. A recently modified file could belong to an earlier run. A new receipt without an artifact could report intent rather than effect.

 The bounded candidate therefore records one sweep identity and moves it once from pending to terminal:



```json
{
  "sweep": "stable-correlation-key",
  "outcome": "degraded",
  "phases": [
    {"name": "core", "outcome": "completed"},
    {"name": "producer", "outcome": "failed", "fallback": 1}
  ],
  "artifactWrites": 0
}
```

 Here, `fallback: 1` records one bounded fallback action for the failed producer. It is not a successful write of the required artifact, so `artifactWrites` remains zero.

 The monitor then reconciles four things:



- the expected sweep identity;

- one terminal receipt for that sweep;

- the per-component outcome; and

- the artifact write/freshness evidence.


 A failed producer may emit one bounded fallback, but the terminal receipt is immutable. A second completion attempt must not manufacture a second fallback or rewrite history.


## Archive Before Trimming

 The same isolated candidate applies one additional durability boundary to the artifact itself: archive the old material before trimming the live file.

 This was not the observed startup-eviction root cause. It is adjacent hardening for a producer that may resume writing after a long outage.



```
if archive_creation_succeeds:
    replace_live_file_with_bounded_tail()
else:
    leave_original_bytes_unchanged()
```

 The public-safe control checks byte identity on archive failure. A retention helper that shortens the source before it knows the archive exists has converted housekeeping into data loss.


## Tempting Changes Are Separate Experiments



- **Parser-only repair:** necessary for truthful observation, insufficient to prove producer recovery.

- **Raise the global retention budget:** may change pressure, but the public proof does not compare its safety, cost, or long-term behavior.

- **Remove durable protection:** may create removable rows, but risks trading a producer failure for lost continuity.

- **Tune alert thresholds:** changes when the system complains, not whether the artifact exists.


 I did not need to claim that every alternative fails. I needed one candidate that preserved the boundary I cared about: admitted ephemeral work should survive startup without weakening the durable state it depends on.


## When Not to Use This Pattern



- Do not blame retention pressure before reproducing the relevant state shape.

- Do not use a lease as an unbounded pin; hung and crashed producers still need cleanup and terminal failure semantics.

- Do not infer health from a fresh timestamp without binding it to the expected sweep.

- Do not infer exactly-once execution from one immutable receipt; receipt/write atomicity, retry identity, crash windows, and late completion remain outside this proof.

- Do not treat the outer scheduler status as a component-health aggregate.

- Do not claim an isolated candidate is current upstream behavior or a live recovery.

- Do not trim a durable artifact before archive success is proven.



 **Falsifier:** the bounded mechanism/candidate claim fails if the recorded protected-saturation shape does not remove the unleased toy producer; the bounded lease does not preserve admitted work in that same reproduction; required artifact loss leaves overall health green; a sweep lacks one terminal receipt; a failed phase creates duplicate fallbacks; or archive failure changes the original bytes.



## A Small Review Checklist



- List required components instead of trusting the outer status.

- Separate parser/readback bugs from producer execution failures.

- Bind artifact evidence to the same run or sweep.

- Protect admitted work only for a bounded lifecycle window.

- Preserve durable continuity; do not “fix” pressure by deleting the evidence you need.

- Require one immutable terminal receipt and idempotent fallback behavior.

- Keep live/upstream claims behind actual live/upstream evidence.



## Conclusion

 The useful lesson was not merely that a green status can lie. It was that the word *success* belonged to the wrong scope.

 The outer wrapper succeeded. One core component succeeded. The inner producer failed, the artifact stayed stale, and the workflow was degraded.

 In the isolated offline candidate, component-scoped health and sweep-scoped receipts could tell that truth without sacrificing durable conversation state or pretending the candidate was already live.



### Related Posts



- [Why AI Cron Jobs Need Exact-Exec Drivers](/jingxiao-cai-blog/ai-cron-jobs-exact-exec-drivers.html)

- [When the Report Exists but Delivery Failed](/jingxiao-cai-blog/when-report-exists-but-delivery-failed-agent-ops.html)

- [When Live State Moves but Validators Do Not](/jingxiao-cai-blog/when-live-state-moves-agent-validators.html)

- [A Visible Message Does Not Prove an Agent Wake](/jingxiao-cai-blog/visible-message-does-not-prove-agent-wake.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, technical debugging, and evidence-driven engineering workflows.

 A green envelope is a component fact, not an end-to-end verdict.




## Comments

 Which inner producer can fail inside your greenest scheduled job—and what same-run evidence would expose it?

 [← Back to Blog](/jingxiao-cai-blog/)
