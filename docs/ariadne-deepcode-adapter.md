# Ariadne Deep Code Adapter Profile

Date: 2026-07-11

Deep Code is the current active DeepSeek transport profile for EMR4. It is an
interactive CLI, not a Codex subagent bridge and not a headless completion
service. The harness invokes its documented prompt entry point:

```powershell
deepcode -p "<bounded packet>"
```

Deep Code requires a real interactive terminal. A non-TTY shell refusal means
this execution surface cannot use the adapter; it does not mean DeepSeek or the
configured API key is unavailable. The interactive operator must review any
Deep Code permission prompt; the harness still requires a durable artifact and
does not treat a local tool approval as sprint or integration authority.

The active profile is `deepseek-v4-flash` with `high` reasoning. The documented
model choices are `deepseek-v4-flash` and `deepseek-v4-pro`; Deep Code exposes
only `high` and `max` reasoning. `deepseek-v4-pro` and `max` are exceptional
choices that require the conductor to record a leverage and cost reason.

Deep Code session controls are `/new`, `/resume`, and `/model`. A new worker
packet starts a fresh session unless a valid context-health receipt explicitly
permits resumption. Deep Code may ask for tool permission. An interaction
approval is local tool permission only: it never grants Ariadne authority to
change scope, integrate, commit, push, or bypass verifier requirements.

Because this adapter is TUI-based, a submitted review, patch, test transcript,
or other durable packet artifact is required before the orchestrator accepts a
result. The harness records `deepcode_cli_observation` for reachability; it
does not infer availability from unrelated Codex or shell bridges.

The user-level API configuration remains outside the repository in
`~/.deepcode/settings.json`; do not commit secrets or project-specific
overrides. Project-level Deep Code settings override user settings, so a worker
must disclose any project-level `.deepcode/settings.json` in its packet receipt.
