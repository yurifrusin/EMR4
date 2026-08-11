# Ariadne agent error and correction register — revision 206

Date: 2026-08-11

Revision 206 adds AER-0240 and brings the register to 240 bounded incidents.

## AER-0240 — recovery state used unvalidated preflight vocabulary

The first deterministic preflight for AES-C1 Sol recovery refused integration
because the new state used an unapproved continuation-event label, supplied a
Codex observation method for the DeepSeek adapter, and omitted the configured
DeepSeek worker-slot inventory. An imprecise positional correction then swapped
the Codex and DeepSeek methods, so the next preflight also refused. No source
was adopted, no external call occurred, and both worktrees remained unchanged.

The correction read the active orchestrator and transport settings directly,
used approved `pre_integration`, keyed `codex_session_observation` and
`deepseek_claude_cli_observation` by their exact adapter IDs, and included the
managed DeepSeek slot with empty active/stale lists. The next receipt passed
with all five rehydration sources and no reasons before integration.

The prevention control is mechanical: new state templates are populated from
the active settings before their first preflight, and adapter-method edits are
keyed by adapter ID rather than positional text replacement.
