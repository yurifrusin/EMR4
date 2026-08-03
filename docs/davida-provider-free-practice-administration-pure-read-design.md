# Davida provider-free practice-administration pure-read design

Date: 2026-08-03

Status: provider-free, unmounted, non-executing, authored-synthetic

Boundary classification:
`provider_free_practice_administration_pure_read_projection`

## 1. Position in the Davida lane

This tranche is the first implementation step after the accepted
architecture-only boundary. It retains the accepted active-practitioner
projection as the pure-read precedent, adds a pure active-location projection,
and freezes a deterministic minimal context desk that composes the two pure
projections over authored-synthetic data. It is backend context preparation
outside any probabilistic cell. It opens no database, auth, route, provider,
proposal or apply authority.

## 2. Read/context-desk topology

```text
already-authenticated backend current_user
  -> pure practice-scoped read services
       (active-practitioner precedent + new active-location projection)
  -> deterministic minimal context desk (pure composer, no DB/network/provider/clock)
       -> strict opaque authored-synthetic context frame
  -> (future) Davida probabilistic work cell receives only the frame
  -> (future) Davida-specific deterministic proofreader policy
```

The composer is deterministic and outside the probabilistic work cell. It
receives caller-supplied already-authorized projections and opaque backend
resource references; it never speaks to PostgreSQL, GraphQL, REST command
endpoints or event actuators.

## 3. Pure projections

### 3.1 Active-practitioner precedent (retained, unchanged)

- REST `GET /api/v1/practice/practitioners` ->
  `app.services.practice.practitioner_directory_read.list_practitioner_directory`;
- GraphQL `Query.practice.practitioners` (activeOnly default true).
- Inspection proves the service is a pure projection: it only queries and
  projects, with no `flush`, no `commit` and no normalization.

### 3.2 New active-location projection

- `ActivePracticeLocationOut` — strict extra-forbid schema containing only
  `id: UUID` and bounded `name: str`.
- `app.services.practice.active_location_directory_read.list_active_location_directory`
  takes an already-authenticated backend `current_user` and a DB session. It
  exposes no role policy and creates no new action/resource identifier.
- It queries exactly `PracticeLocation.id` and `.name`, scoped to
  `current_user.practice_id` and `is_active IS TRUE`, ordered by `name, id`,
  with a fixed maximum of 200 rows under `db.no_autoflush`.
- No address, phone, `waiting_rooms`, active flag, foreign/inactive rows,
  administrative metadata or prototype SDL `displayOrder` is returned or
  modelled. No route or GraphQL field is added.
- Deterministic source inspection proves the service has no `commit`, `flush`,
  `add`, `delete` or normalization path.

### 3.3 Explicitly blocked read sources

The current room and waiting-list GET paths normalize and commit during a
nominal read and are therefore blocked as context sources; the live appointment
waiting-room queue is patient-linked closed data:

- `GET /api/v1/diary/rooms` — `_normalize_resource_order` /
  `_normalize_all_resource_orders` and `db.commit()` during the nominal read.
- `GET /api/v1/diary/waiting-areas` — same normalize/commit behaviour.
- `GET /api/v1/appointments/waiting-room` — live appointment queue joining
  patient data; patient/clinical data is a closed gate for Davida.

## 4. Deterministic minimal context desk

### 4.1 Inputs (caller-supplied, backend-authorized)

- exact already-authorized `list[PractitionerOut]`;
- exact active locations (`list[ActivePracticeLocationOut]`);
- bounded authored-synthetic `practice_ref` and `principal_ref`;
- `correlation_id`;
- timezone-aware `observed_at`;
- immutable bounded backend `ResourceReferenceRegistry`.

The composer has no SQLAlchemy, model, DB, network or provider import and never
reads a clock (no `datetime.now`/`time.time`); `observed_at` is supplied by the
caller. The `datetime` module is used only as a value type and for fixed
two-minute expiry arithmetic.

### 4.2 Opaque resource references

Every internal UUID in the supplied projections — including practitioner IDs,
location IDs and default-location IDs — is replaced with a registered opaque
synthetic resource reference through the immutable bounded
`ResourceReferenceRegistry`. Missing, duplicate, wrong-kind and cross-practice
bindings fail closed at construction or resolution time. The composed frame
emits no UUID.

### 4.3 Frame document

`emr4.davida.practice_administration_context.v1`, strict extra-forbid:

- `data_class = authored_synthetic`;
- `observed_at` and `expires_at` exactly two minutes apart;
- deterministic SHA-256 `content_revision` over the canonical frame;
- two fixed `live_api_fact` frames:
  - `practitioners` — source
    `app.services.practice.practitioner_directory_read.list_practitioner_directory`,
    `projection=pure`, `active_only=true`;
  - `locations` — source
    `app.services.practice.active_location_directory_read.list_active_location_directory`,
    `projection=pure`, `active_only=true`;
- exact blocked sources for diary rooms, diary waiting areas and the
  patient-linked appointment waiting-room queue;
- authority ceiling: `command`, `confirmation`, `write`, `proposal_apply`,
  `provider`, `event_actuator` and `model_to_database` are all literal `false`;
- labels: `minimal`, `non_authoritative` and
  `database_truth_authoritative` are all literal `true`.

Repeated fixed inputs produce identical frames and an identical revision.
Unknown fields, naive time and unsupported values fail closed.

### 4.4 Authority ceiling

The frame is structurally read-only. Command, confirmation, write,
proposal/apply, provider, event actuator and model-to-database authority are
all literal false. Context frames are minimal and non-authoritative; database
truth remains authoritative.

## 5. Machine contract and schema

`orchestration/continuity/davida-provider-free-practice-administration-pure-read/context-contract.json`
and `context-contract.schema.json` encode the exact nested frame values with
required fields and `additionalProperties: false` throughout. Adversarial
mutation tests prove that any authority-bearing or shape-bearing mutation (for
example `command=true`, `data_class=real`, an unknown field, a reordered blocked
source or a removed required field) fails schema validation.

## 6. API Spine conformance

- GraphQL remains scoped read-only for Davida context frames; no new field or
  resolver is added.
- REST/OpenAPI owns any future writes (proposal and confirmation commands).
- Events never carry commands.
- Manifests remain declarative input, runtime-enforced by typed backend code.
- Context frames remain minimal and non-authoritative.

## 7. Gates preserved

This packet opens no live provider runtime, memory/RAG/GraphRAG, real identity,
patient/clinical/document data, model-to-database write, GraphQL mutation,
REST command, external identity write, autonomous write, cloud/IAM change,
deployment, production, release, protected evidence/holdout or protected-ref
authority. No runtime claim is made.
