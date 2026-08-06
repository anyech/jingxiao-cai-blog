# When Reasoning Eats the Answer: Debugging Empty LLM Completions

URL: https://anyech.github.io/jingxiao-cai-blog/when-reasoning-eats-the-answer-empty-llm-completions.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/when-reasoning-eats-the-answer-empty-llm-completions.html.md
Date: 2026-08-06
Tags: llm-debugging, ai-agents, token-budgets, reasoning-models, reliability, self-hosted-ai

Summary: Empty final content with finish_reason=length can be consistent with reasoning exhausting a shared completion budget. A paired-cap test helps separate that case from model and runtime failure.

---

[← Back to Blog](/jingxiao-cai-blog/)

# When Reasoning Eats the Answer: Debugging Empty LLM Completions


 **August 6, 2026** | By Jingxiao Cai

 Tags: llm-debugging, ai-agents, token-budgets, reasoning-models, reliability, self-hosted-ai



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped turn a private debugging trace into a public paired-budget experiment while removing model names, routes, paths, credentials, deployment values, and live configuration details.



 **Short version:** an empty final answer does not always mean the model failed. In runtimes where reasoning and final output share a completion budget, generation can end with `finish_reason=length` before final content begins.




 On runtimes with a shared completion budget, reasoning can leave too little headroom for the final answer.


 The request returned successfully. The model server was reachable. The proxy was reachable. The response even reported reasoning activity.

 The final answer was empty.

 That symptom invites an early diagnosis of broken model weights, a bad serving runtime, a proxy that dropped content, or a request option that disabled the answer. In the case I investigated, a shared-budget explanation fit the controlled evidence better: generation reached a reasoning phase, hit a length limit, and produced final content only in the higher-cap run.


 **An empty answer can be a length-terminated response, not an empty computation.**




 **Reader promise:** by the end of this post, you will have a small diagnostic ladder for distinguishing completion-budget exhaustion from model, proxy, streaming, timeout, and parsing failures.



## The Response Has More Than One Surface

 A reasoning-capable model can expose at least three useful signals:



- **reasoning activity** — evidence that generation progressed inside a reasoning phase;

- **final content** — the answer intended for the user; and

- **termination state** — why generation stopped.


 If the first is non-empty, the second is empty, and the third is `length`, the model did not simply return nothing. Generation reached a reasoning phase and then hit a length boundary before a final answer appeared. A paired test is still needed to identify which effective budget caused that boundary.



| Observed signal | What it supports | What it does not prove |
| --- | --- | --- |
| Reasoning present | Generation reached and progressed through a reasoning phase. | That a usable final answer will fit inside the remaining budget. |
| Final content empty | The caller received no user-facing answer. | That model inference never happened. |
| `finish_reason=length` | The configured completion limit stopped generation. | Whether the limit was consumed by reasoning, final content, or both. |
| `finish_reason=stop` | The model reached a stop condition. | That every adapter preserved or displayed the returned content correctly. |


## The Smallest Useful Experiment: Change One Budget

 The strongest evidence came from a paired run. I preserved the prompt and request shape, then changed only the completion cap.



| Run | Completion cap | Reasoning observed | Final content | Finish reason |
| --- | --- | --- | --- | --- |
| A | 64 tokens | Present | Empty | `length` |
| B | 256 tokens | Present | Expected answer | `stop` |

 A separate, longer workload produced an illustrative observation at a different scale: an approximately four-thousand-token completion cap ended with reasoning activity and no final content, while an approximately twenty-five-thousand-token control reached a non-empty answer and a normal stop. These rounded values describe one controlled workload, not a portable threshold or reproducibility promise.

 The small-cap pair was a single controlled observation, and its response telemetry did not provide stable reasoning-token accounting. It is therefore strong evidence consistent with completion-budget exhaustion in the tested runtime, not proof that reasoning consumed a precisely measured number of tokens or that every empty completion has the same cause. Some stacks also scale reasoning effort with the advertised cap, so a larger cap is a diagnostic probe rather than a linear headroom guarantee.


 **Diagnostic unit:** same prompt, same path, one changed completion cap, different termination state, and a non-empty answer only in the higher-cap run.



## Isolate the Model Path From the Integration Path

 A paired cap is stronger when basic health is established on both sides of the integration boundary.

 In this case, simple prompts returned non-empty answers through both the direct model server and the proxy route. That made several broad explanations less likely:



- the model artifact was loadable;

- the server could produce final content;

- the proxy could preserve final content for a simple request; and

- the basic authentication and routing path worked.


 The failure remained prompt-sensitive and cap-sensitive. That is very different from a dead server or a proxy that always strips the answer.



```
simple prompt, direct path  -> content + stop
simple prompt, proxy path   -> content + stop
complex prompt, low cap     -> reasoning + empty content + length
same prompt, higher cap     -> reasoning + content + stop
```

 This four-row matrix is small enough to run during triage and strong enough to prevent a restart-first debugging ritual. The simple-prompt rows establish basic path health; for a full path comparison, run the reproducing prompt through both direct and proxy routes at the same cap.


## Request Flags May Not Override the Chat Template

 One tempting workaround is to disable reasoning for the request. That only works if the serving stack and chat template honor the control.

 The model in this experiment entered a reasoning block because the template started every assistant turn there. Request-level controls intended to reduce or disable reasoning did not change that template behavior.

 The general lesson is not that reasoning controls never work. It is that a caller flag is not proof of effective behavior. Verify the rendered template or the observed response. If the template owns the transition into reasoning, a request option may be advisory, unsupported, or ignored.


## Completion, Context, and Timeout Are Different Budgets

 Raising the completion cap can expose a second failure mode: the request now has enough tokens to finish, but not enough wall-clock time.



| Budget | Failure signature | Diagnostic question |
| --- | --- | --- |
| Completion/output tokens | `finish_reason=length`, often with partial reasoning or content. | Did the cap exceed observed reasoning plus answer demand? |
| Request timeout | The caller or proxy terminates before a model stop is returned. | Is the outer timeout larger than representative long-completion latency? |
| Context window | Input and requested completion cannot fit together. | Does prompt length plus completion allowance remain within the model context? |

 Do not solve all three with one giant number. Measure them separately: the completion/output cap limits generated work, the context window limits prompt plus generation, and the wall-clock timeout limits elapsed time. Some runtimes expose a separate reasoning budget, while others combine or rename these controls. Verify the effective semantics before changing a value. A higher-cap falsification test needs headroom for observed reasoning activity and the expected answer while the combined request still fits inside the context window and the resource envelope you are willing to support.


## A Diagnostic Ladder That Avoids Guessing



- **Preserve the full response envelope.** Record final-content length, reasoning presence or aggregate usage, termination state, and elapsed time. Keep metrics, not raw reasoning text.

- **Classify the termination.** `length`, `stop`, timeout, safety refusal, tool call, and transport error are different failures.

- **Run a paired-cap test.** Keep the prompt and path fixed; increase only the completion allowance.

- **Compare direct and proxy paths.** Use a simple prompt first, then the reproducing prompt.

- **Compare streaming with non-streaming.** Inspect raw chunks and the aggregated response so a stream assembler cannot turn returned content into an empty string.

- **Check the parser and field mapping.** Verify that the client or proxy did not drop populated content, reasoning, tool-call, structured-output, or safety fields.

- **Inspect effective template behavior.** Do not assume a reasoning-control flag changed the assistant preamble.

- **Check timeout separately.** A token-budget fix can make the request longer than an inherited proxy or client timeout.

- **Run one semantic canary.** Success means a non-empty final answer with the expected meaning, not merely an HTTP success code.



## When This Diagnosis Does Not Apply

 Budget exhaustion is a strong candidate only when the evidence fits. Look elsewhere when:



- the response ends with `stop` but final content disappears after stream aggregation;

- the model returns a tool call or structured object that the client mistakes for empty text;

- a safety or policy field explains the missing content;

- the direct path succeeds but the proxy consistently drops the final-content field;

- the request times out before the model returns a termination state; or

- the same prompt remains empty after the cap comfortably exceeds observed reasoning use.


 That last condition is the falsification test. If a completion cap with reasonable headroom does not change the termination or produce final content, budget exhaustion no longer explains enough. This test is diagnostic, not a general remedy for empty responses.


## Fix the Proven Seam, Then Prove Meaning

 Once the paired experiment produces evidence consistent with budget exhaustion, the candidate mitigation should remain narrow:



- raise the completion cap for the affected route, not every model;

- align the route timeout with measured long-completion latency, not a global guess;

- keep the total request inside the context and resource envelope;

- run the original semantic prompt through the real integration path; and

- roll back if the response is still empty, times out, or violates the intended serving boundary.


 Do not copy hidden reasoning into final content as a workaround. That leaks internal reasoning, changes the response contract, and still does not prove that the model produced a proper answer.


 **Boundary:** the experiment above diagnoses a failure mechanism. It does not claim that any particular live configuration change has been activated, proven safe, or promoted to a default route.



## Conclusion

 “Empty response” is a symptom, not a root cause.

 Reasoning-capable models make that distinction more important because the visible answer and the hidden work can compete for the same completion budget. Preserve the termination state. Compare caps with one variable changed. Check direct and proxy paths. Treat timeout as a separate budget. Then prove the final answer semantically through the real path.


 **Before blaming the model, ask where the tokens went.**





### Related Posts



- [When a Coding-Agent Route Drifts](/jingxiao-cai-blog/coding-agent-route-drift-without-premature-fixes.html)

- [A Local LLM Router Is Not a Panel Lane Yet](/jingxiao-cai-blog/local-llm-router-not-panel-lane-yet.html)

- [A Cold-Start Canary Is Not a Serving SLA](/jingxiao-cai-blog/cold-start-canary-not-serving-sla.html)

- [A Default Is Not Caller Intent](/jingxiao-cai-blog/default-is-not-caller-intent-agent-setting-provenance.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, technical debugging, and evidence-driven engineering workflows.

 The answer can be empty even when the model did a great deal of work.





### Feedback

 Which response fields have been most useful in your LLM debugging? Open an issue in the [blog repository](https://github.com/anyech/jingxiao-cai-blog) or leave a comment below.



 Published on August 6, 2026 • Part of my ongoing AI-agent operations and reliability series

 [← Back to Blog](/jingxiao-cai-blog/)
