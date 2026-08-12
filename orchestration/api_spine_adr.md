# ADR: EMR4 API Spine

| Item | Value |
|---|---|
| Status | Accepted locally for Sprint 100 synthesis |
| Date | 2026-07-06 |
| Programme | Programme 2G / EMR4 API Spine |
| Inputs | `orchestration/api_spine_programme.md`; `plan-api-spine-domain-schema-review.md`; `plan-api-spine-frontend-agent-ux-review.md`; `plan-api-spine-security-audit-deploy-review.md`; Ariadne/Fable 100+ sprint strategy |

## Decision

EMR4 will use a mixed API spine:

- GraphQL for connected, scoped read/context graphs.
- REST/OpenAPI command endpoints for all irreversible, high-risk, external, or
  auditable actions.
- Async/event contracts for integrations and cross-surface state changes.
- YAML manifests for declared setup, policy, capability, and agent context
  contracts, with runtime enforcement in typed code and database policy.

The first schema prototype will be appointment-first. Appointment proposals,
confirmation evidence, freshness, audit, and staff-facing Bernie context are
the best current test of the architecture because they are already implemented
enough to expose real safety boundaries without opening providers, memory, or
historical diary trove gates.

## Non-Negotiable Boundary

GraphQL is read-only by construction. It may expose context, evidence, audit
read models, affordance hints, and event subscriptions. It must not mutate
database state, call external systems, invoke AI providers, write audit events
for confirmed mutations, or act as a generic command tunnel.

Every state-changing or external operation remains a REST/OpenAPI command with
typed input/output, actor, practice scope, idempotency where applicable,
confirmer where applicable, freshness/revalidation, and audit.

## GraphQL Read Graph

Initial graph roots:

- `viewer`: current user, role, practice, practitioner link, feature flags,
  capability hints, and environment posture.
- `practice`: locations, rooms, waiting areas, appointment types,
  practitioners, diary templates, and rosters.
- `patient`: demographics summary, document metadata, active clinical summary,
  recent/future appointments, reminders, and messages.
- `diary(date, locationId)`: diary day context, appointment cards, breaks,
  resources, roster, waiting-room summaries, and read-only availability context.
- `appointment(id)`: appointment details, edges to patient/practitioner/type/
  location, current status, timing, reason/notes, warnings, and audit trail.
- `bernieSession(id)`: typed turn/session read model, candidate slots,
  staff-review context, confirmation readiness as display state only, and
  freshness/session revision metadata.
- `audit`: appointment, clinical-read, Access AI, and future general audit read
  models, filtered by resource, actor, correlation id, and time window.
- `directorySearch`: MBS/SNOMED and future cited knowledge-source lookups.

Computed fields such as `canShowConfirmButton`, `blockedReasonCodes`,
`hasFutureBooking`, `contextFreshness`, or `breaksOverlap` are hints. They are
not write grants.

GraphQL must not expose raw provider prompts, raw model responses, raw diary
trove/H15/H-series fixtures, ignored local outputs, broad tenant introspection,
or unrestricted clinical note dumps.

## REST/OpenAPI Command Plane

Command endpoints own:

- auth/session commands;
- patient create/update and patient-file generation;
- clinical and document writes, including consult finalisation and letters;
- appointment proposal and confirmation commands;
- appointment create/update/status/waiting-area/delete compatibility commands
  until retired;
- slot-search normalize/propose/select command-style reads that produce
  executable proposal envelopes;
- diary admin writes for rooms, waiting areas, rosters, and templates;
- messaging/SMS send, receive, and reminder commands;
- results/referrals ingest, triage, review, and filing;
- billing, invoices, payments, and gateway submissions;
- regulated integrations such as PRODA/IHI/MHR, eRx, Medicare/Tyro, ClickSend,
  3CX, pathology/radiology ingest;
- Access AI invocation, once that gate opens.

If a request changes clinical, financial, scheduling, identity, communication,
audit, provider, or external-system state, it is a command, not GraphQL.

## Appointment Proposal Pattern

Appointment proposals are the canonical high-risk workflow pattern:

1. A proposal command receives staff input or deterministic normalized state.
2. The backend resolves current state and checks conflicts, role, tenant,
   patient/practitioner identity, break overlap, policy, and freshness.
3. The backend returns a typed proposal envelope with intent, safe/blocked
   status, autonomy tier, typed command, warnings, blocks, confirmation
   requirement, confirmation endpoint/payload, evidence, and freshness id.
4. Staff selects or confirms.
5. A REST confirm command echoes proposal/freshness/evidence/session binding.
6. The backend recomputes and verifies before writing.
7. The backend writes the appointment and audit event.

Current proposal envelopes may remain response-shaped for now. The schema
prototype should reserve names for future durable `AppointmentProposal`,
`ProposalEvidence`, and `ConfirmationAuditEvent` objects if pending proposals
need expiry, cross-device continuation, or grid highlighting.

## Context Frames And Agent UX

Agents receive typed, minimal context frames rather than database dumps.

Frame labels should be explicit in UI/review surfaces:

- `Live API fact`
- `Staff selected`
- `Caller signal`
- `Manifest policy`
- `Model interpretation`
- `Fixture/intercepted`

*bernie* uses receptionist context frames: selected diary context, patient
candidates, patient booking history/future bookings, availability context,
policy labels, and proposal/session state.

*davida* uses setup/profile/capability frames and dry-run outcomes. She is an
interface over manifests and command-backed setup paths, not a parallel setup
rules engine.

*consultant* uses curated patient-context frames plus cited knowledge-source
frames. Output remains doctor-reviewed advice or draft text, never autonomous
diagnosis, prescribing, or record mutation.

The UI must preserve the distinction between reads, commands, events, and
manifests: reads explain what is known; commands ask the system to act; events
report committed change; manifests explain evaluated capability/policy.

## Evidence Labelling

Release evidence must say what kind of evidence it is:

- `route-intercepted` when Playwright intercepts routes, Office is stubbed,
  `?smoke=true` is active, or fixture payloads are served.
- `fake-provider` or `mocked-provider` when provider output is deterministic.
- `live backend` only when browser/UI calls are not intercepted and reach the
  intended backend.
- `live provider` only when provider metadata proves `live_provider=true`.

Route-intercepted UI checks are valid deterministic coverage. They are not live
evidence.

## Security Model

Security is part of the API spine.

GraphQL requirements:

- no `Mutation` type in the initial schema;
- no resolver receives write authority, provider adapter, or mutation event bus;
- query depth/cost bounds before production;
- sensitive fields are resolver-authorized by role/action/resource;
- production introspection disabled once a committed SDL artifact exists.

Command requirements:

- single-purpose endpoint per irreversible action;
- action-level authorization before data access;
- practice-scoped tenancy enforcement;
- idempotency keys for mutating/external commands;
- confirmer identity where staff/doctor confirmation is required;
- typed audit event on mutation, external call, provider call, or PHI access.

Near-term production blockers before external clients or live providers:

- PostgreSQL RLS or an explicit RLS-equivalent milestone;
- append-only general audit log;
- idempotency store for command mutations;
- Access AI entitlement and audit checks before provider invocation;
- budget/usage alerting for live AI;
- field-level encryption ADR for national identifiers;
- rate limiting and anti-enumeration for external patient surfaces;
- CORS/XSS/CSRF review for public clients;
- privacy impact assessment for kiosk/patient/external identity flows.

## Async/Event Contracts

Async integrations observe or ingest typed events; they do not bypass commands.

Events are acceleration hints, not current truth, authority or command
receipts. One logical watcher may serve a database event partition and fan
practice-scoped cues to many user sessions. A later active/standby deployment
must fence checkpoint ownership so that only one replica advances a partition;
duplicate delivery during takeover must be idempotent. Regardless of cue
delivery, every consequential REST/OpenAPI command rechecks current authority
and authoritative source state inside its mutation transaction.

Initial event families:

- appointment/proposal staged, expired, confirmed, cancelled, changed;
- waiting-room and waiting-area movement;
- SMS sent/replied/failed;
- caller-ID context observed;
- result/pathology ingested;
- setup-path progress and provider readiness;
- Access AI invocation/audit/cost events;
- future billing, PRODA, eRx, and document workflow events.

Integration endpoints require integration principals such as service accounts,
mTLS certificates, signed payloads, or HMACs. They must be idempotent.

## YAML Manifest Layer

YAML describes declared state and capability; code enforces it.

Allowed uses:

- environment manifests;
- setup paths and rollback hints;
- agent capability charters;
- practice onboarding manifests;
- permission profiles;
- context-frame allowlists;
- integration placeholders with research status.

Browsers and agents should receive backend-evaluated affordance frames, not raw
secrets, provider configuration, or policy documents that imply authority.

## Migration Path

1. Keep current FastAPI routers as the command backend.
2. Inventory Pydantic schemas into read models and command envelopes.
3. Draft appointment/diary GraphQL SDL as a read facade over existing query
   handlers.
4. Draft OpenAPI command conventions from current REST routes without renaming
   routes in the prototype.
5. Add examples for proposal/confirmation/idempotency/audit envelopes.
6. Mark legacy direct writes deprecated only after proposal-confirm equivalents
   have release-gate evidence.
7. Add schema drift tests/lints later, after prototypes are stable.

## First Schema Prototype Artifacts

Sprint 101 should create non-invasive artifacts only:

- GraphQL SDL draft for appointment/diary read graph.
- OpenAPI command envelope draft for appointment proposal/confirmation.
- YAML manifest examples for agent capability and practice onboarding.
- API permission matrix fixture for role/action/resource decisions.
- Async integration placeholder contracts for Caller ID, SMS, pathology,
  Medicare/OPV/PVM/IHI, billing, and clinical knowledge sources.

Prototype checks should prove:

- no GraphQL `Mutation` type exists;
- command examples include actor/practice/idempotency/audit/confirmer fields
  where required;
- GraphQL read examples do not include raw PHI/provider/trove payloads;
- permission matrix examples are default-deny;
- evidence labels distinguish fixture/intercepted/fake/live modes.

## Gates Still Closed

This ADR does not open:

- live providers;
- broad historical diary trove mining;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- model-to-database writes;
- GraphQL mutations;
- external patient clients.

Each remains a dedicated reviewed sprint with Yuri approval where required.

## Dissent And Accepted Risks

- GraphQL can become a write tunnel if the no-mutation rule weakens. Keep the
  first schema read-only and test it mechanically.
- A diary mega-query could become slow or hard to cache. Prefer named
  context-frame queries/fragments over one unbounded practice graph.
- Idempotency partial-failure semantics are hard. Prototype the envelope before
  requiring every route to comply.
- The current role model is coarse. ABAC is accepted as the first step; ReBAC/FGA
  remains a future expansion.
- Per-practice signing keys may be overkill for year one. The security lane's
  dissent is accepted: a single production key can be a pragmatic short-term
  choice if rotation, environment separation, and audit are strong.
- YAML enthusiasm can leak config or create a shadow rules engine. Treat YAML as
  declared input and charters only.

## Next Sprint

Proceed to Sprint 101: non-invasive schema prototype artifacts and validation.
