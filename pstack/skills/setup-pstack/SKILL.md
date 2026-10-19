---
name: setup-pstack
description: Configure pstack's project-scoped Codex or Claude Code agents, role models and reasoning budget. Use for setup-pstack, configure pstack models, pstack budget, or updating pstack agents after updating skills.
---

# Setup pstack

Configure the calling project from the actual installed **pstack-support** location. Read its `references/host-instructions.md`. Do not write global rules or project state in the skill installation.

## Steps

### 1. Detect host, tools and available models

Identify Codex or Claude Code from the current session. Inspect native delegation and model-selection capabilities. Only accept models confirmed available; do not copy provider-specific defaults from another host. `inherit-parent` and `auto` mean no override. If models cannot be enumerated, use inheritance or ask for the user's confirmed choices. Check whether this client supports the current official agent format.

### 2. Load current state

Read the project's `AGENTS.md` (Codex) or `CLAUDE.md` (Claude Code), the two host agent files, and `.pstack/setup-<host>.json` when present. Preserve unrelated content, role choices, permissions and personal edits. The receipt records the source commit, adapter version and each file's last-written SHA-256. An existing name with no receipt is not automatically pstack-owned.

Run the installed support script in preview mode:

```sh
python3 <actual-support-location>/scripts/setup.py --host <codex|claude-code> --project <calling-project>
```

It requires matching `setup-pstack`, `poteto-mode` and support installations. Missing support must be installed explicitly:

```sh
npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/pstack-host-adaptation --skill pstack-support setup-pstack 'Poteto Mode' --agent codex claude-code
```

### 3. Budget, map and confirm

Use the host's question tool when a choice is needed; retain previous choices on reruns. Offer the original budgets `unlimited — max reasoning`, `large — xhigh reasoning`, `medium — high reasoning`, `small — medium reasoning`. Only apply effort levels supported by the selected model and client. Keep model name and effort separate. Inheritance remains inheritance. Report unsupported budget levels and get a supported choice rather than inventing a slug.

Show these original roles with current or inherited choices:

- feature, refactoring; bug-fix; perf-issue; hillclimb.
- judgment and prose; hardest tasks.
- how explorer; how explainer; why investigators; why synthesizer.
- reflect tooling; reflect judgment, divergent, synthesizer.
- arena runners; arena cross-judge pool; swarm workers.
- architect runners; interrogate reviewers.

Panel rows are lists: one native agent per entry, including inherited entries. Default runners/reviewers have two seats. Cross-judge selects one available entry. Keep candidate counts and separate angles even when only one model exists, and disclose the diversity limit. Swarm workers use their role except where race arms explicitly choose models.

### 4. Validate

Run support preflight for the chosen host and installed locations. Every chosen real model must be confirmed available, and each effort level supported. Check named-agent tool selection; do not assume a generic spawn can invoke a registered persona. For local edits or unowned same-name files, show current and proposed content and resolve ownership before writing. There is no force-overwrite mode.

### 5. Write the project configuration

Before the first write or an installed-version update, identify the exact installed fork commit. Prefer installing `https://github.com/vagusX/pstack/tree/<full-commit-sha>` so the project skills lockfile records an immutable ref. If that ref is missing (including local or global installs), supply `--source-commit <verified-installed-fork-sha>` to both preview and write. Do not use the upstream commit or resolve a mutable branch after installation as a substitute. The helper deliberately refuses a write without this provenance. On an unchanged installed version it retains the previous successful source commit.

After reviewing the preview, run the same script with `--write`. This deterministic script registers complete personas into `.codex/agents/poteto-agent.toml` and `comment-sicko.toml`, or `.claude/agents/poteto-agent.md` and `comment-sicko.md`. It merges a bounded pstack section into `AGENTS.md` or `CLAUDE.md`, preserving other content. It reads back files before recording successful hashes. It does not enable automations or change the parent's permission mode.

Then edit user-owned model rows inside that section, retaining all existing choices. The agent performs these model edits; the script does not enumerate models or claim to validate account entitlement. Example after selecting a confirmed model:

```text
pstack-role feature, refactoring: inherit-parent
pstack-role how explorer: inherit-parent
pstack-role arena runners: inherit-parent, inherit-parent
pstack-role arena cross-judge pool: inherit-parent
pstack-role architect runners: inherit-parent, inherit-parent
pstack-role interrogate reviewers: inherit-parent, inherit-parent
```

Record supported effort in the host agent fields (`model_reasoning_effort` for Codex, `effort` for Claude Code) or the current native spawn settings, as appropriate. Agent-file model settings may override role spawn choices; inspect both. Existing permission/tool choices remain user-owned. A model or permission edit is a local modification: review and adopt the merged file with its exact hash before an upstream refresh.

On conflicts, back up local changes, show the last-written/current/new comparison, merge the upstream managed body while retaining user settings, then use the script's `--accept-merge <repo-relative-path>=<sha256>` to adopt that exact reviewed file. Re-run preview first. Never use acceptance to discard a user's changes without review.

### 6. Confirm and verify

Read back host files, role rows and receipt. In a NEW trusted project session actually invoke `poteto-agent` and `comment-sicko`, verify the full persona and dependency read, terminal result and actual permissions. Until that test runs, report registration as written and native loading as unverified. Do not present review-only prose as an isolated sandbox.

For updates: **update skills → rerun setup → verify both agents in a new session**. Updating skills alone does not refresh copied agents. An unchanged installation does not rewrite unchanged files. Upstream updates refresh unmodified managed files. Locally edited files require a reviewed merge. Source commit and last-written hashes remain recorded.

### 7. Offer a verification skill (optional)

If the project has no verified way to drive the real app, offer **create-verification-skill** once. Use project `.agents/skills/` for Codex or `.claude/skills/` for Claude Code. Verify the harness before claiming app-level proof.

For dormant Benny setup, add `--benny` to the reviewed script command to merge its full pack into `.pstack/automations/benny/`, preserving destination-only files and refusing unreviewed local conflicts. User configuration lives separately in `.pstack/benny/`. Read the copied `FOR_AGENTS.md` next. No scheduler is enabled by this command.
