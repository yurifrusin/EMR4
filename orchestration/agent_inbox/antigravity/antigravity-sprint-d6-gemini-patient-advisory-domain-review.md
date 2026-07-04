# antigravity-sprint-d6-gemini-patient-advisory-domain-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | eff7cdd |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-d6-gemini-patient-advisory-domain-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-d6-gemini-patient-advisory-domain-review --commit-message "Sprint D6 Gemini patient advisory domain review" --message "antigravity-sprint-d6-gemini-patient-advisory-domain-review ready for Codex review"` |

## Mission

Use Antigravity/Gemini as an independent backend/domain-policy reviewer for D6 patient future-booking advisory semantics.

## Scope

### In Scope

Review build_patient_booking_context, has_existing_booking_on_requested_day, supervised booking warning generation, and tests. Produce a tangible review artifact with exact semantics for when existing_future_follow_up should be emitted versus when future bookings should remain informational context.

### Out of Scope

No UI/frontend. No GraphRAG. No persisted sessions/migrations. No broad rewrite. No staff-facing copy changes unless explicitly proposing future work.

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

If code changed: py_compile, focused pytest, git diff --check. If review-only: cite exact files/tests and submit artifact.

## Merge Criteria

Ariadne can use the review if it is concrete, file-grounded, and submitted as a repo artifact; stdout alone is not sufficient.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: None (Review-only task packet)
- Verification run: Rerun of patient context unit tests using EMR4 virtual environment (`C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_patient_context.py` - 15 passed, and `tests/test_bernie_booking_outcomes.py` - 39 passed).
- Remaining risks: 
  1. Capping Risk: `has_existing_booking_on_requested_day` relies on `context.future_bookings` which is capped at 3 soonest. A collision on a 4th or later future booking will go undetected (false negative).
  2. Rescheduling self-collision: Without passing `source_appointment_id` or equivalent identifier, rescheduling an existing appointment on the same day will trigger a false duplicate collision warning. This must be addressed in Sprint 106C/107.
  3. Frontend hardcoding: The frontend `diary.js` currently overrides the `existing_future_follow_up` warning message with a hardcoded Margaret-specific string. This must be fixed in the frontend to display `issue.message` directly.

### Domain Review: existing_future_follow_up Semantics Resolution

#### 1. Resolution of the Semantic Disagreement
We side with **Claude's semantic architecture** regarding the definition of `existing_future_follow_up` in the Pydantic schema `BerniePatientBookingContext` and the separation of concerns:
* **`existing_future_follow_up` must remain a broad "any future booking" context flag.** It represents whether a recognized patient has any active booking on or after the reference date, matching `has_future_booking`.
* **Warning emission must remain gated by date collision at the router/policy level** (using `has_existing_booking_on_requested_day` or direct DB lookup).

#### 2. Rationale
* **Separation of Concerns:** `build_patient_booking_context` is a stateless patient history retriever. It is invoked when a patient is recognized, often before a requested slot/date is known. Forcing it to accept `requested_date` couples the static patient history context to the dynamic request constraints.
* **Clinical/Advisory Context:** A patient having *any* future appointment is a valuable general conversational context for Bernie, even if it is not on the same day. Redefining the context boolean to mean "same-day collision" loses this general advisory signal.
* **Misleading Field Name:** If `existing_future_follow_up` in the schema only meant same-day collision, its name would be misleading (since same-day collision is a specific subset of future bookings).

#### 3. Capping Vulnerability & Rescheduling Bug (Yuri's Reported Problem)
* **Capping bug:** `has_existing_booking_on_requested_day` checks `context.future_bookings` (capped at 3). If a patient has 4 future bookings, and the requested booking day matches the 4th booking, no warning is emitted.
* **Rescheduling bug:** In the current implementation, moving an existing appointment to a different time on the same day will trigger a collision warning because the appointment collides with itself in the database.
* **Frontend Overrides:** Even if the backend produces a patient-specific warning message (e.g. "Billy already has..."), `bernieIssueDisplayText()` in `docs/diary/diary.js` hardcodes "Margaret".

#### 4. Action Plan for Sprint D6
* **Production Code:** Do NOT change production code in D6. Changing the Pydantic schema or context builder signature creates unnecessary coupling and breaks existing tests/contracts.
* **Tests:** Add regression tests in D6 proving:
  1. A patient with a future booking on a *different* day does NOT trigger the `existing_future_follow_up` warning for the requested day.
  2. A patient with a booking on the *same* requested day DOES trigger the warning.
* **Follow-up (Sprint 106C/107):**
  1. Update `has_existing_booking_on_requested_day` to accept an optional `source_appointment_id` to prevent self-collision during rescheduling.
  2. Fix the capping vulnerability by doing a direct, lightweight DB check in the router/policy layer for duplicate bookings on the requested day instead of relying on the capped context list.
  3. Clean up the frontend `bernieIssueDisplayText()` in `diary.js` to render the backend-supplied `issue.message` directly.



## Codex Integration Notes

Integrated in Sprint D6 closeout. Ariadne accepted the broad-context/narrow-warning semantics, kept the dedicated D6 regression module as canonical, and recorded follow-ups for frontend copy, capped-context collision lookup, and source appointment exclusion.
