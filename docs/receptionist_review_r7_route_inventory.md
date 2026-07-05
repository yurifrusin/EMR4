# Sprint R7 — Raw Appointment Route Inventory & Temporal Guard Analysis

> **Artifact:** Route-by-route inventory of `app/routers/appointments.py` (274 KB)
> **Scope:** Distinguish **slot-writing routes** (set appointment date/time) from **status/delete routes** (do not set date/time), plus guard/test recommendations.
> **Date:** 2026-07-05
> **Worker:** DeepSeek Flash (route-inventory)
> **Branch:** codex/sprint-r7-raw-route-inventory

---

## 1. Route Classification Legend

| Category | Definition | Example |
|---|---|---|
| **Slot-writing (direct)** | Sets appointment date/time directly — raw compat endpoints bypassing the proposal pipeline | POST /appointments (raw create), PUT /{id} (raw update) |
| **Slot-writing (confirm)** | Writes appointment after proposal confirmation — includes temporal conflict revalidation | POST /proposals/create/confirm, PUT /{id} (via confirm path) |
| **Status-only** | Changes appointment status but does **not** set/reschedule date or time | PATCH /{id}/status, DELETE /{id} |
| **Non-mutating proposal** | Evaluates constraints without writing — returns a command payload for later execution | POST /proposals/create, POST /proposals/update/{id} |
| **Read-only** | Returns data, no side effects | GET /appointments, GET /{id} |
| **Bernie/tooling** | AI assistant related — may be non-mutating or write depending on endpoint | POST /proposals/create/confirm-bernie (writes), POST /proposals/bernie/tool-intent (non-mutating) |
| **Slot search** | Searches available slots without writing | GET /slots/{practitioner_id}, POST /proposals/slot-search |

---

## 2. Full Route Inventory (33 routes)

### 2.1 Direct Write (Raw Compat) — Sets appointment date/time
These endpoints write appointment date/time directly via the _raw_compat_* wrapper. They are the highest-risk slot-writing surface because they lack the proposal workflow's intermediate confirmation step and freshness gating.

| # | Method | Path | Handler | Writes date/time? | Temporal guard? |
|---|---|---|---|---|---|
| 1 | POST | /appointments | create_appointment | **Yes** — calls _create_appointment_from_body → _canonical_create_values ↔ _canonical_time_values | **Conflict check only** (_raise_if_conflict). No past-date guard. |
| 2 | PUT | /{appointment_id} | update_appointment | **Yes** — calls _apply_appointment_update → re-canonicalizes time fields when changed | **Conflict check only** (with exclude_id). No past-date guard. |

**Raw compat evidence tags:**
- create_appointment: "raw_compat_create"
- update_appointment: "raw_compat_update"

Both are governed by settings.appointment_raw_compat_mode (audit/header/off). In off mode, no audit evidence is recorded at all.

### 2.2 Proposal Confirm Write — Sets appointment date/time
These endpoints write appointment date/time after proposal validation, signed confirmation evidence, and freshness checks.

| # | Method | Path | Handler | Writes date/time? | Temporal guard? |
|---|---|---|---|---|---|
| 3 | POST | /proposals/create/confirm | confirm_create_proposal_route | **Yes** — after freshness + signed evidence checks | **Freshness gated** (proposal revalidated before write). Conflict check in _create_appointment_from_body. No explicit past-date guard. |
| 4 | POST | /proposals/update/confirm | confirm_update_proposal_route → confirm_update_proposal | **Yes** — after freshness + signed evidence checks | **Freshness gated + state-bound** (freshness_id includes current state + command). No explicit past-date guard. |
| 5 | POST | /proposals/create/confirm-bernie | confirm_bernie_create_proposal | **Yes** — first Bernie slot-flow endpoint that writes | **Freshness gated + session-bound** (session_binding, turn_ref). Conflict check. No explicit past-date guard. |

### 2.3 Status-Only Write — Does NOT set appointment date/time
These endpoints change appointment status without altering the date/time.

| # | Method | Path | Handler | Writes date/time? | Notes |
|---|---|---|---|---|---|
| 6 | PATCH | /{appointment_id}/status | update_appointment_status | **No** — calls _apply_appointment_status_update | Raw compat tag "raw_compat_status". Changes status only. |
| 7 | DELETE | /{appointment_id} | cancel_appointment | **No** — soft-cancel (sets cancelled status) | Raw compat tag "raw_compat_delete". No date/time fields touched. |
| 8 | POST | /proposals/status-confirm | confirm_status_proposal_route | **No** — writes status change only | After proposal confirmation. No date/time fields set. |
| 9 | POST | /proposals/delete-confirm | confirm_delete_proposal_route | **No** — soft-cancel on confirmation | No date/time fields set. |

### 2.4 Non-Mutating Proposals — Does NOT write, returns command payload
These evaluate constraints without writing anything. The returned command is passed to a confirm endpoint.

| # | Method | Path | Handler | Docstring summary |
|---|---|---|---|---|
| 10 | POST | /proposals/create | propose_create_appointment | Create proposal — evaluates conflicts, returns executable command |
| 11 | POST | /proposals/update/{appointment_id} | propose_update_appointment | Update/reschedule proposal — merges fields, evals conflicts, non-mutating |
| 12 | POST | /proposals/status/{appointment_id} | propose_status_update | Status-change proposal — surfaces waiting-area effects, non-mutating |
| 13 | POST | /proposals/waiting-area/{appointment_id} | propose_waiting_area_update | Waiting-area change proposal — non-mutating |
| 14 | POST | /proposals/delete/{appointment_id} | propose_delete_appointment | Delete proposal — irreversible warning, non-mutating |

### 2.5 Bernie Tooling (Non-Mutating / Read-Only)
These handle AI assistant (Bernie) interactions without writing appointment data.

| # | Method | Path | Handler | Writes? |
|---|---|---|---|---|
| 15 | POST | /proposals/bernie/tool-intent | propose_bernie_tool_intent | No — resolves diary tool intent, never writes |
| 16 | GET | /bernie/pilot-eligibility | get_bernie_pilot_eligibility | No — read-only |
| 17 | GET | /bernie/sessions/active | get_active_bernie_session | No — read-only |
| 18 | POST | /bernie/sessions/new | create_new_bernie_session | Session state only — no appointment data |
| 19 | POST | /bernie/sessions/{session_id}/events | append_bernie_session_event | Session event log — no appointment data |
| 20 | POST | /proposals/bernie/interpret-booking-instruction | interpret_bernie_booking_instruction | No — non-mutating text interpretation. No appointment writes. Bounded Access AI audit metadata only in live mode. |
| 21 | POST | /proposals/bernie/supervised-booking | propose_bernie_supervised_booking | No — composes proposal steps, never writes |
| 22 | POST | /proposals/bernie/no-slot-suggestion-selection | select_no_slot_suggestion | No — non-mutating, validates suggestion, returns pre-populated request |
| 23 | POST | /proposals/slot-search/selection | propose_slot_selection_for_create | No — converts slot-search candidate into create-proposal evidence without writing |

### 2.6 Slot Search (Read-Only)
| # | Method | Path | Handler | Notes |
|---|---|---|---|---|
| 24 | GET | /slots/{practitioner_id} | get_available_slots | Returns available time slots with availability flag |
| 25 | POST | /proposals/slot-search | propose_slot_search | Non-mutating candidate slot search |
| 26 | POST | /proposals/slot-search/normalize |
ormalize_slot_search_proposal_command | Deterministic normalize only — no DB, no mutation |
| 27 | POST | /proposals/slot-search/normalized | propose_normalized_slot_search | Normalize + search when safe, otherwise context only |

### 2.7 Read-Only (General)
| # | Method | Path | Handler | Notes |
|---|---|---|---|---|
| 28 | GET | /types | list_appointment_types | Appointment type list |
| 29 | GET | ` (root) | list_appointments | Appointment list with filters |
| 30 | GET | /{appointment_id} | get_appointment | Single appointment detail |
| 31 | GET | /{appointment_id}/checkin-defaults | get_checkin_defaults | Suggested waiting area for check-in |
| 32 | GET | /{appointment_id}/audit | get_appointment_audit | Mutation audit trail |
| 33 | GET | /waiting-room | get_waiting_room | Today's booked/arrived/in-consult queue |

---

## 3. Temporal Guard Coverage — Current State

### What exists

| Guard | Location | Applied to |
|---|---|---|
| **Conflict detection** (_raise_if_conflict) | _create_appointment_from_body (line 886), _apply_appointment_update (line 4005), and proposal eval paths | All slot-writing routes (direct + confirm) |
| **Break overlap detection** (_get_break_overlaps) | Same functions as above | All slot-writing routes |
| **Freshness gating** | Proposal confirm routes (confirm_create_proposal_route, confirm_update_proposal, confirm_bernie_create_proposal) | Proposal confirm only |
| **Bernie temporal axis** | Bernie proposal eval (around line 3656) | Bernie proposal pipelines only |
| **Same-day window check** | Slot-search pipeline (around line 5732) — "window_fully_past" rejection | Slot-search proposals only |

### What is MISSING (highest risk)

| Missing Guard | Risk | Affected Routes |
|---|---|---|
| **Past-date rejection** — no check that appointment date is >= today (practice-local) | Staff API/reception UI could create or reschedule an appointment into the past via POST /appointments or PUT /{id} | **Routes 1, 2** (direct write), **3, 4, 5** (proposal confirm) |
| **Same-day past-time rejection** — no check that same-day appointment time is >= current time (practice-local) | Staff could create a same-day appointment that has already passed | **Routes 1, 2** (direct write) |
| **Receptionist no-time-field update guard** — no guard preventing date/time from being set alongside a no-time-field status-only request via PUT /{id} when only status/waiting-area changes were intended | Accidental reschedule via reception update (race condition or client error) | **Route 2** (raw update) |
| **No time-zone boundary guard** — no guard that appointment_date and start_time_local are internally consistent across DST transitions | DST spring-forward / fall-back could produce incorrect start_time | **All slot-writing routes** (the _canonical_time_values function does not validate consistency) |

### Additional risk: raw compat off mode

When settings.appointment_raw_compat_mode = "off":

- create_appointment: audit evidence is None — no audit trail for the write
- update_appointment: same — no audit trail
- update_appointment_status: same — no audit trail
- cancel_appointment: same — no audit trail

The routes still execute and write appointment data. Only the audit evidence is suppressed.

---

## 4. Guard Recommendations (Minimum Viable)

### P0 — Direct write temporal guards (Routes 1, 2)

Add a _guard_past_date(practice_tz, appointment_date, start_time_local) check called **before** _raise_if_conflict in both:

- _create_appointment_from_body (raw create path)
- _apply_appointment_update (raw update path, only when date/time fields are being changed)

The guard should:
1. Reject appointment_date < today (practice-local) with 422 and a clear reason code such as "appointment_date_in_past".
2. Handle same-day: when appointment_date == today, check start_time_local >= current_time(local) and reject with "same_day_time_in_past" if the window has closed.

Only existing models with no appointment fields set (e.g. appointment_date=None, start_time_local=None) should skip this guard naturally via the lack of time data.

### P1 — Proposal confirm temporal revalidation (Routes 3, 4, 5)

The confirm routes already have freshness gating that checks state hasn't changed since proposal creation. However, if a proposal was created at 09:00 for a 10:00 slot, and the confirm happens at 10:05 (after the slot window closed), the confirm currently succeeds.

Add a same-day window re-check in each confirm route's execution path after freshness passes but before writing. The implementation could be a single _guard_same_day_window(reference_date, appointment_date, start_time_local, practice_tz) shared between confirm and direct routes.

### P2 — Raw update only-guard (Route 2)

During an update_appointment call, if the body contains waiting-area or status changes but no date/time/practitioner/type fields, skip all conflict and temporal guards (already handled for conflict by checking the field set intersection at line 4004). Extend the same field-intersection pattern for temporal guards to avoid false rejections on status-only-in-update-body requests.

### P3 — Timezone boundary hardening (all slot-writing routes)

Add a test-level check (in tests/) that exercises DST transitions for _canonical_time_values to confirm correct UTC conversion. The code currently does not produce incorrect results for AEST/AEDT, but a regression test would protect against future changes.

---

## 5. Minimum Test Recommendations

### 5.1 Direct create — temporal guard tests

| Test | Route | What to assert |
|---|---|---|
| Reject past-date create | POST /appointments with appointment_date = yesterday | 422, "appointment_date_in_past" |
| Reject same-day past-time create | POST /appointments with appointment_date = today, start_time_local = (now-5min) | 422, "same_day_time_in_past" |
| Accept valid future create | POST /appointments with tomorrow's date | 201, appointment created |
| Accept same-day future-time create | POST /appointments with appointment_date = today, start_time_local = (now+15min) | 201, appointment created |

### 5.2 Direct update — temporal guard tests

| Test | Route | What to assert |
|---|---|---|
| Reject past-date reschedule | PUT /{id} with appointment_date = yesterday | 422, "appointment_date_in_past" |
| Reject same-day past-time reschedule | PUT /{id} with appointment_date = today, start_time_local = (now-5min) | 422, "same_day_time_in_past" |
| Accept non-time field update (bypass guard) | PUT /{id} with only
eason changed (no date/time fields) | 200, unchanged date/time |
| Accept valid future reschedule | PUT /{id} with tomorrow's date | 200, rescheduled |

### 5.3 Proposal confirm — temporal revalidation tests

| Test | Route | What to assert |
|---|---|---|
| Confirm same-day expired proposal | POST /proposals/create/confirm for a slot that has passed since proposal creation | Freshness passes, but same-day window re-check rejects |
| Confirm valid future proposal | Normal confirm path | 200 (successful write) |

### 5.4 Status/delete routes — no temporal impact

| Test | Route | What to assert |
|---|---|---|
| Cancel past appointment | DELETE /{id} for past appointment | 204 (should succeed — cancellation does not set date/time) |
| Change status of past appointment | PATCH /{id}/status for past appointment | 200 (status change is independent of temporal validity) |
| Confirm delete of past appointment | POST /proposals/delete-confirm | 200 (delete proposal does not set date/time) |

### 5.5 Slot-search — same-day window guard (already exists)

| Test | Route | What to assert |
|---|---|---|
| Search slots for already-passed today window | GET /slots/{practitioner_id} or slot-search proposal | Blocked / "window_fully_past" |

---

## 6. Summary Matrix

| Route Group | Routes | Sets date/time? | Past-date guard? | Same-day window guard? | Conflict check? | Freshness gate? |
|---|---|---|---|---|---|---|
| Direct create | 1 | ✅ | ❌ | ❌ | ✅ | ❌ |
| Direct update | 2 | ✅ (when fields present) | ❌ | ❌ | ✅ | ❌ |
| Proposal confirm | 3, 4, 5 | ✅ | ❌ (no re-check) | ❌ (no re-check) | ✅ | ✅ |
| Status-only | 6, 7, 8, 9 | ❌ | N/A | N/A | N/A | Varies |
| Non-mutating proposals | 10–14 | ❌ (by design) | N/A | N/A | N/A | N/A |
| Bernie tooling (non-write) | 15, 20, 21, 22, 23 | ❌ | N/A | N/A | N/A | N/A |
| Slot search | 24–27 | ❌ | N/A | ✅ (some paths) | N/A | N/A |
| Read-only | 28–33 | ❌ | N/A | N/A | N/A | N/A |

---

## 7. Key Code References

| Symbol | Location | Purpose |
|---|---|---|
| create_appointment | Line 984 | Raw direct create — highest-risk slot write |
| update_appointment | Line 4039 | Raw direct update — highest-risk slot write |
| _create_appointment_from_body | Line 869 | Shared create implementation (used by raw + confirm) |
| _apply_appointment_update | Line 3951 | Shared update implementation (used by raw + confirm) |
| _canonical_time_values | Line 474 | Time canonicalization — no past-date guard |
| _raise_if_conflict | Line 703 | Conflict detection only — no temporal guard |
| _raw_compat_evidence_and_headers | Line 219 | Raw compat audit tag + off mode bypass |
| confirm_create_proposal_route | Line 1153 | Proposal confirm (create) — freshness gated |
| confirm_update_proposal | Line 1762 | Proposal confirm (update) — freshness + state gated |
| confirm_bernie_create_proposal | Line 6569 | Bernie proposal confirm (create) — freshness + session gated |
| propose_slot_search | Line 4785 | Slot search — has same-day window check |
| _canonical_create_values | Line 735 | Canonicalize create body — no temporal guard |
| Bernie temporal axis | ~Line 3656 | Bernie-specific temporal evaluation — not applied to raw routes |

---

## 8. Completion Notes

- **Worker:** DeepSeek Flash
- **Artifact created:** docs/receptionist_review_r7_route_inventory.md
- **Scope respected:** No edits to app/ or tests/. Only this document and worker completing notes.
- **Action required:** Submit via host; Python/git environment unavailable to this worker. Artifact is complete.
