# Deep Code S4d Verifier Packet V4

You are the Ariadne verifier. Review
`orchestration/agent_inbox/codex/plan-claude-s4d-deepcode-mailbox-settings-guard-v4.md`
against the committed harness settings at fingerprint
`sha256:cfb5534ea58bb22bdf602ce4f572ea1bc8b68b9ca581f4b4d88d59d060b4a072`.

Write only
`orchestration/agent_inbox/codex/review-deepcode-s4d-mailbox-settings-guard-v4.md`.
Begin with exactly `DECISION: pass` or `DECISION: revision_required`.

Verify: docs/tests-only scope; exactly three disjoint DeepSeek lanes; disposable
worktrees; artifact plus PTY event plus receipt completion; permission prompts
fail closed; bounded forced cleanup only after valid artifact and completed
turn; Antigravity artifact-only veto; no fourth DeepSeek fallback; and GPT Terra
sole integration/commit/push authority.

Do not edit any other file, run commands, dispatch workers, change settings,
commit, push, or claim integration authority. Return `revision_required` for
any conflict rather than silently repairing the plan.
