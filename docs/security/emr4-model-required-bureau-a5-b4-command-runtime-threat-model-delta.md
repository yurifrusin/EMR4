# Threat-model delta — A5.1/B4.1 command runtimes

Date: 2026-08-05
Parent: `docs/security/emr4-model-required-bureaus-controlled-recovery-threat-model-delta.md`

| Threat | Control | Required failure/result |
|---|---|---|
| Rayleen or Davida is treated as command actor | Authenticated current human user is the only actor/confirmer; agent identity is bounded provenance only | Reject or acceptance failure; zero mutation |
| A4 read capability is reused as write authority | Command routes use the ordinary authenticated staff session and exact role checks; A4 token is never admitted | `401/403`; no disclosure or effect |
| Local synthetic command route reaches an ordinary practice | Separate default-off A5.1/B4.1 flags and exact authored-synthetic practice allowlists checked before resource lookup | Closed-gate rejection; zero disclosure/effect |
| Client asserts another practice, actor or role | Session-derived values are authoritative; body assertions must exactly match before resource disclosure | Uniform scope/authorization rejection |
| Runtime role strings drift from architectural role assertions | Exact server mapping `Admin -> practice_manager`, `PracticeOwner -> practice_owner` before equality; no aliases/fallbacks | Assertion mismatch rejection |
| Stale appointment check-in overwrites current state | Dedicated operation, durable claim, appointment row lock, signed-current-state freshness and final revalidation | Blocked confirmation; full rollback |
| Signed check-in evidence is reused with a different key after state restoration | Random signed nonce/expiry plus unique durable evidence hash on the A5 command claim; completed same-key replay is resolved first | `confirmation_replay_rejected`; zero new effects |
| Generic status-confirm widens A5 roles or action set | Dedicated default-off Receptionist-only check-in routes and schemas; generic route semantics unchanged | `403` or closed-gate rejection |
| Waiting area belongs to another appointment location | Same-practice active waiting-area and exact non-null appointment-location equality under lock | Scope/location rejection; zero effects |
| Check-in event leaks patient or clinical data | Exact database and Pydantic payload allowlist with identifiers limited to appointment/practitioner/location/waiting area and fixed reason code | Insert rejected / acceptance failure |
| Status/audit/event/idempotency diverge | One transaction; command id binds audit and event; commit once | Full rollback, no partial result |
| Existing reschedule event is weakened by second event family | Conditional event-type/schema/payload constraints and regression suite | Migration/test failure |
| Check-in row is parsed by the reschedule feed | Reschedule event type is required in cursor validation and row selection | Row excluded; cursor semantics unchanged |
| Read-only Davida proposal secretly reserves or mutates | Proposal is signed self-contained and executes no insert/update/delete | Zero row-count delta |
| Historical server-held evidence contract has no issuance path | Explicit human-attestation route verifies signed proposal/current session/current state before issuing one opaque reference | No domain mutation; exact evidence row only |
| Runtime route exists without declarative API contract | OpenAPI adds the exact attestation operation, schemas, retry semantics and role normalization in the same descendant | Contract test failure |
| Client mints confirmation evidence | Random server-held reference; stored proposal and payload hashes; no client claims create authority | `confirmation_evidence_invalid` |
| Evidence is replayed with another key | Evidence row locked and unique one-way consumed state inside command transaction | `confirmation_replay_rejected`; zero new effects |
| Same idempotency key changes meaning | HMAC-hashed key plus canonical request/proposal fingerprint and exact scoped uniqueness | `idempotency_conflict` |
| Concurrent default-location writes lose an update | Lock practitioner; compare aggregate version and before-state hash immediately before write | `aggregate_version_mismatch` or `before_state_conflict` |
| Inactive/foreign location is assigned | Anti-enumerating same-practice active-location check before disclosure and again under transaction | `not_authorized` or `location_not_active` |
| Role revoked between proposal, attestation and confirm | Re-read current user/role at each step and immediately before mutation | `confirmer_not_authorized`; full rollback |
| Outbox becomes an actuator | Store committed patient-free event only; no dispatcher, publisher, worker or external transport | No external effect |
| Audit/outbox rows are rewritten | Forced practice RLS plus append-only triggers/policies | Database rejection |
| Raw idempotency keys or model/provider data persist | HMAC/hash-only keys, bounded enums/codes and closed typed payloads | Schema/test rejection |
| Parallel worker widens authority or collides on migration head | Isolated descendant worktrees, exact scope packets, Sol-owned sequential migration resolution and explicit-path integration | Worker candidate rejected |

## Residual boundary

This descendant proves local authored-synthetic command semantics and atomic
PostgreSQL behavior only. It does not prove production identity integration,
provider suitability, sovereign processing, participant safety, UI usability,
external event delivery or deployment readiness. Those remain separately
closed.
