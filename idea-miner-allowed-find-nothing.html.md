# An Idea Miner Should Be Allowed to Find Nothing

URL: https://anyech.github.io/jingxiao-cai-blog/idea-miner-allowed-find-nothing.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/idea-miner-allowed-find-nothing.html.md
Date: 2026-07-11
Tags: ai-agents, product-discovery, research, automation, agent-ops, validation

Summary: The useful output of an idea miner is not a pile of concepts. It is an evidence-qualified advance, hold, or reject decision under a hard research bound.

---

[← Back to Blog](/jingxiao-cai-blog/)

# An Idea Miner Should Be Allowed to Find Nothing


 **July 11, 2026** | By Jingxiao Cai

 Tags: ai-agents, product-discovery, research, automation, agent-ops, validation



 This post was co-created with **Clawsistant**, my OpenClaw AI agent. It helped run a bounded public-source research pilot, separate human pain from generated noise, and turn the result into a reusable falsification workflow without contacting anyone or publishing private research artifacts.



 **Boundary:** this is a product-discovery method, not proof that any candidate deserves to be built. Public issue reports can establish pain; they do not establish willingness to switch, install, or pay.


 Most automated idea workflows have a hidden failure condition: they are expected to find an idea.

 That expectation quietly changes the objective. The agent stops asking, “Is there an evidence-qualified opportunity?” and starts asking, “Which candidate can I make sound exciting before the run ends?”


 **An idea miner that cannot return zero advance candidates is a content generator, not a discovery system.**



 I ran a small, time-bounded pilot against problems reported by developers using coding agents and multi-agent systems. The most useful result was not a launch plan. It was one *hold*, several *rejects*, and zero *advance* decisions.

 That outcome made the workflow more credible. It also produced a repeatable method for operators who want agents to research product ideas without laundering noisy search results into a roadmap.


 **Reader promise:** by the end of this post, you will have a compact idea-card contract that forces independent evidence, existing-solution review, a narrow wedge, and explicit advance/kill thresholds before any build begins.



## The Failure Mode: Research Owes You a Winner

 A forced-output miner tends to make four mistakes:



- it treats high comment counts as demand without checking whether the comments are human, independent, or about the same problem;

- it searches for pain but not for capable existing solutions;

- it mistakes an upstream feature request for a portable product surface;

- it turns “interesting” into “build next” without a falsification test.


 The fix is not a more creative prompt. It is a workflow whose valid terminal states include **advance**, **hold**, **reject**, and **none found**.


## A Bounded Pilot Funnel

 One short pilot used a deliberately small search budget. Its public-safe funnel looked like this:



```
7 issue artifacts
  -> 5 human pain observations
  -> 3 clusters
  -> 2 portable clusters
  -> 2 externally corroborated clusters
  -> 1 hold card
  -> 0 advance cards
```

 The numbers are one run's bookkeeping, not a conversion rate, prevalence estimate, or demand metric. They are useful only as a proof unit that the workflow discarded material at every gate instead of preserving every search hit as a candidate.



| Gate | Question | Failure means |
| --- | --- | --- |
| **Human pain** | Is this a first-person problem report rather than an automated tracker or generated roadmap item? | Reject as demand evidence. |
| **Independence** | Does the pain recur across unrelated tools, repositories, or communities? | Keep as a local bug, not a portable opportunity. |
| **Supply** | Do existing products already solve the problem well enough? | Reject or narrow the wedge. |
| **Control** | Can an independent product solve it, or is the behavior naturally owned by the upstream vendor? | Reject as a product surface. |
| **Falsifiability** | Can a cheap test change the decision within days rather than months? | Hold until a sharper test exists. |


## Counterevidence Is a First-Class Deliverable

 The pilot found repeated symptom reports of agents stalling after partial work. Public issues document incomplete actions followed by no response in [VS Code agent mode](https://github.com/microsoft/vscode/issues/253126) and long zero-progress hangs in [Claude Code](https://github.com/anthropics/claude-code/issues/26224).

 That is evidence that the pain can occur across more than one tool. It is not a prevalence estimate, proof of market-wide independent demand, or evidence of an empty market.

 The current public listing for [AgentLens](https://marketplace.visualstudio.com/items?itemName=agentlens.agentlens-dashboard) describes local agent-session observability, traces, file diffs, loop detection, and recommendations. Other local tools offer replay, rewind, or unified usage reporting. A generic dashboard would be duplicate supply.

 The surviving wedge was narrower: a local recovery capsule that turns a likely stalled run into an explicit resume, handoff, or rollback-review packet. Even that candidate remained a hold because the unresolved question is whether it is meaningfully better than observability plus version control.


 **Discovery rule:** pain evidence earns deeper investigation. Strong existing supply removes the right to keep the original idea unchanged.



## The Idea Card Contract

 A useful idea card is designed to make rejection easy:



```
idea_card:
  user:
    who_has_the_problem: specific
    buyer_if_different: explicit_or_unknown
  pain:
    independent_sources: listed
    recurrence: observed_not_assumed
    workaround: recorded
  counterevidence:
    existing_solutions: strongest_first
    upstream_owner: yes_or_no
    duplicate_supply_risk: low_medium_high
  wedge:
    narrower_than_existing_tools: yes_or_no
    unsafe_or_uncontrolled_behavior: absent
  falsification:
    cheapest_comparative_test: defined
    advance_threshold: numeric_or_observable
    kill_threshold: numeric_or_observable
  authority:
    outreach_approved: no_by_default
    install_or_build_approved: no_by_default
  verdict: advance | hold | reject
```

 The card should contain the strongest reason not to build. If the counterevidence section reads like a polite footnote, the miner is still pitching rather than investigating.


## Three Useful Rejections



| Candidate shape | Why it looked attractive | Why it was rejected or held |
| --- | --- | --- |
| **Cross-agent usage tracker** | Unexpected token or cost consumption recurs across tools. | Capable unified reporting already exists, including [ccusage](https://github.com/ccusage/ccusage); an automatic circuit breaker also risks damaging partial work. |
| **Always-visible model thinking** | Users want feedback when an agent appears stuck. | The requested behavior is tightly coupled to vendor UI and API policy, so it is naturally upstream. |
| **Generic no-op detector** | Automated issues and logs can look like evidence of broad frustration. | Bot-generated artifacts are architecture output, not independent human demand; loop detection is already part of existing observability tools. |

 Rejecting these candidates was not lost work. It prevented duplicate products, unsafe automation, and vendor-policy dependencies from entering the build queue.


## Advance and Kill Thresholds

 A hold card should name the evidence that could flip it. For the recovery-capsule wedge, a cheap comparative test could show synthetic stalled-run traces beside existing recovery workflows and ask relevant users which path they would choose.

 The exact thresholds will vary, but they should cover three distinct questions:



- **Recognition:** do target users recognize a recent matching pain?

- **Switching:** do enough users prefer the proposed wedge over their current workaround?

- **Commitment:** will they take a costly next step such as sharing an anonymized trace, trying a local prototype, or accepting plausible pricing?


 The kill rule matters just as much. If users say existing tools plus ordinary retry are adequate, or safe integration requires capturing sensitive source content, the miner should retire the card.


 **Authority boundary:** research can prepare an outreach plan. Contacting users, posting in communities, collecting traces, installing integrations, or building a prototype remains a separate approved action.



## How This Differs From a Pattern Scout

 A pattern scout asks, “What fresh signal deserves attention?” An idea miner asks, “Should this opportunity survive counterevidence and earn a test?”

 The scout protects novelty. The miner protects the build queue.

 They can share sources, but they should not share success criteria. A scout succeeds when it finds a fresh, public-safe pattern. An idea miner succeeds when it produces a defensible decision, including the decision to build nothing.


## When Not To Use This Workflow

 Idea mining is the wrong tool when:



- you are responding to an active incident and need diagnosis, not product discovery;

- the roadmap decision is already made and the real task is execution;

- the only evidence is private or current-work material that should not enter a public research loop;

- meaningful validation requires outreach, data collection, or installs that have not been approved;

- the problem is clearly owned by an upstream vendor and no independent wedge exists.



## Conclusion

 The credibility of an idea miner is not measured by how many polished concepts it produces.

 It is measured by whether it separates human pain from generated noise, searches for the strongest existing alternatives, narrows the wedge, names a cheap verdict-flipping test, and refuses to build when the evidence does not earn it.

 One hold and zero advances can be a successful run. Sometimes that is exactly the result that protects the next month of engineering time.



### Related Posts



- [Building a Pattern Scout That Does Not Chase Its Own Echoes](/jingxiao-cai-blog/building-pattern-scout-does-not-chase-own-echoes.html)

- [Freshness Is Not Permission](/jingxiao-cai-blog/freshness-is-not-permission-agent-opsec-gates.html)

- [Public-Safe Evidence Beats Private Debugging Dumps](/jingxiao-cai-blog/public-safe-agent-pr-evidence-routing.html)

- [When a Dirty-Tree Alert Is Correct](/jingxiao-cai-blog/dirty-tree-alert-review-artifact-agent-ops.html)






### About the Author

 Jingxiao Cai works on distributed ML runtime systems and backend execution reliability, and writes about self-hosted agents, evidence-driven workflows, and operational decision boundaries.

 A research agent earns trust by knowing when not to pitch.





### Feedback

 Questions, critiques, or examples of useful idea rejections? Open an issue in the [blog repository](https://github.com/anyech/jingxiao-cai-blog) or leave a comment below.



 Published on July 11, 2026 • Part of my ongoing AI-agent research and workflow series

 [← Back to Blog](/jingxiao-cai-blog/)
