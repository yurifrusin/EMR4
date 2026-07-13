# T1 Stateful Diary Scenario Laboratory

Status: in progress; T1.1 foundation complete

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

## Golden Scenarios

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

Result: all executable cases passed; one pre-existing expected-xfail and one
pre-existing missing-directory skip remained.

## Boundaries

- fake provider only;
- DB-backed E1 route replay, not live-provider evidence;
- seeded state is test-only and allowlisted;
- no application route, schema, UI, provider, deployment, or write-authority
  behaviour changed; and
- no PHI-bearing replay artifacts are emitted.

## Next T1 Increment

T1.2 should add an allowlisted mid-scenario external-state event so stale and
concurrent-change proposals can be reproduced without attributing fixture
mutations to Bernie. Then add overlap, same-day-distinct, terminal-status, and
stale-confirm golden cases before T1.3 controlled-backend Playwright evidence.
