# Why Custom Skills Did Not Load in OpenClaw - A Historical Bug and Follow-Up

URL: https://anyech.github.io/jingxiao-cai-blog/workspace-skills-bug.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/workspace-skills-bug.html.md
Date: 2026-02-23
Updated: 2026-05-08
Tags: openclaw, bugs, ai-agents, customization

Summary: A historical custom-skill loading bug, refreshed with a generated-Markdown regression lesson and a standalone artifact-contract follow-up.

---

← Back to Blog

# Why Custom Skills Did Not Load in OpenClaw - A Historical Bug and Follow-Up

February 23, 2026 | By Jingxiao Cai | Updated May 8, 2026

Tags: openclaw, bugs, ai-agents, customization

May 2026 follow-up: workspace skill discovery is no longer the only interesting part of this story. The newer lesson is that generated artifacts need regression tests too: a nightly generated-memory report failed on a Markdown heading-level jump, and the durable fix was to normalize the emitted artifact shape rather than merely ask the agent to be more careful. May 7 refinement: the useful regression was two-shaped, not one-shaped: inline daily-note blocks and standalone reports need separate heading-depth checks. May 8 closeout: I split the generated-Markdown lesson into a standalone artifact-contract write-up rather than letting it stay buried inside this historical skill-loading post.

 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped debug the original skill-loading failure and later connect that lesson to generated-artifact regression tests.

I've been building my AI assistant setup with OpenClaw, and recently tried to create a custom "blog-publishing" skill to automate my workflow. After spending hours configuring everything, I discovered it simply doesn't work—and it's not just me.

## The Problem

OpenClaw's skill system allows you to extend your agent with custom skills. According to the docs, you can place custom skills in:

 
- ~/.openclaw/workspace/skills/ (highest priority)
 
- ~/.openclaw/skills/ (shared across agents)
 
- Extra directories via skills.load.extraDirs in config

But when I placed my custom skill there and restarted the gateway, it never appeared in the skills list. Only the bundled skills (5 out of 51) loaded.

## It's a Known Bug

After some research, I found GitHub Issue #10386:

 "The agent is unable to discover or register custom skills located in the workspace or defined via extraDirs. While the agent can 'see' the files via directory listing commands in a chat session, the system registry fails to ingest them, only showing the 50 default bundled skills."

This bug affects multiple users running different setups (Docker, bare metal, various Linux distributions). The issue has been open since version 2026.2.3-1, and persists in the latest version (2026.2.22-2 as of this writing).

## Current Workarounds

While waiting for a fix, here's what works:

 
- Manual execution: Keep your skill as documentation and manually follow the steps when needed
 
- Use bundled skills only: Stick to the 5 ready-to-use skills (healthcheck, skill-creator, tmux, video-frames, weather)
 
- Subscribe to the issue: Track #10386 for updates

## Why This Matters

Custom skills are essential for power users who want to:

 
- Automate personal workflows
 
- Create domain-specific knowledge
 
- Build reusable agent behaviors
 
- Share configurations across agents

Without custom skills, OpenClaw becomes much less customizable. I hope this gets fixed soon—it's a critical feature for the platform's extensibility.

## What I Did

Despite the bug, I created my blog-publishing skill anyway:

 
- Documented all steps in SKILL.md
 
- Added the skill to ~/.openclaw/workspace/skills/blog-publishing/
 
- Manually follow the steps when publishing blog posts

It works—you're reading this blog post! But it's not as elegant as it should be.

## May 2026 Follow-Up: Skill Loading Is Only Half the Contract

This post started as a complaint about custom skills not loading. That was a real operator problem at the time, and later OpenClaw releases made workspace skill discovery much less fragile for this setup.

The more durable lesson showed up in a different place: generated Markdown. A nightly generated-memory report produced a heading-level jump that tripped a Markdown structure rule and broke the automation even though the underlying summary content was fine.

The first tempting fix was too simple: make the generator emit one heading depth everywhere. The real fix had to respect two output shapes:

 
- inline blocks embedded inside a daily note need one parent heading depth
 
- standalone reports need a different parent heading depth

That is the same kind of contract thinking custom skills need. A skill is not only a folder that loads. It is also an artifact producer, and the artifacts need tests at the boundary where users actually consume them.

 For generated agent output, test the rendered artifact shape, not just the prompt intent.

The useful regression test was not “did the agent mention the right topic?” It was “does the generated Markdown have a valid heading hierarchy in each supported context?” That is a small distinction, but it is the difference between a pretty summary and a reliable automation surface.

## May 2026 Follow-Up: One Heading Level Was Enough to Break the Nightly Path

The later closeout made the generated-artifact lesson sharper. The bug was small: one generated report jumped heading levels in a way the Markdown checker correctly rejected. The fix was not to make every generated heading globally shallower or deeper. That would only move the bug.

The real contract had two valid shapes:

 
- an inline generated block embedded under a daily note already has a parent heading
 
- a standalone generated report starts from its own document root

Those two surfaces need different heading depths. A useful regression test therefore has to render both surfaces and validate the final artifact, not just inspect the shared prose generator.

 Generated content has to satisfy the consumer's structure, not the generator's internal convenience.

## May 2026 Follow-Up: The Artifact Contract Got Its Own Post

The generated-Markdown regression eventually deserved its own treatment because it is no longer only a skill-system footnote. The deeper lesson is about output contracts: one generated fragment had to be valid both as an inline note block and as a standalone report, so the final validation needed to test both rendered surfaces.

I wrote that version here: One Heading Level Broke the Nightly Build. This original post stays useful as historical context for extension discovery; the new post focuses on generated artifacts as software interfaces.

## Conclusion

If you are reading this as a current OpenClaw operator, treat the original custom-skill loading bug as historical context rather than a fresh diagnosis. The durable takeaway is broader: extension systems need both discovery checks and artifact-contract tests.

If a skill loads but the files it generates are structurally invalid, the extensibility story is still incomplete.

 
### Related Posts

 
 
- One Heading Level Broke the Nightly Build
 
- Modernizing Agent Skills Without Growing a Skill Jungle
 
- Why AI Cron Jobs Need Exact-Exec Drivers
 
- Building Fail-Closed Stage Environments for AI Agents
 

 
### About the Author

 Jingxiao Cai works on AI/ML infrastructure and writes about self-hosted agents, automation, and the small contracts that keep generated tooling reliable.

 ← Back to Blog
