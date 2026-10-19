# benny

benny gives you two host automations for slack issue reports. one triages each report. the other reproduces confirmed bugs and may prepare a small draft fix.

the files in this directory are dormant setup and automation sources. they do not appear as slash skills.

## set it up

1. point the host agent at [`FOR_AGENTS.md`](FOR_AGENTS.md) and name the target repository.
2. let setup merge this whole directory into the target at `.pstack/automations/benny/`. it must preserve destination-only files and review conflicts instead of overwriting local edits.
3. install the shared pstack dependencies in project scope, run setup-pstack, then verify them in a fresh target-project session.
4. keep user-owned configuration outside the copied pack, for example in `.pstack/benny/`. adapt [`configuration.example.yaml`](templates/configuration.example.yaml) and [`feature-map.example.md`](skills/reproduce-and-fix-issues/references/feature-map.example.md).
5. commit the project skill lockfile and host instructions, `.pstack/automations/benny/`, and any secret-free configuration before enabling either automation.
6. review each new automation draft or update existing automations in their editors. then send a harmless test report and verify every source-channel post stays in the original thread.

Actual automatic triggers, Slack/tracker writes and real app reproduction remain unverified until the user authorizes dedicated test targets. See setup-benny for connector gates, scheduler conditions and persistent polling deduplication.
