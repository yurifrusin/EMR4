# Deep Code S4d Verifier Packet V2

Date: 2026-07-11

## Role And Output

You are the Ariadne verifier. Write exactly one durable Markdown review artifact
at `orchestration/agent_inbox/codex/review-deepcode-s4d-mailbox-settings-guard.md`.
Its first decision line must be either `DECISION: pass` or
`DECISION: revision_required`.

Do not edit any other file, run commands, dispatch workers, change settings,
commit, push, or claim integration authority. A Deep Code permission approval is
local tool permission only and does not change this role boundary.

## Settings Facts

- Settings fingerprint used by the Conductor: `d5e91fee`.
- Deep Code is real-TTY only, defaulting to `deepseek-v4-flash`/`high`.
- `deepseek-v4-pro` and `max` are exceptional only.
- DeepSeek worker lanes must remain within the declared **one-to-three** limit.
- Worker completion needs both a durable artifact and a local notify-outbox
  event. The outbox is untrusted and never substitutes for the durable artifact.
- The base permission profile is `askAll`; only read-in-worktree and Git-log
  queries are pre-allowed. Writes require packet scope; escalation paths remain
  denied or interactive.
- Only the protected GPT Terra orchestrator integrates, commits, or pushes.

## Conductor Plan To Verify

**Boundary:** docs/tests-only guardrail sprint. It adds no runtime, provider,
frontend, database, GraphQL, H15/H-series, D5, deployment, release, or
settings-value work.

**D1:** owns only `tests/test_ariadne_deepcode_adapter_settings.py`, pinning
the Deep Code model, reasoning, interactive-TTY, non-TTY, durable artifact,
and permission-authority settings, including one negative test.

**D2:** owns only `docs/ariadne-deepcode-adapter-authority.md`, documenting
reachability versus authority, non-TTY handling, permissions, and artifacts.

**D3:** owns only `tests/test_ariadne_deepcode_mailbox_settings.py`, pinning
the mailbox local-only/outbox trust and strict capability settings, including
one negative test.

**Antigravity:** review/veto artifact only, no source edits.

All three DeepSeek lanes use separate fresh TTY sessions and have disjoint file
ownership. The Conductor states that if Antigravity fails it could substitute a
**fourth** DeepSeek review lane.

## Required Review

Check the full plan against the stated policy. In particular, assess the
DeepSeek lane-count fallback, authority split, artifact/mailbox requirement,
scope, and whether the Antigravity decision has a real veto surface. Return
`revision_required` for any conflict rather than silently repairing the plan.
