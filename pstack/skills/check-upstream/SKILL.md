---
name: check-upstream
description: Check a pstack source checkout for upstream updates and summarize missing commits and file changes. Use when checking whether cursor/plugins has changed or preparing an upstream update PR.
---

# Check upstream

Run this from the pstack source checkout being maintained, not from the installed plugin directory. The checkout uses `origin` for the user's repository, `upstream` for `https://github.com/cursor/plugins.git`, and `main` as the synchronization branch. Inspect `git remote -v` first. If that relationship is absent or points elsewhere, report it before changing configuration.

## Check for updates

Run the bundled [scripts/check.py](scripts/check.py) with Python 3, using its installed absolute path while keeping the source checkout as the working directory. It fetches upstream `main`, then compares the local `main` commit with the fetched commit. It updates remote-tracking metadata only; it does not change checked-out files, local branches, tracking configuration, or remote repositories.

Report the two commit IDs, the ahead/behind counts, and the missing commit subjects. Summarize `pstack/` changes separately from the rest of the repository, including any generated `harness/pstack/` changes. A zero upstream-only count means there are no new upstream commits to incorporate, even if local commits make the tips different. A failed fetch or missing history is a failed check, not evidence that the repository is current.

Checking for updates ends with that report. It does not authorize merging, pushing, or opening a PR.

## Prepare an update PR when requested

Read the current working-tree status and repository instructions. Preserve unrelated edits. If no upstream-only commits exist, report that there is nothing to import and do not open an empty PR.

Fetch `origin/main` and create a new `codex/` branch from it. Merge the exact upstream commit from the check, preserving local changes through an ordinary merge. If histories have no common ancestor, stop and explain; do not force unrelated histories together. Resolve conflicts by reading both implementations, particularly host-specific skill changes. Do not replace adapted skills wholesale with upstream versions.

Inspect the complete diff against `origin/main`. Follow the checkout's documented validation commands; in the upstream layout these include `node scripts/validate-plugins.mjs` and `node scripts/generate-pstack-harness-trees.mjs --check`. When skill sources change, use the existing generator and commit its output. Run affected behavior checks as needed. Record any checks that could not run.

Push the new branch to `origin` and open a PR explicitly targeting the user's repository and `main`. With GitHub CLI, supply `--repo`, `--base main`, and `--head`, and pass the description using `--body-file`. Include the upstream commit, the changes being imported, conflict decisions, and actual validation results. Read back the PR URL, base/head, and head commit. Leave merging to the user unless they requested it.
