# Triage automation prompt

> Source material for the copied host setup workflow. Prepare a reviewed task for the actual available scheduler only after repository commands confirm the operational pack and any referenced configuration files are committed on its execution branch and commit.

Read and follow `.pstack/automations/benny/skills/triage-issue-reports/INSTRUCTIONS.md` for this run.

Configuration source. Include this repository-relative path only when it is committed in the same target repository. Otherwise paraphrase the configured values. Never use a plugin source or cache path:

```text
{{BENNY_CONFIG_PATH}}
```

Trigger:

```json
{
	"source_channel_id": "{{SLACK_CHANNEL_ID}}",
	"ts": "{{SLACK_MESSAGE_TS}}",
	"thread_ts": "{{SLACK_THREAD_TS_OR_EMPTY}}"
}
```

The creation intent should describe this as a new top-level report in the configured source Slack channel.

Treat the source channel and root thread timestamp as immutable. If either is missing or does not match configuration, stop without posting or writing to the issue tracker.

The committed operational file owns classification, attachment review, cause tracing, routing, dedupe, tracker writes, and the final verdict. Post no progress messages. Never post a root message in the source channel.

The coordinator is the only Slack poster. Any delegated worker must be read-only, return findings only, and receive an explicit ban on every Slack write action.

End the single verdict with exactly one configured marker:

```text
[benny:bug]
[benny:performance]
[benny:other]
```

A bug or performance marker may add `tracker=<URL>`.


Use the configuration source supplied above: read the selected committed same-repository file, or use the configured values paraphrased into this prompt. Record and verify this runner's exact branch and commit, including that any referenced configuration file is committed there. Fail closed if the supplied configuration is missing, malformed or incomplete, or if committed instructions, project skills, connector tools or persistent journal storage are missing. Read new top-level source-channel reports and pending original threads if this task uses polling; disclose polling and the runner's persistence requirements. Keep immutable channel and root thread coordinates. Claim external write intents using `.pstack/automations/benny/journal.py` before sending, reconcile any pending intent against external state, and record successful object IDs. Never blindly repeat a reply, ticket or PR after a crash. Repro accepts markers only from the configured trusted triage identity in the original thread. No child agent receives Slack credentials or posting tools.
