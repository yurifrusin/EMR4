# Claude Review — Sprint 258 Practitioner Directory Blocker Closure

| Item | Value |
|---|---|
| Reviewer | claude (Sonnet 4.6) |
| Sprint | 258 |
| Date | 2026-07-09 |
| Branch | `claude/current` |
| Target route | `GET /api/v1/practice/practitioners` |
| Readiness flag | `rest_route_ready` (must remain `false` after Sprint 258) |
| Review scope | Security/gap wording for rate-limit deferral, deployment surface, RLS gap, field-encryption gap, and external-client scope |
| Recommendation | **PROCEED with Sprint 258 as defined — with wording guidance below** |

---

## Context

Sprint 257 closed with `no_go_blocker_closure_required_before_readiness_approval_request`.
The go-no-go JSON (`docs/api-spine/practitioner-directory-sprint257-go-no-go.json`) identifies
eight blocking items before Ariadne may even ask Yuri to approve `rest_route_ready=true`.
Two of those (isolated runtime test pass record, API-spine artifact test pass record) are
evidence gaps, not documentation gaps — they require a committed pytest run. The remaining
five are gap/decision documents that can be written without touching route code, schemas,
tests, or readiness flags.

This review focuses exclusively on the five gap/decision documents. Evidence gaps are
acknowledged but out of scope here.

**Stopping point — stated once clearly:** Sprint 258 must not create the separate Yuri
approval payload for `rest_route_ready=true`. That payload is the subject of a separate
sprint after all eight blockers are closed. Any artifact that pre-authorises, requests,
or implies a readiness flag change is out of scope and should not be committed.

---

## Review of Proposed Sprint 258 Scope

The sprint should produce exactly five new committed documents:

1. `docs/api-spine/practitioner-directory-rate-limit-deferral.md` (+ JSON)
2. `docs/api-spine/practitioner-directory-deployment-surface.md` (+ JSON)
3. `docs/api-spine/practitioner-directory-rls-gap.md` (+ JSON)
4. `docs/api-spine/practitioner-directory-field-encryption-gap.md` (+ JSON)
5. `docs/api-spine/practitioner-directory-external-client-scope.md` (+ JSON)

It should also update the criteria status in the go-no-go tracker for each closed item. It
must not change `rest_route_ready`, any adjacent gate, any route or service code, any
existing test fixture, the approved gate, or the blocked readiness snapshot.

Tests may be added only to prove the gap documents are committed and schema-valid (static
markdown/JSON parsing only, no app import, no database, no provider).

---

## 1. Rate-Limit Deferral — Wording Criteria

### What the document must establish

The absence of rate limiting on this route is a known gap that must be explicitly
acknowledged before `rest_route_ready=true` can be requested. The document should not
over-claim or under-claim.

### Required wording elements

**Decision:** `rate_limit_deferred_for_internal_read_route`

**Rationale that must appear:**
- This route is accessible only to authenticated, role-gated, same-practice staff users.
  There is no anonymous access, no public endpoint, and no external patient or kiosk
  consumer pathway.
- EMR4 does not currently implement a shared rate-limiting middleware. Implementing one is
  a separate infrastructure concern and is not gated on this specific route becoming ready.
- The deferred risk is: a compromised or malicious authenticated staff credential could
  enumerate the practitioner directory at high request rate without hitting a middleware
  throttle.
- The accepted control against that risk: CloudRun's built-in request concurrency limits
  provide a soft ceiling; any credential abuse would be visible in structured request logs;
  authentication expiry bounds the attack window.

**Trigger that must appear:**
- Rate limiting must be implemented before any external patient-facing or external
  kiosk-facing exposure of this route. `external_patient_client_ready` remains false and
  cannot become true until rate limiting is in place.

**What the document must NOT say:**
- Do not imply rate limiting is implemented, planned for a specific sprint, or handled by
  any current middleware.
- Do not claim this deferral satisfies the rate-limit requirement for any other route.
- Do not mention `rest_route_ready=true` or pre-authorize a readiness flip.

### Wording red flags to reject during review

- "Rate limiting is handled by ngrok" — ngrok is a dev tunnel, not a production control.
- "CloudRun handles rate limiting" — CloudRun concurrency is not the same as per-user
  throttling.
- "Rate limiting is not required for read routes" — this is too broad; it should be
  scoped specifically to internal-staff routes.

---

## 2. Deployment Surface — Wording Criteria

### What the document must establish

The route must be associated with a named deployment surface before the readiness flag
changes. This document names where the route runs without claiming deployment readiness.

### Required wording elements

**Decision:** `deployment_surface_named_not_deployment_ready`

**Surface record that must appear:**
- Production: GCP Cloud Run, `app.main:app`, FastAPI, port 8080. The Cloud Run service
  is the named deployment surface for all EMR4 backend routes including this one.
- Development: `uvicorn app.main:app --reload --port 8001`, localhost only, behind ngrok
  tunnel `property-cinch-backfield.ngrok-free.dev` for external add-in access.
- The route is mounted at `/api/v1/practice/practitioners` in `app/main.py`.
- All requests require `Authorization: Bearer <jwt>`. There is no anonymous or IP-based
  access to this endpoint on any surface.

**What the document must explicitly state:**
- Naming the deployment surface does not constitute deployment readiness.
  `deployment_ready` remains false.
- `production_ready` remains false.
- No Cloud Run service configuration, IAM, VPC connector, ingress rule, or traffic
  policy is changed by this document.

**What the document must NOT say:**
- Do not claim the route is hardened for production use.
- Do not reference deployment readiness approval, Cloud Run scaling config, or any
  infrastructure sprint as part of this document.
- Do not mention `rest_route_ready=true` or imply the deployment surface record
  constitutes approval for anything beyond naming the surface.

### Wording red flags to reject during review

- "The route is production-ready on Cloud Run" — the document names the surface, it
  does not approve production readiness.
- "Deployment is complete" — deployment readiness is a separate gate.
- Any reference to a specific Cloud Run service URL, project ID, or IAM binding —
  those are out of scope here and may leak infrastructure details.

---

## 3. RLS / RLS-Equivalent Gap — Wording Criteria

### What the document must establish

The practitioner directory route relies on application-layer tenancy filtering with no
PostgreSQL Row Level Security backstop. This is an EMR4-wide known gap (noted in
AGENTS.md §8). The document must acknowledge it specifically for this route and record
the accepted risk explicitly.

### Required wording elements

**Decision:** `rls_gap_acknowledged_application_layer_filtering_only`

**Gap statement that must appear:**
- The route enforces tenancy via `Practitioner.practice_id == current_user.practice_id`
  in the SQLAlchemy query in `app/services/practice/practitioner_directory_read.py`.
- No PostgreSQL Row Level Security (RLS) policy exists on the `practitioner` table or
  any related table used by this route.
- This is the same posture as all other EMR4 routes at this stage: tenancy is enforced
  at the application/ORM layer, not at the database layer.

**Risk statement that must appear:**
- If a future code path queries the `practitioner` table and omits the `practice_id`
  filter (e.g., a new route variant, raw SQL, or a migration script), cross-practice
  practitioner data could be returned without a database-level backstop.
- This risk is partially mitigated by: (a) the test matrix including
  `test_practice_scoping_never_returns_other_practice_practitioners` and
  `test_no_cross_practice_existence_leak`; (b) the `PractitionerOut` schema excluding
  sensitive identifier fields; (c) code review requirements for any new route touching
  this service.

**Escalation condition that must appear:**
- PostgreSQL RLS must be in place before any external patient-facing or kiosk-facing
  exposure of practitioner data. The `external_patient_client_ready` gate must not
  change to true without RLS or an approved RLS-equivalent mechanism.
- RLS implementation is deferred as an EMR4-wide infrastructure gap and is not gated
  on this specific route's readiness flag. However, this gap must be acknowledged in
  the practitioner-directory-specific record before `rest_route_ready=true` can be
  requested.

**What the document must NOT say:**
- Do not claim RLS is implemented, in progress, or planned for a specific sprint.
- Do not claim the application-layer filter is equivalent to RLS.
- Do not imply this gap record closes the RLS gap — it acknowledges it.

### Wording red flags to reject during review

- "The application filter provides the same protection as RLS" — false and should be
  rejected. They have different threat models (ORM/code bypass vs. database-level
  enforcement).
- "RLS is not required for internal routes" — this is too broad and conflicts with
  the Sprint 255 criteria which require a gap record regardless.
- "The `practice_id` filter is sufficient" — acceptable as a description of the
  current control, but only if paired with the acknowledged risk of bypass.

---

## 4. Field-Encryption Gap — Wording Criteria

### What the document must establish

The `Practitioner` model holds sensitive Australian health identifiers in plaintext
database columns. These fields are excluded from the API response. The gap document
must acknowledge the storage gap without conflating it with the API-layer exclusion.

### Required wording elements

**Decision:** `field_encryption_gap_acknowledged_schema_exclusion_is_current_control`

**Fields in scope:**
- `practitioner.provider_number` — Medicare provider number (regulated identifier)
- `practitioner.prescriber_number` — PBS prescriber number (regulated identifier)
- `practitioner.ahpra_number` — AHPRA registration number (regulated identifier)
- `practitioner.hpi_i` — Healthcare Provider Identifier — Individual (regulated identifier)

**Gap statement that must appear:**
- These four fields are stored as plaintext VARCHAR columns in the PostgreSQL database.
  No field-level encryption, column-level encryption, or tokenisation is currently
  applied to them.
- Field-level encryption is documented as a future ADR/workstream item in
  `docs/api-spine/practitioner-directory-security-audit-test-harness-preflight.md` §Future Defensive Posture.

**Current control statement that must appear:**
- All four fields are excluded from `PractitionerOut` at the Pydantic schema layer.
  The `test_response_excludes_sensitive_practitioner_fields` test asserts their
  absence from the serialized API response, keyed by both field name and sentinel value.
- This exclusion is defense-in-depth at the application layer: the fields cannot be
  reached via `GET /api/v1/practice/practitioners` in normal operation.

**Residual risk statement that must appear:**
- A database-level breach (e.g., direct database access, a SQL injection vulnerability
  elsewhere, or a compromised Cloud SQL credential) would expose these identifiers in
  plaintext.
- This risk is not mitigated by the API schema exclusion alone.

**Escalation condition that must appear:**
- Field-level encryption or an approved equivalent control must be in place before any
  practitioner production deployment that stores real patient or practitioner data. This
  condition is separate from and additional to the `rest_route_ready` flag.

**What the document must NOT say:**
- Do not claim field-level encryption is implemented.
- Do not claim the Pydantic schema exclusion makes the plaintext storage acceptable
  for production PHI.
- Do not imply this gap record closes the encryption requirement — it acknowledges the gap.

### Wording red flags to reject during review

- "AHPRA/provider/prescriber numbers are protected by the API schema" — this is
  true at the API layer but does not address database-level storage risk.
- "Field encryption will be added in Sprint X" — do not commit to a specific sprint
  in this record; the encryption gap record is an acknowledgment, not a plan.
- "These fields are low sensitivity" — Australian health provider identifiers are
  regulated under the Privacy Act 1988 and Healthcare Identifiers Act 2010; describe
  their regulatory sensitivity accurately.

---

## 5. External-Client Scope — Wording Criteria

### What the document must establish

The Sprint 257 go-no-go JSON records
`external_client_exposure_decision_recorded: "partial_internal_only_boundary_recorded_but_needs_explicit_scope_decision"`.
The document must upgrade this from implicit to explicit, naming the boundary and the
conditions for future change.

### Required wording elements

**Decision:** `external_client_scope_internal_staff_only_current_slice`

**Current posture that must appear:**
- `GET /api/v1/practice/practitioners` is accessible to authenticated, same-practice
  staff users only: GP, Receptionist, Nurse, Admin, PracticeOwner.
- No external patient client, booking portal, mobile app, or kiosk has access to this
  route.
- `external_patient_client_ready` is and must remain `false` for this route.

**Explicit scope decision that must appear:**
- The REST first slice of the practitioner directory is intentionally internal-staff-only.
  This is not a temporary oversight; it is a deliberate scope decision for this slice.
- External patient-facing or kiosk-facing exposure is a separate future scope decision
  that would require its own approval, its own go-no-go sprint, and its own gate.

**Conditions for future external exposure that must appear (as a gating list, not a
promise):**
- PostgreSQL RLS or an approved RLS-equivalent mechanism covering the practitioner table.
- A rate-limiting middleware protecting the route.
- A CORS/CSRF policy specific to the external client surface.
- A privacy impact assessment for exposing practitioner role and location information to
  patients.
- An explicit patient identity proofing and authentication mechanism distinct from staff
  auth.
- A separate Yuri approval payload for external-client exposure.

**What the document must NOT say:**
- Do not pre-authorize any external client, even conditionally.
- Do not set a sprint target for external-client scope opening.
- Do not describe the practitioner directory as "future-public" or "patient-accessible
  in a later phase" without gating it behind the above conditions.

### Wording red flags to reject during review

- "Patients will be able to see practitioner names in a future booking portal" — this
  implies exposure; it should be framed as a gated future decision, not a plan.
- "External access is blocked until Sprint N" — sprint-numbering commitments are
  inappropriate in a gap document.
- "The internal-only boundary is enforced by the JWT scope" — JWT scope is a claim
  from the token issuer; this does not constitute a full access-control boundary
  without the additional controls listed above.

---

## Adjacent Gate Confirmation

These gates must remain false after Sprint 258 and must not be mentioned in any new
document in a way that implies they may change:

| Gate | Must remain | Reason |
|---|---|---|
| `rest_route_ready` | `false` | Sprint 258 closes blockers; it does not flip readiness |
| `graphql_resolver_ready` | `false` | Not in scope for this sprint or any foreseeable blocker sprint |
| `external_read_model_runtime_ready` | `false` | No external read model surface authorized |
| `runtime_or_memory_ready` | `false` | No provider/memory/RAG wiring |
| `provider_or_directory_runtime_ready` | `false` | No provider calls |
| `write_authority_ready` | `false` | Read-only route |
| `deployment_ready` | `false` | Deployment surface is named here; readiness is separate |
| `production_ready` | `false` | Production readiness is a separate future gate |
| `external_patient_client_ready` | `false` | Explicitly out of scope |

---

## Sequence Safety

The five gap documents may be produced in any order. None depends on another.
None requires touching route code, service code, schema, test fixtures, or readiness
snapshots.

The recommended order for minimal risk of scope creep:
1. External-client scope (smallest, most precise)
2. Rate-limit deferral (requires naming the accepted risk explicitly)
3. Deployment surface (naming only, no config)
4. RLS gap (requires precise risk language)
5. Field-encryption gap (requires accurate Australian regulatory framing)

---

## What Sprint 258 Must NOT Produce

- A Yuri approval payload for `rest_route_ready=true`. That is a separate sprint.
- Any change to `docs/api-spine/practitioner-directory-approved-gate.json`.
- Any change to `tests/fixtures/api_spine_external_readiness/blocked_readiness_status.json`.
- Any route, schema, service, or migration file change.
- Any test that imports the FastAPI app, a database session, or a provider.
- Any document that implies a timeline for RLS, field encryption, or external-client
  exposure.

---

## Summary Verdict

Sprint 258 as scoped by the Sprint 257 go-no-go is appropriate: five narrow gap/decision
documents, no code changes, no readiness flag changes, no Yuri approval payload. The
wording criteria above are the main risk surface. Each gap document must acknowledge
the gap honestly, name the accepted risk and current control, and state the escalation
condition without implying the gap is closed or the flag is ready to flip.

Ariadne should review each committed document against the criteria in this packet before
closing Sprint 258. A static test asserting that none of the five documents contains the
string `rest_route_ready.*true` (outside a `must_remain` or `must_not_change` context)
would be a useful guard.

## Files Changed

None. This is a read-only review artifact.

## Verification

```
git status --short --branch
# On branch claude/current, nothing to commit (review packet is the only new file)
```
