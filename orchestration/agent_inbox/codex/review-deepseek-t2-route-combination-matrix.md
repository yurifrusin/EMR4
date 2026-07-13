# Review: T2.3 DB-Backed Route Combination Matrix

| Field | Value |
|---|---|
| **Role** | bounded backend route-test implementation worker |
| **Model** | DeepSeek Flash (`deepseek-v4-flash`) via Deep Code |
| **Parent** | `docs/bernie-t2-deterministic-behaviour-matrix.md` |
| **Task packet** | `orchestration/agent_inbox/deepcode/deepcode-flash-t2-route-combination-matrix.md` |
| **Worker branch** | `deepcode/t2-route-combination-matrix` |

---

## Summary

Added a compact DB-backed route combination matrix for `POST /api/v1/appointments/proposals/slot-search`.
The new test file `tests/test_slot_search_proposal_combination_matrix.py` exercises the real
authenticated route against the test DB across 16 authored scenarios (17 test cases including
the non-mutating proof) covering all required acceptance dimensions.

## Scenario Table

| Case ID | Description | Scenarios | Key Assertion |
|---|---|---|---|
| `BASE-01` | Baseline: no appointment, roster present, 15-min | 1 | All slots free, 09:00 available |
| `ST-BOOKED` | Booked blocks overlapping slot | 1 | 09:00 blocked |
| `ST-CONFIRMED` | Confirmed blocks overlapping slot | 1 | 09:00 blocked |
| `ST-ARRIVED` | Arrived blocks overlapping slot | 1 | 09:00 blocked |
| `ST-INCONSULT` | InConsult blocks overlapping slot | 1 | 09:00 blocked |
| `ST-COMPLETED` | Completed blocks overlapping slot (terminal/blocking) | 1 | 09:00 blocked |
| `ST-CANCELLED` | Cancelled does NOT block (terminal/non-blocking) | 1 | 09:00 available |
| `ST-NOSHOW` | NoShow does NOT block (terminal/non-blocking) | 1 | 09:00 available |
| `ST-DNA` | DNA does NOT block (terminal/non-blocking) | 1 | 09:00 available |
| `LOC-SAME` | Same-location Booked blocks; search same location | 1 | 09:00 blocked |
| `LOC-OTHER` | Booked at site A; search at site B: NOT blocked | 1 | 09:00 available |
| `DUR-30BLOCK` | 30-min appointment blocks two 15-min slots | 1 | 09:00 + 09:15 blocked, 09:30 free |
| `BND-EARLIEST` | earliest_time=10:00 filters earlier slots | 1 | 09:00 blocked by bound |
| `BND-LATEST` | latest_time=11:00 caps candidates | 1 | Candidates < 11:00 |
| `BND-BOTH` | earliest=10:00 + latest=11:00, 30-min duration | 1 | Candidates in [10:00, 11:00) |
| `ROSTER-ABSENT` | No schedule for requested date | 1 | Zero candidates + no_practitioner_schedule warning |
| `BREAK-OVERLAP` | Break yields warning at 10:30 but candidate offered | 1 | 10:30 present with break_overlap warning |
| **Non-mutating proof** | Representative cross-section of search calls | 1 | Zero appointment/audit rows created |

**Total: 18 test cases (16 matrix scenarios + 1 parametrized baseline + 1 non-mutating proof)**

## Acceptance Coverage

| Acceptance Criterion | Covered By |
|---|---|
| Exercise real authenticated route against test DB | All scenarios via `client.post(SEARCH_URL)` with JWT |
| Active + every terminal status relevant to slot blocking | Booked, Confirmed, Arrived, InConsult (active/blocking); Completed (terminal/blocking); Cancelled, NoShow, DNA (terminal/non-blocking) |
| Same-location blocking | `LOC-SAME`: Booked at site A, search at site A → blocked |
| Other-location non-blocking | `LOC-OTHER`: Booked at site A, search at site B → free |
| 15/30-minute appointments with earliest/latest bounds | `DUR-30BLOCK` (30-min), `BND-EARLIEST`, `BND-LATEST`, `BND-BOTH` |
| Roster present/absent | All with-`has_roster` scenarios + `ROSTER-ABSENT` |
| Break-overlap warning without treating as booking conflict | `BREAK-OVERLAP`: 10:30 break yields warning; candidate still offered |
| Normalized date/time bounds per candidate | Every candidate checked for `appointment_date == search date`, correct duration, tz-aware start/end |
| Stable ordering | `starts_local == sorted(starts_local)` in every scenario |
| No occupied same-location overlap | Conflict statuses block 09:00; non-blocking statuses don't; location filtering works |
| No appointment/audit rows created | `test_matrix_overall_writes_no_appointments_and_no_audit_rows` |
| No regression on existing tests | All 21 existing `test_slot_search_proposal.py` tests continue to pass |
| CI budget | 18 test cases, ~10.4s runtime for new file, ~19.8s combined with existing |

## DB / Evidence Boundary

- Tests use `TestClient` against the real FastAPI app with test DB overrides
- `clean_db` truncates between tests (shared `conftest.py` fixture)
- Non-mutating proof: counts `Appointment` and `AppointmentAuditLog` rows before/after a representative cross-section
- No production code (`app/`) was changed
- No existing authored golden expectations were weakened or rewritten

## Changed Files

| File | Change |
|---|---|
| `tests/test_slot_search_proposal_combination_matrix.py` | **Created** — 18 test cases (16 parametrized matrix scenarios + 1 baseline + 1 non-mutating proof) |

## Test Results

```powershell
# New matrix tests only
pytest tests/test_slot_search_proposal_combination_matrix.py -v
# Result: 18 passed in 10.36s

# Combined with existing tests (no regression)
pytest tests/test_slot_search_proposal.py tests/test_slot_search_proposal_combination_matrix.py -v
# Result: 39 passed in 19.83s
#   - 21 existing tests PASS (no regression)
#   - 18 new matrix tests PASS
```

## Reused Coverage

- `conftest.py` fixtures: `client`, `db`, `gp_user`, `practice`, `practitioner`, `patient`, `make_token`
- Helper patterns from existing `test_slot_search_proposal.py`: `_search()`, `_base_body()`, `_make_appt()`
- Route: `POST /api/v1/appointments/proposals/slot-search` (unchanged)

## Findings

No product defects were identified. All 16 matrix scenarios behave as expected:

1. **Status filtering is correct**: Booked, Confirmed, Arrived, InConsult, and Completed all block overlapping slots; Cancelled, NoShow, and DNA do not. This matches `NON_BLOCKING_STATUSES = (Cancelled, NoShow, DNA)` in `app/routers/appointments.py`.
2. **Location filtering is correct**: Same-location appointments block; other-location appointments do not. This matches the `_filter_by_location` logic in the route.
3. **Duration blocking is correct**: A 30-minute appointment blocks both 09:00 and 09:15 15-minute search slots.
4. **Time bounds are applied correctly**: `earliest_time` excludes earlier slots; `latest_time` caps candidates.
5. **Roster absence yields zero candidates** with a `no_practitioner_schedule` warning.
6. **Break overlap yields a warning** at the overlapping slot without removing it as a candidate.
7. **The route is non-mutating**: No appointment or audit-log rows are created by any search call.
8. **Candidates maintain stable earliest-first ordering** in all scenarios.
9. **Every candidate has tz-aware times and correct duration.**

## Candidate Commit

A single clean commit with the new test file is ready. It does not edit `app/`, `review/`, `docs/diary/`, AGENTS, roadmap documents, orchestration policy, providers, schemas, migrations, or unrelated tests. It does not push, integrate master, or move `handoff/current`.

**STATUS: complete**
