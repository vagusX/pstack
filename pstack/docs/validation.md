# Host adaptation validation

Validation window: 2026-10-14–19 (Asia/Shanghai). Tested source is the independent implementation checkout based on upstream `1e5c90a4b6f249917bd21fe361b3a2a7deb741b8`. This is a draft delivery, not a claim that all 54 workflows have run natively.

| Check | Evidence / result |
| --- | --- |
| Original discovery | Real skills CLI 1.7.2 found 54 original names, including Poteto Mode and Make Bot UI. No Benny nested entry. |
| Immutable GitHub installation | Real install from fork commit `16c9d599c6ff7825a3e75878f90822f1c781c682` found all 55 entries. Both setup writes read that exact SHA from skills-lock.json without a manual override; optional Benny merges across hosts, installed hashes unchanged. See remote-install.json. |
| Shared-content layout | Real subset install copied only each selected skill directory; original agents/Benny/guide were absent. This demonstrated the need for one added pstack-support skill. |
| Installation matrix | Node 22.20.0, skills 1.7.2; 16 rows across Codex/Claude Code, project/global, full/subset, copy/link, plus dual-host canonical links. Each source fixture removed before setup. Installed skill hashes unchanged. Final matrix JSON attached in this directory. |
| Runtime dependencies | Bun 1.4.3. Both orch and watch-pr run from calling projects after source removal. First install uses original frozen lock, repeat retains marker mtime, lock revision creates another keyed cache. Installed hashes unchanged. Linked .pstack and a directory named ..calling-project inside a skill are refused. |
| Upstream tools | All 68 upstream Bun tests pass, 246 assertions across 5 files. Strict watch-pr TypeScript check passes from a private project runtime copy. |
| Setup and simulated Benny recovery | 16 Python behavioral tests pass: initial preview/write, provenance, repeat mtimes, both host formats, upstream update, model/effort/permissions preserved, modified files, ambiguous ownership, reviewed hash adoption, pack merge, dual-host pack ownership, damaged metadata, precedence, marker trust/duplicates, restart reconciliation. |
| Independent review | Two independent read-only agents examined code and exercised separate fixtures. Confirmed findings were fixed: adopted instruction loss, symlink cache escape, parent-path segment check, marker order, timestamp schema, stale automate/why assumptions, provenance guidance, cross-host pack receipt and duplicate marker. |
| Codex native session | Follow-up with CLI 0.161.0 in a trusted project invoked both registered names. SQLite agent roles, terminal rollouts and exact developer-instruction hashes confirm actual persona loading. The earlier untrusted fixture had not loaded project roles; it did not establish a host capability limit. See native-agent-followup.json. |
| Claude Code native format | Follow-up with 2.1.300 used the native Agent tool with poteto-agent and comment-sicko subagent types; both completed with actual reads. See native-agent-followup.json. |
| External automations | No tasks activated; no Slack/tracker/PR/app writes for Benny. Journal tests simulate duplicate delivery, trusted markers and restart recovery. Real event triggers, polling scheduling, connector tools and UI repro remain unverified until dedicated targets are authorized. |
| Make Bot UI | Project-local native CLI executor implemented. Both hosts passed actual HTTP-to-agent probe runs; event IDs, session IDs and result hashes are in bot-ui-live-checks.json. Tailscale is not installed and has not been tested. The historical Cursor source is retained. |

## Review follow-up, 2026-10-15

The local fixes based on `a8a489dc2a55d4058f3afb331ee63b140fd5eefc` restore the package's `bun run test` entry point by running the tests in a temporary calling project. All 68 tests and 246 assertions pass with Bun 1.3.13; all 16 Python tests pass. The installation matrix was rerun on these fixes with Node 24.7.0 and skills 1.7.2: all 16 combinations and the additional shared-link case pass, including source removal, setup readback and unchanged installed content where checked by the harness.

Benny setup and both prompt templates now accept the selected committed configuration file or configuration values included in the live prompt. Non-default paths and inline configuration were checked in both templates; no automations were activated.

| Migration goal | Follow-up result |
| --- | --- |
| Source files, resources and invocation policies | 169 source inventory entries accounted for: 168 target files and one explicit Cursor registration removal; 54 original skills plus one support skill; all 53 original manual entries retain Codex implicit-invocation restrictions. |
| Installation, setup and tool tests | Verified by the local matrix and test runs above. Remote installation evidence still refers to `16c9d599c6ff7825a3e75878f90822f1c781c682`, not this follow-up revision. |
| Native named agents and all 54 workflows | Still unverified; the earlier native-host limits remain. File generation and passing tests do not establish actual host execution. |
| Benny real triggers, connectors and application reproduction | Still unverified; no dedicated external targets were activated. |
| Make Bot UI | Still not adapted. |

File migration and the tested installation paths meet their checks. Complete native workflow migration remains unverified, with Make Bot UI still missing an implementation.

## Native and webhook follow-up, 2026-10-19

Both hosts completed actual registered-persona calls; see `native-agent-followup.json`. Codex project trust must be configured by the user before starting a new session. No model change, empty project config or simulated generic delegate is required.

Make Bot UI now has an authenticated local receiver, durable events, native CLI execution, stored results and reviewed manual retry. Actual HTTP probes completed through Codex and Claude Code and returned exactly `ignored`. Both hosts also wrote and read back an exact project-local test artifact under explicit native permissions; see `bot-ui-live-checks.json`. Claude correctly denied the earlier untrusted-project write; the passed check used an explicitly authorized native tool launcher, not a permission bypass. Unit tests also exercise initialization, key permissions, Host/Origin checks, one-shot forwarding, concurrent retries and restart interruption. Tailscale access remains unverified. Real project-writing actions still require an explicitly scoped routine and native host permissions.

`workflow-acceptance.json` tracks a scenario for every original entry, actual execution and independent observable checks separately. An executed scenario is not proof of every branch of a workflow; unrun entries remain unverified. A real help run found the public link root missing `skills/`; it was fixed and its new output checked.

The user supplied a production Feishu topic group for read-only tests and explicitly forbids replies. The added Benny read-only adapter preserves native Feishu IDs, scopes intake by an optional start time, and stores reports plus dedup checkpoints privately. It cannot send messages or perform tracker/app actions. Real Slack/Benny trigger, reply, tracker and application-fix paths remain unverified. Internal group contents and identifiers are not distributed with this repository.

## Local regression checks, 2026-10-19

The follow-up content passed 34 Python tests with resource warnings treated as errors, 68 Bun tests with 246 assertions, and all 17 installation cases. Source mapping, target modes, original names and invocation policies were rechecked. Exact content and local evidence hashes are recorded in `migration-followup-checks.json`. The package test entry preinstalls its locked dependencies in the temporary project before timed test cases begin; slow downloads no longer consume a five-second CLI test budget.

A deterministic shutdown test reproduced a lost condition notification in the old webhook worker. The worker now rechecks stopping while holding the condition; the old code fails that regression and the fix passes. The independent review findings and these fixes do not establish completion of all entry workflows.

## Per-entry coverage

Each entry retains its frontmatter name, resources and invocation/path policy. Static adaptation, references and installation are checked. A representative test does not imply a real execution of every entry. The following statuses deliberately distinguish those facts.

| Directory | Original name | Codex | Claude Code | Invocation |
| --- | --- | --- | --- | --- |
| `architect` | architect | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `arena` | arena | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `automate-me` | automate-me | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `benchmark-checklist` | benchmark-checklist | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `blast-radius` | blast-radius | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `bro` | bro | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `correct` | correct | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `create-verification-skill` | create-verification-skill | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `figure-it-out` | figure-it-out | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `how` | how | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `in-your-own-words` | in-your-own-words | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `interrogate` | interrogate | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `ketchup` | ketchup | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `maintain-verification-skill` | maintain-verification-skill | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `make-bot-ui` | Make Bot UI | not adapted; original webhook contract required | not adapted; original webhook contract required | explicit only / routed read |
| `no-comments` | no-comments | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `poteto-help` | poteto-help | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `poteto-mode` | Poteto Mode | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-attack-the-premise` | principle-attack-the-premise | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-boundary-discipline` | principle-boundary-discipline | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-build-the-lever` | principle-build-the-lever | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-encode-lessons-in-structure` | principle-encode-lessons-in-structure | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-exhaust-the-design-space` | principle-exhaust-the-design-space | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-experience-first` | principle-experience-first | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-explain-the-number` | principle-explain-the-number | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-fix-root-causes` | principle-fix-root-causes | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-foundational-thinking` | principle-foundational-thinking | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-guard-the-context-window` | principle-guard-the-context-window | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-laziness-protocol` | principle-laziness-protocol | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-make-operations-idempotent` | principle-make-operations-idempotent | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-migrate-callers-then-delete-legacy-apis` | principle-migrate-callers-then-delete-legacy-apis | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-minimize-reader-load` | principle-minimize-reader-load | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-model-the-domain` | principle-model-the-domain | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-never-block-on-the-human` | principle-never-block-on-the-human | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-outcome-oriented-execution` | principle-outcome-oriented-execution | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-prove-it-works` | principle-prove-it-works | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-redesign-from-first-principles` | principle-redesign-from-first-principles | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-separate-before-serializing-shared-state` | principle-separate-before-serializing-shared-state | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-sequence-verifiable-units` | principle-sequence-verifiable-units | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-subtract-before-you-add` | principle-subtract-before-you-add | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-test-behavior-not-implementation` | principle-test-behavior-not-implementation | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `principle-type-system-discipline` | principle-type-system-discipline | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `recall` | recall | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `reflect` | reflect | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `setup-pstack` | setup-pstack | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | automatic discovery |
| `sharpen` | sharpen | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `show-me-your-work` | show-me-your-work | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `swarm` | swarm | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `tdd` | tdd | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `teach` | teach | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `technical-writing` | technical-writing | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `typescript-best-practices` | typescript-best-practices | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `unslop` | unslop | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |
| `why` | why | static + install verified; actual workflow unverified | static + install verified; actual workflow unverified | explicit only / routed read |

The added pstack-support entry is shared installation support, not one of the original 54. Manual Codex metadata maps the original disable-model-invocation policy; TypeScript paths remain in frontmatter and are enforced by host routing instructions because unsupported skill fields are not assumed to be native filters.

## Reproduce checks

Run Python 3.11+ behavioral checks:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s pstack/tests -p 'test_*.py'
```

Run the real CLI matrix with paths to a locally prepared Node 22.20+ binary, skills@1.7.2 CLI and Bun 1.4.3:

```sh
python3 pstack/tests/install_matrix.py --node <node> --cli <skills-package>/bin/cli.mjs --bun <bun> --output <results.json>
```

Run preserved upstream tests through the package entry point. It creates and removes a temporary calling project, so dependency installation does not write into the skill directory:

```sh
cd <installed-poteto-mode>/scripts
bun run test
```

For strict typechecking, copy script sources into the calling project's private dependency cache and use that cache's TypeScript compiler. No node_modules or emitted code may be written into the installed skill.

Rebuild the source ledger and integrity metadata after changes with `python3 pstack/scripts/audit.py`. It checks that every original file has a destination or explicit Cursor-manifest removal and that original file modes remain unchanged. It does not create host release copies.

## State and configuration

| Added item | Purpose | Can it be deleted? |
| --- | --- | --- |
| pstack-support/manifest.json | Version/content integrity and mixed-install refusal | No, it is required installed metadata. |
| .pstack/setup-codex.json / setup-claude-code.json | Actual installed fork commit, upstream source, last-write hashes and merge baseline | Keep while using setup; deleting loses ownership evidence and requires explicit adoption. Secret-free configuration only. |
| .codex/agents / .claude/agents | Host-native project persona definitions | Deleting removes that host's registered names. Setup can recreate missing managed files. |
| AGENTS.md / CLAUDE.md bounded block and pstack-role rows | Native persistent instructions and original per-role model choices | Other user content is never removed. Removing the block disables project overrides; rerun setup for a managed installation. |
| .pstack/runtime/poteto-tools | Project-private frozen-lock dependency installation and Bun cache | Yes, disposable; next invocation reinstalls. Ignore in git. |
| .pstack/.setup.lock | Serialize simultaneous setup writes | Yes when no setup is running; ignore in git. |
| .pstack/automations/benny | Committed operational files copied by optional reviewed setup | Delete only when retiring Benny; routine prompts require them. |
| .pstack/benny / external credentials | User-owned configuration/routing/feature map and existing credential mechanism | Required for configured Benny runs, never source-managed or overwritten. |
| .pstack/benny-state.sqlite* | Persistent external-write intents, dedup and restart recovery | Do not delete during operation; losing it loses dedup evidence. Keep out of git and carry across runner restarts. |
| PSTACK_TRANSCRIPTS_DIR | Optional explicitly scoped active-project export for worktree audit | Optional; without it LAST_CHAT is unavailable. No automatic cross-project scan. |

No additional budget/tuning settings were added for Benny. The original poll and workflow budgets remain; scheduler rounding and actual runner conditions are reported. No previous package, global user configuration, main branch or old PR is changed.

## Size and change attribution

The source main contains 936 files / 6,495,568 bytes; its pstack subtree is 169 files / 3,485,346 bytes. Removing other plugins and marketplace files is the user's scope change, not an optimization of pstack. The adapted pstack is slightly larger than its original subtree because of host instructions, integrity metadata, migration evidence, tests and Codex invocation policy files. Shared agents, Benny, guide/images and license have one source instance.

The earlier feat/codex-integration tree is 560 files / 8,782,600 bytes, including 267 files / 824,323 bytes under its generated skills tree (55 skill directories in that actual ref). Differences against it include changing source lineage and not importing its CLI/viewer/generator, so they must not be reported as pure deduplication savings. That branch and its published package are preserved. Exact final measurements are in size-comparison.json.

The large main diff is dominated by 765 explicitly requested non-pstack removals plus the rewritten root README (766 changed files in that group). Host changes and moved public files are counted separately with rename detection disabled in size-comparison.json; normal Git rename detection presents moved agents/assets/guide files as moves.
