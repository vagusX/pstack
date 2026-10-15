# Shared files inside setup-pstack

This revision is based on the existing host-adaptation branch (PR #3), not main. It removes the added pstack-support entry and places its shared files inside the original setup-pstack skill. The published catalog returns from 55 to the original 54 entries.

| Before | After |
| --- | --- |
| setup-pstack plus a separately installed pstack-support | setup-pstack carries its own helper, host instructions, agent personas, Benny, guide, assets and license |
| Workflows locate pstack-support for preflight | Workflows read setup-pstack/references/host-instructions.md and call setup-pstack/scripts/setup.py --check |
| how + pstack-support for a read-only investigation | how + setup-pstack; preflight writes no project configuration |
| setup-pstack + Poteto Mode + pstack-support for agent registration | setup-pstack + Poteto Mode; actual setup still needs an explicit configuration run |
| Integrity manifest schema 1 with support_files | Schema 2 identifies setup-pstack as carrier and hashes shared_files once; the original setup entry remains in the 54-skill catalog |
| Receipt stores support_manifest_sha256 | New writes store setup_manifest_sha256; existing receipt names, source commits, file hashes and merge baselines are retained for ownership checks during upgrade |

Shared source files still have one copy. This is an entry/layout simplification, not a claim of large disk savings. Agent behavior, model choices, permission boundaries, project state paths and dormant automation rules remain as described in the parent migration. The same parent limitations on real named-agent execution, Make Bot UI and external Benny tests remain.

## Install and use

For a minimal investigation install:

```sh
npx skills@1.7.2 add https://github.com/vagusX/pstack/tree/codex/setup-pstack-shared-content --skill how setup-pstack --agent codex claude-code -y
```

Read the installed setup-pstack host instructions and run its helper with `--check --require how --skill-location <actual-how-directory>`. This only validates the installed files and active scope; it does not register agents, change AGENTS.md / CLAUDE.md or enable Benny. Invoke setup-pstack when project configuration is wanted. Agent registration also requires Poteto Mode.

## Upgrade from the separate support entry

Update the selected skills and setup-pstack from the same new commit. Review local edits in the retired support installation, then remove that old entry from the updated host/scope:

```sh
npx skills@1.7.2 remove pstack-support --agent codex claude-code -y
```

Add `--global` for a global installation. The installer does not infer that a different skill name has been retired. The helper does not read or fall back to pstack-support. Keep the existing `.pstack/setup-*.json` files and project agents; deleting them loses ownership evidence. Re-run setup using the exact new installation commit.

The migration test exercises both hosts in one project with real skills CLI installs. It adopts user model/effort/permission changes using the old helper, updates the installation, removes the old entry, deletes source copies, then runs the new helper. Source commits and last-written hashes remain recorded, user model/permission/role choices survive, and user-owned config plus destination-only Benny files survive. Installed skill hashes remain unchanged.

Both hosts share one project Benny pack. When one host refreshes it, the second host recognizes the latest matching other-host receipt instead of treating the managed update as an unreviewed local edit. Actual local changes still require a reviewed merge.

## Validation for this revision

- 16 Python behavior tests pass, including both-host shared-pack refresh and existing model/permission/ownership cases.
- 19 real skills CLI scenarios pass: the 16 project/global, full/subset, copy/link combinations; shared dual-host links; how + setup-pstack without configuration; and old-layout upgrade for both hosts.
- Full-depth discovery finds 54 entries, no pstack-support and no nested Benny entries.
- Source copies are removed before installed preflight/setup runs; skill content hashes do not change.
- Both preserved Bun entry points run from the installed layout, including repeated cache use and a lock-file revision.
- setup-pstack passes the skill validator and local Markdown links resolve.

The parent 68 Bun tests and strict TypeScript check are unchanged implementation evidence; this revision does not edit those tools. Native agent invocation and external automation are not newly verified by these layout tests.

Remote verification also passes for immutable implementation commit `a1c439e509e80fe70d50610120cbc28bde0437c9`: 54 entries, no retired support entry, both host helpers read that exact SHA from the installer lock and merge Benny, and installed content hashes are unchanged. See [remote install evidence](setup-carrier-remote-install.json). Subsequent commits only record validation evidence.
