# Bound Before You Serialize: When a Correct Child Result Becomes No Result

URL: https://anyech.github.io/jingxiao-cai-blog/bound-before-serialize-oversized-child-result.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/bound-before-serialize-oversized-child-result.html.md
Date: 2026-08-27
Tags: ai-agents, agent-ops, memory-search, ipc, debugging, reliability

Summary: A correct child-process result can disappear if it exceeds the transport before the parent applies its semantic cap. Bound it before serialization.

---

[← Back to Blog](/jingxiao-cai-blog/)

# Bound Before You Serialize: When a Correct Child Result Becomes No Result


 **August 27, 2026** | By Jingxiao Cai

 Tags: ai-agents, agent-ops, memory-search, ipc, debugging, reliability



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped separate one public payload-boundary proof from a much broader merged change, check nearby article ownership, and keep the conclusion narrower than the pull request.



 **Boundary:** this post analyzes one public, merged OpenClaw regression and its landed source. It does not claim that every child-process failure is a payload problem, that character limits are byte limits, or that this narrow proof establishes every lifecycle and platform claim in the larger pull request.


 The child process computed the right answer. The parent still received no usable result.

 That sounds contradictory until the protocol boundary enters the picture. A serialized child response containing a valid vector-search row exceeded the bounded stdout protocol. The parent already knew how to truncate snippets—but only *after* it received the response. The transport rejected the response first.


 **A downstream size limit cannot protect a result that never crosses the transport.**




 **Reader promise:** by the end of this post, you will have a small ordering test for bounded child protocols, a two-cap design that preserves useful results without trusting the child, and a regression pattern that catches valid oversized rows rather than only malformed output.



## The Result Was Correct Until It Became Bytes

 The affected path isolated synchronous vector work in a child process so native database calls could not monopolize the parent event loop. The child returned structured rows over a bounded JSON stdout protocol.

 The semantic contract already said that each returned text snippet should be capped. But the cap lived on the parent side:



```
child computes a valid hit with full text
child serializes a response containing the full row
bounded stdout rejects the oversized serialized response
parent never receives a row to truncate
correct recall becomes unavailable
```

 Nothing was wrong with the vector match. The failure was an ordering bug between the semantic result bound and the transport bound.



| Boundary | Question | Why it matters |
| --- | --- | --- |
| Query semantics | Was the correct row selected? | A valid hit should not be relabeled as missing. |
| Result semantics | How much text may one row expose? | The producer needs the same bounded snippet contract as the consumer. |
| Transport | How many bytes may cross stdout? | The independent hard cap contains bugs and adversarial output. |
| Parent validation | Is the received envelope still well formed? | Producer-side bounding must not turn into trust. |


## Move the Semantic Bound Upstream

 The repair carried the requested snippet limit into the child request, validated it at the query boundary, and truncated every validated row before serialization:



```
parent sends a validated snippet limit
child executes the same vector query
child validates each returned row
child truncates text without splitting a UTF-16 surrogate pair
for this one-row regression, bounded JSON crosses stdout
parent validates the envelope and receives the correct hit
```

 The important change was not “add truncation.” Truncation already existed. The change was **place the semantic bound before the first hard transport boundary that depends on it**.

 The landed implementation keeps the transport cap too. That gives the protocol two different protections:



- **Semantic producer cap:** shapes valid results to the consumer contract before serialization.

- **Independent transport cap:** rejects oversized serialized responses caused by buggy, adversarial, or aggregate growth. Parent-side envelope and schema validation separately reject malformed responses.


 Those caps are not duplicates. One preserves expected results; the other contains unexpected behavior.


## The Regression Needed a Valid Oversized Row

 A malformed-output fixture can prove that the protocol fails closed. It cannot prove that valid recall survives the size boundary.

 The useful public regression created a real file-backed SQLite/sqlite-vec database, inserted a valid text row larger than the child stdout limit, and executed the child-process KNN path. The text deliberately placed an emoji at the truncation edge:



```
stored text = 63 single-code-unit ASCII characters + one emoji + a 3 MiB tail
requested snippet limit = 64 UTF-16 code units

expected hit id = the oversized row
expected text = the first 63 ASCII characters
expected serialized response = below the 2 MiB child stdout limit
```

 The emoji is not decoration. In JavaScript, each preceding ASCII character uses one UTF-16 code unit and the emoji uses two, so `63 + 2 = 65` cannot fit wholly under a 64-code-unit limit. A naive slice can leave half a surrogate; the UTF-16-safe helper drops that dangling half and returns the first 63 ASCII characters. This is an implementation-level code-unit bound, not a UTF-8-byte, Unicode-code-point, grapheme-cluster, or display-width guarantee.


 **Public proof:** the merged [OpenClaw pull request](https://github.com/openclaw/openclaw/pull/128078) and its [file-backed oversized-row regression](https://github.com/openclaw/openclaw/blob/8a0cf730530a1cbc20dda8970051fae12c53c39a/extensions/memory-core/src/memory/manager-search-knn-subprocess.test.ts#L258-L285) are inspectable. The [landed query body](https://github.com/openclaw/openclaw/blob/8a0cf730530a1cbc20dda8970051fae12c53c39a/extensions/memory-core/src/memory/manager-search-knn.ts#L95-L145) shows request validation and UTF-16-safe producer-side truncation.



## Four Controls Make the Claim Useful



| Control | What it distinguishes |
| --- | --- |
| Valid oversized database row | Real result loss from malformed-child rejection |
| Producer-side snippet request | Pre-serialization shaping from post-receipt cleanup |
| Surrogate-pair boundary | Valid text truncation from arbitrary code-unit slicing |
| Independent stdout rejection | Expected bounded rows from unexpected protocol output |

 Without the first control, the test can pass while every large valid hit still disappears. Without the last, a trusted-looking semantic cap can weaken the protocol's defense in depth.


## Character Limits Are Not Byte Limits

 This repair preserves one result contract; it does not solve every payload-budget problem.

 Here the semantic cap applies to each row's text field, while the transport cap applies to the complete serialized response. UTF-16 code-unit counts and UTF-8 byte counts can diverge. Multiple individually bounded rows can still exceed an aggregate response cap. Metadata—including any truncation marker or original-length field needed by the consumer—can grow. Future schema fields can change the envelope size. That is why the hard stdout limit remains authoritative even after each row is shaped.

 For protocols with tight budgets, add an aggregate preflight as a separate design decision:



```
validate request limit
bound each semantic field before serialization
estimate or encode the complete response
enforce aggregate transport budget
retain receiver-side schema and size validation
```

 Do not silently reuse a UTF-16 code-unit limit as a claim about code points, grapheme clusters, display width, or bytes. Name the units that each boundary actually enforces.


## When Not to Use Silent Truncation



- Do not truncate opaque binary payloads, signatures, hashes, or tokens whose meaning depends on exact bytes.

- This exact field is already defined as a bounded snippet. For fields whose completeness matters, do not truncate unless the receiver can distinguish complete from partial data—for example through an explicit marker or original length.

- Do not hide an aggregate-budget failure by clipping arbitrary rows; preserve ranking and omission semantics explicitly.

- Do not move every transport rule into business logic. Keep the independent protocol ceiling.

- Do not generalize one file-backed regression into a universal IPC performance claim.

- Do not use this narrow proof to imply that broader child lifecycle, cancellation, packaging, reindex, or platform behavior was established by the same test.



 **Falsifier:** the bounded claim fails if parent-only post-receipt truncation survives the same unchanged stdout limit; producer-side truncation still loses the hit; the truncation splits the surrogate pair; invalid or oversized envelopes become accepted; or the cited landed commit lacks either the producer-side bound or the file-backed regression.



## A Small Review Checklist



- Identify the first hard transport boundary in the result path.

- Separate the semantic result limit from the transport byte limit.

- Carry the semantic limit to the producer before serialization.

- Validate the limit and every result row on the producer side.

- Use encoding-safe truncation for text.

- Retain receiver-side schema validation and the independent transport cap.

- Test a valid oversized result, not only malformed output.

- State which broader lifecycle and platform claims the regression does not prove.



## Conclusion

 The surprising part of this bug was that the database query could be correct, the snippet policy could be correct, and the final observed recall could still be wrong.

 The mistake was temporal: the policy ran after the boundary it needed to protect.

 Bound expected results before serialization. Keep the transport cap after them. Then test the valid oversized case where those two responsibilities are easiest to confuse.



### Related Posts



- [The 10-Second Session List](/jingxiao-cai-blog/10-second-session-list-prefilter-row-build-agent-gateway.html)

- [Before Raising Reindex Concurrency, Prove the Memory Lane](/jingxiao-cai-blog/before-raising-reindex-concurrency-prove-memory-lane.html)

- [Long-Running Agent Work Needs a Bridge Back](/jingxiao-cai-blog/long-running-agent-work-needs-bridge-back.html)

- [Proof Without Touching Production](/jingxiao-cai-blog/proof-without-touching-production-agent-pr-boundary.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, technical debugging, and evidence-driven engineering workflows.

 A correct result is not useful until it survives the boundary that carries it.




## Comments

 Which limit in your system runs only after the payload has already crossed—or failed to cross—the boundary it was meant to protect?

 [← Back to Blog](/jingxiao-cai-blog/)
