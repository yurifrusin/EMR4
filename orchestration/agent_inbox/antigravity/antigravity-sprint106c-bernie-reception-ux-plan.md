# antigravity-sprint106c-bernie-reception-ux-plan

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 1fec462 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint106c-bernie-reception-ux-plan --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint106c-bernie-reception-ux-plan --commit-message "Sprint 106C Bernie reception UX plan" --message "antigravity-sprint106c-bernie-reception-ux-plan ready for Codex review"` |

## Mission

Plan the Diary/reception interaction implications for typed Bernie context frames: how Bernie should present natural, professional responses while deterministic state/guardrail facts prevent false no-slot, stale warning, or future-appointment blocks.

## Scope

### In Scope

Read AGENTS.md, protocol alerts, sprint_closeout, docs/diary Bernie UI code, existing review harness, no-slot suggestion UI, chat transcript state, recent user screenshot issues recorded in closeout context, and backend Bernie response shapes. Produce a plan only: identify UI copy/state surfaces likely affected by typed context frames and what should remain unchanged.

### Out of Scope

No production code during plan phase. No broad Diary redesign, no persisted session work, no autonomous booking, no provider migration, no live PHI, no implementation unless Ariadne explicitly releases complete sprint task.

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

## Implementation Plan

### My Understanding
Sprint 106C requires planning the frontend (Diary/reception UI) and backend interaction implications of migrating to typed context frames for Bernie.
Specifically, we must define how Bernie presents natural, professional responses while using deterministic state and guardrail facts to prevent three primary failure modes:
1. **False "no slots" blocks**: Triggered when browser reference dates/timezones mismatch or same-day clamping logic erroneously filters future slots on adjacent days.
2. **Stale warnings**: Triggered when UI navigation (switching dates, patient selection) fails to clear old proposals/freshness IDs, leading to invalid confirmation attempts.
3. **False future-appointment blocks/warnings**: Triggered when rescheduling an existing appointment (same day or target day) erroneously flags a duplicate booking follow-up, or when the warning message statically hardcodes name copy ("Margaret") instead of being patient-specific.

### Intended Surface / Boundary
- **Bernie Panel (UI)**: Specifically `docs/diary/diary.js` including `buildBernieContextFrames`, `clearStaleBernieBookingState`, `bernieIssueDisplayText`, and transcript/composer rendering.
- **Roster & Context Services (Backend)**: `app/routers/appointments.py` (warning resolution and same-day clamping) and `app/services/bernie_patient_context.py` (duplicate warning generation and exclusion logic).
- **Adjacent surfaces (MUST NOT change)**: Diary grid geometry/layout, booking modal, Waiting Room cards, patient search, and Taskpane view.

### Out of Scope
- Editing production code during this plan-only phase.
- Adding persisted session DB schemas, migrations, or external state-chart runtimes (e.g. XState).
- Changing practitioner roster tables or automating direct booking writes without staff verification.

### Files I Expect To Edit
- `docs/diary/diary.js`
- `app/routers/appointments.py`
- `app/services/bernie_patient_context.py`
- `tests/test_bernie_patient_context.py`

### Implementation Steps
1. **Typed Context Frame Schema Alignment**:
   - Ensure the structure returned by `buildBernieContextFrames()` matches the new backend Pydantic models (discriminated union) exactly.
   - Format all date fields strictly as ISO string dates (`yyyy-mm-dd`) and avoid optional fields falling back to missing keys.
2. **Rescheduling Warning Bypass**:
   - Update `build_patient_booking_context` and `has_existing_booking_on_requested_day` to accept `source_appointment_id`.
   - If the patient has an appointment on the requested day and its ID matches `source_appointment_id`, exclude it from the duplicate warning check.
3. **Dynamic Warning Messages**:
   - Update `build_existing_future_follow_up_warning` on the backend to accept the patient's first name: `f"{patient_first_name} already has another appointment on the requested day. Check whether a new booking is still needed."`
   - Update `bernieIssueDisplayText` in `docs/diary/diary.js` to return `issue.message` directly for `existing_future_follow_up` rather than overriding it with hardcoded Margaret-specific copy.
4. **Timezone-Safe Same-Day Clamping**:
   - Ensure the same-day window clamping logic uses the clinic's local timezone for date comparison.
   - Guard against timezone/browser offsets by validating that the clamping only triggers when `resolved_date` is exactly equal to the calendar day of `clinic_now`.
5. **Clean Transcript & Composer Reset**:
   - Update `clearStaleBernieBookingState` to clear composer text, staged candidates, and freshness IDs while preserving the `#bernie-chat-transcript` content so receptionists see chat history without stale inputs.

### Visual / Behavioural Acceptance Checks
- Check that opening Bernie and calling `interpret-booking-instruction` executes without any console schema validation errors (422).
- Attempting to book a slot for Billy Frusin on a day they already have an appointment shows the warning: `"Billy already has another appointment..."` instead of `"Margaret already has..."`.
- Moving an appointment to another slot on the same day must NOT trigger the `existing_future_follow_up` warning (since it's the `source_appointment_id`).
- When navigating dates in the diary, the current proposal card pulses/stale states are cleared from the diary grid, but the chat history in the transcript sidebar remains populated and readable.

### Risks / Ambiguities
- Timezone boundary conditions: Browser date key calculation (`localDateKey`) could differ from server day boundary during late-night bookings.
- Ensure suggestion chip events (`no_slot_suggestion_click`) pass valid parent turn IDs.

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

Plan must list affected Diary files/selectors/tests if implementation is later approved, specific UI behaviours to preserve, and how to verify that Bernie can show last-message/chat history without stale prompt text or logically false warnings.

## Merge Criteria

Ariadne can accept the plan if it keeps UI changes minimal, respects the chat-turn direction, avoids scripting Bernie voice into brittle copy tables, and identifies deterministic checks for false/no-slot stale-message regressions.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: [antigravity-sprint106c-bernie-reception-ux-plan.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/agent_inbox/antigravity/antigravity-sprint106c-bernie-reception-ux-plan.md)
- Verification run: Captured implementation plan with `python scripts\agent_worktrees.py plan` and verified baseline pytest environment.
- Remaining risks: Late-night timezone browser/server calendar day mismatches (e.g. AEST vs local developer time) which requires careful clinical date anchoring.
