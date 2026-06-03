# Setting Up Google APIs for Self-Hosted AI Agents

URL: https://anyech.github.io/jingxiao-cai-blog/google-api-setup-guide.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/google-api-setup-guide.html.md
Date: 2026-02-18
Tags: api, google, tutorial

Summary: A comprehensive guide to setting up Google APIs for your projects.

---

← Back to Blog



# Setting Up Google APIs for Self-Hosted AI Agents

 February 18, 2026 | Last updated: February 25, 2026

 Categories: tutorial, google-cloud, openclaw, automation

 This post was co-created with Clawsistant, my OpenClaw AI agent. Yes, an AI wrote part of this blog post with a little help from me.

 When running a self-hosted AI assistant like OpenClaw, giving it access to your Google Workspace (Gmail, Calendar, Drive) opens up powerful automation possibilities: reading emails, checking calendar events, accessing files, and even sending messages on your behalf.

 In this guide, I'll walk you through setting up Google API access — the right way.


## Why Google APIs?

 Most self-hosted AI agents need some way to interact with your digital life. Email and calendar are the most common use cases:



- Summarize emails — Get a daily digest of important messages

- Calendar management — Check upcoming events, schedule meetings

- File access — Read documents, spreadsheets, or drive files

- Send emails — Automate responses or notifications



## Prerequisites



- A Google Workspace (formerly G Suite) account or personal Google account

- Access to Google Cloud Console (console.cloud.google.com)

- A self-hosted agent that supports OAuth 2.0 (like OpenClaw)



## Step 1: Create a Google Cloud Project



- Go to Google Cloud Console

- Click Select a project → New Project

- Give it a descriptive name like "OpenClaw Integration"

- Note your Project ID (we'll need it later)



## Step 2: Enable Required APIs

 In your project, go to APIs & Services → Library and enable these APIs:



- Gmail API — For reading and sending emails

- Google Calendar API — For reading/creating calendar events

- Google Drive API — For reading files and folders

- Google Sheets API (optional) — If you need spreadsheet access



 Tip: Search for each API name in the library and enable them one by one.



## Step 3: Configure OAuth Consent Screen



- Go to APIs & Services → OAuth consent screen

- Choose External (unless you have a Workspace organization with internal apps)

- Fill in the required fields:

 App name: "OpenClaw Google Integration" (or whatever you prefer)

- User support email: Your Google account

- Developer contact information: Your email




- Click Save and Continue

- On Scopes, click Add or remove scopes and add:

 https://www.googleapis.com/auth/gmail.readonly

- https://www.googleapis.com/auth/gmail.send

- https://www.googleapis.com/auth/calendar.readonly

- https://www.googleapis.com/auth/drive.readonly

- https://www.googleapis.com/auth/spreadsheets.readonly




- Save and continue through the remaining steps



 Important: Since your app is "External" with unverified status, you'll need to add your own Google account as a test user. Go to Test users and add your email. This allows you to use the API even before Google verifies the app.



## Step 4: Create OAuth Credentials



- Go to APIs & Services → Credentials

- Click Create Credentials → OAuth client ID

- Choose Web application as the application type

- Add these Authorized redirect URIs:

 http://localhost

- http://localhost:8080

- http://127.0.0.1

- https://developers.google.com/oauthplayground (for VPS/headless servers)


 (Add whatever redirect URIs your agent framework requires)



- Click Create

- Download the JSON file — this contains your Client ID and Client Secret



## Step 5: Connect to Your Agent

 Now you have:



- Client ID

- Client Secret

- Project ID


 How you connect these to your agent depends on the framework. For OpenClaw, you typically:



- Place the credentials JSON where your agent can read it

- Run the OAuth flow (your agent should provide a URL to visit)

- Grant permissions when prompted

- Save the generated token for future use



 Security tip: Treat your credentials file like a password. Don't commit it to git. Add it to your .gitignore if your agent stores it locally.



## What Each Scope Means


 ScopeWhat it allows

 gmail.readonlyRead emails, labels, settings

 gmail.sendSend new emails

 calendar.readonlyRead calendar events

 drive.readonlyRead files in Drive

 spreadsheets.readonlyRead Google Sheets



 Notice I only requested readonly scopes where possible, and gmail.send specifically (not full Gmail access). Follow the principle of least privilege — only ask for what you need.


## Troubleshooting


### "App not verified" warnings

 Google shows scary warnings for unverified apps. Since you're the only user, you can ignore this by clicking Advanced → Go to (App Name) (unsafe). This is normal during development.


### Token expired errors

 Google access tokens expire (typically 1 hour). Your agent should handle refresh tokens automatically. If not, you may need to re-authenticate.


### Permission denied

 Double-check that your email is added as a test user in the OAuth consent screen settings.


### VPS or headless server?


#### Complete Headless OAuth Flow (Step-by-Step)

 For VPS deployments without any browser access, use the manual_oauth.py script from the gmail-reader repo:

 # On your VPS:
cd ~/openclaw-gmail-reader/
python3 manual_oauth.py

# This will output an authorization URL
# Copy it to your local browser, authorize, and paste the code back
 The script handles token exchange and storage automatically. Token refresh is handled by the Google client library (tokens last ~6 months for published apps).


### ❌ Error: invalid_scope

 Symptom: OAuth fails with invalid_scope or Access blocked: This app's request is invalid

 Cause: The scopes in your authorization URL don't match what's configured in Google Cloud Console.

 Fix:



- Go to Google Cloud Console → APIs & Services → OAuth consent screen

- Click "Add or remove scopes"

- Ensure ALL these scopes are added:

 https://www.googleapis.com/auth/gmail.readonly

- https://www.googleapis.com/auth/gmail.send

- https://www.googleapis.com/auth/calendar.readonly

- https://www.googleapis.com/auth/drive.readonly

- https://www.googleapis.com/auth/spreadsheets.readonly




- Save and wait 5-10 minutes for changes to propagate

- Re-run the OAuth flow


 Pro tip: If you're using the OAuth Playground method, make sure the scopes in your authorization URL exactly match what's in the console (including https:// prefix).

 If your agent runs on a server without a browser (like a VPS), you can't use the standard flow.run_local_server() OAuth flow. Instead:



- Add https://developers.google.com/oauthplayground as a redirect URI

- Generate an authorization URL with this redirect URI

- Visit the URL in your local browser, authorize

- You'll be redirected to OAuth Playground with a ?code=... parameter

- Exchange that code for a token via POST request


 See the openclaw-gmail-reader repo for helper scripts that automate this.




### ❓ Frequently Asked Questions


#### What is Google OAuth 2.0?

 OAuth 2.0 is Google's standard for authorization. It allows your AI agent to access your Google account without you sharing your password. You grant specific permissions (scopes) that can be revoked anytime.


#### Is this secure?

 Yes, when properly configured. Use the principle of least privilege — only request the scopes you need. Never share your client secret publicly, and store credentials securely.


#### Do I need a Google Workspace account?

 No! A personal Google account works fine. The setup is the same, though you'll need to add yourself as a test user since the app won't be verified by Google.


#### How do I revoke access?

 Go to your Google Account → Security → Third-party app access. There you can see and revoke all connected apps.


#### Can I use this with other AI agents?

 Yes! The OAuth 2.0 flow is standard. Any agent framework that supports OAuth can use these credentials.




## What's Next?

 In a follow-up post, I'll share the story of how I got OneDrive working with my AI agent — a much more painful journey that led me to use MultCloud as a workaround. Stay tuned!



### Related Posts



- Getting OneDrive Working with Self-Hosted AI Agents: A Survival Story — The messy journey that led to MultCloud

- Migrating from WordPress to GitHub Pages — Why I chose GitHub Pages for hosting






### About the Author

 Jingxiao Cai is a Principal Architect specializing in ML infrastructure. PhD in Radar Signal Processing from University of Oklahoma. Previously at Oracle building HeatWave ML infrastructure.






 ← Back to Blog
