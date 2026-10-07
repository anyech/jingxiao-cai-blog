---
layout: post.njk
permalink: 'one-client-two-module-copies-runtime-ownership.html'
title: 'One Client, Two Module Copies: Who Owns the State?'
slug: 'one-client-two-module-copies-runtime-ownership'
description: "Two module evaluations can see one in-memory client but separate owner state. A merged OpenClaw change shares that owner within one build; reported regressions are not deployment reliability."
summary: "Two module evaluations can see one in-memory client but separate owner state. A merged OpenClaw change shares that owner within one build; reported regressions are not deployment reliability."
date: '2026-10-07'
updated: ''
topic: 'agent-architecture-operations'
tags: ['openclaw', 'codex', 'typescript', 'reliability', 'agent-ops']
keywords: ['plugin module copies', 'physical client ownership', 'Codex app server', 'runtime state', 'OpenClaw regression tests']
canonical: 'https://anyech.github.io/jingxiao-cai-blog/one-client-two-module-copies-runtime-ownership.html'
inFeed: true
inSitemap: true
feedTitle: 'One Client, Two Module Copies: Who Owns the State?'
feedDescription: "Two module evaluations can see one in-memory client but separate owner state. A merged OpenClaw change shares that owner within one build; reported regressions are not deployment reliability."
feedPubDate: 'Wed, 07 Oct 2026 00:00:00 +0000'
sitemapLastmod: '2026-10-07'
---
<header>
  <a href="/jingxiao-cai-blog/" class="back-link">← Back to Blog</a>
  <h1>One Client, Two Module Copies: Who Owns the State?</h1>
  <div class="meta">
    <strong>October 7, 2026</strong> | By Jingxiao Cai<br>
    <span class="tags">Tags: openclaw, codex, typescript, reliability, agent-ops</span>
  </div>
  <div class="disclaimer">
    This post was co-created with <strong>Clawsistant</strong>, my OpenClaw AI agent.
    It helped separate public source and reported regression evidence from deployment claims.
  </div>
  <div class="warning">
    <strong>Scope:</strong> This note covers merged public PR #160949 and its public implementation and tests. It does not claim that a particular production incident was fixed or that every deployed version has this behavior.
  </div>
</header>

<p><strong>Relationship disclosure:</strong> <code>anyech</code>, this site’s GitHub identity, authored PR #160949 with AI assistance. Reported execution results are contribution-author reports, not an independent rerun. The article analyzes the October 1 merge, not an assertion that today’s release or main branch is unchanged.</p>
<p>Here, a <em>physical client</em> means the same in-memory app-server client instance, not merely two connections to the same server. A <em>module copy</em> is a separate evaluation of the plugin code. Two copies of the same plugin build can receive the same long-lived app-server client. The client is one object, but if each module evaluation keeps its own registry for that object, the runtime state splits: a second copy can add another callback or fail to see ownership recorded by the first. The symptom looks like a protocol problem even though the broken boundary is local state ownership.</p>

<div class="note">
  <strong>Early bounded proof — PR-reported, with pinned assertion source:</strong> after the test loads a second same-build module copy around the same client, the close-handler count remains one; the second copy can see and release the retained owner exactly once. Separate regressions exercise native-child retirement through the original monitor and visibility of the same rate-limit notification snapshot through both copies.
</div>

<h2>The client is shared; the module registries were not</h2>

<p>The affected Codex app-server runtime associates callbacks, retained-thread release tokens, monitor state, and rate-limit observations with a physical client. Module-level maps normally make that association cheap and clear. The trap appears when the same build is evaluated twice: each copy creates a separate map, while both copies are handed the same client.</p>

<p>That gives the system two answers to “what state belongs to this client?” Copy A may own the close handler and retained-thread release function; copy B sees the same transport but not the same bookkeeping. Registering another handler does not repair the missing ownership relationship. Nor does an extra unsubscribe fallback explain which copy is responsible for releasing the original custody.</p>

<h2>Share ownership at the same boundary as the client</h2>

<p>Merged <a href="https://github.com/openclaw/openclaw/pull/160949">OpenClaw PR #160949</a> moves those client-owned registries under the existing build-scoped state owner. Same-build module copies can then consult one runtime record for the physical client. The claim here is the shared owner at that boundary, not an independently established claim about every identity or generation check.</p>

<p>The practical design rule is narrow: state tied to one physical client should have one owner across copies of the same build. That does not mean making every cache global. Keeping unrelated builds isolated is a design requirement, not a cross-build negative-test result established here.</p>

<h2>What the public tests cover</h2>

<p>The public description reports same-build-copy regressions for one close-handler registration, retained-owner visibility and release, original native-child custody retirement, and rate-limit snapshot visibility. The claim is the state/owner boundary those controls describe—not a deployed-system success rate. Three commit-pinned sources are <a href="https://github.com/openclaw/openclaw/blob/7f60f5f7e51dfa5bb72078e9583c19646e934381/extensions/codex/src/app-server/client-runtime.test.ts">client runtime</a>, <a href="https://github.com/openclaw/openclaw/blob/7f60f5f7e51dfa5bb72078e9583c19646e934381/extensions/codex/src/app-server/native-subagent-monitor.close.test.ts">native-child close</a>, and <a href="https://github.com/openclaw/openclaw/blob/7f60f5f7e51dfa5bb72078e9583c19646e934381/extensions/codex/src/app-server/rate-limit-cache.test.ts">rate-limit cache</a>. The complete pinned client-runtime file declares <em>“keeps the exact retained owner when a same-build plugin module copy resumes the client”</em>: after <code>vi.resetModules()</code> and re-import it asserts one close-handler registration, visibility of the retained owner, and exactly-once release. Reading those assertions confirms what the test checks, not that we executed it. No test was rerun for this article.</p>

<p>The PR description reports 119 tests across eight files and two routed projects, plus a paired native-protocol comparison. Those counts and the comparison remain PR-reported results, not an experiment independently executed for this article. Source inspection is not test execution. The merged revision is <a href="https://github.com/openclaw/openclaw/commit/7f60f5f7e51dfa5bb72078e9583c19646e934381">7f60f5f</a>, merged October 1, 2026.</p>

<h2>Keep the claim at the tested boundary</h2>

<p>These artifacts support the same-build module-copy/client ownership path. They are not a full Gateway or Control UI end-to-end reliability estimate, and they do not establish the cause or resolution of any individual production event. A deployment's live behavior still depends on its actual version and runtime; this article makes no claim about a local installation.</p>

<p>The useful takeaway is not “make every registry global.” It is to put shared state at the narrowest owner that actually survives module duplication: the build-scoped runtime for the physical client.</p>

<div class="related-posts">
  <h3>Related Posts</h3>
  <ul>
    <li><a href="/jingxiao-cai-blog/old-owner-agent-cutovers.html">The Old Owner Was Still There: Why Agent Cutovers Need Ownership Proof</a></li>
    <li><a href="/jingxiao-cai-blog/thread-affinity-safety-boundary-agent-ops.html">Thread Affinity Is a Safety Boundary for Agent Work</a></li>
    <li><a href="/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html">Proof Without Touching Production: A Safer PR Boundary for Agents</a></li>
  </ul>
</div>

<div class="author-box">
  <h3>About the Author</h3>
  <p>Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, automation reliability, and the operational boundaries that keep small systems understandable.</p>
  <p style="margin-top: 15px; font-style: italic; color: #555;">One physical client should not acquire a second owner just because its module was evaluated twice.</p>
</div>

<footer>
  <h2>Comments</h2>
  <p>Found this useful? Leave a comment below, or send it to someone debugging state shared across plugin module copies.</p>
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
