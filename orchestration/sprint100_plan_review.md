# Sprint 100 Plan Review - Bernie Booking Session State Machine

Reviewed by Ariadne on 2026-07-01.

## Sprint Goal

Implement an explicit *bernie* booking-session state machine so receptionist
instructions, relative dates, visible diary navigation, candidate snapshots,
provisional previews, confirmation evidence, and post-confirmation cleanup are
kept as separate concepts.

The sprint is grounded in Yuri's live failure case:

1. `after 3 today` at about 20:40 showed an empty candidate result instead of
   asking whether to use another day.
2. `after 3 tomorrow` produced correct Thursday candidates, but selecting a
   candidate moved the diary to Friday because `tomorrow` was re-resolved after
   the visible diary date changed.
3. `Choose another time` risked reinterpreting the original prompt instead of
   returning to the original candidate snapshot.
4. Confirmed bookings left too much stale request/detail state on screen.

## Accepted Superstructure

Use the design guide in
`orchestration/event_driven_statechart_architecture.md`.

Sprint 100 is not the full API-spine redesign. It is the concrete training
ground for the wider model: bounded context plus events plus embedded
statecharts plus typed API contracts.

## State Machine Shape

| State | Event | Guard | Next State | Required Effect |
|---|---|---|---|---|
| `idle` | `start_session` | context available | `awaiting_instruction` | Create session with immutable `request_reference_date`. |
| `awaiting_instruction` | `submit_instruction` | text present | `interpreting` | Send instruction and locked reference date once. |
| `interpreting` | `clarification_required` | confidence axis asks | `clarification_needed` | Show first-person clarification; no slot search. |
| `interpreting` | `interpreted` | normalized command safe | `searching_slots` | Preserve command snapshot; no reread of `diaryDate`. |
| `searching_slots` | `clinic_day_exhausted` | no remaining same-day bookable slots | `clarification_needed` | Ask for another day/time; no empty candidate-list state. |
| `searching_slots` | `slots_found` | candidates non-empty | `candidate_selection_required` | Store candidate snapshot with absolute dates/times. |
| `candidate_selection_required` | `select_candidate` | index belongs to snapshot | `slot_previewing` | Fetch/prepare confirmation evidence using locked session data. |
| `slot_previewing` | `confirmation_ready` | confirm payload matches selected snapshot | `confirmation_ready` | Show provisional diary card and compact confirmation panel. |
| `confirmation_ready` | `choose_another_time` | snapshot exists | `candidate_selection_required` | Re-render same snapshot; no interpret/search call. |
| `confirmation_ready` | `confirm_clicked` | user explicitly confirms | `confirming` | One write attempt through confirm endpoint. |
| `confirming` | `confirm_success` | appointment created | `confirmed` | Clear preview/confirm controls; show compact confirmed summary. |
| `confirming` | `confirm_stale_or_blocked` | revalidation fails | `stale_or_blocked` | Kill old confirm payload; allow refreshed selection/search. |
| Any active state | `edit_instruction` or `change_context` | explicit user edit | `awaiting_instruction` | Invalidate interpretation, snapshot, preview, and confirm payload. |

## Non-Negotiable Invariants

- `request_reference_date` is immutable for a booking session.
- `today` and `tomorrow` are resolved against `request_reference_date`, never
  against the mutated visible `diaryDate`.
- Diary navigation is a side effect of previewing a slot, not semantic input.
- Candidate lists are snapshots with absolute `appointment_date` and
  `start_time_local`.
- `Choose another time` returns to the same candidate snapshot and must not call
  `interpret-booking-instruction` or slot search.
- Open-ended same-day requests such as `after 3 today` should clamp forward only
  while there are remaining bookable slots that day. If the relevant clinic /
  practitioner day is exhausted, return a temporal clarification state.
- Confirmation evidence must match the selected candidate snapshot.
- Confirmation is the only write transition.
- Confirm success clears stale preview, confirm controls, and verbose request
  evidence while leaving a compact success summary.
- Stale confirm failure kills the old confirm payload; retry requires refreshed
  proposal evidence.

## Worker Plan Review

### Claude - Backend State Contract

Initial plan: good overall contract direction.

Required correction before implementation:

- The plan must treat schedule-aware same-day exhaustion as in scope. It is not
  enough to say "requested window fully past" and leave roster-aware exhaustion
  to a follow-up. Yuri's concrete 20:40 failure is an open-ended same-day
  request. It must be handled by checking whether clamp-to-now leaves any
  remaining bookable same-day slots for the relevant practitioner/day.

Approved backend direction:

- Preserve partly-past in-hours clamping.
- For bounded windows fully past, return temporal ask before slot search.
- For open-ended same-day requests, clamp to now, run or pre-check against the
  relevant schedule, and if no same-day bookable slot can remain, return
  `clinic_day_exhausted` / temporal ask rather than an empty candidate list.
- Do not auto-advance the date to tomorrow.

Revised plan status: accepted after Claude updated the plan to include
schedule-aware exhaustion for open-ended same-day requests, named before-search
and after-search checks, and removed the contradictory follow-up note.

### Antigravity/Gemini - Diary UI State Machine

Initial plan: good state-machine direction but ambiguous about candidate
selection and post-confirm state.

Revised plan: accepted.

Accepted requirements:

- Candidate selection is a formal transition, not just local state mutation.
- It prepares confirmation evidence through the existing supervised
  booking/selection proposal path using the locked reference date and selected
  absolute candidate.
- `Choose another time` reuses the existing snapshot and is verified with
  network spies to make zero interpret/slot-search calls.
- Confirm success transitions to a compact confirmed state, clears stale
  preview/confirm controls, and removes old verbose evidence.

### Codex Worker - Invariant Harness

Plan accepted.

Useful additions adopted:

- Transition table above.
- Backend and UI invariant tests should be named so failures map directly to the
  state-machine invariant they protect.
- Any worker implementation plan must be rejected if it allows diary navigation
  to become semantic input or lets `Choose another time` reinterpret the prompt.

## Implementation Release Criteria

Implementation can start. Claude's revised backend plan, Antigravity's revised
UI plan, and the Codex worker invariant review have been accepted.

Minimum tests before closeout:

- Backend test for same-day after-hours open-ended request returning temporal
  clarification rather than empty candidate state.
- Backend test for partly-past in-hours clamping still proceeding.
- Backend/API test proving relative `tomorrow` is resolved from the original
  session reference date.
- UI test proving candidate selection can navigate the diary without changing
  the session reference date.
- UI test proving `Choose another time` returns to the same snapshot without
  interpret/search calls.
- UI test proving confirm success clears stale preview/confirm controls and
  verbose evidence.
- Confirm path test proving only explicit confirmation writes.
