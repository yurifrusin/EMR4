# Davida practice-administration boundary design

Date: 2026-08-03

Status: architecture-only, provider-free, non-executing

Boundary classification:
`architecture_only_practice_administration_boundary`

## 1. Role and authority posture

Davida is the custodian interface for relatively stable institutional
knowledge: practice-operations customs, setup posture, capability posture and
typed administrative intent. It is not the owner of database truth and not an
autonomous database actor. Database truth, availability, identity, conflicts,
confirmation, writes and audit remain owned by the EMR4 typed backend.

Davida may interpret natural-language intent in a future sandbox, but only
typed candidates may cross into deterministic validation and existing
backend-owned command paths. Model output is never itself a command, a
confirmation, or a fact grant.

## 2. Topology

```text
authenticated EMR4 practice-administration surface
  -> deterministic read/context desk (context compiler)
       -> Davida probabilistic work cell (separate identity from Bernie)
       -> Davida-specific deterministic proofreader policy
  -> shared backend API Spine
       -> GraphQL named scoped read/context frames (read-only)
       -> REST/OpenAPI proposal and confirmation commands (future, backend-owned)
       -> committed events followed by fresh reads
  -> PostgreSQL truth + append-only audit/outbox
```

The read/context desk is deterministic and outside the probabilistic work
cell. It supplies minimal authenticated surface/capability frames and opaque
resource references. Davida never speaks to PostgreSQL, GraphQL mutations,
REST command endpoints or event actuators directly.

## 3. Separate identity, shared kernel, separate policies

### Separate cell/container/agent identity

Bernie and Davida must not inhabit one combined probabilistic container or
runtime identity. A combined service would couple capability manifests,
runtime identity, release, failure, scaling, cost and compromise blast radius.
Each service keeps its own immutable policy, service identity, call budget,
network allowlist and default-off feature gate.

### Shared provider-neutral mechanical kernel

Only these deterministic components are shared with Bernie:

- context-frame envelope mechanics;
- typed draft/proposal/result envelope mechanics;
- deterministic proofreader primitives (schema admission, scope/provenance/
  freshness/authority-ceiling/grounding checks);
- auth-context binding and correlation/idempotency metadata;
- retry/supersession grammar;
- sanitized audit vocabulary and evidence labelling.

### What never crosses

- policies (proofreader policy, capability manifest) — separately pinned;
- scopes (allowed context frames, resource scope) — separately pinned;
- memory / session state — bounded, expiring, per-agent;
- credentials — never shared; Davida holds none.

The proofreader runs in the trusted deterministic boundary. One proofreader
engine may be reused, but Davida's policy instance is separately constructed
and never merged into a union of allowed fields or actions with Bernie.

## 4. Forbidden authorities

Davida receives none of the following:

| Authority | Status |
|---|---|
| Database credential | absent |
| ORM session | absent |
| Generic database client | absent |
| GraphQL mutation | absent |
| REST command credential | absent |
| Event actuator | absent |
| Model-to-database path | absent |

There is no direct or indirect route from a Davida model output to a database
session or command endpoint. The deterministic proofreader is the only egress
for typed drafts, and it releases grounded drafts only — never commands or
facts.

## 5. Authority classes (four distinct stores)

1. **Authoritative structured practice state** — practice, location,
   practitioner, room, waiting-area, opening-hours, role and capability truth
   belongs to backend domain services and PostgreSQL. Reads are
   practice/role/resource scoped and fresh. Changes require typed commands.
2. **Advisory provenance-bearing institutional knowledge** — practice customs
   and setup knowledge carry source, author, capture time, effective dates and
   review status. It can explain or guide a human decision. It cannot
   establish roster truth, a hard policy block, a confirmation affordance or
   command authority. Promotion to authoritative requires a structured policy
   schema and an explicit administration command.
3. **Bounded expiring session/context state** — clarification, selected
   candidate, dry-run proposal, context revision and conversation state. It
   expires, can be superseded and never becomes institutional truth by
   persistence or repetition.
4. **Declarative manifest policy** — the capability manifest and proofreader
   policy are declared input enforced by typed backend code. They are not an
   executable or a shadow policy engine.

Database truth remains authoritative. The four classes are never merged.

## 6. Read/context-desk pattern

The exact read/context-desk sequence:

1. The backend read/context desk supplies minimal authenticated surface and
   capability frames plus opaque resource references (IDs are backend-supplied
   handles, not model-chosen values).
2. Davida emits a typed read-intent draft grounded only in supplied opaque
   references and the allowed vocabulary.
3. The deterministic proofreader checks schema, scope, provenance, freshness,
   authority ceiling and grounding.
4. The backend authorizes and executes exactly one named GraphQL/context read
   backed by a pure practice-scoped read service.
5. Any model-authored explanation is separately proofread and labelled model
   interpretation; returned database fields remain labelled live API facts.

Davida cannot construct arbitrary GraphQL, choose fields, change practice
scope or receive a database session.

### Eligible read surface

Active-practitioner data is eligible only through the existing pure
practice-scoped read:

- REST `GET /api/v1/practice/practitioners` ->
  `app.services.practice.practitioner_directory_read.list_practitioner_directory`;
- GraphQL `Query.practice.practitioners` (activeOnly default true).

Inspection of `list_practitioner_directory` shows a pure projection: it only
queries and projects, with no `flush`, no `commit` and no normalization. It is
the accepted precedent for every Davida read frame.

### Future active-location source

A future active-location source must be a pure side-effect-free projection
before admission. It must be proven (by deterministic source inspection) to
contain no `flush`, no `commit`, no normalization and no write path before it
can feed a Davida context frame.

### Explicitly blocked read paths

Inspection of the current GET routers proves the following paths normalize
and/or commit during a nominal read and are therefore blocked as Davida context
sources:

- `GET /api/v1/diary/rooms` — calls `_normalize_resource_order` /
  `_normalize_all_resource_orders` and `db.commit()` when changed during the
  nominal read.
- `GET /api/v1/diary/waiting-areas` — calls `_normalize_resource_order` /
  `_normalize_all_resource_orders` and `db.commit()` when changed during the
  nominal read.
- `GET /api/v1/appointments/waiting-room` — a live appointment queue that
  joins patient data; patient/clinical data is a closed gate for Davida.

These blocked paths are not pure projections and cannot be reused as Davida
read context until read/write behaviour is separated.

## 7. Closed operation enum (first safe administrative domain)

The first safe administrative domain is **practitioner lifecycle
administration**, chosen because its read surface (active-practitioner pure
projection) is already eligible. Davida operation names use a closed enum, not
an open action string. Unknown operations fail closed at the proofreader and
at the contract.

```text
enum DavidaPracticeAdministrationOperation:
  ADVISORY_EXPLAIN_DIRECTORY                 # advisory read/explain
  ADVISORY_SUMMARIZE_DIRECTORY               # advisory read/summarize
  PROPOSE_DEACTIVATE_PRACTITIONER            # typed proposal candidate
  PROPOSE_REACTIVATE_PRACTITIONER            # typed proposal candidate
  PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION  # typed proposal candidate
  PROPOSE_UPDATE_PRACTITIONER_PROFILE        # typed proposal candidate
```

- `advisory` operations produce typed explanation/summary drafts over eligible
  read frames only.
- `proposal_candidate` operations produce typed, non-mutating dry-run
  proposal candidates. None of them applies a change.
- Any operation code outside this enum is rejected (fail closed).
- Each proposal candidate carries a risk tier (`admin_proposal`) that requires
  human confirmation before any backend command exists.

## 8. Emission ceiling

Davida may emit, after proofreader admission:

- typed advisory drafts (grounded, labelled model interpretation), and
- typed proposal candidates (non-mutating, dry-run only).

Davida never emits:

- a human confirmation envelope;
- a signed command;
- `writes_authorized=true`;
- any release envelope that can mutate state.

The proofreader never substitutes for command authorization, domain
invariants, freshness checks or transactional audit.

## 9. Future backend-owned REST proposal and confirmation envelopes

Before any actual apply command, the backend owns a command plane with the
following envelope fields (they are backend-constructed, never Davida-emitted):

### Proposal envelope (backend-owned, non-mutating)

- `practice_id` — practice binding;
- `actor_context` + `source_surface` + `delegated_agent_identity` —
  actor/session binding;
- `resource_id` — the target resource;
- `command_schema_version` — typed command version;
- `correlation_id` + `idempotency_key` — correlation/idempotency;
- `intent_or_proposal_hash` — candidate hash binding the dry-run proposal;
- `expected_aggregate_version_or_etag` + `context_revision_and_freshness_id` —
  optimistic concurrency / precondition;
- `effective_at` + `expires_at` — expiry and effective time;
- `reason_code` — human reviewable reason;
- `before_state_hash` + explicit diff + `warnings_blocks_and_reason_codes` —
  dry-run evidence.

### Confirmation envelope (backend-owned, post-human-action)

The trusted backend constructs command authority only after an authenticated
human confirms the dry-run. The confirmation envelope adds:

- `confirmation_evidence` — authenticated human action evidence;
- `resulting_revision` — aggregate revision after apply;
- `audit_event_id` + `outbox_event_id` — append-only audit/outbox evidence.

Least-privilege authorization is revalidated at command time by the backend
against current role, practice, resource scope and the capability manifest.
Davida never constructs or emits either envelope.

## 10. Event semantics

Committed events are publish-after-commit signals. Their payloads are never
truth and never commands. An event may request a fresh authorized read through
the read/context desk; the resulting read is re-scoped and re-checked against
practice/role/resource. Davida holds no event actuator and cannot subscribe,
deliver, replay or act on events directly.

## 11. Four-tranche sequence after this architecture

1. **Pure read projections** — side-effect-free projection services for every
   eligible practice resource (practitioners today; locations and other
   resources only after projection purity is proven). Provider-free,
   read-only.
2. **Provider-free typed interpretation/proofreading** — unmounted typed
   read-frame and dry-run proposal contracts over authored-synthetic data,
   with deterministic proofreading. No apply.
3. **One bounded proposal path** — one reversible administrative proposal
   vertical with a before/after dry-run and no apply command.
4. **One separately authorised confirmed write vertical** — a
   human-confirmed, backend-owned command candidate only after tranche 3 is
   accepted without a material fork.

Each tranche is separately dispatched and separately accepted. Standing
authority covers bounded logical descendants; material forks return to Yuri.

## 12. API Spine conformance

- GraphQL remains scoped read-only for Davida context frames.
- REST/OpenAPI owns any future writes (proposal and confirmation commands).
- Events never carry commands.
- Manifests remain declarative input, runtime-enforced by typed backend code.
- Context frames remain minimal and non-authoritative.

## 13. Gates preserved

This boundary opens no live provider runtime, memory/RAG/GraphRAG, real
identity, patient/clinical/document data, model-to-database write, GraphQL
mutation, external identity write, autonomous write, cloud/IAM change,
deployment, production, release, protected evidence/holdout or protected-ref
authority. No runtime claim is made.
