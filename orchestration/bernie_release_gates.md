# Bernie Release Gates

This checklist records the Sprint 97 release rule for Bernie reception work.
It exists to prevent Sprint 96's false pass pattern from recurring: a basic
happy path must be release evidence, not optional post-closeout user review.

## Blocking Happy Path

A Bernie sprint that changes booking interpretation, candidate selection,
confirmation, staged diary preview, staff-facing Bernie copy, or release/review
harnesses cannot close unless the ordinary receptionist prompt is verified as a
release gate:

```text
Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45
```

The gate may be deterministic, provider-backed, or both, depending on the
sprint scope. It must state the exact execution mode, expected outcome, and
evidence. If this ordinary prompt fails in the relevant release surface, closeout
status is blocked until fixed or the sprint is explicitly narrowed away from
Bernie booking interpretation and documented as such.

## Read-Only Schema Awareness

Bernie may know the Diary domain in detail through read-only, source-derived
schema/manifest context: statuses, reason-code policies, confirmation envelope
shape, receptionist-facing states, and backend transition boundaries. This is
desirable because it lets Bernie become a native translator between ordinary
reception language and the Diary's own movement/state grammar.

That knowledge must never become authority. A model response, whether Gemini,
fake provider, or another provider, cannot create live availability facts,
choose between ambiguous patients/practitioners, invent status or reason codes,
grant `writes_authorized=True`, skip staff confirmation, or bypass backend
signed evidence. The backend and signed confirmation routes remain the only
write authorities; manifest literacy is an interpretation aid only.

## Test Label Rules

- A test that intercepts HTTP routes, uses `page.route(...)`, serves fixture
  payloads, stubs Office, runs with `?smoke=true`, or uses fake/mocked provider
  output is a deterministic, route-intercepted, fixture, fake-provider, or
  mocked-provider check. It must not be described as live.
- A true live-provider check must reach the configured provider path without a
  local route intercept or mocked provider factory, and the resulting evidence
  must include provider metadata showing `live_provider: true`.
- A live UI check means the deployed or local UI made real non-intercepted API
  calls to the intended backend. If the browser/API path is intercepted, call it
  route-intercepted even when the UI is rendered in a real browser.

## Browser Driver and Automation Protocol

The browser driver does not determine the evidence class. Interactive browser
control and a task-scoped Playwright script are equally valid when they exercise
the same visible UI and backend boundary. For repeatable S0-S7-style acceptance,
prefer Playwright when it can encode stable selectors, serial synthetic fixture
transitions, screenshots, sanitized request/outcome summaries, and database
readback more economically than manual control.

A Playwright run is `live_local_browser_backend_postgres` only when the Diary
runs in a real browser and its API calls reach the real local FastAPI and
isolated PostgreSQL path without `page.route(...)`, proxy interception, fixture
responses, or mocked transport. Direct HTTP support is separately labelled
`live_local_backend_postgres`. Any intercepted browser path is labelled
`route_intercepted_browser`, even if Playwright renders the full UI.

Automation must click the visible explicit confirmation control, must not call
page internals to simulate staff authority, and must validate backend-owned
appointment, audit, idempotency, typed-receipt, and readback evidence. Saved
artifacts must exclude credentials, bearer tokens, raw headers, or secret-bearing
traces. Protected-safe runs use exact allowlisted paths and exact pytest node IDs
only; browser scripting does not authorize repository-wide discovery.

## Provider-Free Interpretation Harness Gate

The provider-free Bernie Interpretation Harness is not runtime or provider
readiness evidence by itself. It is an authored synthetic contract surface for
mapping small receptionist utterance fixtures to native Diary action grammar,
projected fake-provider-style frames, safe aggregate reports, and blocked
runtime-gate status.

Before any sprint proposes runtime route wiring, provider prompt wiring,
provider dry-run wiring, memory/RAG/GraphRAG use, H15/H-series runtime imports,
or historical diary material access from the interpretation harness, Ariadne
must run and record:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
```

The expected current result is `runtime_or_provider_wiring_ready=false`,
`raw_trove_access_ready=false`, and `runtime_gate_decision=blocked`. If those
values change, or if the readiness command fails, the sprint engine must pause
for explicit review instead of continuing automatically.

Before any sprint proposes enabling, expanding, aliasing, or dry-running a
Bernie booking interpreter provider boundary, Ariadne must also run and record:

```powershell
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
```

The expected current result is `default_provider=disabled`,
`runtime_or_provider_wiring_ready=false`, `live_provider_enabled=false`,
`provider_calls_performed=false`, `route_behavior_changed=false`,
`database_access_performed=false`, `memory_or_rag_access_performed=false`, and
`historical_diary_material_access_performed=false`. If those values change, or
if the provider-boundary report fails, the sprint engine must pause for
explicit review instead of continuing automatically.

The report's `proposal_citation_required_fields` list is the source of truth for
which provider-boundary report fields a proposal must cite. The current list is
`default_provider`, `runtime_or_provider_wiring_ready`,
`live_provider_enabled`, `provider_calls_performed`,
`route_behavior_changed`, `database_access_performed`,
`memory_or_rag_access_performed`, and
`historical_diary_material_access_performed`.

## Practitioner Directory Route Readiness Gate

The practitioner-directory route-scoped readiness status is a static release and
review artifact only. It records that `GET /api/v1/practice/practitioners` has
route-scoped `rest_route_ready=true` approval for authenticated internal-staff
read use while the global external-readiness snapshot remains unchanged.

Before any sprint proposes consuming the route-scoped practitioner-directory
readiness status from runtime app code, the global external-readiness DAG,
deployment gates, GraphQL resolver work, provider prompts, memory/RAG/GraphRAG
access, external patient-client surfaces, or write authority, Ariadne must run
and record:

```powershell
.venv\Scripts\python.exe scripts\practitioner_directory_route_readiness_release_check.py
.venv\Scripts\python.exe scripts\practitioner_directory_route_readiness_status.py
```

The preferred static release check is
`scripts\practitioner_directory_route_readiness_release_check.py`, which wraps
the route-scoped readiness status with the Sprint 261 consumer boundary and may
be used only by static CI/pytest release gates or developer-facing release
summaries. The expected current values are `static_release_check_ready=true`,
`runtime_consumers_allowed=false`, `rest_route_ready=true`,
`global_readiness_snapshot_updated=false`, `adjacent_gate_false_count=8`,
`deployment_ready=false`, `production_ready=false`,
`external_patient_client_ready=false`, `pause_required=false`, and
`sprint_engine_state=continuing`. If those values change, or if the command
fails, the sprint engine must pause for explicit review instead of continuing
automatically.

## Practitioner Directory GraphQL Release Boundary Gate

The practitioner-directory GraphQL release-boundary packet is a proposed
approval surface for `Query.practice.practitioners` only. Until Yuri approves
`docs/api-spine/practitioner-directory-graphql-release-boundary.json`, internal
consumer development remains unauthorized even though the resolver and hardening
tests pass.

Before any sprint proposes internal consumer development, readiness promotion,
deployment or production exposure, external-client access, schema field
expansion, mutation/subscription authority, write authority, provider or memory
use, H15/H-series runtime imports, or historical diary/trove access from this
GraphQL path, Ariadne must run and record:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_graphql_release_boundary.py tests\test_practitioner_directory_graphql_contract_hardening.py -q
```

Expected current values after Yuri's Sprint 272 approval are
`decision=release_boundary_approved_for_internal_staff_consumer_development`,
`internal_consumer_development=true`,
`readiness_flag_changes=false`, `deployment_or_production_exposure=false`,
`external_client_access=false`, `schema_field_expansion=false`,
`write_mutation_or_subscription=false`,
`provider_memory_rag_graphrag_h15_trove=false`,
`approved_contract_commit=d4ed14d3`, `approval_expires_on=2026-08-06`, and
`go_no_go_acknowledged=true`. If any other value changes without explicit Yuri
approval, the sprint engine must pause.

## Practitioner Directory Office Add-in GraphQL Switch Gate

The Office add-in practitioner selector must not send GraphQL traffic or edit
`docs/diary/diary.js` or `EMR4 Sidebar/src/taskpane/taskpane.js` for the
GraphQL practitioner path until Yuri explicitly approves
`docs/api-spine/practitioner-directory-office-addin-graphql-consumer-switch-approval-packet.json`.

Before any such implementation sprint, Ariadne must run and record:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_practitioner_directory_office_addin_graphql_consumer_switch_approval_packet.py tests\test_practitioner_directory_office_addin_graphql_mock_contract.py tests\test_practitioner_directory_graphql_release_boundary.py -q
```

Expected current values after Yuri's Sprint 278 approval are
`decision=approved_for_default_off_office_addin_graphql_practitioner_selector_switch`,
`approval_required_before_code=true`,
`office_addin_taskpane_runtime_implementation=true`,
`office_addin_live_graphql_traffic=false`,
`taskpane_js_edits_for_graphql=true`, `feature_gate_added=true`,
`proposed_switch_approval_expires_on=2026-08-06`,
`runtime_taskpane_switch_ready=false`, `telemetry_endpoint_ready=false`,
`deployment_ready=false`, `production_ready=false`,
`external_patient_client_ready=false`, `write_authority_ready=false`,
`provider_or_memory_ready=false`, and
`h15_h_series_historical_diary_ready=false`. If any value changes without Yuri
approval, the sprint engine must pause.

### Proposal Surface Guard

Any new markdown proposal artifact that discusses runtime route wiring, provider
prompt wiring, provider dry-run wiring, memory/RAG/GraphRAG use, H15/H-series
runtime imports, historical diary material access, or a runtime/provider/trove
proposal from the interpretation harness must also pass:

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_proposal_surface_guard.py <proposal-path>
```

The guard requires the proposal to include the readiness command and the expected
blocked values:

- `runtime_or_provider_wiring_ready=false`
- `raw_trove_access_ready=false`
- `runtime_gate_decision=blocked`

## Closeout Rules

- Basic Bernie happy paths are blocking release checks, not residual user review.
- Route-intercepted Playwright/pytest results may satisfy deterministic coverage
  only when the closeout names them as route-intercepted.
- If a screenshot or visual failure has been reported and remains reproducible,
  the sprint cannot close as integrated/verified. Closeout must instead record
  the failure, reproduction path, owner, and next required fix.
- Residual user review may remain only for checks Ariadne cannot safely perform
  with available tools, such as Yuri's clinical judgment, real-world phone/device
  context, external account ownership, or production service-console decisions.

## Stage 2 Durable Appointment-Create Gate

The approved provider-free Stage 2 local synthetic tranche may close only when
the existing REST Bernie create-confirm variant proves all of the following in
one database authority boundary:

- durable session recovery and ordered event reconstruction after a fresh
  SQLAlchemy session;
- one accepted and one typed stale result for concurrent requests based on one
  session revision;
- exactly one appointment, append-only audit, completed idempotency result,
  confirmation outcome, and stored receipt for simultaneous same-key confirms;
- complete rollback after an injected pre-commit failure, followed by one clean
  retry and a mutation-free fresh-session replay;
- exact command, appointment, audit, retained session coordinate, and receipt
  correlation;
- route-level same-practice checks plus forced PostgreSQL RLS reproduced under
  a non-bypass role with missing context failing closed; and
- direct audit `UPDATE` and `DELETE` rejected independently of RLS.

This gate is local synthetic evidence only. It does not provision a production
database role, authorize PII, deploy a scheduler or cleanup job, add another
appointment action, enable GraphQL mutations, reopen providers, or grant Bernie
confirmation authority.

## Sprint 98 Screenshot Blockers

Sprint 98 release gates must also block the exact regression classes reported
from Yuri's live screenshots:

1. **Resolved practitioner must not become raw missing ID copy.** If the ordinary
   prompt resolves `Dr Shera` to a practitioner, the backend/UI release surface
   must not show `missing_practitioner_id`, `practitioner_id`, raw UUIDs, or
   `Practitioner ID is required` to ordinary reception staff. Developer/debug
   diagnostics may show typed codes only behind the existing debug gates.
2. **Selected booking slot must have a path back.** After staff choose one Bernie
   candidate booking slot and a proposed appointment is staged, the Bernie panel
   must provide a visible path back to the candidate list so staff can choose a
   different slot without closing/reloading the diary.
3. **Confirm failures must be typed, not generic Not Found.** Clicking
   `Confirm booking` must call the configured Bernie confirm endpoint and render
   success or a typed, receptionist-safe failure. A bare `Not Found` / 404 detail,
   raw route error, raw UUID, or snake_case implementation detail in ordinary
   mode blocks closeout.

Recommended blocking evidence:

- Backend/API: focused pytest for the ordinary prompt interpretation ->
  supervised booking contract, confirmation-ready practitioner evidence, and
  invalid/stale confirm payloads returning the typed Bernie confirmation
  envelope with no appointment/audit write.
- Smoke script: deterministic `scripts/smoke_bernie_interpreter.py` run proving
  the ordinary prompt parses `14:00` to `15:45` and carries resolved
  practitioner/patient IDs while compact output remains redacted.
- Route-intercepted UI: `review/test_diary_smoke.py` coverage proving candidate
  slots render, selected-slot state has a visible choose-another-slot path,
  confirming calls `/api/v1/appointments/proposals/create/confirm-bernie`, and
  ordinary panel/card text excludes raw IDs, `missing_practitioner_id`, and
  generic `Not Found`.
- Live/deployed Diary: only a non-intercepted browser/backend/provider run may
  be called live. If not run or not proven, closeout must explicitly say live
  Diary readiness is deferred; route-intercepted checks are not a substitute for
  live evidence.

## Minimum Sprint 97 Evidence

Before Sprint 97 closes, Ariadne should be able to point to all of:

1. A deterministic automated gate for the Margaret Thompson / Dr Shera ordinary
   prompt.
2. Clear labeling that route-intercepted checks are not live checks.
3. A live-provider readiness result: either a true provider-backed pass with
   `live_provider: true`, or a blocked/deferred release note that explicitly
   says live-provider readiness was not proven.
4. A screenshot-failure status: fixed and no longer reproducible, or sprint
   closeout remains blocked.
