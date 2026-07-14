# VPS OAuth Survival Guide: Google APIs Without a Browser

URL: https://anyech.github.io/jingxiao-cai-blog/vps-oauth-survival-guide.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/vps-oauth-survival-guide.html.md
Date: 2026-02-25
Updated: 2026-04-29
Tags: tutorial, oauth, vps, devops, automation, google-cloud

Summary: Complete tutorial on OAuth 2.0 for headless servers, now with a fail-closed readiness gate that links OAuth-backed automation checks to the broader agent-launch gate pattern.

---

[← Back to Blog](/jingxiao-cai-blog/)

# VPS OAuth Survival Guide: Google APIs Without a Browser


 **February 25, 2026** | By Jingxiao Cai | **Updated April 29, 2026**

 Tags: tutorial, oauth, vps, devops, automation, google-cloud



 This post was co-created with Clawsistant, my OpenClaw AI agent. After spending 6 hours fighting OAuth on my VPS, I figured the least the AI could do was help me write about it.



 **📝 Update (April 2026):** Added a fail-closed readiness-gate pattern so OAuth-backed automation stops before side effects when credentials, scopes, or cheap API probes are not healthy. April 29 follow-up: linked that OAuth-specific gate to the broader agent-launch gate pattern.






## The Problem: OAuth on a Headless Server

 You've set up your Google Cloud project, enabled the APIs, and created OAuth credentials. But now you're stuck:



```
Error: Unable to open browser automatically. Please visit this URL manually:
https://accounts.google.com/o/oauth2/auth?client_id=...
```

 Your AI agent runs on a VPS (Virtual Private Server) without a browser. The standard OAuth 2.0 flow requires clicking through Google's consent screen in a browser—but there's no browser on your server.

 **This is the headless OAuth problem.** And it's surprisingly common.

 In this guide, I'll show you:



- ✅ **The OAuth Playground workaround** (works today, no waiting)

- ✅ **Two Python scripts** to automate the flow (ready to use)

- ✅ **Token lifecycle management** (detect expiring tokens, auto-refresh)

- ✅ **Security best practices** (where to store credentials, rotation strategies)

- ✅ **Fail-closed readiness gates** (credential/scopes/API checks before automation or agent tool launches run)

- ✅ **Troubleshooting flowchart** (for when things go wrong)

- ✅ **NEW: Calendar/Drive 403 troubleshooting** (token.json scope staleness fix)



## Why Standard OAuth Fails on VPS

 The typical OAuth 2.0 flow for installed applications looks like this:



```
1. App generates authorization URL
2. App opens browser to that URL
3. User clicks "Allow" on Google's consent screen
4. Google redirects to localhost with authorization code
5. App exchanges code for access token
```

 **Step 2 is the problem.** On a headless VPS, there's no browser to open. The `run_local_server()` function from Google's OAuth library fails immediately.

 You might think: "Can't I just SSH with X11 forwarding and run a browser?" Technically yes, but:



- ❌ Requires X11 setup (complex, security concerns)

- ❌ Slow and laggy over SSH

- ❌ Doesn't work for automated deployments

- ❌ Breaks the "infrastructure as code" philosophy



## Solution Overview: The OAuth Playground Workaround

 Google provides an official tool called the **OAuth 2.0 Playground** that can act as a redirect target for headless servers. Here's how it works:



```
1. Generate auth URL with OAuth Playground as redirect URI
2. Copy URL from VPS terminal to your LOCAL browser
3. Click "Allow" on Google's consent screen (on your laptop)
4. Google redirects to OAuth Playground with authorization code
5. Copy the code from OAuth Playground back to VPS
6. Exchange code for token via Python script
```

 **No browser needed on the VPS.** All browser interaction happens on your local machine.


 **Prerequisites:** Before you start, make sure you have:


- ✅ Google Cloud project with APIs enabled (Gmail, Calendar, Drive, etc.)

- ✅ OAuth 2.0 Client ID (Web application type)

- ✅ OAuth Playground added as an authorized redirect URI

- ✅ Python 3.8+ installed on your VPS

- ✅ SSH access to your VPS (for copying URLs/codes)


 If you haven't completed the Google Cloud setup, see [Google API Setup Guide](/jingxiao-cai-blog/google-api-setup-guide.html) first.




## Step 1: Add OAuth Playground as Redirect URI

 Go to your Google Cloud Console:



- Navigate to **APIs & Services → Credentials**

- Click on your OAuth 2.0 Client ID

- Under **Authorized redirect URIs**, add:


```
https://developers.google.com/oauthplayground
```



- Click **Save**


 **Important:** This is the official Google OAuth Playground URL. Do NOT use any other redirect URI for this workflow.


 **📸 Screenshot: Google Cloud Console - OAuth Credentials**

 *Shows "Authorized redirect URIs" section with https://developers.google.com/oauthplayground added*

 (Screenshot to be added: OAuth-credentials-redirect-uri.png)



## Step 2: Install Python Dependencies



```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Google Auth libraries + requests (for token exchange)
pip install google-auth google-auth-oauthlib google-auth-httplib2 requests

# Freeze dependencies (for reproducibility)
pip freeze > requirements.txt
```


 **📦 Complete Scripts Available on GitHub**

 Instead of copying code from this page, clone the complete repository with both scripts, README, and requirements.txt:

 [github.com/anyech/openclaw-gmail-reader/oauth](https://github.com/anyech/openclaw-gmail-reader/tree/main/oauth)



## Step 3: Create the OAuth URL Generator Script

 The full script is available on [GitHub](https://github.com/anyech/openclaw-gmail-reader/tree/main/oauth). Here are the key parts:



```
# Key parameters for headless OAuth
params = {
    'client_id': client_id,
    'redirect_uri': 'https://developers.google.com/oauthplayground',
    'response_type': 'code',
    'access_type': 'offline',  # critical: get refresh token
    'prompt': 'consent',  # critical: always get refresh token
    'scope': ' '.join(SCOPES),
}

# Generate URL
base_url = 'https://accounts.google.com/o/oauth2/auth'
auth_url = f"{base_url}?{urlencode(params)}"
```

 **Full script:** [generate_oauth_url.py](https://github.com/anyech/openclaw-gmail-reader/blob/main/oauth/generate_oauth_url.py) on GitHub


## Step 4: Create the Code Exchange Script

 The full script is available on [GitHub](https://github.com/anyech/openclaw-gmail-reader/tree/main/oauth). Here are the key parts:



```
# Token exchange endpoint
token_uri = 'https://oauth2.googleapis.com/token'

# Prepare request
data = {
    'code': auth_code,
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': REDIRECT_URI,
    'grant_type': 'authorization_code',
}

# Make POST request
response = requests.post(token_uri, data=data)
response.raise_for_status()

token_data = response.json()

# Add metadata and save with secure permissions
token_data['expiry'] = datetime.utcnow().timestamp() + token_data.get('expires_in', 3600)
os.chmod(filename, 0o600)  # Owner read/write only
```

 **Full script:** [exchange_code.py](https://github.com/anyech/openclaw-gmail-reader/blob/main/oauth/exchange_code.py) on GitHub


 **💡 Pro Tip:** Clone the entire repository to get both scripts, README with full instructions, and requirements.txt:

 `git clone https://github.com/anyech/openclaw-gmail-reader.git`



## Step 5: Run the OAuth Flow

 Now let's put it all together. If you cloned the repository:


### 5.1 Generate Authorization URL



```bash
cd openclaw-gmail-reader/oauth
source venv/bin/activate
python3 generate_oauth_url.py
```


### 5.2 Authorize in Your Local Browser



- **Copy the URL** from the VPS terminal

- **Paste into your local browser** (Chrome, Firefox, Safari on your laptop)

- **Click "Allow"** on Google's consent screen

- **You'll be redirected** to OAuth Playground



 **📸 Screenshot: Google Consent Screen**

 *Shows the Google OAuth consent screen with scopes listed and "Allow" button*

 (Screenshot to be added: google-consent-screen.png)



### 5.3 Copy Authorization Code

 On the OAuth Playground page, you'll see:



```
Authorization code: 4/0AY0e-g7ZxKqL9vN8mP3rT6sU2wV5xY8zA1bC4dE7fG
```

 **Copy this code** (the long string after `code=`).


 **📸 Screenshot: OAuth Playground - Authorization Code**

 *Shows OAuth Playground page with authorization code displayed in "Step 2" section*

 (Screenshot to be added: oauth-playground-code.png)



### 5.4 Exchange Code for Tokens



```bash
python3 exchange_code.py 4/0AY0e-g7ZxKqL9vN8mP3rT6sU2wV5xY8zA1bC4dE7fG
```


 **✅ Success!** Your `token.json` file is now ready to use with your AI agent or any Google API application.



## Security Best Practices


### 1. Where to Store Credentials



| File | Contains | Permissions | Location |
| --- | --- | --- | --- |
| `client_secrets.json` | Client ID + Secret | 600 (owner rw) | `/etc/myapp/` or `~/.config/myapp/` |
| `token.json` | Access + Refresh tokens | 600 (owner rw) | Same as above |
| `.env` | API keys, paths | 600 (owner rw) | App root directory |


 **Never:**


- ❌ Commit to git (add to `.gitignore`)

- ❌ Store in world-readable directories

- ❌ Log token values (redact in logs)





## 2026 Update: Add a Fail-Closed OAuth Readiness Gate

 The headless OAuth flow gets you credentials. It does not, by itself, prove that every automated job should run.

 A later automation lesson made this stricter for me: if an AI-agent cron job depends on OAuth-backed APIs, the job should perform a cheap readiness gate before it starts doing useful work or sending reports. If the gate fails, the job should stop with a clear credential/scope/readiness error instead of drifting into partial output.


 **Fail-closed rule:** missing credentials, stale scopes, refresh failure, or a failed cheap API probe should block the automation before side effects. Do not let a downstream report pretend the integration is merely empty.


 The gate I now prefer checks:



- **Credential file exists** and has restrictive permissions

- **Refresh works** before the main script starts

- **Expected scopes are present** in the loaded token metadata

- **One cheap API probe succeeds** for each required integration family

- **Failure exits nonzero** with a layer-specific message such as credential missing, scope mismatch, refresh failure, or API probe failure




```python
def oauth_readiness_gate(creds, required_scopes, probes):
    if not creds:
        raise SystemExit("oauth readiness failed: credentials missing")
    if not required_scopes.issubset(set(creds.scopes or [])):
        raise SystemExit("oauth readiness failed: scope mismatch")
    if creds.expired and creds.refresh_token:
        creds.refresh(request)
    for name, probe in probes.items():
        if not probe(creds):
            raise SystemExit(f"oauth readiness failed: {name} probe")
```

 This is the same reliability shape as my [exact-exec cron driver](/jingxiao-cai-blog/ai-cron-jobs-exact-exec-drivers.html) rule: make the deterministic preconditions explicit before asking an agent wrapper to summarize or deliver anything.

 The same gate also applies one layer above OAuth itself. In [Fail-Closing Agent Launches](/jingxiao-cai-blog/fail-closing-agent-launches-auth-readiness-gates.html), I describe the broader pattern: prove auth intent, isolate unrelated ambient credentials, run cheap route-readiness probes, and block before starting the tool adapter if the launch contract is not healthy.


## Troubleshooting


 **Note:** If the flowchart below doesn't render well, view the [source on GitHub](https://github.com/anyech/jingxiao-cai-blog/blob/main/vps-oauth-survival-guide.md).




```
OAuth Flow Fails
    │
    ├─▶ "client_secrets.json not found"
    │   └─▶ Download from Google Cloud Console
    │       (APIs & Services → Credentials → Download)
    │
    ├─▶ "redirect_uri_mismatch"
    │   └─▶ Add https://developers.google.com/oauthplayground
    │       to Authorized redirect URIs in Google Cloud Console
    │
    ├─▶ "Authorization code expired"
    │   └─▶ Codes valid for 10 minutes
    │       Generate new URL and re-authorize
    │
    ├─▶ "Code already used"
    │   └─▶ Authorization codes are single-use
    │       Generate new URL and re-authorize
    │
    ├─▶ "App not verified" warning
    │   └─▶ Click Advanced → Go to (unsafe)
    │       This is normal for personal projects
    │
    └─▶ "Token expired"
        └─▶ Access tokens expire in 1 hour (normal)
            Use refresh token to get new access token
            If refresh token expired (6 months), re-authorize
```


## Troubleshooting: Calendar/Drive 403 Errors (Updated March 2026)


 **⚠️ Critical Issue Discovered:** Calendar and Drive APIs returning 403 "insufficient scopes" even after re-authorization. **Don't re-authorize immediately!**



### Symptoms

 Your morning memo or API scripts show:



```
📅 CALENDAR
⚠️ Auth Error (403) - Calendar API has insufficient authentication scopes

📁 GOOGLE DRIVE
⚠️ Auth Error (403) - Drive API has insufficient authentication scopes
```


### Root Cause: token.json Scope Staleness

 **The OAuth refresh token may have all scopes, but `token.json` has stale scope metadata.**

 When you re-authorize Google OAuth:



- ✅ Refresh token is updated with **all requested scopes**

- ❌ `token.json` file may **not be properly saved/updated** after refresh

- ❌ Python Google library reads **stale scope list** from `token.json`

- ❌ API calls fail with 403 "insufficient scopes" even though refresh token is valid



### The Fix (Without Re-authorizing!)


#### Step 1: Check Current Token Scopes



```bash
cat ~/.openclaw/workspace/gmail-reader/credentials/token.json | \
  python3 -m json.tool | grep -A 10 "scopes"
```


#### Step 2: Test APIs with Explicit Scopes



```bash
cd ~/.openclaw/workspace/gmail-reader
source venv/bin/activate

# Test Calendar (explicitly requests calendar.readonly scope)
python3 calendar_events.py

# Test Drive
python3 drive_indexer.py
```

 If these work, the **refresh token has the scopes** — just need to update `token.json`.


#### Step 3: Update token.json Scopes Manually



```bash
cd ~/.openclaw/workspace/gmail-reader
source venv/bin/activate
python3 << 'PYEOF'
from google.oauth2.credentials import Credentials
import json

# Load current token
with open('credentials/token.json', 'r') as f:
    token_data = json.load(f)

print("Current scopes:", token_data.get('scopes'))

# Update with all 5 scopes
new_scopes = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

token_data['scopes'] = new_scopes

with open('credentials/token.json', 'w') as f:
    json.dump(token_data, f, indent=2)

print("✅ Updated scopes:", token_data.get('scopes'))
PYEOF
```


#### Step 4: Verify Fix



```bash
python3 -c "
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('credentials/token.json')
print('Token scopes:', creds.scopes)

# Test Calendar
cal = build('calendar', 'v3', credentials=creds)
events = cal.events().list(calendarId='primary', maxResults=1).execute()
print('Calendar API: ✅ Working')

# Test Drive
drive = build('drive', 'v3', credentials=creds)
files = drive.files().list(pageSize=1).execute()
print('Drive API: ✅ Working')
"
```


 **✅ Key Lesson:** The refresh token is the source of truth, not token.json! Refresh token retains all scopes permanently; `token.json` scope list can become stale.



### Prevention

 After any OAuth re-authorization, always:



- Verify `token.json` was saved correctly

- Check scopes match what was requested

- Test Calendar/Drive APIs immediately




### Related Posts



- [Google API Setup Guide](/jingxiao-cai-blog/google-api-setup-guide.html)

- [Fail-Closing Agent Launches: Why Auth and Readiness Gates Should Block Before Tooling Starts](/jingxiao-cai-blog/fail-closing-agent-launches-auth-readiness-gates.html)

- [Why AI Cron Jobs Need Exact-Exec Drivers Instead of Freeform Agent Prompts](/jingxiao-cai-blog/ai-cron-jobs-exact-exec-drivers.html)

- [Building a Personal AI Assistant with Gmail](/jingxiao-cai-blog/personal-ai-assistant-gmail-morning-memo.html)






### About the Author

 Jingxiao Cai is a Principal Member of Technical Staff with a background in distributed ML runtime systems. PhD in Radar Signal Processing from University of Oklahoma. Previously worked on backend/runtime systems for production ML workloads.

 Note: This guide was born from pain. After spending 6 hours fighting OAuth on my VPS, I created these scripts so you don't have to. May your tokens never expire unexpectedly.




 Updated April 29, 2026 • Found this helpful? Share it with someone else fighting headless OAuth.

 [← Back to Blog](/jingxiao-cai-blog/)
