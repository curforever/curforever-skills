# Official Prompting Playbook

Use this reference when writing high-quality prompts from rough requirements. It synthesizes official OpenAI and Anthropic guidance into practical rules. Do not quote this file to the user unless they ask for the analysis; use it to shape the final prompt.

Sources:
- OpenAI API prompt engineering: https://developers.openai.com/api/docs/guides/prompt-engineering
- OpenAI Help, ChatGPT prompt engineering best practices: https://help.openai.com/ko-kr/articles/10032626-prompt-engineering-best-practices-for-chatgpt
- OpenAI Help, API prompt engineering best practices: https://help.openai.com/ko-kr/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
- OpenAI Help, prompt management in Playground: https://help.openai.com/ko-kr/articles/9824968-prompt-management-in-playground
- Anthropic Claude prompt best practices: https://platform.claude.com/docs/ko/build-with-claude/prompt-engineering/claude-prompting-best-practices

## Universal Rules

- Be clear, direct, and specific. Include enough context for a capable but uninformed assistant to execute the task.
- Put the primary instruction near the start, then separate source text, examples, and variables with explicit labels or delimiters.
- Specify the desired output shape: format, length, sections, schema, style, tone, and success criteria.
- Prefer positive instructions: say what the model should do, not only what it should avoid.
- Replace vague words with measurable constraints, such as exact sentence ranges, section names, or fields.
- Add examples when output consistency matters. Use diverse examples that cover edge cases and show the desired format.
- Start zero-shot for simple tasks. Add few-shot examples when the output format or judgment boundary is not reliable enough.
- For factual, extraction, and deterministic tasks, keep creativity low and make the answer grounded in supplied context or cited sources.
- Iterate prompts by testing outputs, identifying failure modes, and tightening instructions or examples.
- Do not ask for hidden chain-of-thought. Ask the model to reason privately, verify its work, or provide concise rationale when needed.

## Mode Selection

Choose the first matching mode:

1. OpenAI API / reusable prompt: when the prompt will be used in an application, Playground, Responses API, Agents SDK, or repeated workflow.
2. Claude: when the user names Claude, Anthropic, or Claude-specific behavior.
3. Coding agent: when the task involves a repository, files, implementation, debugging, tests, or code review.
4. Research / long-context: when the task involves documents, many sources, citations, policy/legal/medical/financial accuracy, or long files.
5. General assistant: when the task is one-off writing, planning, summarization, brainstorming, tutoring, or analysis.
6. Image/video: when the output is a visual generation prompt.

If multiple modes apply and the choice changes the prompt substantially, present 2-4 options with one recommended default. Otherwise choose the best mode silently and draft the prompt.

## OpenAI API / Production Pattern

Use this structure when targeting OpenAI API, prompt management, or production reuse:

```text
# Identity
[Role and domain specialization]

# Instructions
[Durable task rules and business logic]

# Inputs
Use the following variables:
- {{variable_name}}: [meaning]

# Output Format
[Exact schema, sections, or parseable format]

# Examples
[Optional few-shot examples when format or judgment boundaries matter]

# Quality Check
Before responding, verify that [criteria].
```

Rules:
- Separate durable developer-level rules from per-request user inputs, as if the prompt is a function and the user variables are arguments.
- Keep stable reusable prompt content at the beginning when cost/latency from prompt caching matters.
- Use placeholders for dynamic values. Keep static instructions separate from instance data.
- For production prompts, define eval cases or pass/fail criteria before relying on the prompt.
- In Playground-managed prompts, use versioning, variables, side-by-side comparison, rollback, and eval runs when available.
- Prefer a structured output schema for parsing, extraction, classification, routing, or automation.
- For GPT-style models, precise instructions and required data improve steerability.
- For reasoning models, prefer clear goals, constraints, and success criteria; avoid over-specifying every internal reasoning step.

## ChatGPT / General Assistant Pattern

Use this structure for one-off ChatGPT prompts:

```text
Act as [role].

Task:
[Specific request]

Context:
[Background, audience, source material, constraints]

Output:
- [Required sections or format]
- [Length/tone/style]

Quality bar:
[What a good answer must satisfy]
```

Rules:
- Include the audience and intended use of the answer.
- State tone explicitly when tone matters.
- For summarization or transformation, wrap source content in a labeled block.
- If the user wants exploration, ask for alternatives; if they want action, instruct the model to produce the deliverable directly.

## Claude Pattern

Use Claude-specific structure when Claude is the target:

```text
<role>
[Role or system behavior]
</role>

<instructions>
[Direct task instructions in ordered steps when sequence matters]
</instructions>

<context>
[Background and source material]
</context>

<examples>
[3-5 relevant, diverse examples if consistency matters]
</examples>

<output_format>
[Exact format and style]
</output_format>
```

Rules:
- Use clear, direct instructions. Do not rely on the model to infer desired extra behavior from a vague request.
- XML-style tags help Claude distinguish instructions, context, examples, documents, and input variables.
- Put role in the system prompt when the calling environment supports system prompts.
- Tell Claude what to do instead of only what not to do.
- Match prompt style to desired output style; if prose is desired, write prose-like instructions rather than bullet-heavy prompts.
- For long-context work, put long documents before the query and final instructions, and use document/source metadata tags.
- For long documents, ask Claude to ground the answer in relevant quoted or cited evidence before concluding when factual precision matters.
- For tool-use tasks, explicitly say whether to suggest, implement, inspect, or ask first.

## Coding Agent Pattern

Use this for Codex, Claude Code, ChatGPT coding tasks, repo agents, and debugging:

```text
You are a senior software engineer working in this repository.

Task:
[Bug/feature/change request]

Process:
1. Inspect the relevant files before making claims or edits.
2. Identify the root cause or implementation approach.
3. Make the smallest scoped change that matches existing patterns.
4. Add or update focused tests if the repository has a relevant test pattern.
5. Run the relevant validation command and report the result.

Constraints:
- Do not revert unrelated changes.
- Do not add unrelated refactors.
- Avoid overengineering, unnecessary abstractions, and speculative configurability.
- Do not hardcode values just to satisfy tests.
- Clean up temporary files created during investigation.

Final response:
- What changed
- Files changed
- Verification
- Remaining risks
```

Add stricter instructions for high-risk code:
- Investigate before answering; do not make code claims without reading relevant files.
- Prefer standard tools and real implementation logic over workaround scripts.
- If the task or tests appear wrong, stop and explain rather than forcing a bad implementation.

## Research / Long-Context Pattern

Use this when correctness and evidence matter:

```text
You are a careful research assistant.

Question:
[Research question]

Sources and scope:
[Allowed sources, date constraints, source hierarchy]

Method:
1. Gather current primary sources when facts may have changed.
2. Separate source-backed facts from inference.
3. Resolve conflicts between sources or flag uncertainty.
4. Cite sources for factual claims.

Output:
[Format, length, audience]
```

Rules:
- Define source priority: official docs, primary sources, then reputable secondary sources.
- Require dates when the topic changes over time.
- For long document sets, label each document and ask the model to cite or reference the document ids.
- Ask for uncertainty flags rather than confident guesses.

## Image / Video Prompt Pattern

Use this for generation prompts:

```text
[Medium/style] of [subject], [setting], [composition/framing], [action or state], [lighting], [color palette], [mood], [camera/lens or visual language], [quality/detail constraints].

Avoid: [unwanted elements, text artifacts, style mismatches].
Aspect ratio: [ratio].
```

Rules:
- Name the actual subject and visual state, not just mood.
- Include text handling explicitly when text should appear or be avoided.
- Use negative constraints sparingly and specifically.

## Prompt Quality Checklist

Before finalizing a prompt, check:

- Target model or platform is clear, or the prompt is model-agnostic by design.
- Role, task, context, constraints, output, and success criteria are present when relevant.
- Source material is separated from instructions.
- Dynamic inputs are placeholders or clearly labeled.
- Output format is explicit enough to parse or evaluate.
- Examples are included only when they improve reliability.
- Provider-specific conventions are applied when OpenAI API or Claude is targeted.
- The prompt asks for verification without requesting hidden reasoning.
- The prompt does not add requirements beyond the user's intent.
