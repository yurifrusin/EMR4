# API Spine Domain/Schema Review

| Item | Value |
|---|---|
| Lane | Domain/schema planning |
| Sprint | API root-to-branch plan review |
| Date | 2026-07-06 |
| Scope | Planning artifact only |
| Write boundary | `orchestration/agent_inbox/codex/plan-api-spine-domain-schema-review.md` |

## Summary Recommendation

Adopt the mixed API spine already described in `orchestration/api_spine_programme.md`,
but make the first schema prototype appointment-first rather than whole-EMR-wide.
The current FastAPI surface already has the important command vocabulary:
proposal routes, signed confirmation evidence, freshness ids, session bindings,
slot-search normalization, and appointment audit output. The schema lane should
preserve that work and formalize it.

Recommended root boundary:

- GraphQL is the connected, scoped read/context graph.
- OpenAPI REST remains the command and mutation plane.
- Async/event contracts are for external integrations and eventual fan-out.
- YAML describes allowed capabilities and setup state, but runtime code enforces
  authorization, audit, freshness, and confirmation.

Do not use this sprint to open provider, H15/trove, memory, RAG, GraphRAG, or
runtime interpreter wiring. The schema should be ready for those gates later
without depending on them now.

## Recommended GraphQL Read/Context Graph Boundaries

GraphQL should answer "what does this principal need to see to decide the next
safe action?" It should not execute the action.

Recommended first graph roots:

- `viewer`: current user, role, practice, practitioner link, feature/capability
  flags, dev/prod posture, and safe permission hints.
- `practice(id?)`: practice metadata, locations, rooms, waiting areas,
  appointment types, active practitioners, diary templates, and date-specific
  roster.
- `patient(id)`: demographics summary, document URL metadata, active problems,
  allergies, active medications, recent encounters, recent/future appointments,
  reminders, and relevant messages.
- `diary(date, locationId?)`: diary template, roster entries, appointment list,
  waiting room list, break overlaps, room/waiting-area context, and read-only
  availability context.
- `appointment(id)`: appointment details, patient/practitioner/type/location
  edges, status, timing, waiting area, reason/notes, proposal-relevant current
  state, and appointment audit trail.
- `bernieSession(id?)`: typed turn/session state, read-only outcome events,
  staff-review context, candidate slots, confirmation readiness as display
  state only, and session revision/freshness metadata.
- `audit`: appointment audit and Access AI audit read models, with conservative
  filters by target resource, actor, correlation id, and time window.
- `directorySearch`: read-only MBS/SNOMED lookups and future cited knowledge
  source results, with citations but no mutation authority.

GraphQL should carry only stable object ids and read models. It may expose
computed fields such as `endTime`, `breaksOverlap`, `hasFutureBooking`,
`existingFutureFollowUp`, `contextFreshness`, `canShowConfirmButton`, and
`blockedReasonCodes`, but those are UI/context hints. They must not be treated
as command grants.

Avoid early GraphQL surfaces for:

- raw `raw_document_text`, raw result messages, raw provider prompts, or raw
  model responses;
- direct create/update/delete mutations;
- any route that calls external regulated systems;
- H15/trove/H-series fixtures, ignored local outputs, memory, RAG, or GraphRAG;
- database-like introspection across tenants.

## OpenAPI Command/Mutation Boundaries

OpenAPI should own every operation that changes state, calls an external service,
or creates an auditable clinical/business event. Commands should be explicit
verbs with typed input/output envelopes, idempotency where useful, actor identity,
confirmer identity where applicable, and generated audit records.

Keep these as REST command families:

- Auth/session commands: login, token refresh/revocation when added.
- Patient commands: create patient, create patient with file, update patient,
  duplicate-resolution actions when implemented.
- Clinical commands: add/delete allergy, add history, create care plan, create
  consent form, finalize consultation, generate draft letter.
- Appointment commands:
  - propose create/update/status/waiting-area/delete;
  - confirm create/update/status/delete with signed confirmation evidence;
  - direct legacy create/update/status/delete only while compatibility requires
    them, with a migration path toward proposal-confirm surfaces;
  - slot-search normalize/propose/select as non-mutating command-style reads
    because they return executable proposal envelopes rather than durable graph
    objects.
- Diary admin commands: create/update rooms and waiting areas; future roster
  assignment commands; future template edit commands.
- Messaging/SMS commands: send message, mark read, queue/send SMS, process
  inbound SMS webhook.
- Results/referrals commands: ingest result, triage/review/file result, create
  referral, create reminder, dismiss reminder.
- Billing commands: create/submit/reverse claim, issue invoice, record payment.
- External integration commands: PRODA/IHI/MHR, eRx, Tyro/Medicare, 3CX, ClickSend,
  pathology ingest. These need separate threat-model entries and signed or
  strongly authenticated ingress.
- Access AI commands: invoke capability, record audit/cost decision, but only
  after the Access AI runtime gate opens.

The design rule should be: if a request can alter clinical, financial, scheduling,
identity, communication, audit, or external-system state, it is a REST command
with OpenAPI documentation, not a GraphQL mutation.

## Core Domain Objects And Edges

Core tenant/identity graph:

- `Practice` -> `PracticeLocation`
- `Practice` -> `User`
- `Practice` -> `Practitioner`
- `User` -> optional `Practitioner`
- every PHI-bearing object -> `practice_id`

Patient/clinical graph:

- `Patient` -> `Encounter`
- `Encounter` -> optional `Appointment`
- `Encounter` -> `ClinicalDiagnosis`, `Prescription`, `Allergy`,
  `PatientHistory`, `ConsentForm`, `ClinicalImage`
- `Patient` -> `CarePlan`, `TestRequest`, `Result`, `Referral`, `Reminder`,
  `ScannedDocument`, `MbsClaim`, `Invoice`, `InternalMessage`, `SmsLog`

Diary/appointment graph:

- `DiaryTemplate` -> `DiaryColumn` -> `DiaryBreak`
- `PracticeLocation` -> `Room`
- `Room` -> `DiaryRoster`
- `WaitingArea` -> `Appointment.waiting_area_id`
- `Appointment` -> optional `Patient`
- `Appointment` -> required `Practitioner`
- `Appointment` -> optional `AppointmentType`
- `Appointment` -> optional `PracticeLocation`
- `Appointment` -> `AppointmentAuditLog`

Bernie/context graph:

- `BernieTurnRef` -> session/turn identity for read-only staff flow context.
- `BerniePatientBookingContext` -> compact patient appointment history/future
  bookings once patient recognition is strong enough.
- `BernieStaffReviewPayload` -> proposal display state, identity/practitioner
  evidence, candidate slot summaries, warnings, blocks, and confirmation
  affordance.
- `BernieBookingOutcomeOut` -> typed outcome classification; report-only, never
  a write grant.

Audit/security graph:

- `AppointmentAuditLog` records confirmed appointment writes with action/status
  evidence.
- `AccessAiAuditLog` records future model/tool invocation decisions and cost
  boundaries.
- A future general `AuditLog` remains needed for cross-domain PHI access and
  mutation audit; GraphQL can read it, OpenAPI commands must write it.

## Appointment Proposals, Evidence, And Audit

Appointment proposals should become the canonical schema pattern for high-risk
staff-confirmed workflow:

1. A proposal command receives staff input or normalized deterministic state.
2. The backend resolves current state, checks conflicts, policy, identity, role,
   tenant, break overlap, and freshness.
3. The backend returns a proposal envelope:
   - `intent`
   - `safe`
   - `requires_confirmation`
   - `autonomy_tier`
   - `summary`
   - typed `command`
   - `warnings`
   - `blocks`
   - `confirm_endpoint`
   - `confirm_payload`
   - proposal freshness id
   - signed confirmation evidence where required
4. The UI/staff select or confirm.
5. A REST confirm command echoes the proposal, freshness id, warnings, signed
   evidence, and session binding where applicable.
6. The backend recomputes and verifies before writing.
7. The backend writes the appointment and an `AppointmentAuditLog` record.

GraphQL should expose the read side of proposals only after they exist as server
state or session state. It should not allow clients to synthesize proposal state
and then call a generic mutation.

Near-term domain decision: current proposal envelopes are response-shaped rather
than durable rows. That is acceptable for Sprint 101 prototypes, but the schema
should reserve names for future persistent `AppointmentProposal`,
`ProposalEvidence`, and `ConfirmationAuditEvent` objects if pending proposals
need cross-device continuation, expiry, or UI highlighting.

## What Must Stay REST Command-Only

These must not move to GraphQL mutations:

- appointment create/update/status/waiting-area/delete confirmations;
- direct appointment write compatibility routes until retired;
- patient create/update and patient-file generation;
- consultation finalize and any document-writing workflow;
- consent creation and signature capture;
- billing claim submission, invoice issue, payment record, gateway callbacks;
- results ingest, result review/file/triage, and relay/webhook ingress;
- SMS send, inbound SMS processing, reminder queue execution;
- external service calls: ClickSend, 3CX, Tyro/Medicare, eRx, PRODA/IHI/MHR,
  pathology/radiology ingest;
- Access AI/model invocation and model-output audit;
- any future H15/trove/memory/RAG/GraphRAG runtime access if a gate ever opens.

GraphQL may display outcomes, status, audit records, and context frames from
these operations. It should not be the execution channel.

## Migration Path From Current FastAPI Routers

Recommended migration is additive:

1. Inventory current Pydantic schemas into read models and command envelopes.
   Start with `app/schemas/appointments.py`, `diary.py`, `patients.py`, and
   `clinical.py` because they already define the active product surface.
2. Draft GraphQL SDL as a read facade over existing query handlers:
   appointments, diary template, roster, rooms, waiting areas, patient summary,
   appointment audit, and Bernie session snapshots.
3. Draft OpenAPI command conventions using current REST routes as the source of
   truth. Do not rename routes in the prototype; instead define stable operation
   ids and command envelope names.
4. Mark legacy direct writes with deprecation metadata once proposal-confirm
   equivalents exist and have release-gate evidence.
5. Introduce schema tests or lint-only checks in a later sprint to prevent drift
   between Pydantic command schemas, OpenAPI examples, and GraphQL read types.
6. Add persistent proposal/session objects only when a product workflow requires
   cross-device or long-lived pending state. Do not force persistence merely to
   make the graph look elegant.
7. Keep existing FastAPI routers as the command backend. GraphQL should be a
   read adapter layer, not a second domain implementation.

Suggested first adapter order:

- `appointments.py`: appointment list/detail, waiting room, audit, slots, Bernie
  session/read-only context.
- `diary.py`: locations, rooms, waiting areas, template, roster.
- `patients.py`: search/detail/summary/duplicate-read surfaces.
- `clinical.py`: patient clinical summary edges.
- `auth.py`: viewer/me read surface only; login stays REST.

## First 5 Schema Prototype Artifacts

1. `docs/api-spine/graphql/appointment-diary-read.graphql`
   - SDL draft for `Viewer`, `Practice`, `DiaryDay`, `Appointment`,
     `AppointmentAuditEvent`, `WaitingArea`, `Room`, `DiaryTemplate`,
     `Practitioner`, `PatientBrief`, and `BernieSession`.

2. `docs/api-spine/openapi/appointment-command-surface.yaml`
   - OpenAPI slice covering current appointment proposal/confirm routes,
     slot-search proposal/normalize/select routes, direct compatibility writes,
     and audit read endpoints with explicit operation ids.

3. `docs/api-spine/domain/appointment-proposal-state-machine.md`
   - State machine for `draft_intent -> proposal_ready -> confirmation_ready ->
     confirmed_write | blocked | stale | superseded`, with freshness/evidence
     rules and audit requirements.

4. `docs/api-spine/schema-map/current-fastapi-to-spine.md`
   - Mapping table from current routers/schemas/models to GraphQL read types and
     REST command envelopes, including fields intentionally excluded from the
     graph.

5. `docs/api-spine/examples/bernie-booking-context-frame.json`
   - Synthetic, non-PHI example of the typed read/context frame sequence:
     viewer/practice/diary day, recognized patient booking context, slot-search
     normalization result, proposal envelope, confirmation audit result.

These should be non-invasive docs/schema artifacts only. No route wiring,
database migrations, provider calls, runtime memory, H15/trove access, RAG, or
GraphRAG.

## Risks And Dissent

- Appointment schema gravity is high. `app/schemas/appointments.py` already
  contains many overlapping envelopes. Prototype work should clarify names and
  boundaries before adding more.
- GraphQL can become a permission footgun if it exposes deep patient graphs by
  default. The graph needs strict field authorization, tenant scoping, pagination,
  depth/complexity limits, and audit for sensitive PHI reads.
- Proposal envelopes currently appear mostly transient. If Bernie pending
  proposals become cross-device or long-running, durable proposal rows may be
  needed. That should be a product-driven migration, not an architectural reflex.
- The current appointment audit is domain-specific. EMR4 still needs the broader
  append-only audit foundation called out in implementation plan section 15A
  before results, billing, ADHA, and external patient surfaces expand.
- Some existing REST reads, especially slot-search proposal/normalize endpoints,
  are command-shaped but non-mutating. That is acceptable: they prepare safe
  command envelopes and belong in OpenAPI even though they read.
- Dissent: do not make GraphQL the universal API yet. The first practical win is
  a typed read/context graph for the diary and Bernie booking loop, paired with
  existing REST command routes. A whole-system GraphQL schema before the booking
  loop settles will likely encode churn.
- Dissent: do not build a new generic "agent action" mutation. Agents should use
  the same explicit command surfaces as humans, with role/capability checks,
  confirmation, freshness, and audit.
- Dissent: do not let schema prototypes import H15/trove/memory/RAG concepts as
  first-class runtime graph objects. The programme's current blocker is consumer
  shape, not historical-data availability.

## Boundary Check

This artifact proposes no production code, tests, migrations, provider calls,
runtime wiring, H15/trove access, memory, RAG, or GraphRAG. It is intended as
input to the API Spine ADR and Sprint 101 non-invasive schema prototype.
