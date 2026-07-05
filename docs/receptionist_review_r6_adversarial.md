# Sprint R6 Adversarial Temporal Boundary Review

> **Reviewer:** DeepSeek Flash (Shen) — Adversarial track
> **Date:** 2026-07-05
> **Scope:** Appointment temporal boundary — every date/time/schedule/reference-date
> code path accessible from the reception surface
> **Mode:** Read-only review. No production code, tests, fixtures, or harness
> changes made. Findings may be converted to test cases or route-level fixes by
> a subsequent implementation lane (recommended: Claude/Ariadne).

---

## 1. Executive Summary

The temporal boundary is **mostly solid** for the Bernie supervised path (NL →
normalizer → slot search → proposal → signed confirmation). The normalizer
enforces date_from >= reference_date (blocking past-date searches), and the
Bernie interpreter path uses explicit eference_date binding to align relative
NL tokens. The diary-domain 	emporal.py is cleanly pure with no DB or clock
reads, and evaluate_same_day_window correctly defers route-level decisions to
callers.

The principal gap is **asymmetric enforcement between the Bernie path and the
direct raw-compat paths.** A receptionist can bypass all temporal guardrails by
calling the legacy POST /appointments or POST /proposals/create directly
with any date — past, future, or unbound — because the raw-compat path validates
only entity existence and slot conflict, never reference-date alignment,
schedule availability, or temporal recency.

---

## 2. Key Strengths

### 2.1. Pure temporal policy module (diary/temporal.py)

All same-day window evaluation, NL time parsing, and weekday-resolution logic
is pure — no DB, no wall clock. Callers inject clinic_now explicitly.

### 2.2. Bernie normalizer past-date blocking

ernie_slot_normalizer.normalize_slot_search_command explicitly checks
date_from < reference_date and returns a "requested_date_in_past" block.
The Bernie NL path cannot search for past appointments.

### 2.3. Reference-date binding in Bernie session

Bernie sessions capture an immutable reference_date on turn-0 and reject turns
that supply a different value. This prevents replay across calendar boundaries.

### 2.4. Same-day window handling

evaluate_same_day_window correctly classifies window_fully_past, clamp_earliest,
and ok. The clamping logic re-normalises the constraint when earliest_time has
passed but the window is still open.

### 2.5. Schedule override + roster unavailability

_resolve_day_schedule correctly returns None when
ScheduleOverride.is_unavailable is set. evaluate_reception_context keeps
oster_unavailable as a distinct first-class classification.

---

## 3. Adversarial Findings

### Finding 1 (High) — Raw direct create bypasses all temporal policy

**Route:** POST /appointments → _create_appointment_from_body

**What happens:** The direct create path calls _canonical_create_values,
_ensure_* entity checks, _raise_if_conflict, and _write_audit. It never
calls _resolve_day_schedule, never checks date >= today, never evaluates
evaluate_same_day_window, and never validates against the practice roster.

**Exploitation:**
1. Receptionist POSTs an appointment for yesterday or last week with any valid
   ppointment_date and start_time_local.
2. If no conflicting appointment exists (same practitioner, same local time),
   the appointment is created successfully with a past date.
3. A "Booked" or "Completed" appointment exists in the audit log for a time
   that has already passed — a billing/compliance discrepancy.

**Evidence:** _create_appointment_from_body (line 869) calls _raise_if_conflict
but never _resolve_day_schedule or any date-vs-now predicate.

**Same applies to:** propose_create_appointment (line 1003) →
_build_create_appointment_proposal — same lack of temporal validation.

**Mitigation:** Add a reference-date check (appointment_date < clinic_now.date()
→ blocked) to the raw-compat path, or route raw creates through the normalizer.

---

### Finding 2 (High) — Raw appointment update can reschedule to any date

**Route:** POST /proposals/update/{appointment_id} → propose_update_appointment

**What happens:** The update proposal merges incoming date/time over existing
appointment values, then checks entity validity and conflicts. It does not
validate that the new appointment_date is today or in the future.

**Exploitation:**
1. Receptionist proposes to reschedule a tomorrow appointment to yesterday.
2. If no conflict, proposal returns safe=True.
3. Confirming the proposal writes an appointment rescheduled into the past.

**Same for:** PATCH /{appointment_id}/status (line 4156) — no date recency
validation.

**Mitigation:** Add appointment_date >= clinic_now.date() validation to the
update proposal builder and the raw status-update apply path.

---

### Finding 3 (Low) — _overlaps end-boundary arithmetic edge case

**Location:** pp/routers/appointments.py line 643-651

`python
def _overlaps(start_a, duration_a, start_b, duration_b):
    end_a = start_a + timedelta(minutes=duration_a)
    end_b = start_b + timedelta(minutes=duration_b)
    return start_a < end_b and end_a > start_b
`

**Issue:** Two zero-duration appointments at the same time would not overlap
(start_a < end_b(=start_a) is false). Mitigated by schema gt=0 on
duration_minutes, but the raw-compat path could reach this state via a
misconfigured client that bypasses Pydantic validation. Low risk.

---

### Finding 4 (Medium) — Slot search bypasses past-date check on the non-Bernie path

**Route:** POST /proposals/slot-search → _build_slot_search_proposal

**What happens:** SlotSearchProposalIn validates date_from <= date_to and the
14-day ceiling, but does not enforce date_from >= today. The Bernie normalizer
enforces this; the raw slot-search endpoint does not.

**Exploitation:**
1. Receptionist passes date_from=2026-07-01 (past) to raw slot search.
2. _resolve_day_schedule returns the practitioner's schedule for that day.
3. Slots are generated for a past date, surfacing stale availability.

**Mitigation:** Enforce date_from >= clinic_now.date() at the slot-search route
level.

---

### Finding 5 (Low) — Completed appointments blocking semantics are misleading

**Location:** pp/routers/appointments.py lines 660-666

`python
NON_BLOCKING_STATUSES = (
    AppointmentStatus.Cancelled,
    AppointmentStatus.NoShow,
    AppointmentStatus.DNA,
)
`

**Issue:** _find_conflicting_appointment filters by exact appointment_date
match. A Completed appointment from a different day is never returned. Same-day
Completed appointments should block (the slot was used). The code is correct
but NON_BLOCKING_STATUSES could be read to imply Completed is blocking. No
actual bug — rename or add a comment for clarity.

---

### Finding 6 (Medium) — _as_practice_local misinterprets naive UTC datetimes

**Location:** pp/routers/appointments.py line 458-461

`python
def _as_practice_local(start_time, practice_tz):
    if start_time.tzinfo is None:
        return start_time.replace(tzinfo=practice_tz)
    return start_time.astimezone(practice_tz)
`

**Issue:** When a client sends a naive datetime with UTC semantics (e.g.,
2026-07-05T04:00:00 meaning UTC), the function treats it as being in
practice_tz. If practice_tz is Australia/Sydney (UTC+10), the resulting local
time would be 04:00 instead of 14:00 — a 10-hour error.

**Exploitation:** A misconfigured client sends a naive start_time with UTC
intent. Appointment created at wrong local time, potentially causing a double-book
or missed consultation.

**Mitigation:** Reject naive datetimes explicitly for start_time in the
AppointmentCreate schema validator, or always interpret incoming naive datetimes
as UTC before converting to practice-local.

---

### Finding 7 (Low) — No maximum future-date bound on appointment creation

**Issue:** AppointmentCreate validates duration_minutes with le=480 but places
no bound on future dates. A receptionist could create an appointment 5 years
hence, bypassing the 14-day slot-search constraint.

**Mitigation:** Add a configurable max_booking_ahead_days to practice settings
and enforce it in create/update proposal builders.

---

### Finding 8 (Low) — Direct status update can skip attendance audit trail

**Route:** PATCH /{appointment_id}/status

**Issue:** A receptionist can move a past Booked appointment directly to
Completed without an Arrived→InConsult→Completed transition, bypassing the
no-show/DNA audit trail.

**Mitigation:** Deprecate the raw PATCH or add a status transition graph
validator.

---

### Finding 9 (Low) — _resolve_day_schedule over-midnight ScheduleOverride silently yields zero slots

**Issue:** If ScheduleOverride has override_start=22:00 and override_end=02:00,
datetime.combine puts both on the same calendar date, day_end < day_start,
and the while loop never executes. Over-midnight sessions are silently invisible.

**Mitigation:** Validate override_end > override_start at the ScheduleOverride
persistence layer, or handle over-midnight by creating two same-date ranges.

---

### Finding 10 (Informational) — parse_time_fragment defensive guards

**Location:** pp/services/diary/temporal.py lines 61-74

parse_time_fragment safely returns None for impossible meridiem/hour
combinations (13 pm → hour=25 → None). Value like   pm normalises to 12:00,
which is sensible for NL. No exploit path identified; documented for awareness.

---

## 4. Risk Summary by Route

| Route | Temporal guard | Risk | Finding |
|---|---|---|---|
| POST /appointments (raw create) | None | **High** | F1 |
| POST /proposals/create | None | **High** | F1 |
| POST /proposals/update/{id} | Terminal check only | **High** | F2 |
| PATCH /{id}/status (raw) | None | **Medium** | F8 |
| POST /proposals/slot-search (raw) | None | **Medium** | F4 |
| POST /proposals/slot-search/normalized | Full (normalizer) | Low | — |
| Bernie supervised booking | Full (normalizer + ref_date) | Low | — |
| _overlaps / _find_conflicting | Per-day + status excludes | Low | F3, F5 |
| Timezone conversion | Misinterprets naive UTC | **Medium** | F6 |
| Max future date | None | **Low** | F7 |
| Over-midnight schedule | Silent fail | **Low** | F9 |

---

## 5. Testing Recommendation

### 5.1. Highest-value test: latest-only fully-past same-day

Claude/Ariadne should create a route-level pytest that:

1. Sets clinic-now to a past time (e.g., 15:00 clinic-local).
2. Creates a BernieSupervisedBookingIn with same-day date,
   earliest_time=09:00, latest_time=10:00 (fully past).
3. Asserts window_fully_past and that no slot search runs.

This tests the critical temporal guard before any DB query.

### 5.2. Approach: route-level pytest over replay-harness clock injection

Use direct unit tests for the pure temporal layer, and route-level tests with
monkeypatched _clinic_local_now for integration. The monkeypatch pattern is
already present (docstring: "Monkeypatchable in tests").

**Do not** build a replay-harness clock-injection framework — that adds surface
area without proportional test value.

### 5.3. Priority

1. Pure unit: evaluate_same_day_window — all four SameDayWindowKind branches
2. Route-level: raw create with past date
3. Route-level: raw update to past date
4. Route-level: slot-search with past date on raw path
5. Route-level: naive UTC datetime rejection
6. Pure unit: parse_time_fragment edge cases (12am, 12pm, 0am, 13pm, 13am)

---

## 6. Caveats

- DST transition dates: _resolve_day_schedule slot-generation uses naive
  datetime.combine with no timezone awareness. On DST boundary, the range could
  be off by ±1 hour. Known limitation of the naive-local-time model.
- Cross-practice timezone booking: Assumes all appointments in the same practice
  timezone. A practitioner working across two timezones could see misaligned
  slots.

---

## 7. Artifact Status

This file is a **review artifact only**. No production code, tests, fixtures, or
harness changes were made.

Git operations in this worktree are blocked by filesystem sandbox (parent repo
.git at C:\Users\sarashera\emr4\.git is not writable from this sandbox). The
review artifact is created locally. Claude/Ariadne should pick it up from
docs/receptionist_review_r6_adversarial.md, review the findings, and implement
route-level temporal guards on the raw-compat paths following the recommended
testing approach in Section 5.
