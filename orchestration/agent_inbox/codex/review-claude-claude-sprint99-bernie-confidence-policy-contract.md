# review-claude-claude-sprint99-bernie-confidence-policy-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint99-bernie-confidence-policy-contract` |
| Status | integrated |

## Review Request

claude-sprint99-bernie-confidence-policy-contract ready for Codex review

## Worker Completion Notes

Implementation completion update - supersedes the earlier plan-gate notes below.

- Files changed:
  - `app/config.py`
  - `app/routers/appointments.py`
  - `app/schemas/appointments.py`
  - `app/services/bernie_booking_interpreter.py`
  - `tests/test_bernie_sprint98_release_gates.py`
  - `tests/test_bernie_confidence_policy.py`
- Implementation summary:
  - Added confidence axes and banded decisioning for *bernie*: intent, temporal,
    practitioner, patient identity, slot validity, and a speech placeholder.
  - Kept the scalar confidence value advisory/display-only; API gating uses the
    most conservative axis band.
  - Added first-person clarification text for assumptions, typo resolution, and
    blocked/ask states.
  - Added deterministic same-day temporal handling so "today" never proposes
    slots in the past and partly-past windows clamp forward.
  - Added patient candidate handling for fuzzy/ambiguous patient names without
    silently linking a fuzzy match.
  - Preserved the no-write-before-confirm guardrail; no migration required.
- Verification run:
  - `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m py_compile app\config.py app\schemas\appointments.py app\services\bernie_booking_interpreter.py app\routers\appointments.py tests\test_bernie_confidence_policy.py tests\test_bernie_sprint98_release_gates.py`
  - `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpret_booking_instruction.py tests\test_bernie_sprint98_release_gates.py tests\test_bernie_confidence_policy.py -q` -> 44 passed.
  - `git diff --check`
- Remaining risks:
  - The UI must consume the new axes and candidate/clarification fields without
    exposing raw debug detail in ordinary receptionist mode.
  - Voice input is still placeholder-only; no speech transcription confidence is
    calculated yet.

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-sprint99-bernie-confidence-policy-contract.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result: Accepted and integrated. Ariadne added an extra open-ended same-day temporal clamp regression after review so `after 3 today` searches forward from clinic-now instead of asking or offering past slots.
- Follow-up required: Later API-spine work should formalize patient candidate selection/linking; Sprint 99 keeps fuzzy candidates proposal-only.
