---
name: setup-benny
description: Configure Benny and prepare its triage and repro automations. Use when installing Benny or changing its Slack, tracker, repository, routing, control, model, or budget settings.
disable-model-invocation: true
---

# Set up Benny

Benny ships as a dormant automation pack inside pstack. The plugin manifest exposes only pstack's normal skill root; this file and the two operational files are not slash skills.

The human enters setup by pointing the host agent at the pack's `FOR_AGENTS.md`. The bootstrap flow copies the whole pack into the target repository, then reads this file directly at `.pstack/automations/benny/skills/setup-benny/INSTRUCTIONS.md`.

Benny needs external configuration and two live host automations.

Do not create or update an automation until the user explicitly asks. Never put a secret value in plugin files, prompts, or committed configuration.

## 1. Copy the pack and enable shared pstack skills

Do this before asking for Benny configuration and before choosing a host scheduler.

Ask which repository will run the automations. The source pack is the directory containing `FOR_AGENTS.md`. The destination is `<target-repository>/.pstack/automations/benny/`.

Merge the entire source pack into the destination:

1. Create the destination when it is absent.
2. Copy every source file to the same relative path.
3. Preserve destination-only files. Never delete unrelated files during install or refresh.
4. Keep user-owned configuration, feature maps, and routing maps outside the destination. Never overwrite them.
5. When an existing source-managed file differs, inspect the diff and merge without discarding local edits. If ownership is ambiguous, stop and ask before replacing it.
6. Verify that the destination contains `FOR_AGENTS.md`, this setup file, both operational files, their references, and the templates.

If this file is already being read from the target destination, treat the copy as complete and run the same verification before continuing.

Install the full pstack skill set into this target project with the pinned skills CLI for its host. Do not use a global installation as evidence of project dependencies. Run setup-pstack and its reviewed `--benny` merge. Codex project skills are in `.agents/skills/`; Claude Code uses `.claude/skills/` (or CLI-created links to `.agents/skills/`). No plugin-enablement setting is required.

Reload the target project or start a fresh agent rooted there. Verify that these shared pstack skills resolve from project scope:

- `how`
- `why`
- `tdd`
- `unslop`
- `principle-separate-before-serializing-shared-state`
- `principle-minimize-reader-load`
- `principle-guard-the-context-window`
- `principle-sequence-verifiable-units`
- `principle-fix-root-causes`
- `principle-prove-it-works`

Do not count a skill loaded from the current session or a user-scoped plugin. The check must show that a fresh agent in the target repository receives the project-installed skills.

If project-scoped skill installation is unavailable or any shared dependency does not resolve, stop and explain the failure.

The Benny files are read directly from `.pstack/automations/benny/`. Do not add that directory to a plugin manifest or expect its `INSTRUCTIONS.md` files to appear in the slash-skill list.

Tell the user that project skill lockfile and host instructions, `.pstack/automations/benny/`, and any referenced secret-free configuration must be committed before either automation is enabled. Do not commit them unless the user asks.

Once this check passes, live automation prompts may read the committed operational files by their stable repository-relative paths. They must not embed a plugin cache path or copy the file contents.

## 2. Adapt the configuration

Open these copied examples:

- `../../templates/configuration.example.yaml`
- `../reproduce-and-fix-issues/references/feature-map.example.md`

Create user-owned copies outside `.pstack/automations/benny/`. These are configuration files, not pack files. Example locations:

- Project config, such as `.pstack/benny/configuration.yaml`
- Project feature map, such as `.pstack/benny/feature-map.md`
- Project routing map, such as `.pstack/benny/routing.md`
- User config, such as `~/.config/benny/configuration.yaml`
- User feature map, such as `~/.config/benny/feature-map.md`

Fill one feature-map section for every user-facing feature the automation may reproduce. Keep it at the user point of view. Do not freeze implementation details or current code paths in the map.

Do not edit the copied examples. Pack refreshes may update source-managed files after conflict review, but they must never touch the user-owned copies.

Prefer committed, secret-free files in the target repository when a fresh automation checkout must read them. Otherwise paraphrase the required values into the live prompt. Reference a repository file only after verifying through repository commands that the file is committed in the repository where the automation runs.

Use stable repository-relative paths for committed pack and configuration files. Never reference the plugin source directory or a plugin cache path from a live automation.

## 3. Fill the required choices

Ask for or confirm:

- Source Slack channel ID
- Optional operations or status channel ID
- Repository URL and default branch
- Triage identity or Slack user ID
- Issue tracker type, team, project, labels, and intake status
- Tracker adapter skill or MCP actions
- Optional routing map path
- Required control skill name
- Required user-facing feature-map path
- Status emoji strings
- Pull request URL format
- Polling and effort budgets
- Model slug for triage, repro, code work, and media review

Use only model slugs shown as available in the user's current host session's available model list. Do not guess a slug or carry over a private default. When enumeration is unavailable, use inherited model settings or the user's independently confirmed choice; configure effort separately where supported.

The source channel, triage identity, repository, tracker adapter, control skill, and feature map must be explicit. Fail setup if any required value stays ambiguous.

Use pstack's `unslop` skill on the final automation names, descriptions, and prompt shims before saving them.

## 4. Check integration capabilities

The triage automation needs:

- Read access to the configured source Slack channel and its threads
- Thread-reply access in that channel
- Attachment metadata and file download access when reports include media
- Search, read, create, and update access through the configured issue-tracker adapter

The repro automation needs:

- Read access to the source thread
- Thread-reply access in the source channel
- Optional post and edit access in the configured operations channel
- Repository read and history access
- A pull request action that can open a draft pull request
- The configured control-adapter skill

Prefer configured connected Slack tools for reads and posts. The optional `BENNY_SLACK_BOT_TOKEN` may fill a narrow gap such as editing one operations status message or downloading an attachment. Store the value in a secret manager or environment, not in YAML.

Do not use undocumented integration endpoints.

## 5. Prepare the routing map

If the user wants reroutes or owner pings:

1. Copy `../triage-issue-reports/references/routing.example.md` outside `.pstack/automations/benny/`.
2. Replace every placeholder with public or organization-local values.
3. Keep owner pings off by default.
4. Allow a ping only for a configured feature owner or a confirmed likely regression author.

If no routing map is configured, triage may classify a report but must not guess a destination or owner.

## 6. Verify the control adapter

Read `../reproduce-and-fix-issues/references/control-adapter.md` and the user's completed feature map.

Confirm that the named skill can:

- Bring up the target app
- Navigate every mapped feature through the real UI
- Exercise mapped states through declared adapter actions
- Inspect state without forcing the result
- Capture screenshots
- Start and stop a recording
- Clean up its processes and temporary data

If any capability is missing, leave the repro automation disabled. It must fail closed rather than claim a reproduction it did not perform.

## 7. Prepare the live automations

Ask whether this is first-time creation or configuration of existing automations.

Read `../../FOR_AGENTS.md` from the copied pack as the primary user-intent source for either path. Use it to understand the two triggers, tools, instructions, outcomes, and shared rules.

### First-time creation

Do not create a scheduler task before the user explicitly requests activation and chooses a dedicated test Slack channel, tracker project and safe application environment. Prepare and review both templates with the finished configuration first.

Inspect the current account and tool catalog for direct Slack event triggers. A scheduler does not provide Slack reading, thread replies, attachments, tracker mutations or app control. Require actual configured tools for each operation, including draft-only PR creation and tracker compensation. Do not continue if tools are absent.

If direct event triggers are supported, bind both workflows to the same new top-level report, retaining channel ID and root thread timestamp. Otherwise use **polling**: on each scheduled run read new top-level messages in the configured channel plus previously pending threads, and deduplicate by `(channel_id, root_thread_ts)`. Repro continues pending threads until its verdict wait deadline. Thread replies must not become new intake reports.

For Codex, use an actually exposed application automation/task interface with this target project and its connectors, or prepare the task for the user's application scheduler when no callable scheduling tool exists. Verify the task can read Slack content before activation. Codex CLI alone is not a Slack event trigger.

For Claude Code, prefer a persistent Desktop scheduled task or cloud scheduled task only if its actual connectors, repository checkout and app control satisfy the workflow. Desktop requires the machine running; cloud starts from a fresh clone and may not access a local app. `/loop` is session-bound and must be reported as such. Set polling from the existing configured poll budget, subject to the host's actual minimum interval, and disclose rounding. A persistent remote runner needs persistent dedup storage; a fresh clone without that storage fails closed. Do not add a new hosting service without a demonstrated need and user choice.

Each task reads its operational file directly from `.pstack/automations/benny/skills/<workflow>/INSTRUCTIONS.md` and the user configuration path under `.pstack/benny/`. Use repository commands to confirm those files are committed on the exact execution branch/commit. Never point live prompts at skill caches or global installations. Run a fresh target-project session to verify how, why, tdd, unslop and the listed principle skills in project scope.

Before any external side effect, use the copied pack's `journal.py` to durably claim its intent. A repeated or pending intent requires reconciling the external thread/ticket/PR, not blindly repeating the write. Complete it with the external ID after success. A crash between the external write and local completion requires finding and recording that existing object. Use existing tracker search and source link to deduplicate tickets. The ledger lives at `.pstack/benny-state.sqlite` outside the copied pack, never in a skill or fresh throwaway clone.

Triage must publish exactly one marker reply in the original thread. Repro must check the configured trusted author's marker in that same thread, check existing ownership/fixes, reproduce twice, then use the original verification and bounded-fix order. Delegate only sanitized evidence; no Slack credentials, Slack connector handles or posting rights may reach workers. If the host cannot restrict inherited Slack write tools, do not delegate Benny to those workers. Report that permission gap and keep external operations in the coordinator.

### Existing automations

Inspect each existing task by its actual scheduler ID. Update reviewed fields rather than creating replacements. Check repository/commit, operational instruction and configuration paths, source channel, thread-only tools, tracker and draft PR actions, app-control tools, schedule/trigger and state persistence. Re-read the saved task. Do not invent a Cursor editor handoff or assume `/automate` exists.

### Creation boundary

Setup and pack copying never enable a task. Actual Slack, tracker or PR writes require explicit authorized test targets. Keep both tasks disabled until the thread-safety tests pass through a real trigger. Simulation or manually invoking a prompt is not automatic-trigger evidence.

## 8. Test thread safety

Use the dedicated test channel, tracker project and application environment explicitly chosen and authorized by the user.

Before testing, confirm that the target repository's project skill lockfile and host instructions, `.pstack/automations/benny/`, and every referenced secret-free configuration file are committed on the branch used by the automation checkout. Confirm that both live prompts point at their exact committed operational files. If any check fails, stop. Tell the user that the automation cannot be enabled yet.

Verify:

1. Triage stores the root `thread_ts` and posts exactly one verdict as a reply.
2. The verdict contains one configured marker.
3. Repro accepts the marker only from the configured triage identity.
4. Repro keeps the same immutable source coordinates.
5. No source-channel root message appears.
6. A delegated worker cannot use any Slack write action.
7. Missing coordinates, a deleted parent, or a failed preflight produces no post and no tracker issue.

Enable normal traffic only after all seven checks pass.
