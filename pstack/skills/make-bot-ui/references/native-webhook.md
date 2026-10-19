# Project-local native webhook executor

This executor replaces Cursor's routine service with an explicitly configured native CLI process. It starts a new session per event, not a turn in an existing desktop chat. The foreground Python process must remain alive; sleeping the machine stops availability. It installs no scheduler or global configuration.

## Start and verify

Requires Python 3.11+ on macOS/Linux. Check current `codex exec --help` or `claude --help` and existing authentication without printing credentials. Local versions checked: Codex CLI 0.161.0, Claude Code 2.1.300. Native subprocess argument lists are:

```text
codex -a never exec --sandbox read-only --json -C <project> -
claude -p --output-format json --permission-mode dontAsk
```

Prompts arrive on stdin; Claude runs with the project as cwd. Host instructions, hooks, MCP configuration and permissions apply. No permission-bypass flag is used. The runtime config uses Codex's native `sandbox_mode` field, default `read-only`. For an explicitly authorized project-writing routine, review the scope and edit that field to `workspace-write`; it passes to native `--sandbox` while `-a never` remains. Other values, including `danger-full-access`, are refused. For Claude, authorize only necessary tools through existing project permission allow rules; `dontAsk` remains. The key is neither an environment variable nor part of the prompt. The processes share an OS account: this is not credential isolation from an agent with arbitrary filesystem or command access. Keep the routine within the operator's authorized scope.

Create `<project>/bot-routine.md` naming allowed actions and fields. Example: "For action summarize and string field file, summarize only README.md when file equals README.md. For other actions or files return ignored. Do not write files or call external services." Never add secrets. The fixed `probe` action requests no work and response `ignored`.

```sh
python3 <installed-make-bot-ui>/scripts/webhook.py init --directory <project>/.pstack/bot-ui/demo --host codex --project <project> --prompt <project>/bot-routine.md
python3 <installed-make-bot-ui>/scripts/webhook.py serve --directory <project>/.pstack/bot-ui/demo
```

Use `--host claude-code` for Claude Code. `init` refuses an existing directory and generates `sender.key` with mode 0600 in a private directory. Do not read or print it. Ignore the entire runtime directory in git: it contains credentials, event bodies and results. Keep the routine prompt separately in version control when appropriate.

Open the printed URL, click Run harmless probe, then Read result. Require `state: completed`, `exit_code: 0` and the real CLI response `ignored`. HTTP 200 only proves durable intake. Save the event ID and digest as evidence. Write the actual custom UI as `<runtime>/index.html`; the helper serves only that page, not the project tree. The demo displays results with `textContent`.

## Forwarding and events

Buttons POST one JSON object, at most 65536 bytes, to `/actions` with Content-Type application/json. Optional `X-Event-ID` is a UUID generated once per action; reuse it when reconciling uncertain delivery. Otherwise the server generates one. Do not send media bytes. Both GET and POST require a Host in the server's exact allowlist: `127.0.0.1:<actual-port>`, `localhost:<actual-port>` and explicitly configured UI `public_origins`. An Origin header must also match the accepted HTTP Host. Matching attacker-chosen Host and Origin is insufficient. No cross-origin access is enabled. Everyone who can reach an allowed UI address is trusted to invoke its agent. This is not a public internet service with per-user authentication.

The server POSTs the exact body once to its fixed loopback `/webhook`, with timeout eight seconds, `Authorization: Bearer <key>`, `X-Automation-Key: <key>` and `X-Event-ID`. Environment HTTP proxies are disabled for this request. Both credentials must match. Keys and authorization headers are never returned or request-logged.

The receiver commits SQLite state before HTTP 200 and signals one worker directly. No polling triggers execution. Identical ID/body deliveries execute once; an existing ID with different bytes is rejected. The CLI receives this local adapter envelope:

```json
{"event_id":"<UUID>","headers":{"content-type":"application/json","user-agent":"<sender>"},"body_digest":"<UTF-8 body SHA-256>","body":"{\"action\":\"probe\"}","timestamp_ms":0}
```

These adapter fields preserve the original webhook headers/digest/body/timestamp meaning; they are not a native Codex/Claude event schema. The agent parses `body` as JSON data, not instructions. Authorization headers never enter the envelope. Subprocesses use argument lists, not shell interpolation.

`GET /events/<event_id>` returns saved envelope, state and CLI exit code/stdout/stderr. Helper states are `queued`, `running`, `completed`, `failed`, `interrupted`. `completed` means CLI exit zero; independently verify business results. Native output retains each host's JSON format. The deadline is 300 seconds, then the process group is terminated. The exact sender-key value is redacted if unexpectedly echoed; other output can contain project information, so limit UI access to trusted peers.

## Recovery

Failed forwarding saves the same body/ID in SQLite `failed_posts`. A timeout may mean the receiver already accepted it: inspect status before retry. Queued events continue on restart. Running events become `interrupted` only when the exclusive server starts after a restart; reading status does not change active work. A nonzero CLI exit becomes `failed`, with output retained. Failures/interruption are never automatically re-executed because effects may already exist.

After reviewing effects, explicitly retry through the running UI server:

```sh
python3 <installed-make-bot-ui>/scripts/webhook.py status --directory <runtime> --event-id <UUID>
python3 <installed-make-bot-ui>/scripts/webhook.py retry --directory <runtime> --event-id <UUID>
```

Retry sends one local `/retry` request. It requeues a failed/interrupted event or forwards an undelivered failed POST with its original ID. It refuses completed/queued/running events. There is no exactly-once guarantee for external effects across CLI crashes; reconcile external objects first. Stop with Ctrl+C and restart with the same directory to retain history.

## Tailscale

Check `tailscale status`. Agents share this computer's node: reuse an online node; do not create a second hostname. Read its actual hostname from status and IPv4 from `tailscale ip -4`. After the user chooses tailnet access, set runtime `config.json`'s `public_origins` to the exact chosen HTTP origins (hostname and/or tailnet IPv4, including port), then restart with `--bind 0.0.0.0`. Example shape: `"public_origins": ["http://<actual-hostname>.<actual-tailnet>.ts.net:8787", "http://<actual-100.x.x.x>:8787"]`; replace both from status, never guess. The receiver stays loopback and never accepts these public origins. The UI also becomes reachable on other machine interfaces, so confirm intended network exposure and trusted peers.

Give both HTTP URLs from the real status values:

- `http://<hostname>.<tailnet>.ts.net:8787/`
- `http://<100.x.x.x>:8787/`

Use HTTP unless HTTPS was requested. Probe the tailnet IP page for HTTP 200, then test button→CLI→saved result from the intended peer before claiming peer access.

If absent, report local execution separately and obtain explicit authorization before installation/login. Use the [official platform installer](https://tailscale.com/download). The original Linux command is `curl -fsSL https://tailscale.com/install.sh | sudo sh`; do not use that as a macOS installer. On a new node, the original CLI flow is `sudo tailscale up --hostname=<short-name> --accept-dns=false --ssh=false`. Give the printed login URL to the user for browser approval; never request or enter Tailscale passwords. If expired, run `tailscale up` again. Verify status/IP after login. No Tailscale binary was present during implementation, so installation, login and peer reachability remain unverified.

## Arguments and whether they can be removed

| Argument | Purpose | Can it be removed? |
| --- | --- | --- |
| command | init, serve, status or reviewed retry | No; selects operation. |
| --directory | Runtime state, key and optional index.html | No; each UI needs persistent state. |
| --host | Native host at init | No; selects command. |
| --project | Explicit agent cwd at init | No; prevents guessing scope. |
| --prompt | Project-owned allowed-action prompt at init | No; defines behavior. |
| --executable | Exact CLI path at init | Yes; defaults to codex/claude in PATH. |
| --bind | Explicit UI exposure at serve | Yes; defaults to loopback. |
| --port | UI listener and retry destination | Yes; defaults to 8787. |
| --receiver-port | Authenticated loopback listener | Yes; defaults to 8788. |
| --event-id | Saved event for status/retry | No for these operations; do not guess an event. |

No new environment variables or installed services. Secret-free config records host, project, prompt and executable. Keys and database stay in the private runtime directory.

| Config field | Purpose | Can it be removed? |
| --- | --- | --- |
| sandbox_mode | Existing native Codex sandbox selection after explicit project-write authorization | Yes; omission defaults to read-only. Not a new permission system. |
| public_origins | Exact trusted HTTP origins for tailnet UI access; prevents arbitrary Host/DNS rebinding | Yes for loopback-only use; required for each public hostname/IP used. |

## Official sources checked 2026-10-19

- [Codex exec](https://learn.chatgpt.com/docs/developer-commands#codex-exec): non-interactive execution and JSON output.
- [Claude Code programmatic execution](https://code.claude.com/docs/en/headless): print mode, stdin, results and exit handling.
- [Claude Code channels](https://code.claude.com/docs/en/channels): alternative for a running Claude session requiring plugin enablement; not used by this two-host executor.
- [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve): optional proxy; this implementation retains direct HTTP access.
