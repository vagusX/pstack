# Pstack host instructions

Use the calling project's configuration and the actual skill locations supplied by the host. Project skills take precedence over global skills. Do not search a plugin cache or select a version by sorting paths. A skill's sibling references use the active installation; if a dependency is absent, install that named skill and pstack-support from the same source. `skills add` does not resolve dependencies.

Before a delegated workflow, find the active pstack-support and run its `scripts/setup.py --host <codex|claude-code> --project <project> --check --skill-location <invoking skill directory>`. A broken support copy, mixed source, modified published content or missing required skill is a failed preflight. Add `--require <installed directory name>` for each workflow dependency. For poteto-mode, require every principle or routed skill the selected playbook uses before starting it. Do not substitute the source checkout for an installed dependency. Missing support: `npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/pstack-host-adaptation --skill pstack-support --agent codex claude-code`.

Manual invocation is preserved: Claude Code retains `disable-model-invocation`, and Codex receives `agents/openai.yaml` with `allow_implicit_invocation: false` for the same original entries. Setup remains automatically discoverable. A routed skill is read explicitly as a workflow dependency. For an entry with `paths` frontmatter, gate routing on those patterns against the actual task files; in particular typescript-best-practices applies only to `.ts`/`.tsx`. Do not assume an unsupported skill frontmatter field is enforced by the host parser.

## Models

Read `pstack-role <role>: <model>[, <model>...]` rows from this project's managed instruction block. A role without a row inherits the parent model. `auto` and `inherit-parent` mean omit a model override. Default arena runners, architect runners and interrogate reviewers each have TWO inherited-model seats; keep distinct approaches and review angles. Reflect keeps three reviewers and one synthesizer. Swarm retains its requested or derived N. The cross-judge pool defaults to one inherited seat. Report when the host only supplies one vendor or one model. This is not cross-vendor evaluation.

Only use model names confirmed available in this session or account. Never translate provider-specific slugs by string editing. Set reasoning effort separately using fields that the host and selected model actually accept. No hardcoded Grok, Composer or provider model defaults. A rejected model falls back to inheritance once and is reported. Setup preserves user model and permission settings. Named agent configuration can override spawn defaults; inspect it before claiming a role ran on a particular model.

## Native delegation

First inspect the current session's tool schemas. If native delegation is absent, explain that the delegated workflow cannot run here. Do not simulate agents by repeated self-questioning. A caller may explicitly choose a separately described direct workflow, but that is not native-delegation verification.

In Codex, use the exposed native spawn/send/wait/close lifecycle (or the application's collaboration tools when those are the provided interface). Use the supported custom-agent selector for `poteto-agent` or `comment-sicko`; if this interface cannot select registered agents, report the gap rather than calling a generic agent a successful named-agent invocation. Pass a standalone task with exact scope, file pointers, skill locations, SHA and success checks. Track returned IDs; wait for terminal results, review outputs and release completed agents. Fresh agents handle new tasks; resume only when the original workflow's state-reuse conditions apply.

In Claude Code, use the exposed Agent tool, its supported `subagent_type`, `model`, background and resume fields. Select the project registered agent for named delegates, and a confirmed general-purpose type for other workflow roles. Use the tool's returned task identifier and its actual result/wait mechanism. Do not assume Cursor's tool names, cloud parameters or status UI. Inspect supported effort configuration rather than adding an effort suffix to a model name.

Codex agents are standalone `.codex/agents/<name>.toml` files with `name`, `description`, and complete `developer_instructions`. Parent permissions, provider and MCP servers are inherited; `sandbox_mode` in a custom agent file does not create a new sandbox. Claude Code uses `.claude/agents/<name>.md` frontmatter and complete body; `background` is supported, whereas the upstream `is_background` field is not. Configuration loading, inherited permissions and model overrides depend on the installed client version. Start a new trusted project session after setup and actually invoke both names. Parsed TOML/YAML alone is not proof of registration.

Review-only personas are instructions, not access isolation. A reviewer with Bash or write-capable MCP tools can still mutate state. Check its real tool permissions; do not claim complete read-only isolation. MCP access does not disappear merely because a task is described as read-only.

## Execution and persistence

Writing project skills or named agents can require additional host permission even inside the project. Codex's default `workspace-write` policy protects existing `.agents/`, `.codex/`, `.git/` and `.aws/` directories recursively. When a required skill or setup edit is denied, use the host's native approval mechanism for that exact change. Do not disable the sandbox, relocate the output and call it installed, or silently skip the write. If approval is unavailable, retain a reviewable draft outside the protected directory, report the exact destination that remains unwritten, and keep installation or maintenance unverified. See [Codex protected paths](https://learn.chatgpt.com/docs/agent-approvals-security#protected-paths-in-writable-roots).

Check whether a real cloud executor is provided before asking for cloud execution. Describe the actual location. With only local delegation, create independent worktrees at exact requested SHAs and isolate ports, build output and application state. Worktrees share a machine, network and credentials and do not persist an agent after the client closes. Resume from committed briefs, decision logs and branches; verify executor liveness before reattaching work. Report cloud-only requirements that cannot be satisfied locally.

For long-running work, inspect the host's actual scheduler and tool access. Codex application automations need a configured project and usable connectors; the CLI's ability to run a prompt is not an event trigger. Claude Code Desktop scheduled tasks need the machine running; cloud scheduled tasks use a fresh clone and task-specific connectors; session `/loop` requires an active session. Never promise persistence from an in-session loop. Do not activate anything without the user's request.

Use the project's existing control harness for CLI, browser or native-app proof. If unavailable, use **create-verification-skill** to build and verify a project-local harness. A diff cleanup pass removes narrating comments, dead code, unsupported guards and unrelated changes; **no-comments** and **unslop** supply the pstack reviews. Other Cursor plugins are not required. For skill authoring use Codex **skill-creator** when available; otherwise write and validate Agent Skills frontmatter, references and behavior directly.

Transcripts come from active-session metadata or scoped exports. Verify the recorded project before reading. Report missing history rather than deriving a Cursor workspace slug or reading unrelated projects. Run tool scripts from the calling project; `.pstack/runtime/` holds locked dependencies and caches. Ignore `.pstack/runtime/`, `.pstack/.setup.lock`, `.pstack/benny-state.sqlite*` in project version control. Keep the secret-free setup receipt if configuration provenance needs to be shared.

## Sources checked on 2026-10-14

- [Codex custom agents and inherited permissions](https://learn.chatgpt.com/docs/agent-configuration/subagents).
- [Codex skills and invocation controls](https://developers.openai.com/codex/skills).
- [Claude Code subagents](https://code.claude.com/docs/en/sub-agents).
- [Claude Code skills](https://code.claude.com/docs/en/skills).
- [Claude Code scheduled tasks](https://code.claude.com/docs/en/scheduled-tasks).
- [Codex application automations](https://developers.openai.com/codex/app/automations).
