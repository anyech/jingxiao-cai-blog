# Blog topic taxonomy

Every post has exactly one reader-oriented primary `topic`. Detailed `tags` remain many-to-many and should not be used as a substitute for the primary topic.

## Assignment rules

Choose the topic that best answers: “Why would a reader open this post?” Use the first matching rule below when a post spans multiple subjects.

1. `reliability-security` — the main lesson is an incident, authorization boundary, recovery procedure, supply-chain risk, privacy concern, or fail-closed control.
2. `distributed-runtime-systems` — the main lesson is distributed execution, model serving, performance, capacity, memory, or runtime behavior independent of a specific agent product.
3. `developer-workflow-open-source` — the main lesson is PR evidence, review, Git/GitHub workflow, or public open-source collaboration.
4. `openclaw-self-hosting` — the post depends on concrete OpenClaw or self-hosted-agent setup, operation, upgrade, or debugging details.
5. `agent-architecture-operations` — the post presents a reusable agent orchestration, handoff, panel, memory, monitoring, or operational-contract pattern not tied to one product.
6. `personal-automation-tutorials` — the post is primarily a setup guide, migration, personal automation walkthrough, or personal introduction.

## Drift guard

- New posts must use a slug defined in `src/_data/topics.json`.
- Do not add a seventh topic for one or two posts; prefer detailed tags until a stable reader need emerges.
- Review any topic that exceeds half of all posts or any topic with no posts.
- When classification is genuinely ambiguous, record the reusable reader-intent rule here before moving multiple posts.
- `npm run check:metadata` enforces known topics, one topic per post, valid dates, unique slugs, and the broad-topic threshold.
