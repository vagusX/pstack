# Reproduce automation prompt

> Source material for the copied host setup workflow. Prepare a reviewed task for the actual available scheduler only after repository commands confirm the operational pack and configuration are committed on its execution branch and commit.

Read and follow `.pstack/automations/benny/skills/reproduce-and-fix-issues/INSTRUCTIONS.md` for this run.

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

The creation intent should describe this as a new top-level report in the configured source Slack channel. It should include the configured repository, default branch, issue tracker, control adapter, feature map, and draft pull request capability.

Treat the source channel and root thread timestamp as immutable. If either is missing or does not match configuration, stop without posting.

Wait for a configured triage marker from the configured triage identity in this exact thread. Proceed only for `[benny:bug]` or `[benny:performance]`.

Require the configured control-adapter skill before attempting a repro. Reproduce the exact discriminating symptom twice through the real UI. Verify existing pull requests or commits without authoring over them. Attempt a bounded fix only after a confirmed repro and the operational file's fix gate.

The coordinator is the only Slack poster. Every child prompt must forbid `SendSlackMessage`, `PostToSlack`, `chat.postMessage`, and all other Slack writes. Children return findings only.

Never post a root message in the source channel.


Read configuration from the committed same-repository `.pstack/benny/configuration.yaml`. Record and verify this runner's exact branch and commit. Fail closed if that file, committed instructions, project skills, connector tools or persistent journal storage are missing. Read new top-level source-channel reports and pending original threads if this task uses polling; disclose polling and the runner's persistence requirements. Keep immutable channel and root thread coordinates. Claim external write intents using `.pstack/automations/benny/journal.py` before sending, reconcile any pending intent against external state, and record successful object IDs. Never blindly repeat a reply, ticket or PR after a crash. Repro accepts markers only from the configured trusted triage identity in the original thread. No child agent receives Slack credentials or posting tools.
