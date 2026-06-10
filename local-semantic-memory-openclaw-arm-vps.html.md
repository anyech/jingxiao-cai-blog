# Local Semantic Memory on a 4-Core ARM VPS: How I Got OpenClaw Memory Search Working Without External APIs

URL: https://anyech.github.io/jingxiao-cai-blog/local-semantic-memory-openclaw-arm-vps.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/local-semantic-memory-openclaw-arm-vps.html.md
Date: 2026-03-19
Updated: 2026-06-10
Tags: openclaw, ai-agents, self-hosted, memory, embeddings, devops

Summary: How I got OpenClaw local memory search working on a small ARM VPS, now with safer rollout, host-pressure caveats, session-list fast paths, and a stricter active-memory promotion gate.

---

← Back to Blog

# Local Semantic Memory on a 4-Core ARM VPS: How I Got OpenClaw Memory Search Working Without External APIs


 March 19, 2026 | By Jingxiao Cai | Updated June 10, 2026

 Tags: openclaw, ai-agents, self-hosted, memory, embeddings, devops



 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped turn a messy debugging session into a cleaner explanation of what actually broke, what actually fixed it, and why a small self-hosted box was not the limiting factor.


 April 8 follow-up: I added a public limitations section covering rebuild-safety limits in the indexing path, the safer shadow-index workaround, more conservative live sync behavior, and the diagnostic split between timeout-style failures and request-path instability.

 April 29 follow-up: I added a source-hygiene section about anti-echo retrieval: generated scout reports can suggest candidates, but direct evidence and fresh operator friction should remain the primary sources.

 May 9 follow-up: I added the active-memory canary trade-off explicitly: a helper that works only under a long budget may be a valuable diagnostic ceiling, but it is not ready for the normal reply path until scope, query shape, or delivery mode makes it feel boring.

 June 7 follow-up: I added a sharper reply-path distinction: fast embeddings and a working search wrapper do not automatically mean the active-memory helper is production-comfortable inside the synchronous response path.

 June 8 follow-up: I added the host-pressure version of the same rule: even when ordinary search looks healthy, a pre-reply memory helper still has to survive the full setup, tool, judgment, and delivery budget under host pressure.

 June 9 follow-up: I tightened the promotion gate again: a helper that works at a long canary budget is operational evidence, not reply-path production readiness, until the whole user-visible path stays boring.

 June 10 follow-up: I added the operational-test version of the same rule: a canary must prove both completion and placement. If it only proves completion, the next step is scope reduction or async delivery, not promotion.





## The Goal

 I wanted semantic memory search in OpenClaw without paying an external embedding provider and without shipping my memory corpus out to somebody else's API.

 The target environment was not glamorous: a 4-core ARM VPS running my personal OpenClaw deployment. In other words, exactly the kind of box where people assume local embeddings are going to be too slow, too fragile, or too annoying to be worth it.

 That assumption turned out to be wrong.


 Result: local semantic memory search came up successfully with node-llama-cpp + embeddinggemma, indexing 239 files into 1,778 chunks with hybrid search active and no external embedding API required.



## Why I Wanted Local Memory in the First Place

 OpenClaw memory search is one of those features that gets much more valuable the moment you have real history:



- durable notes in MEMORY.md

- daily troubleshooting logs

- operational runbooks

- small but important facts that are annoying to rediscover


 Remote embeddings work, but local mode has three obvious advantages:




 Reason
 Why it matters





 Cost
 No per-query or per-reindex embedding bill for your memory corpus



 Privacy
 Your memory notes stay on your own host instead of becoming another API payload



 Independence
 No key management, remote quota surprises, or embedding-provider drift just to search your own notes






## What Failed First

 The first version of this story looked like a disappointing cliché: local memory search seemed flaky, the index did not complete cleanly in the interactive workflow I was using, and it would have been very easy to blame the VPS.

 But that diagnosis would have been lazy.


 The problem was not that ARM was too weak. The problem was that the local runtime was incomplete and the indexing workflow was wrong for the machine.



 The actual root cause was a missing optional dependency in the OpenClaw install:

 node-llama-cpp
 Once that was fixed, the rest of the story changed completely.


## The Useful OpenClaw Details

 The local docs were clear on two points that mattered:



- memory search is configured under agents.defaults.memorySearch, not a top-level memorySearch block

- local mode uses node-llama-cpp and supports a GGUF or hf: model path


 The documented default local embedding model is:

 hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf
 That is a very reasonable fit for this use case: small enough to be practical on a modest VPS, but good enough for personal-assistant memory retrieval.


## The Config Shape That Matters

 This is the important part of the config shape, simplified to the pieces that mattered operationally:

 {
 "agents": {
 "defaults": {
 "memorySearch": {
 "enabled": true,
 "provider": "local",
 "fallback": "none",
 "local": {
 "modelPath": "hf:ggml-org/embeddinggemma-300m-qat-q8_0-GGUF/embeddinggemma-300m-qat-Q8_0.gguf"
 }
 }
 }
 }
}
 I like the explicit fallback: "none" here for one reason: if the point of the exercise is "stay local", silently falling back to a remote embedding provider defeats the whole point.


 Important nuance: the local docs also note that some installs may need native-build approval for node-llama-cpp. In my case the immediate failure was simpler: the dependency was missing, not just unapproved.



## The Operational Fix That Actually Made It Work

 Even after local mode was correctly wired, I hit another trap: trying to do a full index build in a foreground, short-lived interactive flow on a small box is a dumb way to judge whether local semantic memory works.

 Initial indexing is the expensive part. Search after the index is built is the easy part.

 So the fix was operational, not architectural:



- fix the missing local runtime dependency

- use the default embeddinggemma GGUF path

- run the full index as a detached, low-priority background job overnight

- verify status the next session instead of babysitting it in a fragile foreground turn


 That last step mattered more than it sounds. On a small VPS, background indexing is not a workaround for failure. It's just the sane execution model.


## The Verification

 Once the overnight run completed, the status check was exactly what I wanted to see:

 openclaw memory status --agent main --deep --json
 {
 "files": 239,
 "chunks": 1778,
 "embedding_cache": 1761,
 "provider": "local",
 "searchMode": "hybrid",
 "dirty": false
}

 More importantly, semantic search started returning useful results rather than placebo noise.



- career-context queries surfaced the right durable notes

- Moltbook-related searches found the correct incident writeups

- personal-reference lookups returned the expected memory files



 In plain English: this was not just "the index command finished." It was real semantic recall on a self-hosted memory corpus.



## What This Taught Me About Small VPSes

 People often compress two different questions into one:



- Can this machine run local embeddings at all?

- Is foreground full reindexing a pleasant interactive experience on this machine?


 The answer I got was:



- Yes, the machine can run local embeddings just fine for this use case

- No, you should not confuse "overnight background indexing is smarter" with "the machine cannot do it"


 Those are different statements, and too many self-hosting discussions blur them.


## What I’d Recommend to Other OpenClaw Users




 If your goal is…
 Recommendation





 cheapest durable memory search
 Try local first



 best privacy for personal notes
 Prefer local and keep fallback explicit



 fastest large-corpus reindexing with minimal host CPU pressure
 Remote embeddings may still be easier operationally



 testing whether your host is "good enough"
 Do not judge from one foreground timeout






## The Real Pattern

 The interesting lesson here is broader than memory search:


 When self-hosted AI features fail, the first suspect should be wiring and execution model—not automatically the hardware.



 In this case:



- the hardware was adequate

- the local embedding model was adequate

- the broken part was a missing dependency plus an impatient indexing workflow



## One Honest Caveat

 This post is specifically about the local-memory win. Later on I also tested remote embedding providers for different operational reasons. That later work eventually stabilized on a separate memory-only remote lane with text-embedding-3-small after larger or more ambitious candidates kept tripping timeout and indexing-path problems.

 I am deliberately not turning that into the main story here, because it answers a different question. The local result already stood on its own: once the dependency and indexing model were fixed, local semantic memory worked on the small ARM VPS.


 OpenClaw local semantic memory absolutely worked on this 4-core ARM VPS once the dependency and indexing strategy were corrected.



## Retrieval Audit Results (March 2026)

 After the original local-memory win, I wanted one more sanity check: was the system merely indexed, or was it actually retrieving the right things cleanly?

 The useful answer was yes, with two important caveats about noise and memory hygiene.




 Audit question
 What I saw
 Operational lesson





 Did English recall work?
 Yes — targeted queries about memory-search stabilization returned the expected durable daily-note hits.
 Real retrieval quality matters more than a pretty "index complete" message.



 Did Chinese recall work?
 Yes — Chinese queries surfaced Chinese-language content again instead of falling back to generic noise.
 Cross-language recall was viable on the same memory corpus once the indexing path was clean again.



 What reduced noise most?
 Dropping session transcripts and keeping the index focused on durable memory notes made retrieval calmer and more relevant.
 More source material is not automatically better. Curated memory often beats transcript sprawl.



 What content stayed noisy?
 Transactional, Gmail-style, daily operational content is still much noisier than curated notes and troubleshooting writeups.
 If everything becomes memory, nothing feels like memory.



 What improved transferability?
 Clear headings, explicit labels, and disciplined note structure consistently made later recall easier.
 Metadata discipline is a retrieval feature, not just a writing preference.





 The biggest practical lesson is boring and useful: embedding quality is only part of memory quality. Index scope, note structure, and whether you keep high-noise material out of the main retrieval path matter just as much.


## Later Developments: Why the Remote Story Became Its Own Post

 The later remote-memory work taught a different lesson from the original local-memory post. The important instability was not “local bad, remote good.” It was that source scope and indexing-path behavior mattered more than jumping to a bigger model.



- Dropping session transcripts and focusing on durable memory notes made retrieval calmer and more relevant.

- Several larger or more exotic remote candidates looked stronger on paper but were less stable in the real indexing workflow.

- The boring stable remote landing zone ended up being text-embedding-3-small on a memory-only path, not the flashiest model I tried.


 That is why the remote stabilization story belongs in the separate follow-up, Bigger Embeddings ≠ Better Memory, instead of being pasted wholesale into this post. This page is about proving that local semantic memory was viable on a modest self-hosted box. The later page is about what happened when I kept experimenting after that proof.


## April 2026 Follow-Up: Session Transcript Indexing Turned This Into a Blue/Green Rollout Problem

 The next meaningful step after the original local-memory win was not “try another embedding model.” It was add session transcripts without breaking the live lane.

 That sounds like a small follow-up. It was not. The first design correction was easy to miss: session transcript indexing is agent-scoped. A brand-new shadow agent would index its own mostly empty session folder, not the real history from my main agent. That meant the honest experiment kept the same agent identity and changed the config and SQLite target instead.


 The easy comparison trap: comparing memory-only + 4B against memory + sessions + 0.6B looks tidy, but it changes two variables at once — source set and embedding model. That is not an A/B test. It is an accidental mash-up.





 Lane
 Sources
 Embedding model
 Why I kept it





 A
 memory + sessions
 perplexity/pplx-embed-v1-4b
 Isolate the effect of adding session transcripts while holding the stronger known-good model family constant.



 B
 memory + sessions
 perplexity/pplx-embed-v1-0.6b
 Test the cheaper lane on the same corpus instead of hiding a source-set change inside a model swap.





 The trade-off was real. The smaller 0.6b lane was about 7.5× cheaper per embedded token, used 1024-dimensional vectors instead of 2560, and produced a meaningfully denser on-disk index. The bigger 4b lane still looked stronger on several public retrieval benchmarks I checked by low-single-digit absolute margins. That is exactly why I wanted the rollout to separate source-set enablement from model choice instead of hiding both inside one “upgrade”.

 The honest operational pattern turned out to be blue/green, not clever live toggling:



- build shadow configs first

- keep agent-scoped SQLite paths because the session index is agent-scoped too

- validate with real memory status and memory search checks

- patch the live config deliberately

- restart manually on purpose so rollback is obvious if the first live sync goes wrong



 Important scope note: I am not claiming that agent-scoped storage is a universal best practice for every retrieval system. It was the honest fit for this design because the session corpus itself was scoped per agent.


 The rollout target was a smaller session-enabled lane, expressed generically as:

 sources: ["memory", "sessions"]
embedding lane: smaller session-enabled remote path
vector shape: smaller than the previous lane
dbPath: agent-scoped shadow SQLite path

 More importantly, the live checks return real source: "sessions" hits. That is the proof I actually care about. The point was never to win an embedding beauty pageant. The point was to add session recall without lying to myself about what changed.


## April 2026 Follow-Up: A Separate Multimodal Lane Worked Better Than Forcing Everything Through Text Memory

 The cleanest later example came from a photo-clustering problem, not from memory search itself. I wanted semantically similar stills and GIFs grouped together. Hash-only approaches were fine for exact or near-duplicate cleanup, but they were the wrong primary feature space for “these belong together” ordering.

 That turned into a deliberately separate Gemini Embedding 2 pilot instead of another attempt to overload the memory stack:




 Pilot signal
 What I saw
 Why it matters





 Corpus
 96 items total: 72 stills and 24 GIFs
 Large enough to expose whether the workflow was real or just a toy success.



 Embedding lane
 Gemini Embedding 2 returned 3072-dimensional vectors
 The API path worked cleanly for a separate multimodal workflow on the same VPS.



 Top-1 similarity
 min 0.6609, max 0.9947, avg 0.8900
 The neighbors were strong enough to justify moving on from hash-only tuning.



 Sanity check
 Top-1 neighbors stayed same-lane (still→still, GIF→GIF)
 The results passed a basic modality sanity check instead of collapsing into obvious nonsense.





 The operational pattern mattered as much as the numbers. I did not change the live gateway memory configuration. I created a dedicated local virtual environment and called Gemini Embedding 2 directly from small task-specific scripts, while keeping the vectors and review artifacts local.

 python3 -m venv .venv/photo-semantic
source .venv/photo-semantic/bin/activate
python3 task-specific-embedding-probe.py
python3 task-specific-embedding-pilot.py


 Why this matters: the honest architecture is hybrid. Use local embeddinggemma when the problem is text memory on your own notes. Use a separate remote multimodal lane when the problem is image/GIF semantics or another feature space the text-memory lane was never meant to solve.




- Keep local when privacy, cost, and durable text recall are the primary goals.

- Use remote when the input is multimodal or when the feature space itself is different enough that reusing the text-memory lane would be fake simplicity.

- Keep the lanes separate when you want task-specific experimentation without turning a stable memory pipeline into a moving target.


 That distinction matters because the title claim here is still true. Local semantic memory worked on this VPS without external APIs. The later Gemini pilot did not overturn that result. It showed where a separate remote lane was the right tool for a different class of problem.


## Known Limitations: A Stable Live Lane Is Not the Same Thing as a Universally Safe Rebuild Path

 The session-transcript upgrade made the memory lane more useful, but it did not magically make every indexing path safe. The hardest limit I can now state plainly is this: the built-in full indexing path can still fail against a shorter-than-expected embedding timeout ceiling even when the surrounding status surface suggests a much longer configured timeout.

 That distinction matters because two failure families showed up, and they are similar only if you look at them too casually:



- one points to the builtin sync/indexing envelope timing out during embedding work

- the other looks more like request-path or provider instability during the embedding call


 The practical workaround that actually held up was not “just tune the live lane harder.” The reliable recovery path was a shadow indexing workflow: build or rebuild the index in a reduced-pressure lane first, validate that it is queryable, and only then treat it as a promotion candidate instead of assuming the stock live rebuild path is trustworthy under pressure.


 What I would not claim: the current live setup has become calmer, but I would still not describe plain built-in full reindex as a boring solved problem in this environment. The shadow path is still the safety net I trust when a real rebuild matters.


 More conservative live sync behavior is still worth keeping because it makes the system less eager to stampede itself on ordinary session churn.

 Those settings help by reducing how often automatic sync fires. They do not prove that a manual full build is now safe. That is the operational split I wish I had written down earlier:



- reduced sync pressure is a stability helper for normal live use

- shadow indexing is the safer recovery/rebuild plan

- a plain forced rebuild is still where the timeout ceiling can reappear



 Best current reading: the memory stack is stable enough to use, but not yet honest to describe as “full rebuild is solved.” The right mental model is a useful live lane with a separate lower-risk rebuild path, not one magical knob that fixed everything.



## April 2026 Follow-Up: Source Hygiene Is an Anti-Echo Control

 The latest memory-search lesson was not another embedding benchmark. It was source hygiene.

 Any retrieval or scouting system can accidentally start chasing its own echoes. A generated report summarizes yesterday's evidence. The next scan sees that report and treats it as fresh signal. A later summary then cites the summary of the summary. If you are not careful, the system starts amplifying its own prose instead of discovering new reality.




 Source type
 How I treat it now
 Why





 Direct artifact or command result
 Primary evidence.
 It is closest to what actually happened.



 Durable human- or agent-written note
 Useful context, especially when it records outcome and next step.
 It preserves intent, but still needs freshness checks.



 Generated scout or roundup
 Candidate source, not proof of novelty.
 It may already contain prior rankings, bias, or repeated phrasing.



 Older scout report
 Anti-repeat evidence.
 It is good for avoiding duplicates, not for claiming something is newly important.





 That gives me a cleaner rule for local memory and topic scouting:


 Use generated summaries to find candidates. Use direct evidence to decide what is true.



 This also changes how I interpret retrieval quality. A search result is not good just because it is semantically similar. It is good when the source tier matches the decision. For a new blog idea, fresh daily-memory evidence should outrank an older generated scout. For an operational claim, a direct validation artifact should outrank a polished recap.


 Connection to skill governance: the same anti-echo rule applies to agent skills. A skill radar should not create new skills merely because prior skill-radar prose kept mentioning them. See Modernizing Agent Skills Without Growing a Skill Jungle for the catalog-governance version of this lesson.



## May 2026 Follow-Up: Active Memory Canaries Need a Latency Budget

 The next memory lesson was not about whether a helper could finish. It was about whether it could finish inside the reply path without making the whole assistant feel stuck.

 A 60-second active-memory canary found a working setting in the narrow sense: the helper stopped immediately failing under the previous shorter timeout pattern, and early real runs produced non-empty summaries instead of timing out. But the observed pre-reply latency was still roughly 45-53 seconds.




 Question
 Canary answer
 Operational interpretation





 Can the helper complete under a larger budget?
 Yes, in early real runs.
 The failure class changed from immediate timeout to slow success.



 Is that comfortable for the reply path?
 No.
 Forty-plus seconds before a response is a ceiling, not a polished default.



 What should tighten first?
 Helper shape and query scope.
 Reducing work is safer than blindly shrinking the timeout and rediscovering failure.






 “It completes” is not the same as “it belongs on the critical reply path.”



 That is now how I think about active-memory helpers: a successful canary proves a ceiling, not a production tuning. The next step after a slow success is to make the helper smaller, more targeted, or more asynchronous before treating it as part of the normal interaction loop.

 The May 7 refinement is mostly about wording and rollout discipline: a slow successful canary should be recorded as working but not yet user-comfortable. That keeps the team from declaring victory merely because the timeout class disappeared.

 The May 8 closeout made the promotion gate stricter: I would not treat a long canary budget as a normal product budget. Before this belongs in the ordinary reply path, the helper needs a narrower query contract, a smaller source set, or an asynchronous delivery shape that keeps normal replies responsive.

 The May 9 framing is the one I would keep: slow success is a promotion candidate, not a promotion. A useful active-memory canary should answer two questions separately: can the recall path complete at all, and can it complete without becoming the dominant user-visible latency. If the first answer is yes and the second answer is no, the next move is to shrink or relocate the work, not to celebrate the long timeout as a finished setting.




 Canary result
 What it proves
 What it does not prove





 Slow success
 The helper can finish under the larger budget.
 The helper belongs synchronously in every reply path.



 Non-empty summaries
 The recall path can produce useful material.
 The query shape is already minimal enough.



 No immediate timeouts
 The previous budget was too tight for this lane.
 A permanent large timeout is the right product behavior.






## June 2026 Follow-Up: Fast Search Is Not the Whole Reply Path

 The June follow-up made the active-memory lesson more concrete. The raw embedding lane was fast. Short direct embedding probes finished in milliseconds, and ordinary memory-search wrapper calls were in the several-second range rather than the tens-of-seconds range.

 But the active-memory helper still sometimes made the normal reply path feel slow because the expensive part was not only vector search. The embedded helper had to set up, choose a query, call tools, judge relevance, and return a usable memory summary while the host itself was under pressure.




 Layer
 Observed shape
 What it means





 Embedding call
 Millisecond-level in direct probes.
 The embedding endpoint was not the main bottleneck.



 Search wrapper
 Several seconds in ordinary memory-search probes.
 Real cost, but not enough by itself to explain long pre-reply stalls.



 Active-memory helper
 Useful when it completed, but vulnerable to tail latency and host pressure.
 The production question is the whole helper budget, not just embedding speed.





 The practical tuning moved in a conservative direction: keep the feature on, but reduce the worst-case blocking budget and let future evidence decide whether the helper needs narrower scope, asynchronous delivery, or deeper instrumentation.

 The next pressure check made that distinction less theoretical. Ordinary memory-search probes could still look healthy while the full pre-reply helper remained sensitive to host pressure and long-tail orchestration cost. That is the version of the lesson I trust most: do not promote a memory helper because one layer is fast. Promote it only when the whole user-visible path stays boring under host pressure.


 Fast embeddings prove the retrieval substrate can work. They do not prove an embedded pre-reply helper is cheap enough for every turn.



 That is the sharper version of the canary rule: measure the end-to-end user-visible path. If the memory feature is useful but becomes the dominant latency, the fix is not to pretend the embedding benchmark answered the product question.

 The June 9 promotion rule is deliberately stricter: working at a long canary budget is evidence, not readiness. I would only call the helper production-comfortable when normal replies stay responsive with the helper enabled, the query contract is narrow enough to avoid broad archaeology, and the system has a fallback delivery shape when recall is useful but slow.

 The June 10 refinement turns that into a two-part promotion test: completion and placement. Completion asks whether the helper can return useful memory at all. Placement asks whether that work belongs in the synchronous reply path, a narrower pre-reply hook, an async follow-up, or a manual retrieval lane. A canary that answers only the first question is still valuable, but it is not enough to promote the feature into every normal turn.


 Canary rule: if the helper succeeds only by consuming the user-visible latency budget, the feature is not failed, but its placement is wrong. Shrink the query, narrow the trigger, or move the work out of the blocking path.





 Evidence
 Good conclusion
 Bad conclusion





 Long-budget canary completes
 The path can work when given room.
 The normal reply path should always wait for it.



 Recall is useful when returned
 The feature is worth preserving and tuning.
 Every turn deserves a broad memory scan.



 Search substrate is fast
 The bottleneck is likely orchestration, query scope, or host pressure.
 The end-to-end helper is automatically cheap.






## May 2026 Follow-Up: Session Lists Have a Memory-Search Lesson Too

 The session-list latency work looked separate at first, but it rhymed with the memory story. The gateway was doing expensive derived-row work before cheap filters had narrowed the candidate set.

 In a stage-style filtered probe, the fast-path fix collapsed expensive row construction from 381 rows to 2 rows. Transcript-derived fallback time moved from roughly 953 ms to 28 ms, child-relationship resolution from roughly 109 ms to 2 ms, and total filtered-probe wall time from roughly 1.31 seconds to 216 ms.

 The takeaway is the same as the memory-indexing lesson: source scope matters. A tiny query should not behave like a full-corpus operation just because the implementation builds the rich view too early.


 Related write-up: I expanded the control-plane performance side of this into The 10-Second Session List.



## Why I Think This Matters

 A lot of OpenClaw users are exactly in this bucket:



- self-hosted

- cost-sensitive

- privacy-conscious

- running on modest hardware rather than a giant GPU box


 For that audience, local semantic memory is not some philosophical purity test. It's a practical pattern:



- keep memory search on your own host

- accept that first indexing is the heavy step

- run that heavy step in the background

- enjoy cheap, private recall afterward



 Sanitization note: I kept the overall architecture, provider names, model path, and performance/result numbers because those are the useful parts. I intentionally left out deployment-specific IDs, host-specific paths, exact tuning knobs, and any secrets or internal tokens.




### Related Posts



- Modernizing Agent Skills Without Growing a Skill Jungle

- Bigger Embeddings ≠ Better Memory: Why I Chose text-embedding-3-small for OpenClaw Remote Memory

- OpenClaw 2026.3.12 Regression: When logs --follow Breaks But the Gateway Stays Healthy

- Gateway Restart Behavior: What OpenClaw Users Need to Know About Config Changes

- The Hidden Input Limit: When "202K Context" Doesn't Mean 202K






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and spends an unreasonable amount of time turning vague "it should work" self-hosting advice into concrete operational evidence. He likes cheap, boring systems that keep working after the benchmark crowd gets bored and leaves.

 If a feature can run privately on a small box with one careful fix and one good operational decision, that is usually more interesting than a flashy demo on oversized hardware.




 Found this useful? Send it to someone who assumes every memory problem needs another API key.

 ← Back to Blog
