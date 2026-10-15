---
name: Make Bot UI
description: Build a bot webhook UI with server-held credentials and Tailscale exposure. The original Cursor routine integration is not yet adapted to Codex or Claude Code; use to identify required webhook capabilities before proceeding.
disable-model-invocation: true
---

# How to make a bot UI

**Codex and Claude Code status: not yet adapted.** The original workflow requires Cursor's `update_state` webhook routine, sender-key secret request, routine panel and wake-event contract. Neither a native agent spawn nor a scheduled prompt supplies those interfaces. Stop before routine creation, credential collection or probing an external endpoint. Report the missing interfaces. Do not call a nonexistent tool or substitute a guessed webhook.

The complete [original webhook workflow](references/cursor-webhook.md) is retained as a reference, including its server proxy, sender-key handling, Tailscale steps, one-try eight-second POST and wake-body parsing. It is historical source material, not executable instructions in these hosts.

A future adaptation requires an explicitly configured webhook executor with a documented endpoint and authenticated event schema, a credential mechanism that keeps the key out of chat/browser/logs, server-side forwarding, actual agent execution access and authorized harmless test payload. The host must provide or the user must choose that executor before implementation. Keep the original UI behavior and bounded forwarding policy. Do not invent a local server and claim it provides the original routine service.
