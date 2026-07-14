# Building a Personal AI Assistant: From Gmail to Morning Memos

URL: https://anyech.github.io/jingxiao-cai-blog/personal-ai-assistant-gmail-morning-memo.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/personal-ai-assistant-gmail-morning-memo.html.md
Date: 2026-02-21
Updated: 2026-03-03
Tags: ai, automation, gmail

Summary: How I built an AI assistant to automate my morning email routine.

---

[← Back to Blog](/jingxiao-cai-blog/)



# Building a Personal AI Assistant: From Gmail to Morning Memos

 Published: February 21, 2026 | Last Updated: March 3, 2026 | By Jingxiao Cai

 *This post was co-created with Clawsistant, my OpenClaw AI agent. Because sometimes the best way to explain your career path is to have an AI help you connect the dots.*


 **📝 Update (March 2026):** Added unified Gmail reader library reference and enhanced Calendar/Drive integration details.



 AI Assistant
 Gmail Automation
 OpenClaw
 Productivity



## Introduction

 What if you woke up every morning to a curated summary of what matters? No more scrolling through 100+ emails. No more missing important calendar events. Just a clean, actionable memo that tells you exactly what you need to know.

 That's what I built: a personal AI assistant running on a small cloud VM that reads my Gmail, monitors my Google Drive, checks my calendar, and delivers a daily morning memo to my phone.

 In this post, I'll walk you through how to build this for yourself using **OpenClaw** — an open-source AI assistant framework — and Google's APIs.


## What is OpenClaw?

 OpenClaw is an open-source AI assistant that runs on your own infrastructure. Unlike cloud-based assistants (ChatGPT, Claude, etc.), OpenClaw runs locally, gives you full control, and integrates with your personal data sources.

 Key features:



- Self-hosted — your data stays with you

- Connects to Gmail, Calendar, Drive, and more

- Scheduled tasks (cron-like) for automation

- Multiple communication channels (Telegram, WhatsApp, etc.)

- Custom skills and plugins



## Architecture Overview

 Here's what the system looks like:



```
┌─────────────────────────────────────────────────────────┐
│                    Your Cloud VM                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   OpenClaw                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ Gmail API   │  │ Drive API   │  │Calendar API │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │         │                │                │           │   │
│  │         └────────────────┼────────────────┘           │   │
│  │                          ▼                            │   │
│  │              ┌─────────────────────┐                  │   │
│  │              │   AI Processing     │                  │   │
│  │              │   (Priority + Summ)│                  │   │
│  │              └─────────────────────┘                  │   │
│  │                          │                            │   │
│  │                          ▼                            │   │
│  │              ┌─────────────────────┐                  │   │
│  │              │  Morning Memo Gen  │                  │   │
│  │              └─────────────────────┘                  │   │
│  └───────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│              ┌─────────────────────┐                       │
│              │  Telegram/WhatsApp │                       │
│              │     Delivery        │                       │
│              └─────────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```


## Prerequisites



- A cloud VM (AWS, GCP, Oracle Cloud, etc.) — I use Oracle Cloud free tier

- A Google account with Gmail

- Basic command line knowledge

- Telegram or WhatsApp for delivery



## Step 1: Set Up Google APIs

 You'll need to create a Google Cloud project and enable the APIs:



- Go to [Google Cloud Console](https://console.cloud.google.com/)

- Create a new project

- Enable these APIs:

 Gmail API

- Google Calendar API

- Google Drive API




- Create OAuth 2.0 credentials:

 Application type: Desktop app

- Download the credentials.json file






 **Note:** For read-only access (which is safer), use the "gmail.readonly" scope. If you want the assistant to also send emails, add "gmail.send".



## Step 2: Install OpenClaw

 Install OpenClaw on your VM:



```
npm install -g openclaw
openclaw init
openclaw start
```


## Step 3: Connect Gmail - Unified Library Approach


 **✅ Recommended:** Use the unified `openclaw-gmail-reader` library instead of custom scripts.


 **GitHub Repository:** [github.com/anyech/openclaw-gmail-reader](https://github.com/anyech/openclaw-gmail-reader)

 This unified library provides:



- **GmailReader class** with `fetch_emails()`, `send_email()`, `categorize_priority()`

- **Calendar integration** via `calendar_events.py`

- **Drive integration** via `drive_indexer.py` (change detection)

- **Headless OAuth** via `manual_oauth.py` (VPS-friendly)

- **Virtual environment** setup with all dependencies



### Quick Start:



```bash
# Clone the unified library
git clone https://github.com/anyech/openclaw-gmail-reader.git
cd openclaw-gmail-reader

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run OAuth setup (headless-friendly)
python3 manual_oauth.py

# Test Gmail fetch
python3 gmail_reader.py --summary
```

 **For detailed OAuth setup on headless servers,** see [VPS OAuth Survival Guide](/jingxiao-cai-blog/vps-oauth-survival-guide.html).


## Step 4: Smart Priority Detection

 Not all emails are equal. I built a priority system:



- **HIGH:** School, medical, insurance, billing, urgent keywords

- **MEDIUM:** Work emails, shipping, appointments

- **LOW:** Promos, newsletters, social


 This transforms 100+ emails into an actionable 5-10 item list.


## Step 5: Schedule the Morning Memo

 Use OpenClaw's cron to run daily:



```
openclaw cron add --schedule "0 18 * * *" --task "morning-memo"
```

 This runs at 10 AM PST (6 PM UTC) every day.


## Step 6: Deliver to Your Phone

 Configure Telegram or WhatsApp delivery in OpenClaw:



```
{
  "channels": {
    "telegram": {
      "enabled": true,
      "chat_id": "YOUR_CHAT_ID"
    }
  }
}
```


## Sample Output

 Here's what the morning memo looks like:



```
📬 Gmail (24h): 45 emails

HIGH PRIORITY:
• School: Parent-Teacher Conference (Mar 5), Newsletter
• Billing: Water utility payment confirmed ($89.50)
• Medical: Appointment reminder - Dr. Smith (Mar 3)

WORK:
• Project deadline: Q1 deliverables (Mar 15)
• Team meeting: Weekly sync (tomorrow 10am)

QUICK ACTIONS:
1. Confirm parent-teacher conference attendance
2. Review Q1 project timeline
```


## API Status Monitoring (Updated March 2026)

 The morning memo now includes real-time API status for all connected services. This helps diagnose issues before they become problems.


### Current Status Display



```
🔌 API Status
├── Gmail: ✅ Working (last check: 6:02 AM PST)
├── Calendar: ✅ Working (5 events today)
├── Drive: ✅ Working (460 files, 2 new since yesterday)
└── MiniMax: ✅ Working (78% quota used - 3,510/4,500 calls)
```


### MiniMax Quota Monitoring


 **📊 Why Monitor MiniMax?** MiniMax is my primary fallback model. If quota runs out, the morning memo falls back to slower models, potentially causing delays.


 **My Setup:**



- **Provider:** MiniMax Direct (separate $20/mo subscription)

- **Quota:** 4,500 model calls per 5-hour window

- **Alerts:** ⚠️ Warning at 80% (>3,600 calls), 🚨 Critical at 95% (>4,275 calls)


 **Automated Cron Monitoring:**



```
# Daily quota check at 9 AM PST
0 17 * * * cd ~/.openclaw && python3 scripts/check_minimax_quota.py
```

 The check script:



- Fetches current quota from MiniMax API

- Logs usage to memory file

- Alerts if approaching limit

- Reports in morning memo for transparency



### Google Drive Live Scan


 **✅ Real-Time Drive Monitoring:** Morning memo queries Google Drive live on each run — no stale cache. Can detect new files within the last 24 hours.


 **Current Capabilities:**



- **File count:** Total files in Drive (currently ~460)

- **New files:** Detected since last scan

- **Change detection:** Monitors specific folders for updates


 **Sample Drive Section:**



```
📁 Google Drive Updates
├── Total files: 460
├── New since yesterday: 2
│   ├── Resume_Draft_2026.pdf (Documents/)
│   └── Project_Notes.docx (Work/)
└── ⚠️ Action needed: Review new resume draft
```


### Troubleshooting: Calendar/Drive 403 Errors


 **⚠️ Common Issue:** Calendar and Drive APIs may return 403 "insufficient scopes" even after re-authorization.


 **Root Cause:** The OAuth refresh token may have all scopes, but `token.json` has stale scope metadata.

 **The Fix (Don't Re-authorize!):**



```bash
# Step 1: Check current token scopes
cat credentials/token.json | python3 -m json.tool | grep scopes

# Step 2: Update token.json with all 5 scopes
python3 -c "
import json
with open('credentials/token.json', 'r') as f:
    t = json.load(f)
t['scopes'] = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]
with open('credentials/token.json', 'w') as f:
    json.dump(t, f, indent=2)
print('✅ Scopes updated')
"
```

 **Key Lesson:** Refresh token retains all scopes permanently; `token.json` scope list can become stale.


## Privacy Considerations


 **Important:** This setup gives an AI assistant access to your emails. Consider:


- Use read-only scopes where possible

- Run on a VM you control (not shared hosting)

- Review what the assistant has access to regularly





## Future Enhancements

 What I'm planning to add:



- **Calendar integration:** Pull today's meetings

- **Drive monitoring:** Alert on new files in specific folders

- **Weather check:** Include weather for commute planning

- **Job board monitoring:** Scrape LinkedIn for relevant roles



## Conclusion

 Building a personal AI assistant is surprisingly straightforward with tools like OpenClaw. The key insight isn't the technology — it's knowing what information matters to you and automating its delivery.

 Start small. Maybe just email summaries first. Then expand to calendar, Drive, and beyond.

 The future of personal productivity isn't a better to-do app. It's having your own AI that knows what matters and tells you.




 [← Back to Blog](/jingxiao-cai-blog/)
