---
name: pstack-support
description: Shared pstack host instructions, original agent personas, guide and dormant Benny pack. Read when setting up pstack or running its delegated workflows in Codex or Claude Code.
---

# Pstack support

This is an added support skill, not an upstream pstack entry. It contains the shared files that the skills installer cannot carry from outside a selected skill directory.

Read [host instructions](references/host-instructions.md) before running a delegated workflow. Run `python3 <this skill location>/scripts/setup.py --host codex --project <calling project> --check` (use `claude-code` for Claude Code). Python 3.11+ is required. This validates installed files, provenance and project-over-global precedence. It does not register agents or enable automations.

For registration, use **setup-pstack**. For Benny, read [FOR_AGENTS.md](automations/benny/FOR_AGENTS.md) from this installed location, then merge the pack into the target project. Operational Benny files are `INSTRUCTIONS.md`, so neither the installer nor host registers them as skills, even during recursive discovery.

The [guide](docs/guide/README.md), [poteto-agent persona](agents/poteto-agent.md), [comment-sicko persona](agents/comment-sicko.md), assets and [upstream license](LICENSE) are stored here once. Never write project state or dependencies into this installed directory.
