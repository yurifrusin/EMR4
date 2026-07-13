# T1 Stateful Diary Scenario Laboratory

Status: in progress; T1.1 foundation + T1.2 external-event state matrix complete

Date: 2026-07-13

## Outcome

The existing Bernie YAML replay harness now supports deterministic stateful
booking workflows rather than interpretation-only or isolated route turns.

T1.1 adds:

- a scenario-local clinic clock, defaulting to 08:00 on `reference_date`;
- allowlisted `initial_state.seeded_appointments` using the fixture patient and
  practitioner;
- a first-class `supervise` turn for the real DB-backed deterministic
  `/proposals/bernie/supervised-booking` route;
- confirmation from the supervised route's authoritative
  `staff_review.confirm_payload`;
- exact per-turn appointment and audit-row delta assertions; and
- optional redacted `bernie.scenario.evidence.v1` JSON output through
  `BERNIE_SCENARIO_EVIDENCE_DIR`.

The evidence record contains action, status, result kind, safety/confirmation
flags, and row deltas. It excludes raw instructions, request/response bodies,
and entity identifiers.

T1.2 adds:

- a canonical `external_appointment` scenario action for fixture-owned
  mid-scenario appointment events (operations: `create`, `set_status`);
- the action is allowlisted and validated at load time: only known fields,
  positive bounded duration, recognised patient/practitioner aliases, and
  supported statuses are accepted; unknown fields and unsupported operations
  are rejected;
- fixture events are tracked separately from product writes in the evidence
  record via `fixture_event_count` and do not affect the per-turn
  `appointment_delta`/`audit_delta` assertions — they are scenario-environment
  mutations, not Bernie or system product writes;
- the existing fake-provider guard and deterministic clinic-local clock are
  preserved.

## Golden Scenarios

### T1.1

`booking_create_then_exact_duplicate.yaml` reproduces Yuri's reported workflow:

1. interpret a request for Margaret Thompson with Dr Shera tomorrow between
   15:00 and 16:30;
2. supervise and explicitly confirm the first candidate;
3. prove exactly one appointment and audit row were written;
4. repeat the same natural-language request; and
5. receive `existing_booking_found`, no confirmation payload, and zero further
   appointment/audit writes.

`booking_seeded_exact_duplicate.yaml` proves the same classifier against an
allowlisted appointment seeded before replay. Seed rows form initial state and
are excluded from product-write deltas.

### T1.2 — Booking State Transition Matrix

Four new golden scenarios use the `external_appointment` action to distinguish
between booking states that an exact-duplicate classifier must handle:

| Scenario | Setup | Expected Outcome |
|---|---|---|
| `booking_overlap_not_exact_duplicate` | External `create` at 15:00-15:15 same patient/practitioner | `existing_booking_found` — exact match detected via external event |
| `booking_same_day_distinct_not_exact_duplicate` | Seed at 09:00 + external `create` at 10:00; request 15:00 | `confirmation_ready` — distinct times not treated as duplicate |
| `booking_terminal_status_not_existing` | Seed at 15:00 Booked → external `set_status` Cancelled; request same slot | `confirmation_ready` — cancelled appointment does not masquerade as existing |
| `booking_stale_confirm_revalidates` | Interpret + supervise → external `create` conflicting slot → confirm | `safe=false`, no write — stale confirm fails closed |

The stale-confirm scenario proves that an appointment inserted between
proposal preparation and the confirm call causes the confirm endpoint to return
`safe=false` without creating a second booking or audit row.

## External Appointment Action Schema

The `external_appointment` action is a turn-level action that creates or mutates
appointment rows as scenario-environment events. It is not a product operation
and does not count toward `appointment_delta` or `audit_delta`.

```yaml
- action: external_appointment
  input:
    operation: create              # or set_status
    patient: Margaret Thompson      # fixture alias or {patient_id}
    practitioner: Dr Shera         # fixture alias or {practitioner_id}
    date: "2026-07-15"            # required for create
    time: "15:00"                 # required for create
    duration_minutes: 15          # positive int; defaults to 15
    status: Booked                # required for create, required for set_status
    id: ext-appt                  # optional alias for {appointment_id:ext-appt}
    appointment_id: existing      # required for set_status; references a prior
                                  # seed or external appointment by alias
```

## Baseline Repair

The scenario runner previously used wall-clock time despite fixture
`reference_date` values. On 2026-07-13 this made three otherwise deterministic
fixtures fail as their requested times moved into the past. Pinning
`_clinic_local_now` to scenario state restored the demo confirmation path,
default-duration interpretation, and full-name interpretation without changing
runtime product code or fixture expectations.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\bernie_scenarios\ tests\test_bernie_scenario_integrity.py -q
```

Result: all 56 executable cases passed; one pre-existing expected-xfail and one
pre-existing missing-directory skip remained.

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_evidence_snapshot.py -q
```

Result: all 9 evidence snapshot tests passed.

## Boundaries

- fake provider only;
- DB-backed E1 route replay, not live-provider evidence;
- seeded/external state is test-only and allowlisted;
- no application route, schema, UI, provider, deployment, or write-authority
  behaviour changed;
- no PHI-bearing replay artifacts are emitted;
- fixture events are tracked separately via `fixture_event_count` and excluded
  from product delta assertions.

## Next T1 Increment

T1.3 should add selected controlled-backend Playwright evidence for the
diary grid interaction surface, keeping autonomous/model-to-database writes,
patient-specific consultant runtime, reception triage, PHI-enabled new
providers, live clinical pilots, deployment/release, external clients,
H15/historical-trove runtime use, memory/RAG/GraphRAG authority, and
GraphQL mutations closed.
