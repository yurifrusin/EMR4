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

- Files changed: Plan-only packet — no production code changed. REVISED (v2) the
  Codex implementation-plan packet
  `orchestration/agent_inbox/codex/plan-claude-claude-sprint99-bernie-confidence-policy-contract.md`
  per Ariadne/Yuri feedback and kept this task packet status `pending_plan_review`.
  No `app/`, tests, migrations, diary UI, or taskpane files were edited.
  `git status` shows only the plan/coordination artifacts.
- v2 revisions (this resubmission): (1) Patient matching policy changed — fuzzy
  search is now ALLOWED but only to propose candidate choices / ask "Do you
  mean...?" (band=ask, new `patient_candidates` list), never to silently link
  identity, auto-select, or confirm. A unique EXACT name match may proceed subject
  to a staff DOB/identity check; a unique FUZZY match stays candidate-selection
  (ask) unless backed by a second identifier (DOB/Medicare/phone), which may raise
  it to proceed_with_check. Fuzzy never reaches assume and never yields a linked
  patient_id. Candidate list is capped/ranked so it cannot dump the patient table.
  (2) Added explicit same-day temporal validity — when the date resolves to today
  (explicit or inferred), Bernie never offers past slots; a fully-past same-day
  window => temporal band=ask ("that time has already passed today — later time or
  another day?"); a partly-past window is clamped forward to clinic-local now
  (never backward). Reuse the existing clinic-local time model. New tests named for
  both. The strong per-axis/lattice-min approach and staff-confirmation gate are
  unchanged.
- Verification run: None executed (plan gate — no code to test yet). The plan
  names exact backend files (`app/schemas/appointments.py`,
  `app/services/bernie_booking_interpreter.py`, `app/routers/appointments.py`,
  `app/config.py`) and tests (`tests/test_bernie_interpret_booking_instruction.py`,
  `tests/test_bernie_sprint98_release_gates.py`, new
  `tests/test_bernie_confidence_policy.py`), the confidence bands/gates to test
  (assume/proceed_with_check/ask/block lattice-min), appointment/audit no-write
  assertions, the ordinary Margaret Thompson / Dr Shera release-gate prompt,
  omitted-date test, same-day passed/partly-past temporal tests, practitioner-typo
  test, patient exact/duplicate/fuzzy-candidate tests, fuzzy+identifier
  corroboration test, debug-disclosure gating, and a no-migration rationale
  (response-shape + service logic only; one additive config flag, nothing
  persisted).
- Remaining risks: Highest risk is a fuzzy patient candidate leaking into a linked
  `patient_id` or an auto-selected identity — enforced by making `patient_candidates`
  a display-only choice list, keeping exact-match as the only proceeding path (with
  a staff DOB/identity check), capping/ranking candidates, and covering both with
  explicit tests. Same-day validity depends on a correct clinic-local "now"
  (naive/UTC would misjudge); mitigated by reusing the existing clinic-local time
  model and pinning now in tests, with forward-only clamping. Bands remain the sole
  decision source so the advisory scalar cannot re-introduce an unsafe gating path;
  `confidence` stays display-only for backward-compat. Open question flagged for
  Codex: whether the new axes/candidates should also surface on
  `BernieStaffReviewPayload` now or in a follow-up (plan defers to keep scope
  narrow). Awaiting explicit `complete sprint task` before any implementation.
