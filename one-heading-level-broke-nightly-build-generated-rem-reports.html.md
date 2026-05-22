# One Heading Level Broke the Nightly Build: Fixing Markdown Drift in Generated REM Reports

URL: https://anyech.github.io/jingxiao-cai-blog/one-heading-level-broke-nightly-build-generated-rem-reports.html
Markdown mirror: https://anyech.github.io/jingxiao-cai-blog/one-heading-level-broke-nightly-build-generated-rem-reports.html.md
Date: 2026-05-08
Tags: openclaw, automation, markdown, regression-testing, ai-agents, writing

Summary: A generated Markdown report failed over one heading-level jump; the durable fix was testing each rendered output surface as its own artifact contract.

---

← Back to Blog
 
# One Heading Level Broke the Nightly Build: Fixing Markdown Drift in Generated REM Reports

 
 May 8, 2026 | By Jingxiao Cai

 Tags: openclaw, automation, markdown, regression-testing, ai-agents, writing
 

 
 This post was co-created with Clawsistant, my OpenClaw AI agent. It helped reconstruct the heading-depth failure, keep the public version free of deployment fingerprints, and turn a small Markdown bug into a reusable artifact-contract lesson.
 

 
 Short version: a generated report failed because one heading jumped to the wrong level. The durable fix was not “tell the agent to format better”; it was to test each rendered output surface as its own artifact contract.
 

 The bug was almost comically small: a generated Markdown report emitted a heading at the wrong depth. The content was fine. The summary was useful. The automation around it was doing exactly what I wanted.

 And then the nightly check failed anyway.

 
 Generated Markdown is not “just text” once another tool consumes it. It is an API with indentation, heading depth, and document-shape contracts.

 

 
 Conceptual scope: this is a public OpenClaw/tooling lesson from a self-hosted agent workflow. I am intentionally leaving out private paths, job names, thread identifiers, runtime topology, exact local schedules, and raw command logs. The public teaching point is the artifact contract, not my deployment fingerprint.
 

 
## The Failure: Valid Words, Invalid Document Shape

 The failing artifact was a generated REM-style memory report. It looked readable to a human, but the Markdown structure had a heading-level jump that violated the repository's structure rule. A linter saw what a human skimmer might miss: the document tree was malformed.

 That distinction matters because automation usually does not consume prose the way humans do. It consumes the rendered artifact shape:

 
 
- headings define hierarchy;
 
- hierarchy controls navigation, summaries, and downstream linting;
 
- lint rules become the contract between a generator and the rest of the pipeline.
 

 So the bug was not “the agent wrote a bad paragraph.” The bug was “the generator emitted a structurally invalid document for one of its consumers.”

 
## The First Fix Was Too Simple

 The tempting patch was obvious: change the heading depth globally. If a standalone report starts with a top-level title, then its child sections should move one level lower. Easy.

 Except the same generated text had two valid destinations:

 
 
 
 Output surface
 Parent context
 Correct contract
 

 
 
 
 Inline daily-note block
 Already nested under an existing section.
 Keep deeper child headings so the block remains under its parent.
 

 
 Standalone REM report
 Starts from its own document root.
 Lower the same conceptual headings to fit under the document title.
 

 
 

 A global heading change would fix one surface while breaking the other. That is the part I liked about the eventual review feedback: it was not bike-shedding Markdown style. It caught a real two-consumer contract.

 
 Public reference: this became an upstream OpenClaw fix shape in openclaw/openclaw#68505. The useful part was not the PR number; it was the realization that inline and standalone output paths needed separate rendered-shape validation.
 

 
## The Correct Fix: Normalize at the Boundary

 The durable fix was to keep the shared generated content in the shape needed by the inline consumer, then adjust the heading depth at the boundary where the standalone report is written.

 That may sound like a small implementation detail, but it is the design rule:

 
 When one generated fragment has multiple consumers, normalize for each output boundary instead of pretending there is one universally correct shape.

 

 In practice, this meant the validation had to prove both outputs:

 
 
- render the inline block inside its parent context;
 
- render the standalone report from its document root;
 
- run the Markdown structure check against both rendered artifacts;
 
- keep the tests close enough to the writer paths that a future refactor cannot silently reintroduce the drift.
 

 The fix was not to make the generator “try harder.” It was to make the generator accountable to the exact artifacts other tools read.

 
## Why Prompting Alone Would Have Failed

 This is a useful little example of why prompt-only reliability has a ceiling.

 You can ask an agent to “use proper Markdown.” You can add examples. You can add style rules. Those things help, but they do not define the parent heading context at the moment the artifact is written. The same fragment can be proper in one document and improper in another.

 That means the reliable layer is not the prompt. The reliable layer is the renderer plus the artifact-level test.

 
 
 
 Weak guard
 Better guard
 Why
 

 
 
 
 “Please use valid Markdown.”
 Render the final Markdown and lint it.
 The linter checks the artifact, not the intention.
 

 
 One shared template assumption.
 Per-output boundary normalization.
 Different consumers can require different heading depth.
 

 
 Manual spot-checking.
 Regression tests for each supported surface.
 The bug was small enough for humans to miss and automation to catch.
 

 
 

 
## The General Lesson for Agent Workflows

 Agent systems increasingly generate things that are not just chat responses: reports, memory notes, issue bodies, changelogs, config snippets, release packets, and review summaries. Those artifacts often become inputs to other tools.

 The more that happens, the more generated prose starts behaving like a public interface. The interface may be Markdown instead of JSON, but the principle is the same:

 
 
- name the consumer;
 
- define the artifact shape;
 
- validate the final rendered output;
 
- test every supported output surface, not just the shared prose generator.
 

 This is especially important for “almost the same” outputs. Inline and standalone reports feel similar enough that a shared helper is attractive. That is fine. But once their parent contexts differ, their heading contracts differ too.

 
## A Checklist I Would Use Next Time

 If I were designing another generated-Markdown feature now, I would start with this checklist:

 
 
- List every output surface. Inline note, standalone report, issue body, email draft, feed excerpt—each one gets a row.
 
- Write down the parent context. What heading level, wrapper, or metadata already exists before the generated fragment appears?
 
- Render examples, not just fragments. Test the whole document shape that downstream tools will consume.
 
- Lint the final artifacts. Structure rules should fail before the artifact reaches a nightly job or public surface.
 
- Treat review comments as contract probes. If a reviewer says a fix handles one output but breaks another, assume that is real until proven otherwise.
 

 
 The tiny bug was useful because it was tiny. It exposed a boundary that would have been easy to ignore: generated text becomes software once other software depends on its structure.
 

 
## Conclusion

 The important part of this story is not Markdown trivia. It is that “valid enough for a human reader” and “valid for the pipeline” are different standards.

 One heading level was enough to break the nightly path because the artifact had become part of an automated system. The fix was to respect that system: define the output contracts, normalize at the boundaries, and test the final rendered documents.

 If an agent generates an artifact that another tool consumes, do not only review the words. Review the shape.

 
 
### Related Posts

 
 
- Why Custom Skills Did Not Load in OpenClaw - A Historical Bug and Follow-Up
 
- Why AI Cron Jobs Need Exact-Exec Drivers
 
- The Nightly Build: How My Agent Runs Security Audits While I Sleep
 
- Long-Running Agent Work Needs a Bridge Back
 

 

 
 
### About the Author

 Jingxiao Cai works on AI/ML infrastructure and writes about self-hosted agents, generated artifacts, automation, and the boring reliability contracts that keep agent workflows useful.

 One heading level is not a big deal until the pipeline says it is.

 

 
## Comments

 Found this useful? Leave a comment below, or send it to someone building generated reports that have quietly become APIs.

 ← Back to Blog
