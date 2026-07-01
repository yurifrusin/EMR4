# claude-sprint99-bernie-confidence-policy-contract

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | submitted |
| Created | 76e00f9 |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-sprint99-bernie-confidence-policy-contract --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-sprint99-bernie-confidence-policy-contract --commit-message "Sprint 99 Bernie confidence policy contract" --message "claude-sprint99-bernie-confidence-policy-contract ready for Codex review"` |

## Mission

Plan the backend/API confidence and decision-policy contract for Bernie booking interpretation: separate intent, temporal, practitioner, patient identity, slot-validity, and future speech/transcription axes; decide assume/proceed-with-check/ask/block bands; preserve human-confirmed mutation gates.

## Scope

### In Scope

Plan packet first only. Review app/schemas/appointments.py, app/routers/appointments.py, app/services/bernie_booking_interpreter.py, tests/test_bernie_interpret_booking_instruction.py, tests/test_bernie_sprint98_release_gates.py, orchestration/bernie_release_gates.md. Propose exact typed response fields for confidence axes, assumptions/inferences, staff checks, details/debug disclosure, first-person clarification copy, and deterministic rules for omitted today, misspelled practitioner names, and fuzzy patient matches. Include how small practitioner set matching differs from large patient database matching.

### Out of Scope

Production code before plan approval; diary UI implementation; live phone/voice/Caller ID/Medicare/OPV/PVM integrations; broad GraphQL/API-spine redesign; weakening staff confirmation; broad refactors unrelated to Bernie booking interpretation.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Plan must name exact backend files/tests, confidence thresholds/gates to test, no-write assertions, ordinary prompt release gates, omitted-date test, practitioner typo test, patient ambiguity/duplicate test, and migration/no-migration rationale.

## Merge Criteria

Ariadne can approve only if the plan defines stable API fields, avoids multiplying raw scalar scores into unsafe decisions, distinguishes warning/check states from hard blocks, and preserves explicit staff confirmation for appointment creation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

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
