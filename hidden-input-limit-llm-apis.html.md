# The Hidden Input Limit: When "202K Context" Doesn't Mean 202K

URL: https://anyech.github.io/jingxiao-cai-blog/hidden-input-limit-llm-apis.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/hidden-input-limit-llm-apis.html.md
Date: 2026-02-24
Updated: 2026-03-16
Tags: llm, debugging, bailian, openclaw, claude, pricing

Summary: A debugging story about hidden platform caps, now updated with Anthropic&#39;s March 2026 flat 1M Claude pricing change and why cheaper long context still doesn&#39;t eliminate API-level ceilings.

---

[← Back to Blog](/jingxiao-cai-blog/)


# The Hidden Input Limit: When "202K Context" Doesn't Mean 202K

 February 24, 2026 | By Jingxiao Cai | **Updated March 16, 2026**

 Tags: llm, debugging, bailian, openclaw, claude, pricing


 **📝 Update (March 2026):** Added troubleshooting guidance earlier this month, and now a follow-up on Anthropic's March 14 flat-pricing change for 1M-token Claude requests. The economics got better for some users; the hidden-platform-limit lesson did not disappear.



 This post was co-created with **Clawsistant**, my OpenClaw AI agent.
 It helped turn a frustrating context-window debugging session into a clearer explanation of where provider marketing ends and platform reality begins.


 Last week, my blog scout cron job started crashing with a cryptic error:



```
InternalError.Algo.InvalidParameter: Range of input length should be [1, 73728]
```

 At first, I was confused. I'm using GLM-5 through Alibaba Cloud Bailian, which advertises a **202,752 token context window**. My agent was only loading about 60K tokens of context—well under the limit. What was going on?


## The Investigation

 The blog scout job reads a lot of context:



- 7-14 days of memory files

- Gmail summaries from the morning memo

- ML news and Moltbook trends

- Multiple web searches for blog topics


 All of this adds up. But with a 202K context window, I should have plenty of room, right?


## The Discovery

 After digging through documentation (in Chinese, which added to the challenge), I found the real limits. Alibaba Cloud Bailian imposes a **platform-level input limit** that's separate from the model's native context window:



| Model | Native Context | Bailian Max Input | Gap |
| --- | --- | --- | --- |
| GLM-5 | 202,752 | **73,728** | -64% |
| GLM-4.7 | 169,984 | **73,728** | -57% |
| GLM-4.5 | 131,072 | **98,304** | -25% |

 That's right—**the API only accepts 73K tokens**, even though the model can theoretically handle 202K. This is documented in the [official English docs](https://www.alibabacloud.com/help/en/model-studio/glm) (also available in [Chinese](https://help.aliyun.com/zh/model-studio/glm)), but it's easy to miss if you're skimming.


## Why This Matters

 If you're building AI agents that:



- Read multiple memory or context files

- Fetch web content dynamically

- Accumulate conversation history

- Run complex multi-step reasoning


 ...you might silently exceed the platform limit even though the model *claims* to support a much larger context.

 And the error message doesn't help—it just says "input length should be [1, 73728]" without explaining why.


## The Fix

 Configure your agent framework to respect the **platform limit**, not the model's advertised context window. In OpenClaw, that looks like this:



```
{
  "agents": {
    "defaults": {
      "models": {
        "bailian/glm-5": {
          "contextWindow": 65000
        }
      }
    }
  }
}
```

 Notice I set it to 65K, not 73K. That leaves a buffer for:



- Tool outputs (web fetches, file reads)

- Response generation

- Unexpected context bloat



## Troubleshooting: Step-by-Step Debugging Guide


 **⚠️ Symptoms:** Getting "input length should be [1, XXXXX]" errors even though your context is well under the model's advertised limit.



### Step 1: Check Error Message



```
InternalError.Algo.InvalidParameter: Range of input length should be [1, 73728]
```

 The number at the end (73728) is your **actual platform limit**, not the model's native context.


### Step 2: Verify Model Documentation

 Check both the model's native specs AND the API provider's limits:



```
# Check model's native context
curl -s https://www.alibabacloud.com/help/en/model-studio/glm | grep -i "context"

# Check for platform-specific limits in API docs
curl -s https://www.alibabacloud.com/help/en/model-studio/api-reference | grep -i "input\|limit"
```


### Step 3: Measure Your Actual Input

 Add logging to see what you're actually sending:



```
import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")
tokens = encoder.encode(your_input_text)
print(f"Input tokens: {len(tokens)}")
```


### Step 4: Check Provider Dashboard

 Some providers show input/output stats in their dashboard:



- Bailian Console → Model Studio → Usage Statistics

- Look for "Input Tokens" vs "Context Window"



### Step 5: Apply Conservative Buffer

 Set your configured context window to 80-90% of the platform limit:



```
# Platform limit: 73,728 tokens
# Conservative config: 65,000 tokens (88% of limit)
"bailian/glm-5": {
  "contextWindow": 65000
}
```


 **💡 Pro Tip:** If you're hitting this limit frequently, consider switching to a model with better platform support (Qwen 3.5 Plus has 1M native context with no artificial caps on Bailian).



## Lessons Learned


### 1. Platform ≠ Model

 API providers often impose their own limits. The model might support 202K, but the platform you're accessing it through might only accept 73K.


### 2. Read the Fine Print

 Especially when dealing with translated documentation. The limits were clearly documented—I just didn't look closely enough.


### 3. Defensive Configuration

 Set your context windows conservatively. Better to trigger compaction early than to hit a hard platform limit mid-request.


### 4. Check Compaction Logs

 My logs showed "compaction wait aborted" multiple times—the framework was trying to compact context but timing out before the API call. This was a hint that something was wrong with the context sizing.


## A Wider Pattern

 I suspect this isn't unique to Bailian. Many API providers likely impose platform limits that differ from model capabilities:



- Rate limiting at the platform level

- Input size caps for infrastructure reasons

- Token counting differences (platform vs. model)


 When debugging context issues, check both the model specs *and* the API documentation.


## March 2026 Follow-Up: Anthropic Just Changed the Long-Context Economics

 On March 14, Anthropic updated its pricing docs to say that **Claude Opus 4.6 and Sonnet 4.6 now include the full 1M-token context window at standard pricing**. Anthropic's own example is blunt: *a 900K-token request is billed at the same per-token rate as a 9K-token request.*


 **What changed:** for Claude users on the supported models, chunking purely to dodge a long-context surcharge is much less compelling than it was during the earlier premium-priced long-context phase.


 That does **not** invalidate the main point of this post. My debugging problem here was not "long context is expensive." It was "the platform advertised one number and enforced another." Those are different failure modes:



- **Pricing problem:** the model can accept the prompt, but you pay extra when you cross a threshold

- **Platform-cap problem:** the model may support the prompt in theory, but the API path rejects it before you ever get there


 So yes, Anthropic just made long documents and big codebase passes more attractive on Claude. But the operational lesson still holds across the industry:



- provider docs can lag real behavior

- platform limits can be lower than model-native limits

- "big context" marketing still needs verification in the actual API you use


 If anything, Anthropic's pricing shift makes the contrast sharper. Once one provider removes the long-context premium, the next constraint you notice is often **not price** but **the hidden ceiling in the toolchain around the model**.


## Conclusion

 The "202K context" marketing number doesn't tell the whole story. When using models through intermediary platforms, there's often a hidden input limit that can bite you.


 **Platform limits exist. Check them before you ship.**



 After adjusting my configuration, the blog scout job runs smoothly again. But this was a frustrating few days of debugging that could have been avoided with clearer documentation—or just reading it more carefully in the first place.



### Related Posts



- [OpenClaw 2026.3.12 Regression: When `logs --follow` Breaks But the Gateway Stays Healthy](/jingxiao-cai-blog/openclaw-logs-follow-regression-2026-3-12.html)

- [Troubleshooting AI Agent Skills](/jingxiao-cai-blog/troubleshooting-ai-agent-skills.html)

- [The Supply Chain Attack on AI Agents: What OpenClaw Users Need to Know](/jingxiao-cai-blog/supply-chain-attack-ai-agents.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and spends an unhealthy amount of time turning vague model-platform mismatches into concrete operational lessons. This one started as a simple "why is my prompt failing?" question and ended with a much lower opinion of marketing context numbers.




 [← Back to Blog](/jingxiao-cai-blog/)
