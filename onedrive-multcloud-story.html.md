# Getting OneDrive Working with Self-Hosted AI Agents: A Survival Story

URL: https://anyech.github.io/jingxiao-cai-blog/onedrive-multcloud-story.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/onedrive-multcloud-story.html.md
Date: 2026-02-18
Tags: cloud, onedrive, multcloud

Summary: How I migrated my cloud storage using MultCloud.

---

← Back to Blog

 
# Getting OneDrive Working with Self-Hosted AI Agents: A Survival Story

 February 18, 2026 | Last updated: February 18, 2026

 Categories: story, onedrive, multcloud, automation, openclaw

 This post was co-created with Clawsistant, my OpenClaw AI agent. Yes, an AI and a human brainstormed this mess together.

 If you read my previous post, you know how to set up Google APIs for your AI agent. What I didn't mention? Getting Google Drive working was the easy part. The real adventure was OneDrive.

 
 TL;DR: Microsoft Graph API for OneDrive is painful. Use MultCloud as a workaround — it handles the OAuth mess so you don't have to. Free tier works for basic use; lifetime deals show up occasionally.
 

 This is the story of how I finally got my AI agent to access files from OneDrive — and why I ended up using a third-party service to make it happen.

 
## The Problem

 I store a lot of important files on OneDrive: tax documents, resumes, work-related PDFs, family photos. My AI agent needed access to these files for tasks like:

 
 
- Finding and summarizing documents
 
- Organizing files
 
- Accessing work materials while working remotely
 

 Simple enough, right? Just set up the OneDrive API like we did with Google. How hard could it be?

 
## The Answer: Very Hard

 
### Attempt 1: Microsoft Graph API

 Microsoft provides the OneDrive API through Microsoft Graph. In theory, it's similar to Google APIs:

 
 
- Create an Azure App registration
 
- Configure OAuth permissions
 
- Get client credentials
 
- Connect to your agent
 

 The reality: Microsoft's developer ecosystem feels like it was designed by a committee that never talked to each other. Here's what went wrong:

 
 
- Consent issues: Even with a personal Microsoft account, the OAuth flow kept failing with cryptic error messages
 
- Permission scopes are confusing: Files.Read, Files.Read.All, Files.ReadWrite — which one do I need?
 
- Token refresh problems: Unlike Google's relatively stable token system, Microsoft's refresh tokens have all sorts of edge cases
 
- No straightforward "service account" option: For personal accounts, you're stuck with delegated permissions, not the application permissions you'd use in an enterprise setup
 

 
 Fun fact: Microsoft charges for some Azure AD features. What started as "free" quickly became "wait, I need to pay for that?"
 

 
### Attempt 2: rclone

 rclone is the gold standard for command-line cloud storage sync. It's free, open-source, and supports OneDrive out of the box.

 The setup involves:

 
 
- Installing rclone
 
- Running rclone config to authorize OneDrive
 
- Using rclone commands to sync/mount folders
 

 The problem: rclone works great for a human typing commands, but integrating it with an AI agent? That's tricky. The agent would need to:

 
 
- Execute shell commands
 
- Handle the OAuth flow interactively
 
- Manage mounted filesystems
 

 It's doable, but it adds complexity. I wanted something cleaner.

 
### Attempt 3: Other Options

 I also looked at:

 
 
- onedrive-docker — Docker containers that sync OneDrive locally. Good, but still requires server resources and maintenance.
 
- ownCloud/Nextcloud — Self-hosted alternatives. Overkill for my use case.
 
- Direct WebDAV — OneDrive doesn't natively support WebDAV anymore.
 

 
## The Solution: MultCloud

 After weeks of frustration, I discovered MultCloud — a service that lets you manage multiple cloud storage providers from one interface.

 Here's why it won:

 
 
- Easy setup: Connect OneDrive and Google Drive (or other clouds) with a few clicks
 
- Built-in sync: Schedule automatic sync between clouds
 
- Agent-friendly: The AI agent talks to Google Drive (which we already set up), and files are automatically synced from OneDrive
 
- Reliable: No more OAuth headaches
 

 
 The workaround: I set up MultCloud to automatically sync specific folders from OneDrive to Google Drive. Now my AI agent accesses everything through Google Drive — the "easy" API we set up in the previous post.
 

 
## How It Works

 
 
- Sign up for MultCloud (free tier available, paid for more features)
 
- Add OneDrive — authorize access to your OneDrive account
 
- Add Google Drive — authorize access
 
- Create a sync job — choose which OneDrive folders to sync to Google Drive
 
- Schedule it — sync hourly, daily, or in real-time
 

 
 Tip: I caught MultCloud on a Valentine's Day lifetime deal — normally it's subscription-based. If you see a deal, grab it!
 

 
## The Trade-offs

 Is MultCloud perfect? No. Here's the reality:

 
 ProsCons

 Simple to set upThird-party dependency

 Works reliablySubscription cost (or one-time deal)

 No OAuth headachesData passes through their servers

 Supports 80+ cloudsFree tier has limits

 

 For me, the trade-off was worth it. My time is valuable, and MultCloud lets me focus on actually using my AI agent rather than debugging OAuth flows.

 
## What I'd Do Differently

 If I were starting fresh today, here's my advice:

 
 
- Start with MultCloud from day one if you need multi-cloud access
 
- Don't waste time on Microsoft Graph unless you have a business need
 
- Use rclone if you want a free, self-hosted solution and don't mind the CLI
 
- Consider the sync approach: One-way sync (OneDrive → Google Drive) is simpler than two-way
 

 
## Lessons Learned

 This whole saga taught me a few things:

 
 
- Not all clouds are equal: Google's developer experience is far ahead of Microsoft's
 
- Workarounds are valid: Sometimes the "elegant" solution isn't worth the headache
 
- AI agents need stable APIs: The less friction in cloud access, the more useful the agent
 
- Third-party services exist for a reason: MultCloud fills a real gap
 

 
## What's Next

 Now that my AI agent has access to both Google Drive and OneDrive (via sync), the automation possibilities have opened up. I can:

 
 
- Search across both clouds
 
- Get file summaries
 
- Automate document organization
 

 Next, I'm working on more advanced automation — maybe automatic file categorization or intelligent document routing. Stay tuned!

 
 
### Related Posts

 
 
- Setting Up Google APIs for Self-Hosted AI Agents — How to set up Google Drive access
 
- Migrating from WordPress to GitHub Pages — This blog's hosting setup
 

 

 
 
### About the Author

 Jingxiao Cai is a Principal Architect specializing in ML infrastructure. PhD in Radar Signal Processing from University of Oklahoma. Previously at Oracle building HeatWave ML infrastructure.

 

 ← Back to Blog
