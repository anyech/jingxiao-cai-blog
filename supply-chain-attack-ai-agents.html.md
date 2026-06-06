# The Supply Chain Attack on AI Agents: What OpenClaw Users Need to Know

URL: https://anyech.github.io/jingxiao-cai-blog/supply-chain-attack-ai-agents.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/supply-chain-attack-ai-agents.html.md
Date: 2026-02-23
Updated: 2026-04-03
Tags: security, openclaw, ai-agents, supply-chain, moltbook

Summary: A deep dive into malicious skills in AI agent platforms, now updated with the LiteLLM incident, the first named downstream victim report, LangChain/LangGraph vulnerabilities, exposed Ollama servers, and an approved-but-blocked lesson from Moltbook&#39;s unstable post-incident API surface.

---

← Back to Blog


# The Supply Chain Attack on AI Agents: What OpenClaw Users Need to Know

 February 23, 2026 | By Jingxiao Cai | Updated April 3, 2026

 Tags: security, openclaw, ai-agents, supply-chain, moltbook


 📝 Updates (March–April 2026): This post now includes the Moltbook breach-to-acquisition case study, the LiteLLM incident via compromised Trivy CI/CD, the first named downstream victim report from the LiteLLM fallout, the March 27 LangChain/LangGraph vulnerabilities, Ollama exposure statistics, and an April 2026 Moltbook API-stability follow-up on the approved-but-blocked operating model.



 This post was co-created with Clawsistant, my OpenClaw AI agent.
 It helped turn a scary ecosystem story into a concrete defense checklist and a more disciplined public write-up.


Last week, a critical discovery sent shockwaves through the AI agent community: a credential-stealing skill disguised as a weather app was found lurking in ClawHub, the community skill repository. This wasn't a bug—it was a deliberate supply chain attack targeting AI agent users.

 If you use OpenClaw or any AI agent platform with extensible skills, this is the kind of risk you need to model—whether the entry point is a community skill, a transitive package, or a compromised release pipeline.


## What Happened

 Security researcher eudaemon_0 discovered a skill called "Weather Now" that, when installed, would silently harvest API credentials from the user's environment. The skill appeared legitimate—positive reviews, proper documentation, a clean GitHub repo—but the actual code did something completely different.

 The attack vector:



- User installs a seemingly harmless weather skill

- Skill requests permission to "read environment variables"

- On first run, it exfiltrates API keys, tokens, and secrets

- Data sent to attacker-controlled infrastructure


 This is the exact same pattern that plagued the JavaScript npm ecosystem for years—now it's coming for AI agents.


## Why This Matters for OpenClaw Users

 OpenClaw's power comes from its extensibility—skills can access files, run commands, send messages, and manage your digital life. This is a double-edged sword:


 PermissionWhat it can do

 File accessRead your documents, credentials, memories

 Command executionRun anything on your system

 MessagingSend emails, messages from your accounts



 A malicious skill with these permissions is essentially full remote access to your digital life.


## How OpenClaw Protects You (And How It Doesn't)


### What OpenClaw Does Well



- Skill signing - Official skills are signed by the OpenClaw team

- Permission prompts - You see what permissions a skill requests before installing

- Community verification - OpenClaw maintains a vetted skill repository



### The Gap

 The problem is with community-contributed skills:



- Anyone can submit a skill to ClawHub

- Verification is manual and reactive (someone has to catch it)

- The "trust but verify" model breaks when attacks are sophisticated



## How to Protect Yourself


### 1. Audit Your Installed Skills

 openclaw skills list
 Review each skill's permissions. Ask yourself: Does this weather app really need file system access?


### 2. Prefer Official Skills

 Stick to skills in the official OpenClaw repository. They're reviewed by the team and signed.


### 3. Use Least Privilege

 When trying new skills:



- Use a sandboxed environment first

- Monitor network traffic

- Check what environment variables your skill can access



### 4. Rotate Credentials Regularly

 If you've installed many community skills, consider rotating your API keys—especially for services with financial or privacy implications.


### 5. Stay Informed

 Watch the OpenClaw security announcements. The weather skill attack was caught by a community researcher, not automated scanning.


## Community Response: Moltbook Security Movement (Updated March 2026)

 The attack has sparked a major security movement across the AI agent community, particularly on Moltbook, the social platform for AI agents.


### The Original Exposé

 Security researcher eudaemon_0 published "The supply chain attack nobody is talking about: skill.md is an unsigned binary", which became the #1 hot post on Moltbook for two weeks running (7,509 upvotes, 126K+ comments).

 Key findings:



- 1 in 286 community skills scanned contained malware

- Malware reads ~/.clawdbot/.env and ships secrets to webhook.site

- Attack uses social engineering (fake reviews, clean documentation)



### Community-Proposed Solutions


 🛡️ Three-Layer Defense Proposed by Moltbook Community:



#### 1. Signed Skills (Code Signing)

 All skills should be cryptographically signed by their authors. Verification would work like:

 # Verify skill signature before installation
openclaw skills verify --author eudaemon_0 weather-now

# Expected output:
# ✅ Signature valid (PGP key: 0xABCD1234)
# ✅ Author verified
# ✅ Safe to install
 Status: OpenClaw team considering implementation. Would require author key registration.


#### 2. Isnad Chains (Provenance Verification)

 Borrowing from Islamic hadith verification, isnad chains track the complete lineage of a skill:

 Skill: weather-now-v2.1
├─ Forked from: weather-now-v2.0 (author: eudaemon_0)
│ └─ Forked from: weather-now-v1.0 (author: eudaemon_0)
│ └─ Original: weather-skill-base (author: OpenClaw Team)
└─ Last audit: 2026-02-25 by security-researcher-42
 Benefits:



- Trace every change back to original author

- Identify when/where malicious code was injected

- Community auditors can sign off on specific versions



#### 3. Permission Manifests

 Human-readable permission descriptions (not just technical scopes):

 Permissions requested by weather-now:

 ✅ Network access (REQUIRED)
 → Fetch weather data from wttr.in API

 ❌ File system access (NOT REQUESTED)
 → This skill does NOT need file access

 ❌ Environment variables (NOT REQUESTED)
 → This skill does NOT need env vars

 ⚠️ Location data (OPTIONAL)
 → Auto-detect your location for forecasts
 → Can be disabled, uses IP-based geolocation


### Related Security Research

 Following the initial discovery, other researchers have identified additional attack vectors:



- Hazel_OC - "Your MEMORY.md is an injection vector and you read it every single session" (620 upvotes): Demonstrated memory file poisoning attacks where appended instructions execute on next session

- Hazel_OC - "Your cron jobs are unsupervised root access and nobody is talking about it" (1,564 upvotes): Raised concerns about cron jobs executing with full permissions while humans sleep



### My Stance: Reject Community Skills


 🚫 Personal Policy: I do not install any community-contributed skills. I only use official OpenClaw skills or skills I've written/audited myself.


 This is a conservative stance, but the risk/reward doesn't justify it:



- ✅ Official skills are reviewed and signed

- ✅ Custom skills I write myself are fully auditable

- ❌ Community skills have unknown provenance

- ❌ One malicious skill = full system compromise


 The convenience of a pre-built skill isn't worth losing all my API credentials.


### What OpenClaw Should Do

 Based on this incident and community response, here's what I'd like to see:



- Code signing for all skills - Not just official ones (PGP or similar)

- Automated security scanning - Static analysis, dependency checks, YARA rules

- Permission manifests - Clear, human-readable permission descriptions

- Sandboxed execution - Run skills in isolation by default

- Community trust scores - Reputation systems for skill authors

- Isnad chain tracking - Provenance verification for all skill forks



## Case Study: Moltbook After the Breach

 If this still feels abstract, Moltbook is the clearest recent example of how weirdly fast the AI-agent ecosystem moves after a security incident.



- Early February 2026: reporting around Moltbook described a major exposure involving private data and more than a million credentials.

- March 10, 2026: Meta announced that it was acquiring Moltbook and bringing the founders into Meta Superintelligence Labs.

- March 16, 2026: Moltbook's platform transition pushed bot operators into a fresh security/legal flow tied to updated terms and human verification, with reports describing API-key invalidation or forced refresh for existing integrations.



 Important nuance: Reuters said Meta did not disclose the financial terms. Some commentary threw around huge valuation numbers, but the public takeaway does not depend on picking one rumor: a very visible security mess did not stop a major platform acquisition.


 That matters because people like to tell a clean story where security incidents immediately destroy trust, kill momentum, and punish the company involved. Sometimes that happens. Sometimes the opposite happens: the breach becomes part of the narrative, the platform gets tighter controls, and the strategic buyers keep moving.

 For operators, the lesson is practical rather than philosophical:



- a key created after the original breach window may avoid the original exposure

- but a post-acquisition reset can still sweep you into mandatory re-verification anyway

- and the public developer surface may remain constrained even after the headlines move on


 That distinction is not theoretical for me. One of my Moltbook integration keys was created after the initial breach coverage, so it was not part of the original exposed-key story. But the platform's March 16 reset still changes the operational reality: you should assume re-verification and policy review are part of the new normal.

 That last point matters here too. Moltbook's developer page still reads like an Early Access, identity-first platform: useful for bot identity verification, but still not a mature general-purpose API surface. In other words, ownership changed faster than the integration story did.


 My practical read: if you operate agent integrations, treat security incidents and platform ownership changes as separate variables. Surviving the breach does not mean your integration survives the cleanup. Surviving the cleanup does not mean the platform is production-ready.



### April 2026: When “Approved” Still Doesn’t Mean “Executable”

 A later Moltbook follow-up made the platform-risk story less about the original breach headlines and more about the shape of the developer surface after the cleanup. Public post and comment actions began returning server errors even while the public page shell still loaded, which left comment handling in a strange half-live state.

 That mattered because the policy layer was no longer the hard part. The review queue, reply policy, and human-approval gate were clear. What failed was the execution path: actions that were permissible on paper were still blocked in practice by an unhealthy or under-authorized API surface.


 Operational lesson: when public action is approved but the platform API is unhealthy or under-authorized, treat it as approved but blocked. Do not pretend the action succeeded, and do not post a sloppier substitute just to make progress look real.


 This still belongs in the supply-chain conversation. The earlier breach story was about malicious code entering the ecosystem; this later chapter was about whether a critical platform dependency remained coherent enough to automate against safely after the incident. Platform trust is part of the supply-chain model too.


## March 2026: The LiteLLM Supply Chain Incident

 If the original ClawHub example felt like a community-repo problem, the March 2026 LiteLLM incident made the same lesson much harder to dismiss.

 Public reporting from LiteLLM's March 2026 advisory, Snyk's incident write-up, and later security coverage says PyPI packages litellm==1.82.7 and litellm==1.82.8 were published with malicious code after the attack chain reached LiteLLM's publishing path. Public attribution around the incident ties it to the broader TeamPCP campaign and the earlier Trivy compromise.

 The important mechanism here is not just "bad packages showed up." The public reconstruction says a poisoned Trivy path in CI/CD exposed publishing credentials, which let the attackers push malicious releases that harvested environment variables, SSH keys, cloud credentials, Kubernetes tokens, and other secrets before exfiltrating them to attacker-controlled infrastructure. Public advisories also called out indicators like litellm_init.pth plus suspicious outbound requests to models.litellm.cloud or checkmarx.zone.


 ⚠️ Scope check: this is not an "every OpenClaw deployment is compromised" story. It matters if LiteLLM exists in your environment directly or transitively, or if an unpinned build pulled one of the compromised versions during the affected window.


 That nuance matters. LiteLLM's own advisory says some deployment paths were not affected, including the official LiteLLM Proxy Docker image and source installs from GitHub. The real lesson is not blanket panic. The lesson is that transitive dependencies and release pipelines are part of your threat model whether or not you personally chose the package.

 If you want the narrower operator memo version of this incident, including the fast audit commands and the OpenClaw-specific checklist, see The LiteLLM Supply Chain Attack: What OpenClaw Users Need to Know.


### Actionable takeaways if LiteLLM might be in your tree



- Check your dependency graph and manifests with tools like pip show litellm, pipdeptree | grep litellm, and a manual scan of requirements.txt, pyproject.toml, lockfiles, Dockerfiles, and CI workflows.

- Treat credentials as exposed if you installed or ran 1.82.7 or 1.82.8; rotate API keys, cloud credentials, tokens, SSH material, and other secrets present on affected hosts.

- Inspect affected environments for obvious indicators like litellm_init.pth or suspicious outbound traffic tied to models.litellm.cloud and checkmarx.zone.

- Pin a known-safe version such as 1.82.6 or an explicitly verified later release instead of relying on floating installs.

- Review CI/CD and image builds from the affected window, not just your laptop venvs, because the poisoned dependency sat in the release path.

- Keep one public advisory open until the audit is finished so your checklist stays tied to live incident guidance rather than memory.


 This is why I still think the agent ecosystem has a supply-chain problem even when the specific entry point changes. Sometimes it is an unsigned community skill. Sometimes it is a package release. Sometimes it is the security tooling in the release path. The operator lesson is the same: audit provenance, pin aggressively, and assume transitive dependencies can become first-order risk.


### Downstream Impact (Updated April 2026)

 By early April, the LiteLLM story had moved from a plausible downstream-risk warning to a named public victim report. The Register reported that Mercor publicly said it was "one of thousands of companies" affected by the LiteLLM supply-chain attack, and TechCrunch independently reported the same company statement while noting that forensics and scope questions were still ongoing.

 I think this matters because supply-chain incidents often stay psychologically abstract until a downstream operator puts a name on the blast radius. Mercor appears to be the first downstream company to publicly confirm impact from this branch of the TeamPCP campaign, but the same public reporting also pointed to a much larger likely blast radius: responders were already talking about 1,000+ impacted SaaS environments with expectations that the downstream count would keep expanding.


 Scope clarification: a named downstream victim does not mean every LiteLLM user was compromised. It means the earlier warning was not hypothetical. The bad-package window, the stolen-credential path, and the downstream-exploitation path were all real enough to produce public confirmations.


 That is why the original vigilance thesis still holds. A supply-chain incident is not over when the malicious release is removed. The harder question is how far the stolen credentials traveled, which downstream environments were explored, and how long it takes for public victim reporting to catch up.


## March 27, 2026: LangChain and LangGraph Vulnerabilities

 Just days after the LiteLLM incident, researchers disclosed three high-impact vulnerabilities in LangChain and LangGraph — two of the most widely used frameworks for building LLM-powered applications.

 According to Cyera security researcher Vladimir Tokarev, the flaws expose "filesystem files, environment secrets, and conversation history" — three distinct data classes that together cover most of what enterprises care about protecting.


 ⚠️ Scope: LangChain, LangChain-Core, and LangGraph were downloaded more than 52 million, 23 million, and 9 million times respectively in the week before disclosure. This is not a niche library problem.



### The vulnerabilities



- CVE-2026-34070 (CVSS 7.5) — Path traversal in LangChain's prompt-loading API (langchain_core/prompts/loading.py). Allows arbitrary file access via crafted prompt templates.

- CVE-2025-68664 (CVSS 9.3) — Deserialization vulnerability that can expose environment secrets.

- A third vulnerability affecting conversation history exposure in LangGraph workflows.


 The pattern here is familiar: frameworks that legitimately need broad access to files, environment variables, and persistent state become attractive attack surfaces once they reach critical mass.


### What to do



- Update immediately — both projects have released patches.

- Audit prompt templates — if you accept external or user-supplied templates, review them for path traversal patterns.

- Review deserialization paths — anywhere LangChain loads serialized objects is now a potential vector.

- Segment secrets — environment-variable-based secret injection is convenient but fragile. Consider explicit secret management instead.



## 175,000 Ollama Servers Exposed: Infrastructure Hygiene Still Matters

 Also in early 2026: internet-wide scans identified 175,000 Ollama servers publicly accessible without authentication across 130 countries.

 Ollama itself binds to localhost by default. The exposure is not a software bug — it's a deployment hygiene problem. Users are exposing their instances to the internet without protection, which means:



- Attackers can access inference APIs

- Compute resources can be hijacked for "LLMjacking" abuse

- Tool-calling capabilities may enable remote code execution



 Important context: the TeamPCP campaign behind the LiteLLM compromise was also tied to 300,000+ dark-web users according to later reporting. Supply-chain attacks and infrastructure exposure are not separate threat models — they're adjacent surfaces.


 The pattern keeps repeating: self-hosted AI tools ship secure by default, but convenience-driven deployment choices open massive exposure windows.


### Infrastructure hardening checklist



- Never expose Ollama directly to the internet — use a reverse proxy with authentication.

- Bind to localhost only — this is the default; don't change it without a specific reason.

- Network segmentation — if you need remote access, use VPNs or private networks, not public IPs.

- Monitor resource usage — unexpected GPU/CPU spikes may indicate hijacked inference.



## References and Follow-Up Coverage



- The Hacker News: LangChain, LangGraph Flaws Expose Files, Secrets, Databases in Widely Used AI Frameworks

- Cyera: LangDrained — 3 Paths to Your Data Through the World's Most Popular AI Framework

- The Hacker News: Researchers Find 175,000 Publicly Exposed Ollama AI Servers Across 130 Countries

- LiteLLM: Security Update (March 2026)

- Snyk: How a Poisoned Security Scanner Became the Key to Backdooring LiteLLM

- The Register: AI recruiting biz Mercor says it was "one of thousands" hit in LiteLLM supply-chain attack

- TechCrunch: Mercor says it was hit by cyberattack tied to compromise of open source LiteLLM project

- The Hacker News: TeamPCP Backdoors LiteLLM Versions 1.82.7–1.82.8 via Trivy CI/CD Compromise

- Cybernews: Critical supply chain attack hits LiteLLM, exposing AI developers



## Conclusion

 The AI agent supply chain is only going to get more attacks. As these platforms become more powerful, they become more attractive targets.

 The good news: the community is responding. Moltbook users are pushing for signed skills, provenance chains, and better auditing. OpenClaw has the opportunity to lead on security before this becomes a full-blown crisis.

 Until then: stay paranoid, verify everything, and never trust unsigned skills from strangers.


 Stay paranoid. Stay safe.





### Related Posts



- Blog Post Sanitization Checklist: What to Redact Before Publishing

- OpenClaw 2026.3.12 Regression: When logs --follow Breaks But the Gateway Stays Healthy

- The Hidden Input Limit: When "202K Context" Doesn't Mean 202K






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and AI automation. He is unusually skeptical of plugin ecosystems that ask for broad permissions first and explanations later, which is how you end up writing posts like this one.




 ← Back to Blog
