---
name: swarm
description: "Fan out N parallel workers, drain them, and return one report. Use for /swarm, 'swarm this', or parallel coverage, races, gauntlets, and exploration."
disable-model-invocation: true
---

Before executing, read the installed **pstack-support** `references/host-instructions.md` and run its preflight with this skill's actual location. If support is missing, stop and show `npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/pstack-host-adaptation --skill pstack-support --agent codex claude-code`. Read sibling dependencies from the host's active skill locations, with project copies taking precedence.


# Swarm

Fan out N parallel native workers, using isolated execution locations. They may cover separate slices, race the same brief, or mix both. The parent waits, aggregates, and returns one report.

## Start

Open a todolist with one entry per phase before launching anything.

1. Frame
2. Fan out
3. Aggregate
4. Report

## Phase A: Frame

1. State the done predicate and the artifact or report the swarm must return.
2. Choose the shape. Partition into slices, race N workers on identical briefs, or mix both. For a race or mixed shape, declare `first pass`, `rank all`, or `best-of` before spawning.
3. Set N from the user or derive it from the shape. N is total workers, not the host concurrency limit.
4. Pick the worker model from the `swarm workers` line in the pstack-managed model block in `AGENTS.md` or `CLAUDE.md`. If the rule or that line is missing, use `inherit-parent`. For `auto` or `inherit-parent`, omit `model` so the workers run on the parent model. If the native delegation tool rejects a slug, use the default and say so. If it rejects the default, use the closest valid slug of the same family from its error message. For a model race, name each arm's model up front. Pick each subagent's reasoning level and fast or standard speed for the job, per the Subagents section of the **poteto-mode** skill.
5. Give each worker its own writable output when it writes. When workers verify or measure commits, each brief names the exact SHAs. A measurement brief also names the method (sample count, what one sample is, order). The worker records both in its result.

## Phase B: Fan out

Spawn all N workers through the current host's native delegation interface described in **pstack-support**. First inspect available capabilities. Prefer a separate execution environment when the host actually supplies one. Otherwise use separate local worktrees, state that execution is local, and check required tools and credentials there. A worktree does not provide a VM, separate network, or cloud persistence.

Each worker must check out the exact branch and SHA specified in its brief. Do not pass a host-specific cloud branch parameter to a local agent.

Every brief stands alone. Include the goal, scope, exact slice or race arm, how to verify, and what to report. Reports use `PASS`, `ISSUES`, or `BLOCKED` with evidence. A worker that can prove a defect reports `ISSUES` and lists every issue it can prove, not only the first.

If a worker drops out, proceed with N-1 and note it.

## Phase C: Aggregate

Read the terminal results. Drop a result that does not record the SHAs and method its brief names, and respawn that worker once. After a second miss, record a gap. A gap does not count as a pass. For coverage, every required slice needs a result. For a race, apply the selection rule declared up front. Use first pass, rank all, or best-of. Do not paste raw worker dumps.

Keep a compact result table, one-line evidenced issues, and explicit gaps or dropouts.

## Phase D: Report

Return one consolidated in-chat report with the table, issue one-liners, gaps or dropouts, and the race rule when used.
