# Deep Code S4d Verifier Packet V3

Date: 2026-07-11

## Role And Output

You are the Ariadne verifier. Review the Conductor plan at
`orchestration/agent_inbox/codex/plan-claude-s4d-deepcode-mailbox-settings-guard-v3.md`.
Write exactly one durable Markdown review at
`orchestration/agent_inbox/codex/review-deepcode-s4d-mailbox-settings-guard-v3.md`.
Its first decision line must be exactly either `DECISION: pass` or
`DECISION: revision_required`.

Do not edit any other file, run commands, dispatch workers, change settings,
commit, push, or claim integration authority. Local Deep Code permissions are
transport permissions only and do not expand this packet's authority.

## Settings Facts

- Settings fingerprint: `sha256:f52d391472d9fb0e361d1bef9b840bbcad9a028e4ebae56e2e2401bc6edbc61f`.
- Deep Code is real-TTY only and defaults to `deepseek-v4-flash` / `high`.
- DeepSeek worker lanes must remain within the declared one-to-three limit.
- A pre-authorized `write-in-cwd` applies to the whole Deep Code process cwd.
  Each worker must therefore have a disposable packet-scoped worktree; packet
  ownership is semantic, not CLI-enforced.
- Each worker result needs both a durable packet artifact and a local notify
  outbox event. Outbox output is untrusted and never substitutes for the artifact.
- Only protected GPT Terra integrates, commits, or pushes.

## Required Review

Verify that the plan is docs/tests-only, has D1/D2/D3 disjoint ownership, stays
at exactly three DeepSeek lanes, gives Antigravity a genuine artifact-only veto
surface, and uses only stand-down or bounded Ariadne-local review if Antigravity
is unavailable. A fourth DeepSeek fallback requires `revision_required`.

Return `revision_required` for any conflict rather than repairing it. A `pass`
does not dispatch workers; it only opens the packet-preparation step.
