# Set up pstack

In this page you install the plugin, pick which models pstack uses, and run your first task. Setup is one command plus a short conversation.

## Install the plugin

In a terminal with Node 22.20+ installed, run the pinned skills CLI:

Install all 54 original skills plus shared support with `npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/setup-pstack-shared-content --skill "*" --agent codex claude-code -y`. Use `--copy` for copies, the default for links between host directories, and `--global` for global content. Run setup from each calling project.

## Pick your models

Run:

```text
/setup-pstack
```

[`/setup-pstack`](../../../setup-pstack/SKILL.md) detects the models you have access to, asks for a reasoning budget, shows you each role (code delegates, judgment, the review panels), and asks what you want. Answer the questions. It writes the pstack-managed block in project `AGENTS.md` or `CLAUDE.md`, a small rule every pstack skill reads.

Defaults inherit the current host model. Setup retains the original roles and budget choices, with effort configured separately only where supported. Panels keep their original seat counts and independent angles. Different vendors are not assumed available; disclose same-model evaluation.

You only override what you care about. A role with no line in the rule keeps the skill's default. To restore a default, delete that role's line. A rerun of `/setup-pstack` keeps any role whose model differs from the default. To restore inheritance, remove only that role's pstack-role row. Never delete AGENTS.md or CLAUDE.md to reset models; they may contain unrelated project instructions.

You might be wondering what happens if you use Auto. Set a role to `inherit-parent` or `auto` and pstack omits the subagent `model` field, so the subagent inherits your parent chat model. Both values mean the same thing, and neither is a model slug. For a panel role the value is a list, and one subagent runs per entry, so the list length sets the panel size. Setup also configures `swarm workers`, the default model for every `/swarm` worker unless a race names a model for each arm.

## Accept the verification offer, or don't

At the end of setup, `/setup-pstack` looks for a way to prove app behavior in your project, either a `verify-*` skill or an existing harness. If it finds neither, it offers once to generate one with [`/create-verification-skill`](../../../create-verification-skill/SKILL.md).

Say yes and it writes a project-local verification skill in `.agents/skills/verify-<app>/` for Codex or `.claude/skills/verify-<app>/` for Claude Code, a project-local skill that teaches agents to drive your app the way a user does. It proves the skill works once before handing it over. Say no and setup moves on. You can run `/create-verification-skill` yourself any time. [Verify and ship](06-verify-and-ship.md#create-a-project-verification-skill) covers it in depth.

If you're new to pstack, say yes. An agent that can check its own work keeps going until the check passes. An agent that can't hands every result back to you to check by hand. Of everything in this guide, the verification skill pays off the most.

After setup, start a new trusted project chat and actually invoke both named agents. Update skills, rerun setup, then verify in another new session. Agent files do not update just because skills changed. Pin the install to its fork commit; when the lockfile does not retain it, the helper requires --source-commit with the verified installed SHA.

## Keep the cost in check

pstack spends extra tokens on subagents and review panels. That's the price of the rigor. To spend fewer:

- Rerun `/setup-pstack` and pick a smaller reasoning budget or cheaper models. A strong model in the main chat with cheaper, faster models in the code roles is a good split.
- Set a role to `auto` or `inherit-parent` so it runs on the chat's own model.
- Shorten a panel list. Each entry runs one subagent.
- Save `/poteto-mode` for work that needs rigor. A small, obvious edit doesn't.

## Run your first task

Pick something real but small, and describe it the way you'd describe it to a colleague:

```text
/poteto-mode add a --json flag to this command. text output stays byte-identical. verify both.
```

Watch the todo list. Its first items are the matched playbook's steps copied in, the Feature playbook for this prompt. If `/poteto-mode` skips a step, the step stays in the list with `skip: <reason>`, so you can see what it chose not to do.

Start each task by explicitly invoking `poteto-mode` (`$poteto-mode` in Codex, `/poteto-mode` in Claude Code), then state the goal and finish condition. The project instructions load host behavior on new sessions. Do not rely on a Custom Mode shortcut or assume skill attachment persists across compaction.

Next: [Route work through `/poteto-mode`](02-poteto-mode.md).
