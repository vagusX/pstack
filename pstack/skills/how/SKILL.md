---
name: how
description: "Use for \"how does X work\", code walkthroughs before changing something, and placement / ownership / layering questions (\"where should this live\", \"which package owns this\", \"is this the right layer\"). Explains subsystem architecture, runtime flow, onboarding mental models. Use why for motivation."
disable-model-invocation: true
---

Before executing, read the installed **pstack-support** `references/host-instructions.md` and run its preflight with this skill's actual location. If support is missing, stop and show `npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/pstack-host-adaptation --skill pstack-support --agent codex claude-code`. Read sibling dependencies from the host's active skill locations, with project copies taking precedence.


# How

Explore the codebase to answer "how does X work?" questions. Produce architectural explanations at the level of a senior engineer onboarding onto a subsystem, enough to build a working mental model, not so much that it reads like annotated source code.

Resolve this workflow's role models from the pstack-managed block in the project `AGENTS.md` (Codex) or `CLAUDE.md` (Claude Code). Default to `inherit-parent`; retain the original panel size with distinct review angles. Use only models confirmed available in this session. Do not invent vendor aliases or retry with another vendor's model. See the installed **pstack-support** host instructions for native delegation, effort and permission behavior.

Explorers use the `how explorer` role and explainers the `how explainer` role. Both default to inheritance. Use the host's confirmed general-purpose native type with review-only instructions and verified real tool permissions.

## 1. Assess complexity

If the scope is ambiguous, state your interpretation and explore. The user can redirect.

- **Simple** (a single module, a small utility, a narrow question such as "how does function X work"): no explorers. Spawn one explainer that explores and explains in one pass, built from `references/explainer-prompt.md` without the explorer-findings section. Go to step 4.
- **Complex** (a subsystem spanning multiple files or services, a cross-cutting feature, a full architectural overview): go to step 2.

When in doubt, take the simple path.

## 2. Explore (complex only)

Decompose the question into 2 to 4 angles, each a distinct slice of the subsystem. Spawn all explorers in a single message, each with `references/explorer-prompt.md` and its angle filled in.

## 3. Synthesize (complex only)

Once all explorers have returned, spawn one explainer with `references/explainer-prompt.md` and every explorer's findings filled in.

## 4. Present

Present the explainer's output. Light edits for clarity or context from the conversation are fine. Do not substantially rewrite it.

## Output format

The explanation uses the sections defined in `references/explainer-prompt.md`, dropping any that do not apply: Overview, Key Concepts, How It Works, Where Things Live, Gotchas.
