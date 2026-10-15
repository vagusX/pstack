# Source migration ledger

Upstream: `https://github.com/cursor/plugins` at `1e5c90a4b6f249917bd21fe361b3a2a7deb741b8`. All original 54 frontmatter names and manual/path policies are retained. Benny instruction filenames change to avoid skill discovery, including full-depth scans.

| Source | Target | Decision | Verification |
| --- | --- | --- | --- |
| `pstack/.cursor-plugin/plugin.json` | `(removed)` | remove Cursor-only plugin registration; npx skills is the entry point | scope removal |
| `pstack/.gitignore` | `pstack/.gitignore` | preserve byte for byte | hash matches |
| `pstack/LICENSE` | `pstack/skills/pstack-support/LICENSE` | preserve byte for byte | hash matches |
| `pstack/README.md` | `pstack/skills/pstack-support/README.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/agents/comment-sicko.md` | `pstack/skills/pstack-support/agents/comment-sicko.md` | preserve byte for byte | hash matches |
| `pstack/agents/poteto-agent.md` | `pstack/skills/pstack-support/agents/poteto-agent.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/assets/logo.png` | `pstack/skills/pstack-support/assets/logo.png` | preserve byte for byte | hash matches |
| `pstack/automations/benny/FOR_AGENTS.md` | `pstack/skills/pstack-support/automations/benny/FOR_AGENTS.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/README.md` | `pstack/skills/pstack-support/automations/benny/README.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/skills/reproduce-and-fix-issues/SKILL.md` | `pstack/skills/pstack-support/automations/benny/skills/reproduce-and-fix-issues/INSTRUCTIONS.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md` | `pstack/skills/pstack-support/automations/benny/skills/reproduce-and-fix-issues/references/control-adapter.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/skills/reproduce-and-fix-issues/references/feature-map.example.md` | `pstack/skills/pstack-support/automations/benny/skills/reproduce-and-fix-issues/references/feature-map.example.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md` | `pstack/skills/pstack-support/automations/benny/skills/reproduce-and-fix-issues/references/verify-existing-fix.md` | preserve byte for byte | hash matches |
| `pstack/automations/benny/skills/setup-benny/SKILL.md` | `pstack/skills/pstack-support/automations/benny/skills/setup-benny/INSTRUCTIONS.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/skills/triage-issue-reports/SKILL.md` | `pstack/skills/pstack-support/automations/benny/skills/triage-issue-reports/INSTRUCTIONS.md` | preserve byte for byte | hash matches |
| `pstack/automations/benny/skills/triage-issue-reports/references/routing.example.md` | `pstack/skills/pstack-support/automations/benny/skills/triage-issue-reports/references/routing.example.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/templates/configuration.example.yaml` | `pstack/skills/pstack-support/automations/benny/templates/configuration.example.yaml` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/templates/reproduce-automation-prompt.md` | `pstack/skills/pstack-support/automations/benny/templates/reproduce-automation-prompt.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/automations/benny/templates/triage-automation-prompt.md` | `pstack/skills/pstack-support/automations/benny/templates/triage-automation-prompt.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/01-setup.md` | `pstack/skills/pstack-support/docs/guide/01-setup.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/02-poteto-mode.md` | `pstack/skills/pstack-support/docs/guide/02-poteto-mode.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/03-understand.md` | `pstack/skills/pstack-support/docs/guide/03-understand.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/04-design.md` | `pstack/skills/pstack-support/docs/guide/04-design.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/05-build-and-clean.md` | `pstack/skills/pstack-support/docs/guide/05-build-and-clean.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/06-verify-and-ship.md` | `pstack/skills/pstack-support/docs/guide/06-verify-and-ship.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/07-overnight.md` | `pstack/skills/pstack-support/docs/guide/07-overnight.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/08-principles.md` | `pstack/skills/pstack-support/docs/guide/08-principles.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/09-make-it-yours.md` | `pstack/skills/pstack-support/docs/guide/09-make-it-yours.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/10-recipes-and-pitfalls.md` | `pstack/skills/pstack-support/docs/guide/10-recipes-and-pitfalls.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/README.md` | `pstack/skills/pstack-support/docs/guide/README.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/docs/guide/images/design.jpg` | `pstack/skills/pstack-support/docs/guide/images/design.jpg` | preserve byte for byte | hash matches |
| `pstack/docs/guide/images/overnight.jpg` | `pstack/skills/pstack-support/docs/guide/images/overnight.jpg` | preserve byte for byte | hash matches |
| `pstack/docs/guide/images/recipes.jpg` | `pstack/skills/pstack-support/docs/guide/images/recipes.jpg` | preserve byte for byte | hash matches |
| `pstack/docs/guide/images/router.jpg` | `pstack/skills/pstack-support/docs/guide/images/router.jpg` | preserve byte for byte | hash matches |
| `pstack/docs/guide/images/understanding.jpg` | `pstack/skills/pstack-support/docs/guide/images/understanding.jpg` | preserve byte for byte | hash matches |
| `pstack/docs/guide/images/verification.jpg` | `pstack/skills/pstack-support/docs/guide/images/verification.jpg` | preserve byte for byte | hash matches |
| `pstack/plugin.json` | `pstack/plugin.json` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/architect/SKILL.md` | `pstack/skills/architect/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/architect/references/design-red-flags.md` | `pstack/skills/architect/references/design-red-flags.md` | preserve byte for byte | hash matches |
| `pstack/skills/architect/references/rationale-template.md` | `pstack/skills/architect/references/rationale-template.md` | preserve byte for byte | hash matches |
| `pstack/skills/architect/references/runner-prompt.md` | `pstack/skills/architect/references/runner-prompt.md` | preserve byte for byte | hash matches |
| `pstack/skills/arena/SKILL.md` | `pstack/skills/arena/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/automate-me/SKILL.md` | `pstack/skills/automate-me/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/benchmark-checklist/SKILL.md` | `pstack/skills/benchmark-checklist/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/blast-radius/SKILL.md` | `pstack/skills/blast-radius/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/bro/SKILL.md` | `pstack/skills/bro/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/correct/SKILL.md` | `pstack/skills/correct/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/create-verification-skill/SKILL.md` | `pstack/skills/create-verification-skill/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/create-verification-skill/references/feature-map-example/README.md` | `pstack/skills/create-verification-skill/references/feature-map-example/README.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/create-verification-skill/references/feature-map-example/create-note.md` | `pstack/skills/create-verification-skill/references/feature-map-example/create-note.md` | preserve byte for byte | hash matches |
| `pstack/skills/create-verification-skill/references/feature-map-example/search.md` | `pstack/skills/create-verification-skill/references/feature-map-example/search.md` | preserve byte for byte | hash matches |
| `pstack/skills/figure-it-out/SKILL.md` | `pstack/skills/figure-it-out/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/how/SKILL.md` | `pstack/skills/how/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/how/references/explainer-prompt.md` | `pstack/skills/how/references/explainer-prompt.md` | preserve byte for byte | hash matches |
| `pstack/skills/how/references/explorer-prompt.md` | `pstack/skills/how/references/explorer-prompt.md` | preserve byte for byte | hash matches |
| `pstack/skills/in-your-own-words/SKILL.md` | `pstack/skills/in-your-own-words/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/interrogate/SKILL.md` | `pstack/skills/interrogate/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/interrogate/references/code-quality-review.md` | `pstack/skills/interrogate/references/code-quality-review.md` | preserve byte for byte | hash matches |
| `pstack/skills/interrogate/references/lead-judgment.md` | `pstack/skills/interrogate/references/lead-judgment.md` | preserve byte for byte | hash matches |
| `pstack/skills/interrogate/references/reviewer-prompt.md` | `pstack/skills/interrogate/references/reviewer-prompt.md` | preserve byte for byte | hash matches |
| `pstack/skills/interrogate/references/rubric.md` | `pstack/skills/interrogate/references/rubric.md` | preserve byte for byte | hash matches |
| `pstack/skills/ketchup/SKILL.md` | `pstack/skills/ketchup/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/maintain-verification-skill/SKILL.md` | `pstack/skills/maintain-verification-skill/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/make-bot-ui/SKILL.md` | `pstack/skills/make-bot-ui/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/no-comments/SKILL.md` | `pstack/skills/no-comments/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-help/SKILL.md` | `pstack/skills/poteto-help/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-help/references/prompting.md` | `pstack/skills/poteto-help/references/prompting.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-help/references/recipes.md` | `pstack/skills/poteto-help/references/recipes.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/SKILL.md` | `pstack/skills/poteto-mode/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/authoring-a-skill.md` | `pstack/skills/poteto-mode/playbooks/authoring-a-skill.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/autonomous-run.md` | `pstack/skills/poteto-mode/playbooks/autonomous-run.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/autopilot-full.md` | `pstack/skills/poteto-mode/playbooks/autopilot-full.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/autopilot-stack.md` | `pstack/skills/poteto-mode/playbooks/autopilot-stack.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/playbooks/babysit.md` | `pstack/skills/poteto-mode/playbooks/babysit.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/bug-fix.md` | `pstack/skills/poteto-mode/playbooks/bug-fix.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/eval.md` | `pstack/skills/poteto-mode/playbooks/eval.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/feature.md` | `pstack/skills/poteto-mode/playbooks/feature.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/hillclimb.md` | `pstack/skills/poteto-mode/playbooks/hillclimb.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/investigation.md` | `pstack/skills/poteto-mode/playbooks/investigation.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/playbooks/multi-phase-plan.md` | `pstack/skills/poteto-mode/playbooks/multi-phase-plan.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/opening-a-pr.md` | `pstack/skills/poteto-mode/playbooks/opening-a-pr.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/orchestrate.md` | `pstack/skills/poteto-mode/playbooks/orchestrate.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/pause-safely.md` | `pstack/skills/poteto-mode/playbooks/pause-safely.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/playbooks/perf-issue.md` | `pstack/skills/poteto-mode/playbooks/perf-issue.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/prototype.md` | `pstack/skills/poteto-mode/playbooks/prototype.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/playbooks/refactoring.md` | `pstack/skills/poteto-mode/playbooks/refactoring.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/runtime-forensics.md` | `pstack/skills/poteto-mode/playbooks/runtime-forensics.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/playbooks/session-pickup.md` | `pstack/skills/poteto-mode/playbooks/session-pickup.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/shipping.md` | `pstack/skills/poteto-mode/playbooks/shipping.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/playbooks/trace-forensics.md` | `pstack/skills/poteto-mode/playbooks/trace-forensics.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/playbooks/visual-parity.md` | `pstack/skills/poteto-mode/playbooks/visual-parity.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/playbooks/worktree-cleanup.md` | `pstack/skills/poteto-mode/playbooks/worktree-cleanup.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/references/bugbot-triage.md` | `pstack/skills/poteto-mode/references/bugbot-triage.md` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/bootstrap.ts` | `pstack/skills/poteto-mode/scripts/bootstrap.ts` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/scripts/bun.lock` | `pstack/skills/poteto-mode/scripts/bun.lock` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/check-plan.mjs` | `pstack/skills/poteto-mode/scripts/check-plan.mjs` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/check-plan.test.ts` | `pstack/skills/poteto-mode/scripts/check-plan.test.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/orch/orch.test.ts` | `pstack/skills/poteto-mode/scripts/orch/orch.test.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/orch/orch.ts` | `pstack/skills/poteto-mode/scripts/orch/orch.ts` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/scripts/orch/store.ts` | `pstack/skills/poteto-mode/scripts/orch/store.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/package.json` | `pstack/skills/poteto-mode/scripts/package.json` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/cli.test.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/cli.test.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/cli.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/cli.ts` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/poteto-mode/scripts/watch-pr/fakes.test-helper.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/fakes.test-helper.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/github.test.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/github.test.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/github.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/github.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/policy.test.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/policy.test.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/policy.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/policy.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/render.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/render.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/tsconfig.json` | `pstack/skills/poteto-mode/scripts/watch-pr/tsconfig.json` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/types.compile.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/types.compile.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/types.ts` | `pstack/skills/poteto-mode/scripts/watch-pr/types.ts` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/watch-pr/watch-pr` | `pstack/skills/poteto-mode/scripts/watch-pr/watch-pr` | preserve byte for byte | hash matches |
| `pstack/skills/poteto-mode/scripts/worktree-audit.sh` | `pstack/skills/poteto-mode/scripts/worktree-audit.sh` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/principle-attack-the-premise/SKILL.md` | `pstack/skills/principle-attack-the-premise/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-boundary-discipline/SKILL.md` | `pstack/skills/principle-boundary-discipline/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-build-the-lever/SKILL.md` | `pstack/skills/principle-build-the-lever/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-encode-lessons-in-structure/SKILL.md` | `pstack/skills/principle-encode-lessons-in-structure/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-exhaust-the-design-space/SKILL.md` | `pstack/skills/principle-exhaust-the-design-space/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-experience-first/SKILL.md` | `pstack/skills/principle-experience-first/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-explain-the-number/SKILL.md` | `pstack/skills/principle-explain-the-number/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-fix-root-causes/SKILL.md` | `pstack/skills/principle-fix-root-causes/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-foundational-thinking/SKILL.md` | `pstack/skills/principle-foundational-thinking/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-guard-the-context-window/SKILL.md` | `pstack/skills/principle-guard-the-context-window/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-laziness-protocol/SKILL.md` | `pstack/skills/principle-laziness-protocol/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-make-operations-idempotent/SKILL.md` | `pstack/skills/principle-make-operations-idempotent/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md` | `pstack/skills/principle-migrate-callers-then-delete-legacy-apis/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-minimize-reader-load/SKILL.md` | `pstack/skills/principle-minimize-reader-load/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-model-the-domain/SKILL.md` | `pstack/skills/principle-model-the-domain/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-never-block-on-the-human/SKILL.md` | `pstack/skills/principle-never-block-on-the-human/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-outcome-oriented-execution/SKILL.md` | `pstack/skills/principle-outcome-oriented-execution/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-prove-it-works/SKILL.md` | `pstack/skills/principle-prove-it-works/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-redesign-from-first-principles/SKILL.md` | `pstack/skills/principle-redesign-from-first-principles/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md` | `pstack/skills/principle-separate-before-serializing-shared-state/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-sequence-verifiable-units/SKILL.md` | `pstack/skills/principle-sequence-verifiable-units/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-subtract-before-you-add/SKILL.md` | `pstack/skills/principle-subtract-before-you-add/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-test-behavior-not-implementation/SKILL.md` | `pstack/skills/principle-test-behavior-not-implementation/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/principle-type-system-discipline/SKILL.md` | `pstack/skills/principle-type-system-discipline/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/recall/SKILL.md` | `pstack/skills/recall/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/reflect/SKILL.md` | `pstack/skills/reflect/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/reflect/references/divergent-reviewer.md` | `pstack/skills/reflect/references/divergent-reviewer.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/reflect/references/judgment-reviewer.md` | `pstack/skills/reflect/references/judgment-reviewer.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/reflect/references/synthesizer.md` | `pstack/skills/reflect/references/synthesizer.md` | preserve byte for byte | hash matches |
| `pstack/skills/reflect/references/tooling-reviewer.md` | `pstack/skills/reflect/references/tooling-reviewer.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/setup-pstack/SKILL.md` | `pstack/skills/setup-pstack/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/sharpen/SKILL.md` | `pstack/skills/sharpen/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/show-me-your-work/SKILL.md` | `pstack/skills/show-me-your-work/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/show-me-your-work/references/decision-log-template.tsv` | `pstack/skills/show-me-your-work/references/decision-log-template.tsv` | preserve byte for byte | hash matches |
| `pstack/skills/show-me-your-work/scripts/log.sh` | `pstack/skills/show-me-your-work/scripts/log.sh` | preserve byte for byte | hash matches |
| `pstack/skills/swarm/SKILL.md` | `pstack/skills/swarm/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/tdd/SKILL.md` | `pstack/skills/tdd/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/teach/SKILL.md` | `pstack/skills/teach/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/technical-writing/SKILL.md` | `pstack/skills/technical-writing/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/typescript-best-practices/SKILL.md` | `pstack/skills/typescript-best-practices/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/typescript-best-practices/references/patterns.md` | `pstack/skills/typescript-best-practices/references/patterns.md` | preserve byte for byte | hash matches |
| `pstack/skills/unslop/SKILL.md` | `pstack/skills/unslop/SKILL.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/SKILL.md` | `pstack/skills/why/SKILL.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/why/references/epistemics.md` | `pstack/skills/why/references/epistemics.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/investigator-prompt.md` | `pstack/skills/why/references/investigator-prompt.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/source-playbook.md` | `pstack/skills/why/references/source-playbook.md` | host adaptation; full workflow retained (Make Bot UI original retained in its reference) | present; source hash recorded; static/test coverage in validation report |
| `pstack/skills/why/references/sources/code-archaeology.md` | `pstack/skills/why/references/sources/code-archaeology.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/sources/databricks.md` | `pstack/skills/why/references/sources/databricks.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/sources/datadog.md` | `pstack/skills/why/references/sources/datadog.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/sources/incident-postmortem.md` | `pstack/skills/why/references/sources/incident-postmortem.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/sources/linear.md` | `pstack/skills/why/references/sources/linear.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/sources/notion.md` | `pstack/skills/why/references/sources/notion.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/sources/sentry.md` | `pstack/skills/why/references/sources/sentry.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/sources/slack.md` | `pstack/skills/why/references/sources/slack.md` | preserve byte for byte | hash matches |
| `pstack/skills/why/references/synthesizer-prompt.md` | `pstack/skills/why/references/synthesizer-prompt.md` | preserve byte for byte | hash matches |
