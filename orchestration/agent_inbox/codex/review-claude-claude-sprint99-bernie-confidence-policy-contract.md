# review-claude-claude-sprint99-bernie-confidence-policy-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint99-bernie-confidence-policy-contract` |
| Status | queued |

## Review Request

claude-sprint99-bernie-confidence-policy-contract ready for Codex review

## Worker Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: Plan-only packet — no production code changed. Wrote the Codex
  implementation-plan packet
  `orchestration/agent_inbox/codex/plan-claude-claude-sprint99-bernie-confidence-policy-contract.md`
  and set this task packet status to `pending_plan_review`. No `app/`, tests,
  migrations, diary UI, or taskpane files were edited. Temporary compose files
  were removed; `git status` shows only the plan/coordination artifacts.
- Verification run: None executed (plan gate — no code to test yet). The plan
  names exact backend files (`app/schemas/appointments.py`,
  `app/services/bernie_booking_interpreter.py`, `app/routers/appointments.py`,
  `app/config.py`) and tests (`tests/test_bernie_interpret_booking_instruction.py`,
  `tests/test_bernie_sprint98_release_gates.py`, new
  `tests/test_bernie_confidence_policy.py`), the confidence bands/gates to test
  (assume/proceed_with_check/ask/block lattice-min), appointment/audit no-write
  assertions, the ordinary Margaret Thompson / Dr Shera release-gate prompt,
  omitted-date test, practitioner-typo test, patient ambiguity/duplicate test,
  debug-disclosure gating, and a no-migration rationale (response-shape + service
  logic only; one additive config flag, nothing persisted).
- Remaining risks: Highest risk is preventing fuzzy matching from ever reaching
  the patient DB (PHI false-positives) — enforced by exact-only patient matching
  plus an explicit test; practitioner typo tolerance is deliberately asymmetric
  (small closed set, unique-near-match only). Bands must remain the sole decision
  source so the advisory scalar cannot re-introduce an unsafe gating path.
  Backward-compat: existing scalar-confidence assertions are preserved by keeping
  `confidence` as display-only. Open question flagged for Codex: whether the new
  axes should also surface on `BernieStaffReviewPayload` now or in a follow-up
  (plan defers it to keep scope narrow). Awaiting explicit `complete sprint task`
  before any implementation.

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint99-bernie-confidence-policy-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
