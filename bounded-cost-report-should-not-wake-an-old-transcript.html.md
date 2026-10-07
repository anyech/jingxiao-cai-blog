# A Bounded Cost Report Should Not Wake an Old Transcript

URL: https://anyech.github.io/jingxiao-cai-blog/bounded-cost-report-should-not-wake-an-old-transcript.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/bounded-cost-report-should-not-wake-an-old-transcript.html.md
Date: 2026-10-07
Tags: openclaw, sqlite, usage-cost, reliability, agent-ops

Summary: An old transcript can contain recent usage. OpenClaw’s bounded-cost proposal uses event time and verified archive exclusions; its synthetic proof is not a production-performance claim.

---

[← Back to Blog](/jingxiao-cai-blog/)

# A Bounded Cost Report Should Not Wake an Old Transcript


 **October 7, 2026** | By Jingxiao Cai

 Tags: openclaw, sqlite, usage-cost, reliability, agent-ops



 This post was co-created with **Clawsistant**, my OpenClaw AI agent.
 It helped separate the public synthetic evidence from the broader production claims it does not establish.



 **Scope:** As of the public-source snapshot on October 7, 2026 at 11:07 UTC, PR #157922 was open and unmerged at [1f38be1](https://github.com/openclaw/openclaw/commit/1f38be1ee4c41156c8e3b8c837f69737105f6752). This is a dated analysis of that proposal, not shipped behavior; a later revision may change it.


A recent usage-cost report faces two opposite mistakes when a transcript's session metadata is mistaken for the time of its usage events. It can reopen unrelated old history just to answer a narrow question. Or it can skip an imported transcript whose session row is old even though the transcript contains usage from inside the requested window.

The distinction is the event timestamp. At the pinned public proposal revision of [PR #157922](https://github.com/openclaw/openclaw/pull/157922), bounded cost aggregation selects transcript evidence by usage-event time rather than treating preserved session-mutation time as a proxy. The proposal keeps uncertain event bounds eligible instead of risking an undercount.

**Reported synthetic result:** The public PR body describes a source-only authenticated Gateway end-to-end test against isolated synthetic SQLite cold storage. It reports two bounded current-UTC-day requests, a separate imported archive with in-window usage, and a distinct all-history request.

| Request | Reported total | Old unrolled archive |
| --- | --- | --- |
| Two identical bounded current-day requests | 47 tokens each | Stayed cold; zero hot transcript rows after both requests |
| Imported contribution: old session-row metadata, usage inside the requested window | 17 tokens reported as a contribution to the bounded total, not another total to add to 47 | Recent usage remains eligible despite row age |
| Separate all-history request | 307 tokens | Restored; full-history remains a distinct operation |

The PR says imported current-day usage contributed 17 tokens to the bounded result. It is a contribution within the 47-token total, not an extra total to add to it. The 307-token all-history request is a distinct control. The figures are source-reported, not tests rerun for this article. They describe a synthetic behavior distinction, not a production benchmark.

**Relationship disclosure:** PR #157922 was authored by `anyech`, this site’s GitHub identity, with AI assistance. Reported tests are author evidence, not independent replication.

## A time window needs two edges

A bounded query is an interval, not just an end timestamp. The public PR description explicitly says both start and end are carried through queued refreshes. That is the limited implementation claim made here; no additional coalescing-test result is inferred from this article.

The proposal also limits reuse of a cold-archive exclusion to verified out-of-range evidence and rechecks archive identity. A finite query window is not permission to guess that an unread or uncertain source is irrelevant. Preserve unknown bounds rather than risking an undercount.

The same distinction constrains cleanup: evidence from a bounded inventory cannot establish what a full-history inventory would show. The all-history control remains a different operation.

## Discovery is still a separate question

Event-time selection for a usage-cost calculation does not turn every session-discovery API into an event-time query. The PR keeps the existing session-list discovery cutoffs separate from bounded cost aggregation. A reader should not infer that the change enumerates every historical session by message timestamp.

## What the synthetic proof does—and does not—show

The current public PR body reports a 1/1 source-only Gateway end-to-end case and 104/104 focused infrastructure tests across four files. These are claims in the public PR, not tests I reran. The report also cautions that an immediate 1.4 ms repeated RPC may have used the fresh top-level result cache; that timing alone does not prove a second worker scan.

The fixture demonstrates a bounded behavior distinction using synthetic storage. It is not a production-scale benchmark and does not measure production slow-storage behavior. At the 11:07 UTC source read-back the PR remained open and unmerged at the pinned head. GitHub’s exact-head `openclaw/ci-gate` check and combined status reported success. Individual check-run enumeration was partial, and source inspection is not a local test rerun or a claim of automated-review clearance. It also does not establish the separate behavior of sessions.usage or explain repeated refresh timeouts.

The practical rule is modest: use the event that the report is about, preserve uncertainty rather than guessing an archive is irrelevant, and keep bounded inventory separate from full-history cleanup. The current proposal has a concrete test for that boundary; its production impact remains unmeasured.


### Related Posts



- [The 10-Second Session List: Why Prefiltering Before Row Build Matters in Agent Gateways](/jingxiao-cai-blog/10-second-session-list-prefilter-row-build-agent-gateway.html)

- [The Snapshot Moved. The SQLite Integrity Scan Did Not.](/jingxiao-cai-blog/sqlite-snapshot-cache-not-integrity-scan.html)

- [A Cold-Start Canary Is Not a Serving SLA](/jingxiao-cai-blog/cold-start-canary-not-serving-sla.html)

- [Proof Without Touching Production: A Safer PR Boundary for Agents](/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html)



### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, automation reliability, and the operational boundaries that keep small systems understandable.

 A bounded report should follow the event it counts—not the age of the row that stores it.


## Comments

 Found this useful? Leave a comment below, or send it to someone debugging a bounded usage report over archived history.

 [← Back to Blog](/jingxiao-cai-blog/)
