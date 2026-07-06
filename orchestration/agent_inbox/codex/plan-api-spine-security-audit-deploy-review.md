# API Spine — Security / Audit / Deployment Lane

> **Plan-gate artifact** for Sprint 99 (API Root-To-Branch Plan Review).
> Worker lane: Codex. Owned file — do not revert unrelated changes.
> Scope: security rules, auth/RBAC/FGA, audit events, idempotency, deployment
> posture, live-provider/external-client preconditions, first 5 prototype checks,
> and dissenting notes.

**Status:** Plan gate, not implementation. No production code, no migrations,
no provider calls, no H15/trove/memory/RAG/GraphRAG runtime wiring.

---

## 1. Security Rules for GraphQL Reads vs Command Mutations

### Principle

The mixed API architecture (`api_spine_programme.md`) draws a bright line:
GraphQL is for the connected read/context graph; command-style REST/OpenAPI
mutations are for irreversible or high-risk writes. Security must treat that
line as an access boundary, not a stylistic preference.

### Rule 1 — GraphQL is read-only *by construction*

GraphQL resolvers must never write to a database, call an external service that
mutates state, or emit an audit event with decision=`confirmed`/`mutated`.
This is enforced by:

- No GraphQL mutations in the schema. EMR4 GraphQL ships only `Query` and
  `Subscription` types. Zero `Mutation` type at schema compile time.
- Every resolver returns computed or fetched data only. No resolver receives a
  DB session scoped for writes, an event bus publisher, or a provider adapter.
- Read-only GraphQL resolvers may still emit audit events for PHI access
  (`decision: recorded`), but only after a practice_id-scoped role check that
  the same read result would have satisfied.
- A GraphQL subscription (e.g., diary state change notifications) must never
  trigger a write. Subscriptions observe committed events; they do not produce
  them.

### Rule 2 — Command mutations are single-purpose and audited

Each command REST endpoint does exactly one irreversible thing:

- `POST /api/v1/appointments/proposals/create/confirm-bernie` confirms.
- `POST /api/v1/appointments/:id/cancel` cancels.
- `POST /api/v1/consultations/:id/finalise` finalises.

A command endpoint must not also return a patient list, diary graph, or context
frame in the same call. If the caller needs context before the command, it
fetches context first through GraphQL (or an existing read REST path) and then
issues the command with the IDs and idempotency key it already has.

### Rule 3 — Async integrations do not bypass the command boundary

Event/async contracts (Caller ID, SMS, pathology, Medicare Online, billing)
ingest or emit events through their own authenticated integration endpoints.
Each integration endpoint is a command in its own right and must carry:

- An integration-level principal (service account, mTLS cert, signed payload
  HMAC), not a user session token.
- An explicit event contract that maps to a typed action, not a free-form
  callback that can mutate arbitrary tables.
- An idempotency check (see §4) so redelivery does not double-book results.

### Rule 4 — GraphQL complexity and cost bounding

Before the first GraphQL query reaches production:

- **Query depth limiting** — max 6 levels of nested object resolution.
- **Query cost analysis** — each resolver declares a cost weight; aggregate
  per-query cost is capped.
- **Field allowlisting** — sensitive fields (national identifiers, clinical
  notes) are resolvable only when the requesting role is in the allowlist for
  that field. This is checked inside the resolver, not at schema level, so the
  SDL stays stable while policy evolves.
- **No batch introspection in production** — `__schema` introspection is
  disabled outside dev. The SDL is published as a committed artifact instead.

---

## 2. Auth/RBAC/FGA Posture

### Current state

| Layer | Mechanism | Where |
|---|---|---|
| Identity | JWT via `OAuth2PasswordBearer` | `app/dependencies.py` |
| Practice tenancy | `User.practice_id` FK | `app/models/tenancy.py` |
| Roles | `UserRole` enum: GP/Receptionist/Nurse/Admin/PracticeOwner | `app/models/tenancy.py` |
| Access AI roles | `AiAccessRole` vocabulary mapped from `UserRole` | `app/services/ai/entitlements.py` |
| External identity | `ExternalIdentityRoleMapping` (config-only) | `app/services/ai/external_identity.py` |
| Secret validation | Fail-closed `model_validator` on `secret_key` outside dev | `app/config.py` |

### Gaps before production

1. **PostgreSQL Row-Level Security** (`implementation_plan.md` §15A). Without
   RLS keyed on `practice_id`, a bug in any app-layer `practice_id` filter can
   leak cross-tenant data. Every mutation endpoint and every GraphQL resolver
   must also pass an `practice_id`-scoped RLS check. Implementation: set
   `SET app.current_practice_id = <uuid>` per-request using a middleware hook,
   then `CREATE POLICY practice_isolation ON ... USING (practice_id =
   current_setting('app.current_practice_id')::uuid)`.

2. **Field-level encryption** for national identifiers. The `Practitioner` model
   stores `provider_number`, `prescriber_number`, `ahpra_number`, and `hpi_i` in
   plaintext. The `Patient` model (not yet reviewed) will store Medicare, IHI,
   DVA numbers. These must be encrypted at the column level with a per-practice
   key before any clinical data migration.

3. **No FGA / ReBAC model yet.** The current role model is flat
   (`UserRole` enum). Receptionist can see all diary entries for their practice;
   GP can see all patients. There is no resource-level policy such as "Nurse may
   see appointment slots but not clinical notes" or "Admin may see billing but
   not diagnoses." The API spine programme should adopt a coarse
   permission-model ADR before GraphQL schema design: either attribute-based
   (ABAC) with resource type + action + role, or relationship-based (ReBAC/FGA)
   with a schema like `patient:user:view` / `appointment:user:confirm`. An ABAC
   model is simpler for the first schema prototype and can expand to ReBAC later
   if court/discovery segregation (e.g., subpoena wall) becomes a requirement.

4. **No per-practice signing key or token issuer.** The current `secret_key` is
   global. A compromised key lets an attacker forge tokens for any practice.
   Production must either rotate to per-practice signing keys (with a master
   key for cross-practice admin tokens) or adopt an external OIDC provider
   (Google Cloud Identity, WorkOS, or Auth0) so that the global signing key is
   only a bootstrap.

### Recommended FGA posture for first schema prototype

```
Permission model: ABAC initially
  Resources: patient, appointment, consultation, billing_record
  Actions:  read, list, propose, confirm, cancel, administer, delete
  Roles:    GP, Receptionist, Nurse, Admin, PracticeOwner, Agent(bernie/scribe)

  Default deny. A role-action-resource triple is explicitly allowed or the
  request is rejected before the resolver/route handler runs.

  Agents (bernie, scribe, consultant, davida) are principals with their own
  role strings (e.g., "agent:bernie"). The same permission model applies.
  An agent must not have broader access than the human who invoked it.
```

The permission model must be enforced at two layers:

- **Infrastructure** (PostgreSQL RLS) — prevents cross-tenant data leakage even
  if app-level permission has a bug.
- **Application** (FastAPI middleware or dependency) — validates action-level
  permission for each request/resolver call before any data access.

---

## 3. Audit Event Requirements

### Current coverage

| Audit domain | Existing | Gaps |
|---|---|---|
| Access AI invocations | `AccessAiAuditLog` table, typed event model, PHI-safe metadata | Not yet wired to all routers; cost envelope attached but no budget threshold alert |
| Bernie proposals | `BERNIE_PROPOSAL_CREATED/CONFIRMED/CANCELLED` event types | Event types defined but proposal persistence not yet wired to audit log |
| Clinical reads | None | No audit trail for which GP viewed which patient record, when, from which surface |
| Appointment mutations | None | No typed audit for confirms, cancels, reschedules, or no-shows |
| External identity mapping | None | No log of external group-to-role mapping decisions |
| Data export / bulk access | None | No audit for bulk patient or appointment list exports |

### Minimum audit requirement before any production data

Every production practice must have at least:

1. **Appointment mutation audit** — every confirm, cancel, reschedule, no-show,
   or DNA flag carries: `{event_id, practice_id, actor_user_id, action,
   appointment_id, patient_id, timestamp, correlation_id, idempotency_key}`.
   No raw PHI in metadata; patient_id is a UUID reference, not name/DOB.
2. **Clinical read audit** — every GraphQL or REST read endpoint that returns
   patient clinical data records: `{event_id, practice_id, actor_user_id,
   resource_type, resource_id, timestamp, correlation_id, surface}`.
   Recorded, not allowed/blocked — the audit is for access tracking, not
   gate decisions.
3. **Access AI audit** — already defined (§`audit_events.py`). Must add
   budget-threshold warning: when a practice's rolling 30-day Access AI cost
   exceeds 80% of its configured budget, emit a capability-level warning audit
   event.
4. **Staff confirmation audit** — every action that requires "GP or practice
   manager confirmed this" records the confirmer identity, confirmation
   timestamp, and what was confirmed. This is separate from the actor audit.
5. **Bulk export / backup audit** — any endpoint or script that returns >100
   patient records or runs a diagnostic that touches >1000 rows must emit a
   bulk-access audit event.

### Append-only enforcement

The audit log table must be append-only at the database level:

- `INSERT` only. No `UPDATE` or `DELETE` privileges for the application
  database user.
- Audit rows carry an immutable `event_timestamp` (server-generated) and an
  `event_id` (application-generated UUID). If an application event has an
  `event_id` collision (UUID collision risk is negligible), the second INSERT
  fails — no upsert.
- A separate audit admin script (not the API) prunes rows older than the legal
  retention period via a controlled batch DELETE under a dedicated restricted
  role.

---

## 4. Idempotency and Confirmer Requirements

### Idempotency

Every command mutation (confirm, cancel, reschedule, finalise, send message,
submit billing, or call external regulated service) must support an
`Idempotency-Key` header:

```
POST /api/v1/appointments/:id/cancel
Idempotency-Key: 7c1e5e1e-3b4a-4f7a-9c5a-8e2b1c3d4e5f
```

- On first request with a new key: execute the command, store the result keyed
  by `(practice_id, idempotency_key)`, return the result.
- On retry with the same key: return the stored result without re-executing.
- Key expiry: 24 hours from first use, minimum. Keys may be purged after the
  appointment's scheduled date has passed.
- Key collision check: the store is keyed by practice_id + idempotency_key so
  cross-practice collisions are impossible.

### Confirmer requirements

An EMR4 write that changes appointment or clinical state requires two roles:

| Role | Responsibility | Examples |
|---|---|---|
| **Actor** | Principal who initiated the action | Receptionist clicks Confirm, Bernie proposes, API client posts |
| **Confirmer** | Principal who authorised the write | Practice owner, GP, reception supervisor with delegated authority |

**Where confirmer is required:**

- Appointment confirm (actor may be receptionist; confirmer must be a
  supervising principal, or the action must pass through `confirm-bernie`
  which performs its own signed-confirmation check).
- Cancel / no-show / DNA (actor may be receptionist; confirmer must be a GP
  or practice manager for the clinical record).
- Consultation finalise (actor is GP; confirmer may be the GP themselves for
  the finalise action, but any medication or referral within the consultation
  must carry the prescriber as confirmer).
- Billing submission (actor may be admin; confirmer must be GP or practice
  owner).

**Where confirmer is not required:**

- Read-only access (GraphQL queries, read REST).
- AI proposal creation (`BERNIE_PROPOSAL_CREATED`) — the proposal is a pending
  state, not a final appointment. Confirmer is required when the proposal is
  *confirmed* into an appointment.
- Slot-search or diary-view requests.

### Audit of confirmer

When a confirmer is required, the audit event must include:

```json
{
  "actor_user_id": "...",
  "confirmer_user_id": "...",
  "confirmation_timestamp": "2026-07-06T10:00:00Z",
  "confirmed_action": "appointment.confirm",
  "confirmation_evidence": "signed_proposal_token_v1"
}
```

The `confirmation_evidence` field names the mechanism (e.g., a signed proposal
token, a UI accept, a staff-typed confirmation code) so that future audit
reviews can distinguish "receptionist clicked confirm" from "practice owner
confirmed via signed token."

---

## 5. Deployment Preview/Promote/Rollback Implications

### Principle

EMR4 runs on GCP (FastAPI + PostgreSQL + Vertex AI). The deployment model must
support:

- **Preview** — a full stack deploy (backend + DB migrations + AI capability
  activation) to an isolated environment that mirrors production schema and
  permissions but has no live patient data or external client traffic.
- **Promote** — a controlled, audited, gated promotion from preview to staging
  to canary to production.
- **Rollback** — a procedure that reverts backend code, DB schema, and AI
  capability configuration independently, with documented ordering.

### Environment model

| Environment | Purpose | Data | AI provider | External clients |
|---|---|---|---|---|
| `dev` | Local agent/human development | Synthetic/fake | Disabled or fake | None |
| `preview` | CI/CD pre-merge integration | Synthetic/fake | Fake only | None |
| `staging` | Pre-production validation | De-identified snapshot or synthetic | Dev project, fake-default | Test harness only |
| `canary` | Live practice(s), opt-in | Real practice data | Prod project, real provider | Real clients, bounded |
| `production` | All practices | Real practice data | Prod project, real provider | All clients |

### Migration and rollback rules

1. **Backward-compatible schema migrations only.** A migration that adds a
   column or table is safe; one that renames or drops a column is not, because
   a rollback would need the old code to work with the new schema. Use
   `ALTER TABLE ... ADD COLUMN ...` and dual-read patterns for at least one
   deploy cycle before removing old columns.
2. **Feature flags on every new command.** Every command mutation endpoint and
   every new AI capability must be gated by an environment-level or
   practice-level flag defaulting to `false`. The flag is toggled per practice
   only after the release gate (see Bernie Release Gates pattern) passes.
3. **DB rollback is schema downgrade, not data revert.** A rollback reverts the
   application to the previous code version; the schema stays at the newer
   version if the migration was additive. If the migration was destructive (a
   column dropped), the rollback must restore the column and re-populate it
   from audit log or CDC — this is why destructive migrations are forbidden in
   rule 1.
4. **AI provider rollback is config change, not code change.** The provider
   adapter is injected; a rollback from one provider version to another is a
   config change (`default_provider`, `model_name`, `default_project`). The
   capability registry metadata in `app/services/ai/registry.py` must be
   config-driven enough that a provider rollback does not require a code deploy.
5. **Preview and staging must run the same audit and permission checks as
   production.** If a permission bypass exists in preview, it must be fixed
   before promotion, not after.

### Deployment CI/CD requirements (before any external client)

- Separate service accounts for preview, staging, canary, and production.
- No shared DB between environments.
- Preview and staging use fake providers only — no live AI cost.
- A `db/migrations/` directory with numbered, reversible Alembic migrations.
- A deployment manifest (`env/preview.yaml`, `env/staging.yaml`, etc.) that
  documents every environment-specific override.

---

## 6. What Must Precede Any Live Provider or External Patient Client

This is the sprint-engine pause checklist. A sprint that proposes opening a
live provider path or an external patient/client surface must satisfy every
item before the sprint plan is approved:

### Before any live provider (even dry-run to dev project)

- [ ] PostgreSQL RLS keyed on practice_id is deployed and integration-tested.
- [ ] `audit_log` append-only table (for appointment/clinical mutations,
  independent of Access AI audit) exists and is wired into the relevant
  mutation endpoints.
- [ ] Idempotency-key handling is implemented for every mutation endpoint the
  provider path touches.
- [ ] Access AI entitlement check passes for the target capability with the
  production environment value (not just `("dev",)`).
- [ ] Multi-practice signing key or OIDC integration is deployed (per-practice
  key or external IdP).
- [ ] Budget alerts enabled: a Cloud Billing alert for the AI project at 80%
  and 100% of a configured monthly cap.
- [ ] The `bernie_interpretation_readiness_check.py` output is recorded and
  matches expected values (the readiness gate itself remains `blocked` for
  runtime wiring until the gate review explicitly opens it).
- [ ] Field-level encryption for national identifiers is at least designed; a
  committed encryption ADR exists even if implementation is deferred.

### Before any external patient client (PWA, kiosk, online booking)

All of the above, plus:

- [ ] Rate limiting per identity (IP, patient ID, practice) is deployed at the
  load balancer or API gateway level.
- [ ] Anti-enumeration controls: patient-search endpoint does not reveal
  whether a name/DOB/Medicare combination exists when the searcher has no
  existing relationship.
- [ ] Identity proofing for self-service registration is designed and reviewed
  (name+DOB+Medicare alone is weak and enumerable — see implementation_plan.md
  §15A).
- [ ] The online booking portal API contract is committed and reviewed — no
  ad-hoc patient-facing endpoints without a published contract.
- [ ] CORS policy is scoped to known origins (current config is only GitHub
  Pages + localhost; any patient-facing origin is a new addition).
- [ ] XSS/CSRF defence for patient-facing surfaces is reviewed (JWT in
  localStorage is vulnerable to XSS; consider httpOnly cookie strategy for
  patient surfaces).
- [ ] Privacy impact assessment (PIA) for the patient self-service surface
  exists and is reviewed.

---

## 7. First 5 Security Prototype Checks

These are small, deterministic, no-live-provider checks that should be written
and committed before or during the first API spine schema prototype sprint:

| # | Check | What it proves |
|---|---|---|
| 1 | **GraphQL schema compile-time audit**: `gql_schema.py` or equivalent
  imports the SDL and asserts that the `Mutation` type has zero fields. |
  GraphQL stays read-only by construction from sprint 1. |
| 2 | **Permission matrix test**: an authored fixture of
  `(role, action, resource_type, expected_decision)` tuples is checked against
  a stub `check_permission(role, action, resource_type)` function. Every role
  is denied for actions it should not have (e.g., Receptionist cannot
  `administer` any resource). | The ABAC/ReBAC model is well-defined before
  route wiring. |
| 3 | **Idempotency-key collision test**: an authored fixture of
  `(practice_id, idempotency_key, request_payload)` tuples is checked against
  a stub `resolve_idempotency(practice_id, key)` function. Duplicate keys
  from the same practice return the stored result; duplicate keys from
  different practices (collision scenario) are treated as independent. |
  Idempotency is isolated per practice. |
| 4 | **Audit PHI-contract test**: a fixture of audit metadata dicts with known
  PHI-like keys (`raw_prompt`, `medicare`, `patient_name`, `dob`) is checked
  against the `AccessAiAuditEvent` validator. Each PHI-like key is rejected,
  and safe keys (`latency_ms`, `risk_tier`, `default_provider`) are allowed. |
  The audit PHI contract is enforced at the Pydantic layer, not by convention. |
| 5 | **RLS mimic test**: a stub `current_practice_id` context function and an
  authored fixture of `(request_practice_id, record_practice_id,
  expected_allowed)` tuples. A request practice_id that does not match the
  record practice_id is denied, even when the role has broad permissions. |
  The app-layer RLS mimic behaves as PostgreSQL RLS will. |

---

## 8. Risks and Dissent

### Risk 1 — GraphQL read-only by convention, not by compile-time check

If the GraphQL library (e.g., Strawberry, Ariadne, Graphene) supports
mutations, a future developer could add a `Mutation` type that writes to the
DB through a resolver. **Mitigation:** the schema compile-time audit (check #1)
must be in CI and fail if `Mutation` is non-empty. A runtime middleware check
on GraphQL requests should also reject any request whose operation type is
`mutation`.

### Risk 2 — RLS is the last line of defence and is bypassed by superuser

PostgreSQL RLS does not apply to the table owner or superuser. If the
application DB user is the table owner or has `BYPASSRLS`, RLS is useless.
**Mitigation:** the application DB user must be a non-owner role with
`NOBYPASSRLS`. Schema migrations run as a separate migration user with
`BYPASSRLS` but never during application requests.

### Risk 3 — Idempotency is complex around partial failures

A command endpoint may start processing, write partial state to the DB, then
fail before returning a response. A retry with the same idempotency key sees
the key in the store and returns the stored (failure) result, even though the
partial write exists. **Mitigation:** the idempotency store must be
transactional with the command — if the command fails, the idempotency entry
is rolled back (not committed) so a retry re-executes the full command. This
means the idempotency check and the command execution share a DB transaction.

### Risk 4 — External identity mapping is config-only and not tested

The `external_identity.py` module defines mappings from Cloud Identity / WorkOS
groups to `AiAccessRole` but no runtime path reads those mappings.
**Mitigation:** before any SSO/OIDC integration, a test harness must prove
`access_roles_from_external_groups()` with each provider type and at least one
pass and one deny case per provider.

### Risk 5 — Deployment environments add maintenance burden

Five environments (dev, preview, staging, canary, production) create drift risk:
a config change tested in staging may not be deployed identically to production.
**Mitigation:** deployment manifests are YAML files committed to the repo,
reviewed in the same PR as code changes. Environment-specific values are
overrides in `env/<name>.yaml`, not separate branches or manual GCP Console
changes.

### Risk 6 — Staff confirmation is a product change, not just a security control

Requiring a confirmer role (actor + confirmer distinction) changes the
receptionist workflow. A receptionist who has always been able to cancel
appointments will need GP sign-off. **Mitigation:** the confirmer requirement
is gated by practice-level configuration and is phased in per practice. The
default for dev/preview/staging is `confirmer_required_for_cancel=false` until
the practice explicitly opts in.

### Risk 7 — Per-practice signing keys add operational cost

Per-practice JWT signing keys require a key management service (KMS or Secret
Manager), a key-per-practice provisioning flow, and a rotation schedule.
**Alternative (dissent note):** a single strong signing key rotated quarterly,
with per-practice `practice_id` embedded in every token payload, may be
sufficient for the first year of production if the audit log and RLS are fully
functional. The per-practice key model can be introduced in year 2 as part of
an enterprise/SSO integration sprint. The per-practice key is the safer design;
the single-key approach is the pragmatic trade-off.

---

*End of security/audit/deployment lane artifact. Ready for Sprint 99 synthesis.*
