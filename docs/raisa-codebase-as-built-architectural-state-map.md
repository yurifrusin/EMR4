# EMR4 as-built architectural state map

Date: 2026-08-11

Reviewed source: `95ce6b75723d57e672858619c3621d4a273c1f34`

This map is a read-only reconstruction of the repository at the reviewed
source. It is not a deployment inventory, runtime-health claim or authority
grant. The status labels deliberately separate code presence from mounting,
default enablement and future intent.

## State vocabulary

| State | Meaning |
|---|---|
| `mounted_current` | Imported by `app.main` and part of the ordinary application surface. |
| `mounted_default_off` | Mounted code exists, but its special capability remains behind an explicit default-off setting and any additional role/practice gate. |
| `accepted_unmounted` | Accepted contract, service, adapter, client or database artifact exists but ordinary `app.main` does not mount or apply it. |
| `future_planned` | Direction is accepted, but implementation/runtime authority has not been granted or completed. |
| `retired_historical` | Retained for provenance, evidence or superseded design context; it is not current product architecture. |

## Current composition

| Area | State | As-built boundary |
|---|---|---|
| FastAPI application shell | `mounted_current` | `app/main.py` mounts authentication, patients, clinical, letters, consultation, search, appointments, Diary, committed-event, development-fixture, practice, practice-administration and GraphQL routers. The development fixture router separately requires `ENVIRONMENT=dev` and an authenticated user. |
| Authentication and tenancy | `mounted_current` | Shared bearer authentication and practice-scoped users feed both REST and GraphQL. Non-development startup rejects the public default JWT secret. |
| Appointment and Diary REST surface | `mounted_current` | Reads, compatibility CRUD, proposal/confirm command families, Bernie session support, slot search and Diary operations are concentrated in `app/routers/appointments.py`. State-changing endpoints require one of the mutating appointment roles. Canonical confirm families own durable idempotency and audit/readback; raw compatibility writes remain explicitly supported and audit-labelled. |
| Practitioner directory GraphQL | `mounted_current` | `/api/v1/graphql` exposes a Query-only runtime: health plus practice-scoped practitioners. It has no Mutation or Subscription root, requires existing bearer authentication, constrains depth/tokens/aliases, reuses the REST read service and suppresses cross-practice data. |
| Practitioner directory REST | `mounted_current` | `GET /api/v1/practice/practitioners` is an authenticated, practice-scoped read with bounded pagination and privileged inactive-record access. |
| Practice-administration reads/advisory | `mounted_current` | Practice-location and administration projections are backend-owned. Advisory output remains non-authoritative and proofread. |
| Committed Diary event feed | `mounted_default_off` | The route is mounted, but `reception_one_committed_event_runtime_enabled` defaults false. Events are typed signals for a fresh authorized read, not command authority. |
| Reception One product-context planner | `mounted_default_off` | Separate runtime, exact synthetic-practice and provider gates default false. The provider-free path is isolated from the legacy Bernie provider setting. |
| Rayleen A4 read and A5 check-in | `mounted_default_off` | Separate feature and authored-synthetic practice gates default false. A5 is a narrow human-confirmed arrival command; it is not a generic status actuator. |
| Davida default-location command | `mounted_default_off` | A separate runtime flag, practice allowlist and server secret all fail closed by default. |
| Legacy Bernie interpreter provider | `mounted_default_off` | The REST interpretation route is mounted but the provider setting defaults `disabled`, and a repository gate blocks live provider configuration. The legacy fallback setting still defaults true and is therefore a future conformance hazard, not an active provider opening. |
| Native-Diary application-session practitioner composition | `accepted_unmounted` | Separate GraphQL/application factories and client composition evidence exist; the ordinary application does not mount those factories. |
| Rayleen waiting-room projection and Context Fabric adapter | `accepted_unmounted` | Typed read projection, invalidation/reassembly and fresh-generation artifacts pass over authored-synthetic evidence. They do not create an ordinary production route or source watcher. |
| Practice Context Fabric and Bureau Memory Bank | `accepted_unmounted` | Typed `ContextNeed`/`ContextFrameSet`, temporal weave, memory, source-adapter and durability artifacts exist. The PostgreSQL DDL and behavior evidence are not an applied migration or operational persistence layer. |
| Context Fabric watcher/listener and operational source access | `future_planned` | No operational watcher, feed, outbox consumer, source credential, retention operation or product-data assembly is opened. |
| Agent Execution Surface and Containment Gate | `future_planned` | AES-C0 through AES-C5 are planned. No capability broker, work-cell runtime, lease, credential flow, tool or occupied product-context cell exists. |
| Consultant and Clinician One Bureaus | `future_planned` | Safety-first differential doctrine and future requests/referrals, prescribing and billing directions are recorded. They grant no clinical model, data or command authority. |
| Word/SharePoint Living Diary | `retired_historical` | Superseded by the native HTML/JavaScript Diary with PostgreSQL appointment truth. Some overview diagrams and phase tables still show the old design. |
| LC4 model-evaluation/certification modules | `retired_historical` | Sealed development and holdout evidence remains under `app/services/bernie`. It is not mounted product behavior, but its co-location with current domain code currently complicates safe whole-tree verification. |

## Critical authority and transaction paths

### Read path

`authenticated user -> REST GET or GraphQL Query -> practice/patient scope ->
shared read service -> PostgreSQL truth -> minimized typed projection`

GraphQL stops at this path. Runtime tests explicitly prohibit Mutation and
Subscription roots, provider/memory/write imports, sensitive practitioner
fields and cross-practice disclosure.

### Appointment command path

`authenticated mutating role -> proposal/current read -> explicit confirmation
-> REST command -> idempotency claim -> domain validation -> transaction ->
audit -> deterministic readback`

The canonical proposal/confirm families implement the intended API Spine.
Raw compatibility CRUD remains a deliberately supported transitional side
path; it is role-gated and audit-labelled, but does not receive the canonical
proposal-confirm idempotency envelope.

### Event consequence path

`committed backend event -> practice/practitioner scope -> duplicate and
relevance suppression -> fresh authorized read -> quiet UI cue`

The event is never accepted as current truth or a command. The default-off
runtime preserves this separation.

### Future Bureau path

`authorized request -> minimized ContextNeed -> typed expiring ContextFrameSet
-> occupied model cell -> deterministic proofreader -> proposal only ->
separately authorized REST command -> deterministic readback`

The planned external capability broker belongs between the proofreader and
every provider, read, tool or command adapter. It must not inherit ambient
credentials or allow the model to select destinations, methods or executables.

## Concentration and lifecycle observations

- The application contains 233 Python files and about 89,195 lines at the
  reviewed source.
- `app/routers/appointments.py` contains 8,658 lines, 36 route decorators, 189
  top-level functions and 33 imports. It combines current reads, legacy writes,
  canonical commands, session behavior, model interpretation and several
  default-off descendants.
- `app/services/bernie` contains 75 Python files spanning mounted domain
  contracts and sealed historical evaluation/holdout machinery. The current
  verification allowlist intentionally excludes the directory as a whole and
  admits only two named files.
- `docs/api-spine` preserves the complete decision history, but has no one
  canonical current-state index. Early gap inventories and later runtime
  implementations therefore coexist without a machine-checkable supersession
  relationship.

## Claim boundary

This map proves only repository composition and selected local tests at the
reviewed source. It does not prove deployment state, operational database
health, concurrency, production configuration, provider availability, clinical
safety, product-data admission or exhaustive absence of defects.
