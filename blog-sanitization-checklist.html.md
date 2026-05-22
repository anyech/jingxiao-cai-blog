# Blog Post Sanitization Checklist: What to Redact Before Publishing

URL: https://anyech.github.io/jingxiao-cai-blog/blog-sanitization-checklist.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/blog-sanitization-checklist.html.md
Date: 2026-03-03
Tags: writing, security, blogging, opsec, technical-writing

Summary: I created a sanitization checklist after nearly publishing sensitive deployment details. Here&#39;s what to redact, what to keep, and validation scripts for technical bloggers.

---

← Back to Blog
 
# Blog Post Sanitization Checklist: What to Redact Before Publishing

 
 March 3, 2026 | By Jingxiao Cai

 Tags: writing, security, blogging, opsec, technical-writing
 

 
 This post was co-created with Clawsistant, my OpenClaw AI agent. It flagged the operational security leak in the original draft and helped create the sanitization checklist. Because sometimes the best way to learn opsec is to have your AI catch your mistakes before publishing.
 

 

 
 
## The Incident That Started This

 Yesterday, I wrote a blog post called "The Nightly Build" about my autonomous AI agent that runs security audits at 3 AM. Great content, timely topic, aligned with community discussions.

 Then my AI assistant (Clawsistant) flagged something:

 
 "Wait. You're about to publish specific cron job names, channel IDs, and exact deployment counts. This is operational security information."
 

 Ouch.

 I had written things like:

 My `moltbook-lunch-scan` cron job (ID: 89dcec9f-5e45-4ef3-824b-1a4761779e54) 
runs at 12:00 PM PST and sends reports to Telegram channel -1003892593540.
 That's three unique identifiers that could be used to:

 
 
- Identify my specific deployment
 
- Correlate logs or activity patterns
 
- Target attacks against known infrastructure
 

 None of this was malicious. I just didn't think about it. I was focused on writing good technical content, not protecting operational details.

 
## Why This Matters

 Blog posts are permanent and public. Once published:

 
 
- They're indexed by search engines
 
- They're cached by archives (Wayback Machine, etc.)
 
- They can be quoted, shared, and screenshot
 
- You can't fully delete them (even if you remove the post, copies exist)
 

 Unlike GitHub issues (where you can edit comments) or social media (where you can delete posts), blog posts should be treated as immutable.

 So what do you redact?

 
## The Redaction Rules

 
### 🔴 ALWAYS REDACT

 
 
 
 Category
 Examples
 Replacement
 

 
 
 
 Cron Job Names
 moltbook-lunch-scan, healthcheck-nightly-audit
 "daily scan job", "security audit job"
 

 
 Cron Job IDs
 89dcec9f-5e45-4ef3-824b-1a4761779e54
 Remove entirely or "job ID"
 

 
 Channel IDs
 Telegram -1003892593540, Discord guild IDs
 "my Telegram channel", "configured channel"
 

 
 API Keys/Tokens
 moltbook_sk_*, gmail tokens
 "API key", "stored credentials"
 

 
 File Paths with Usernames
 /home/ubuntu/.openclaw/
 ~/.openclaw/ or [workspace]/
 

 
 Exact Deployment Counts
 "7 cron jobs"
 "multiple cron jobs", "several automated jobs"
 

 
 Specific Schedule Times
 "3:00 AM PST" (exact)
 "early morning", "nightly" (keep timezone, generalize time)
 

 
 Infrastructure Details
 VM specs, IP addresses, hostnames
 "cloud VM", "VPS"
 

 
 Personal Schedule Patterns
 "I wake up at 10 AM daily"
 "I review results each morning"
 

 
 Family/Personal Details
 Children's names, specific school info
 Generic: "family", "school updates"
 

 
 Financial Details
 Exact account balances, trade amounts
 Ranges or omit
 

 
 

 
### ✅ SAFE TO KEEP

 
 
 
 Category
 Examples
 Why Safe
 

 
 
 
 Software Versions
 "OpenClaw 2026.2.26"
 Public information
 

 
 OS and Platform
 "Ubuntu 22.04 LTS", "arm64"
 Generic deployment info
 

 
 Error Messages
 "403 insufficient scopes"
 Technical details, no secrets
 

 
 Configuration Structure
 JSON schema, field names
 Not actual values
 

 
 Technical Analysis
 Root cause, troubleshooting steps
 Educational value
 

 
 Your Name/Employer
 "Jingxiao Cai", "Oracle"
 It's your blog—be transparent about authorship
 

 
 Timezones
 "PST/PDT"
 General location info
 

 
 

 
## Before/After Examples

 
 ❌ Before (Unsanitized)
 My `moltbook-lunch-scan` cron job (ID: 89dcec9f-5e45-4ef3-824b-1a4761779e54) 
runs at 12:00 PM PST and sends reports to Telegram channel -1003892593540.
 

 
 ✅ After (Sanitized)
 My daily Moltbook scan job runs at noon PST and sends reports to my Telegram channel.
 

 What changed:

 
 
- ❌ Removed specific job name (moltbook-lunch-scan)
 
- ❌ Removed job ID (UUID)
 
- ❌ Removed exact time (12:00 PM → noon)
 
- ❌ Removed channel ID
 
- ✅ Kept timezone (PST)
 
- ✅ Kept functional description (what it does)
 

 
## Validation: Automated Checks

 Before publishing, I run these grep commands:

 
### 1. Check for UUIDs

 grep -E "[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}" draft.html
 Expected: No results ✅

 
### 2. Check for Telegram Channel IDs

 grep -E "\-100[0-9]+" draft.html
 Expected: No results ✅

 
### 3. Check for Specific Job Names

 grep -E "moltbook-|healthcheck-|morning-" draft.html
 Expected: Only in generic context (e.g., "Moltbook scan" not moltbook-lunch-scan)

 
### 4. Check for Full Paths with Usernames

 grep -E "/home/[a-z]+" draft.html
 Expected: No results ✅ (use ~ instead)

 
### 5. Manual Review

 Read the entire post asking:

 
 "Could someone identify my specific deployment from this?"
 

 Check for combination leaks—multiple harmless details that together identify you.

 
## Blog Posts ≠ GitHub Issues

 I adapted this from my GitHub Issue Sanitization Checklist, but blog posts are different:

 
### More Lenient (It's Your Content)

 
 
- ✅ Use your name (it's your blog)
 
- ✅ Mention your employer (public info)
 
- ✅ Share your architecture patterns
 
- ✅ Link to your GitHub and social profiles
 

 
### But Still Protect

 
 
- ❌ Operational security (cron schedules, job names)
 
- ❌ Access patterns (specific channel IDs, monitored endpoints)
 
- ❌ Family privacy (children's details, school info)
 
- ❌ Financial privacy (exact compensation, account balances)
 

 Key principle: Protect how your deployment works, not who you are.

 
## The Checklist I Use Now

 
 
### Pre-Flight Check (Before Publishing)

 Drafted full post with all technical details

 Applied redaction rules (see tables above)

 Checked for indirect leaks (combination of details)

 Ran automated validation (grep commands)

 Manual review: "Could someone identify my deployment?"

 Saved sanitized version to git repo

 
### After Publishing

 Save post URL to memory

 Document what was redacted

 Note any feedback received

 

 Location: I keep this checklist at memory/categories/blog-sanitization-checklist.md and review it before every post.

 
## Lessons Learned

 
### 1. Operational Security > Anonymity

 The goal isn't to hide who you are—it's to protect how your systems work.

 
 
- ✅ "I run security audits" (general capability)
 
- ❌ "My healthcheck-nightly-audit job runs at exactly 3:00 AM" (specific pattern)
 

 
### 2. Consistency Matters

 Use the same sanitization rules across:

 
 
- Blog posts
 
- GitHub issues
 
- Social media (Moltbook, Twitter, etc.)
 
- Public discussions
 

 Inconsistency creates leaks.

 
### 3. Automate What You Can

 Don't rely on memory. Use grep commands, checklists, and validation scripts. Make it hard to forget.

 
### 4. Think in Combinations

 Individual details might be harmless, but together they can identify you:

 ❌ "Oracle PMTS" + "HeatWave ML" + "Fremont CA" + "36M" = Specific person
✅ "Principal Architect" + "ML Infrastructure" + "Bay Area" = Many people

 
## Why I'm Publishing This

 Because I made this mistake. And if I made it, others will too.

 The AI agent community is growing fast. People are building autonomous systems, running cron jobs, connecting to their personal data. We're sharing our experiences, our architectures, our lessons learned.

 That's great. But let's do it safely.

 Use this checklist. Adapt it. Improve it. But use something.

 
 Your blog is permanent. Your operational security matters. Redact before you publish.

 

 
 
### Related Posts

 
 
- The Nightly Build: How My Agent Runs 3 AM Security Audits While I Sleep
 
- The Supply Chain Attack on AI Agents: What OpenClaw Users Need to Know
 
- VPS OAuth Survival Guide: Google APIs Without a Browser
 

 

 
 
### About the Author

 Jingxiao Cai is a Principal Architect at Oracle, working on MySQL HeatWave ML Infrastructure. PhD in Electrical Engineering (Radar Signal Processing) from University of Oklahoma. He runs his personal AI agent, Clawsistant, on a cloud VM.

 Note: This post was sanitized using the checklist it describes. No deployment-specific identifiers were harmed in the making of this blog post.

 

 
 Found this helpful? Share it with someone else writing about their infrastructure.

 ← Back to Blog
