# A5.1 Rayleen check-in command runtime — DeepSeek worker packet

Source head: `902040a551668bf8e5a1dd9abaae379224995eec`

Worktree:
`C:\Users\sarashera\EMR4-worktrees\model-required-bureau-a5-1-check-in`

Branch: `codex/worker-model-required-bureau-a5-1-check-in`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No fallback is authorised.

## Mandatory source pass

Read `AGENTS.md` completely and state the exact five rehydration sources. Read
`docs/emr4-model-required-bureau-a5-b4-command-runtime-plan.md`, its threat-model
delta, the controlled-recovery development plan, `orchestration/api_spine_adr.md`,
`orchestration/api_spine_programme.md`, `orchestration/bernie_release_gates.md`,
the API Steward skill and checklist, and only the relevant current appointment,
idempotency, committed-event, config, migration and API Spine sources. Verify the
exact branch/source and a clean worktree before editing.

## Exact task

Implement only plan section 4 and the A5.1 acceptance matrix: a dedicated,
default-off, authored-synthetic-practice-only, Receptionist-confirmed check-in
proposal/confirm command for exact `Booked|Confirmed -> Arrived`. Rayleen is
proposal provenance only. Reuse authoritative appointment/waiting-area truth;
do not widen the generic status-confirm route.

The proposal is non-mutating and returns one opaque HMAC-signed, maximum-
120-second, random-nonce, purpose-bound, actor/practice/appointment/state/
waiting-area/freshness-bound evidence token. Confirmation uses operation id
`confirmAppointmentCheckInProposal`, exact current-user practice and
Receptionist authority, row locking and fresh state/area checks. Same-key exact
replay returns the stored receipt before evidence consumption; same-key changed
fingerprint conflicts; different-key reuse of the evidence hash rejects even
after appointment state restoration. Claim concurrent evidence use through a
unique partial constraint and conflict-aware savepoint/insert path.

`waiting_area_id=<UUID>` may assign only when no waiting area is currently set.
Omitted/null preserves an existing area and never removes or moves it. Every
assigned or preserved area must be active, same-practice and have the same
non-null location as the appointment; an appointment without a resolved
location cannot be assigned an area.

One transaction updates status/optional area, appends exactly one command-bound
`AppointmentAuditLog`, appends exactly one patient-free
`diary.appointment_checked_in` / `diary.appointment_checked_in.v1` committed
event with the exact plan payload and reason code, and completes one bounded
idempotency receipt. Extend all three named committed-event constraints. Keep
the existing reschedule behavior unchanged and add exact reschedule event-type
filters to both cursor validation and row selection. Add no check-in consumer,
publisher or worker.

## Owned paths

- `app/config.py`
- `app/models/appointments.py`
- `app/models/diary_events.py`
- `app/routers/appointments.py`
- `app/routers/diary_events.py`
- `app/schemas/appointments.py`
- `app/services/appointment_idempotency.py`
- `app/services/diary_committed_events.py`
- `alembic/versions/v1w2x3y4z5a6_add_a5_check_in_runtime.py` (new provisional
  descendant of exact `u0v1w2x3y4z5`; Sol owns final cross-lane chain)
- `docs/api-spine/openapi/appointment-commands.yaml`
- `docs/api-spine/openapi/diary-committed-events.yaml`
- `docs/api-spine/async/integration-events.yaml`
- `tests/test_model_required_bureau_a5_1_check_in_runtime.py` (new)

Do not edit any other path. In particular do not edit `AGENTS.md`, the frozen
plan/threat/review artifacts, `app/main.py`, practitioner/practice-
administration sources, another migration, GraphQL, provider configuration,
deployment/workflows, Continuity/Compass global maps, `docs/branding/**`,
protected/historical evidence or the other worker lane.

## Required tests in the owned test file

Cover both valid source states, with/without assignment, preservation of an
existing area, non-mutating proposal, default-off and non-allowlisted rejection,
exact Receptionist-only authority, tamper/expiry/purpose/actor/practice failures,
location and active-area checks, null-location denial, stale state, no-op and
terminal-state denial, same-key replay, changed-body conflict, in-progress
denial, different-key evidence replay after deliberate state restoration,
concurrent distinct-key single winner, atomic rollback injection, exact audit
and event payload, reschedule-feed isolation, migration constraints and one
Alembic head. Assert zero patient-bearing fields and zero product-provider calls.

## Mechanics and forbidden claims

Use `apply_patch` only. Do not run PostgreSQL pytest or the acceptance script;
Sol holds the shared serial database/test lease. You may run Ruff, py_compile,
AST/static checks, YAML parsing and `git diff --check`. Stage only the owned
paths by explicit pathname, verify no `docs/branding/` path is cached, and
commit once to the worker branch. Do not fetch, merge, rebase, switch, push,
deploy or move protected refs.

This is local/provider-free/authored-synthetic command implementation only. No
patient, clinical, product-derived, participant, protected or production data;
no product-provider call, GraphQL mutation, autonomous action, external event
delivery, kiosk, voice, deployment, release, Pages or protected-ref authority.

Return the five-source statement, exact commit/files/checks/blockers and finish
with exactly one `DECISION: pass` or `DECISION: revision_required`.
