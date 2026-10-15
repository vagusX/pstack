# Previous fork capabilities

The checked-out main and origin/main both point to the Cursor source commit `1e5c90a4b6f249917bd21fe361b3a2a7deb741b8`. The previous port is available at `feat/codex-integration`; its CLI/viewer are not files on this source baseline. This implementation does not remove them from that branch or change a published package.

| Previous capability | Source | Decision / upgrade impact |
| --- | --- | --- |
| Five-host build generator and generated skill copies | `core/`, `skills/`, build workflow | Not imported. This fork installs the original skill directories plus one shared support directory through skills CLI. Existing installs are not automatically migrated. |
| Python installation and management CLI | `packaging/src/pstack_cli/` (`init`, `update`, `uninstall`, `doctor`, `status`, profiles, receipts) | Keep the old branch/package usable. No command-compatible replacement and no silent uninstall. Users choose separately whether to retire it. The new setup helper only manages project personas/instructions/Benny files. |
| Session viewer | `packaging/src/pstack_cli/observe/`, local `serve` | Not imported into source adaptation. No equivalent UI is claimed. Keep old viewer/package if required. |
| Execution / run-record tooling | `core/skills/poteto-mode/scripts/run-record.py`, CLI observer readers and run contracts | Not imported. Upstream decision TSV, orch ledger and watch-pr remain. They do not replace the previous session/run viewer. |
| Other Cursor plugins / marketplace | Original repository top-level plugins | Removed from this branch per user's explicit 2026-10-14 instruction: final distribution contains pstack only. History retains the source. |

Do not run the old CLI's update/uninstall over a new skills installation without a separate migration decision. Host configs and run records already created by the old package remain user-owned. No release, package upgrade, user-global install or old-PR closure is performed by this change.
