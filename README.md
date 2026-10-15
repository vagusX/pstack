# pstack for Codex and Claude Code

This fork adapts [Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack) from upstream commit `1e5c90a4b6f249917bd21fe361b3a2a7deb741b8`. The repository distributes only pstack: 54 original skills, their resources and playbooks, two agent personas and the dormant Benny pack. `pstack-support` is one added shared skill; it carries files that a single-skill install cannot otherwise include.

Use Node 22.20+ and the pinned skills CLI:

```sh
npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/pstack-host-adaptation --skill '*' --agent codex claude-code -y
```

Use `--global` for global skill content, `--copy` for copies. Setup always targets the calling project. For a subset, explicitly include `pstack-support` and each workflow's dependencies. For example:

```sh
npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/pstack-host-adaptation --skill setup-pstack 'Poteto Mode' pstack-support --agent codex -y
```

Invoke `$setup-pstack` in Codex or `/setup-pstack` in Claude Code. It reads the installed support, previews project configuration and registers the complete personas through a Python 3.11+ helper. Existing user content is preserved; locally changed or unowned files require a reviewed merge. Pin installation to an immutable fork commit for reproducibility; setup records that actual commit separately from the upstream commit. If the installer does not retain it, pass `--source-commit <verified installed fork SHA>` to the reviewed helper command.

After updating skills, rerun setup and verify both named agents in a new trusted project session. Updating skills alone does not update project agent files. Model names are confirmed at runtime, with inheritance as the default. Role models live in managed `AGENTS.md`/`CLAUDE.md` sections; no Cursor model rule or cloud-agent API is required. Workflows report the actual local/cloud execution location and available model diversity.

[The full guide and original-author README](pstack/skills/pstack-support/README.md) retain the upstream workflows, with host-specific instructions adapted. [Migration ledger](pstack/docs/migration.md), [Cursor coupling inventory](pstack/docs/cursor-coupling.json) and [validation report](pstack/docs/validation.md) describe what changed and what was actually tested.

Make Bot UI remains **not adapted** because these hosts do not supply the original webhook routine and secret-request contract. Its full original instructions are retained as a historical reference behind an explicit blocked entry. Benny setup copies the complete pack to `.pstack/automations/benny/` but never enables tasks. Real Slack/tracker/application tests require explicitly chosen and authorized targets. [Host instructions](pstack/skills/pstack-support/references/host-instructions.md) document tool gates and execution limitations.

The previous five-host generator, Python installation CLI, session viewer and run-record tooling remain available on `feat/codex-integration`; this source-based branch neither modifies that branch nor publishes a replacement package. See [legacy scope](pstack/docs/legacy-scope.md).

Copyright and attribution remain with their original authors under the [upstream MIT license](pstack/skills/pstack-support/LICENSE).
