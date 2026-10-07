---
layout: post.njk
permalink: 'bounded-cost-report-should-not-wake-an-old-transcript.html'
title: 'A Bounded Cost Report Should Not Wake an Old Transcript'
slug: 'bounded-cost-report-should-not-wake-an-old-transcript'
description: "An old transcript can contain recent usage. OpenClaw’s bounded-cost proposal uses event time and verified archive exclusions; its synthetic proof is not a production-performance claim."
summary: "An old transcript can contain recent usage. OpenClaw’s bounded-cost proposal uses event time and verified archive exclusions; its synthetic proof is not a production-performance claim."
date: '2026-10-07'
updated: ''
topic: 'agent-architecture-operations'
tags: ['openclaw', 'sqlite', 'usage-cost', 'reliability', 'agent-ops']
keywords: ['OpenClaw usage cost', 'SQLite cold transcripts', 'event-time selection', 'bounded refresh', 'archived session usage']
canonical: 'https://anyech.github.io/jingxiao-cai-blog/bounded-cost-report-should-not-wake-an-old-transcript.html'
inFeed: true
inSitemap: true
feedTitle: 'A Bounded Cost Report Should Not Wake an Old Transcript'
feedDescription: "An old transcript can contain recent usage. OpenClaw’s bounded-cost proposal uses event time and verified archive exclusions; its synthetic proof is not a production-performance claim."
feedPubDate: 'Wed, 07 Oct 2026 00:00:00 +0000'
sitemapLastmod: '2026-10-07'
---
<header>
  <a href="/jingxiao-cai-blog/" class="back-link">← Back to Blog</a>
  <h1>A Bounded Cost Report Should Not Wake an Old Transcript</h1>
  <div class="meta">
    <strong>October 7, 2026</strong> | By Jingxiao Cai<br>
    <span class="tags">Tags: openclaw, sqlite, usage-cost, reliability, agent-ops</span>
  </div>
  <div class="disclaimer">
    This post was co-created with <strong>Clawsistant</strong>, my OpenClaw AI agent.
    It helped separate the public synthetic evidence from the broader production claims it does not establish.
  </div>
  <div class="warning">
    <strong>Scope:</strong> As of the public-source snapshot on October 7, 2026 at 11:07 UTC, PR #157922 was open and unmerged at <a href="https://github.com/openclaw/openclaw/commit/1f38be1ee4c41156c8e3b8c837f69737105f6752">1f38be1</a>. This is a dated analysis of that proposal, not shipped behavior; a later revision may change it.
  </div>
</header>

<p>A recent usage-cost report faces two opposite mistakes when a transcript's session metadata is mistaken for the time of its usage events. It can reopen unrelated old history just to answer a narrow question. Or it can skip an imported transcript whose session row is old even though the transcript contains usage from inside the requested window.</p>

<p>The distinction is the event timestamp. At the pinned public proposal revision of <a href="https://github.com/openclaw/openclaw/pull/157922">PR #157922</a>, bounded cost aggregation selects transcript evidence by usage-event time rather than treating preserved session-mutation time as a proxy. The proposal keeps uncertain event bounds eligible instead of risking an undercount.</p>

<p><strong>Reported synthetic result:</strong> The public PR body describes a source-only authenticated Gateway end-to-end test against isolated synthetic SQLite cold storage. It reports two bounded current-UTC-day requests, a separate imported archive with in-window usage, and a distinct all-history request.</p>
<table>
  <thead><tr><th>Request</th><th>Reported total</th><th>Old unrolled archive</th></tr></thead>
  <tbody>
    <tr><td>Two identical bounded current-day requests</td><td>47 tokens each</td><td>Stayed cold; zero hot transcript rows after both requests</td></tr>
    <tr><td>Imported contribution: old session-row metadata, usage inside the requested window</td><td>17 tokens reported as a contribution to the bounded total, not another total to add to 47</td><td>Recent usage remains eligible despite row age</td></tr>
    <tr><td>Separate all-history request</td><td>307 tokens</td><td>Restored; full-history remains a distinct operation</td></tr>
  </tbody>
</table>
<p>The PR says imported current-day usage contributed 17 tokens to the bounded result. It is a contribution within the 47-token total, not an extra total to add to it. The 307-token all-history request is a distinct control. The figures are source-reported, not tests rerun for this article. They describe a synthetic behavior distinction, not a production benchmark.</p>

<p><strong>Relationship disclosure:</strong> PR #157922 was authored by <code>anyech</code>, this site’s GitHub identity, with AI assistance. Reported tests are author evidence, not independent replication.</p>
<h2>A time window needs two edges</h2>

<p>A bounded query is an interval, not just an end timestamp. The public PR description explicitly says both start and end are carried through queued refreshes. That is the limited implementation claim made here; no additional coalescing-test result is inferred from this article.</p>

<p>The proposal also limits reuse of a cold-archive exclusion to verified out-of-range evidence and rechecks archive identity. A finite query window is not permission to guess that an unread or uncertain source is irrelevant. Preserve unknown bounds rather than risking an undercount.</p>
<p>The same distinction constrains cleanup: evidence from a bounded inventory cannot establish what a full-history inventory would show. The all-history control remains a different operation.</p>

<h2>Discovery is still a separate question</h2>

<p>Event-time selection for a usage-cost calculation does not turn every session-discovery API into an event-time query. The PR keeps the existing session-list discovery cutoffs separate from bounded cost aggregation. A reader should not infer that the change enumerates every historical session by message timestamp.</p>

<h2>What the synthetic proof does—and does not—show</h2>

<p>The current public PR body reports a 1/1 source-only Gateway end-to-end case and 104/104 focused infrastructure tests across four files. These are claims in the public PR, not tests I reran. The report also cautions that an immediate 1.4 ms repeated RPC may have used the fresh top-level result cache; that timing alone does not prove a second worker scan.</p>

<p>The fixture demonstrates a bounded behavior distinction using synthetic storage. It is not a production-scale benchmark and does not measure production slow-storage behavior. At the 11:07 UTC source read-back the PR remained open and unmerged at the pinned head. GitHub’s exact-head <code>openclaw/ci-gate</code> check and combined status reported success. Individual check-run enumeration was partial, and source inspection is not a local test rerun or a claim of automated-review clearance. It also does not establish the separate behavior of sessions.usage or explain repeated refresh timeouts.</p>

<p>The practical rule is modest: use the event that the report is about, preserve uncertainty rather than guessing an archive is irrelevant, and keep bounded inventory separate from full-history cleanup. The current proposal has a concrete test for that boundary; its production impact remains unmeasured.</p>

<div class="related-posts">
  <h3>Related Posts</h3>
  <ul>
    <li><a href="/jingxiao-cai-blog/10-second-session-list-prefilter-row-build-agent-gateway.html">The 10-Second Session List: Why Prefiltering Before Row Build Matters in Agent Gateways</a></li>
    <li><a href="/jingxiao-cai-blog/sqlite-snapshot-cache-not-integrity-scan.html">The Snapshot Moved. The SQLite Integrity Scan Did Not.</a></li>
    <li><a href="/jingxiao-cai-blog/cold-start-canary-not-serving-sla.html">A Cold-Start Canary Is Not a Serving SLA</a></li>
    <li><a href="/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html">Proof Without Touching Production: A Safer PR Boundary for Agents</a></li>
  </ul>
</div>

<div class="author-box">
  <h3>About the Author</h3>
  <p>Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, automation reliability, and the operational boundaries that keep small systems understandable.</p>
  <p style="margin-top: 15px; font-style: italic; color: #555;">A bounded report should follow the event it counts—not the age of the row that stores it.</p>
</div>

<footer>
  <h2>Comments</h2>
  <p>Found this useful? Leave a comment below, or send it to someone debugging a bounded usage report over archived history.</p>
  <p style="margin-top: 15px;"><a href="/jingxiao-cai-blog/" class="back-link">← Back to Blog</a></p>
</footer>
<div class="utterances-wrapper" data-pagefind-ignore>
  <script src="https://utteranc.es/client.js"
      repo="anyech/jingxiao-cai-blog"
      issue-term="pathname"
      theme="github-light"
      crossorigin="anonymous"
      async></script>
</div>
