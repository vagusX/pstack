# benny automation intent

## what i want to automate

i want two host automations that work together in one slack issue channel.

### automation 1: triage issue reports

- trigger: when someone posts a new top-level report in my configured source slack channel, i want this automation to start on that report and keep its original thread coordinates.
- behavior: i want it to read the thread and attachments, classify the report as a bug or performance issue, feature request, question or feedback, or reroute, and trace the likely owning layer before routing.
- tracker: i want it to search my configured tracker for duplicates, update a confident duplicate, and create a ticket only for a clear net-new bug.
- tools: i want slack thread read and reply access, my configured tracker integration, and my optional routing map.
- outcome: i want exactly one reply in the source thread with a short verdict and `[benny:bug]`, `[benny:performance]`, or `[benny:other]`. a bug or performance marker may include the tracker url.
- boundary: i never want this automation to post a root message in the source channel.

### automation 2: reproduce and fix confirmed bugs

- trigger: i want this automation to start from the same new top-level report, or another supported trigger chosen during setup, then wait for the trusted triage marker in the original thread.
- gates: i want it to stop when someone clearly owns the fix. if an existing pull request or merged commit may fix the report, i want verification instead of a competing change.
- behavior: i want it to use my configured control adapter and feature map, reproduce the exact symptom twice through the real ui, and capture screenshots, video, and a read-only state cross-check.
- fix: i want it to verify existing pull requests without authoring over them. after a confirmed repro, it may attempt one bounded root-cause fix, use tdd when the test is cheap, smoke the blast radius, and open a draft pull request only when before-and-after proof passes.
- tools: i want slack thread read and reply access, repository and history access, draft pull request creation, my configured tracker, and my control adapter.
- outcome: i want evidence and a verified result in the source or optional operations threads, plus an optional draft pull request. updates should be concise.
- boundary: i never want this automation to post a root message in the source channel.

### shared rules

- i want the source channel and root thread coordinates to stay immutable for the whole run.
- i treat utility and debug bots as evidence, not delegation or fix ownership.
- i allow subagents to help, but they cannot post to slack or receive slack credentials.
- i want this entire pack committed at `.pstack/automations/benny/` in the target repository. its `INSTRUCTIONS.md` files are direct automation instructions, not registered plugin skills.
- i want project-installed pstack skills for shared dependencies such as `how`, `why`, `tdd`, `unslop`, and the required principle skills.
- i want each live automation prompt to read its committed operational file directly. i do not want plugin cache paths, copied excerpts, or slash-skill discovery.
- i keep user-owned configuration, feature maps, routing maps, and secrets outside `.pstack/automations/benny/` so pack refreshes cannot overwrite them.
- i want both automations to fail closed when channel coordinates, tracker access, the control adapter, or the feature map are missing or uncertain.
- i want draft pull requests only. do not merge or deploy.

### my configuration

- source slack channel: `<channel>`
- optional operations channel: `<channel or none>`
- repository and default branch: `<repo>`, `<branch>`
- tracker: `<type, team, project, labels, intake status>`
- routing map: `<path or none>`
- triage identity: `<slack identity>`
- control skill: `<configured skill or adapter>`
- feature map: `<committed same-repo path outside the copied pack, or behavior to paraphrase>`
- models: `<triage, reproduce, code, media review>`
- status emoji strings: `<seen, reproducing, reproduced, blocked, fixing, failed, pull request opened>`
- budgets: `<polling, verdict wait, follow-up, repro, rejection, fix>`
- optional bot token capability: `<none, file download, or editable operations status>`

start from [`configuration.example.yaml`](templates/configuration.example.yaml) and [`feature-map.example.md`](skills/reproduce-and-fix-issues/references/feature-map.example.md). copy and fill them outside this pack, for example under `.pstack/benny/`. keep secret values in a secret manager or environment.

## for the agent

the human enters setup by pointing the host agent at this file. do not look for or invoke a discovered benny slash skill.

1. ask which repository will run the automations.
2. treat the directory containing this `FOR_AGENTS.md` as the source pack.
3. merge the entire source pack into `<target-repository>/.pstack/automations/benny/`.
4. preserve every destination-only file. never delete unrelated files or overwrite user-owned configuration, feature maps, or routing maps.
5. when an existing destination file at a source-managed path differs, review the diff and merge without discarding local edits. if ownership is ambiguous, stop and ask before replacing it.
6. verify that the copied `FOR_AGENTS.md` and `skills/setup-benny/INSTRUCTIONS.md` exist in the target repository.
7. read and follow `.pstack/automations/benny/skills/setup-benny/INSTRUCTIONS.md` directly from the target repository.

Install pstack dependencies in the target project with `npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/setup-pstack-shared-content --skill "*" --agent <codex|claude-code> -y`. Read the installed setup-pstack and use its preview/write/merge contract. Do not enable a plugin through Cursor settings.

Verify from a fresh session rooted in the target repository that how, why, tdd, unslop and Benny's required principle skills resolve in project scope. Global or current-session visibility is not proof. Operational files are INSTRUCTIONS.md, so they are never slash-skill entries.

Commit the project skill lockfile, host instructions, `.pstack/automations/benny/` and referenced secret-free configuration before activation. Config, routing and feature maps live under `.pstack/benny/`, outside the source-managed pack; credentials come from existing connectors, secret managers or the environment. Keep `.pstack/benny-state.sqlite` outside the pack and persistent across runner restarts.

Read the copied setup-benny INSTRUCTIONS.md for the actual host scheduler preflight and polling fallback. No task, Slack post, tracker mutation or draft PR is authorized merely by installing/copying this pack. Real tests require an explicit dedicated channel/project/environment and approval. Keep automation disabled when connectors, trigger access, durable state or app control are absent.
