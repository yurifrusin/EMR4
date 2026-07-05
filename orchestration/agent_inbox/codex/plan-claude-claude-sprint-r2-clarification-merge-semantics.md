# plan-claude-claude-sprint-r2-clarification-merge-semantics

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-sprint-r2-clarification-merge-semantics` |
| Status | integrated |
| Created | 2026-07-05 14:12 +1000 |
| Source HEAD | `89cb837` |

## Plan Summary

Add selective clarification-merge to Bernie's read-only interpret route so a clarification reply carries forward already-resolved patient/practitioner/date/time/duration from a prior request frame (new-reply-wins, gap-fill only), plus a test-only NL scenario executor to promote the R1 xfail clarification fixtures where deterministic.

## My Understanding

The interpret endpoint (/api/v1/appointments/proposals/bernie/interpret-booking-instruction) is stateless per instruction. A clarification reply is a fresh instruction; the deterministic path (_extract_fake_command -> _resolve_bernie_interpretation_context) only carries forward practitioner_id, patient_id (context_frames) and date_from (resolve_booking_date_transition). earliest_time/latest_time, duration_minutes, appointment_type_id, location_id, date_to are NOT carried, so replies like 'A long appointment is 30 minutes' or 'With Dr Shera please' drop resolved patient/date/time and re-ask known fields. Antigravity corpus fixtures (booking_clarify_*, clarification_reply_merges_missing_field_only) encode the target and are xfail; they use NL user-turn shape which loader.py skips as NonExecutableScenario.

## Intended Surface / Boundary

Backend clarification-merge in the interpret route + a small pure carry-forward helper, and a TEST-ONLY harness NL executor. NOT touched: diary grid, cards, booking slots, panels, waiting-room, status controls; Bernie staff copy; persisted session tables; GraphRAG; live provider calls; mutation grammar; D8 collision hardening.

## Out Of Scope

Diary visual redesign, UI copy rewrites, persisted session tables, live Gemini/provider calls, auto-mode, unrelated patient-collision hardening, raw appointment mutation grammar changes.

## Files I Expect To Edit

app/routers/appointments.py (extend _resolve_bernie_interpretation_context carry-forward + selective merge); possibly app/services/bernie_transition_table.py or a small new pure merge helper; NEW tests/test_bernie_clarification_merge.py; tests/bernie_scenarios/loader.py + replay.py (or new NL executor module); the four corpus fixtures (flip xfail only where deterministically green, Antigravity-owned).

## Implementation Steps

1) Pure helper merge_clarification_command(prior_frame,new_command): per field practitioner_id/patient_id/date_from/date_to/earliest_time/latest_time/duration_minutes/appointment_type_id/location_id keep new when present else carry prior (new-reply-wins, gap-fill only). 2) Represent existing frame as context frame type=requested_appointment (aligned with BernieRequestedAppointmentFrame.payload); seed command_values gaps before existing practitioner/patient/date resolution which stays authoritative. 3) Emit assumption/axis note for merged fields; do not report carried fields as missing_fields; preserve intent literal and request_reference_date immutability. 4) Keep read-only: no appointment/audit rows, no provider call. 5) HTTP tests: turn1 clarification_required preserving patient/date/time + correct missing; turn2 reply + requested_appointment frame -> interpreted preserving patient/practitioner/date/time and filling clarified field; assert zero new Appointment/AppointmentAuditLog rows. 6) Harness NL executor: parse user+expect.outcome/preserved/missing, drive interpret (fake provider, DB name resolution, forbidden-provider guard), thread request frame between turns, map interpreted->proceed and optionally supervised booking for confirmation_ready where deterministic; assert preserved fields + no pre-confirm mutation. 7) Promote corpus fixtures off xfail where deterministic; keep documented xfail for confirmation_ready turns needing non-deterministic seeding. 8) Verification.

## Visual / Behavioural Acceptance Checks

No visual changes. 'A long appointment is 30 minutes' after a long-appt clarification keeps Margaret Thompson/Dr Shera/2026-07-14/15:30 and fills duration_minutes=30 without re-asking practitioner or date. 'With Dr Shera please' fills practitioner and keeps patient/date/time plus default 15-min duration. Forbidden: no diary mutation before confirmation, no lost patient identity, no date/time drift.

## Risks / Ambiguities

Outcome-vocab bridge: interpret returns 'interpreted' but corpus expects 'confirmation_ready' (supervised-booking result) needing seeded schedule/roster; non-deterministic turns stay xfail with documented reason while still proving merge via interpret. Corpus fixtures are Antigravity-owned; flipping xfail edits their files (limit to the flag, flag to Codex). Stale carry-forward risk mitigated by new-reply-wins + gap-only fill. _resolve_bernie_interpretation_context also hosts same-day clamp + D6/D8 advisory/collision logic; must not regress existing interpret/collision tests.

## Codex Plan Review

- Review result: Accepted and integrated through Sprint R2.
- Required changes before implementation: Bound implementation to backend clarification merge semantics and focused tests.
- Approved to proceed: yes
