# Reception One same-update-family multi-change kernel rehearsal threat-model delta

Date: 2026-08-14

Timestamp: 2026-08-14T22:44:44+10:00 (Australia/Brisbane)

Status: `frozen`

Parent result: `raisa_reception_one_multi_change_request_atomicity_orientation_pass`
at reviewed source `fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`

## Changed evidence surface

The tranche adds authored-synthetic tests of the existing appointment update
proposal/confirm route. It changes no product, API schema, UI, database schema
or runtime configuration.

## Threats and required controls

| Threat | Required control |
|---|---|
| Three requested fields become three independently committed writes | Send practitioner, time and duration in one closed update patch and prove one confirmation, one appointment outcome, one audit and one completed idempotency result. |
| A proposal mutates or reserves a slot | Count appointment, audit and idempotency state before and after proposal; all remain unchanged. |
| Signed proposal evidence is treated as permanent truth | Change authoritative appointment state after proposal and require freshness denial with no candidate write. |
| A new target-practitioner conflict is missed at confirmation | Insert the conflict after proposal and require confirm-time re-proposal to block without subject mutation. |
| Practitioner authority/state changes after proposal | Deactivate the proposed practitioner and require confirm-time `practitioner_inactive` denial. |
| Same-key replay performs the update again | Reinvoke from a fresh database session and require the exact stored response with unchanged appointment/audit/ledger counts and no revalidation. |
| Same key is reused for a different command | Require typed `idempotency_key_conflict` and no mutation. |
| Appointment and audit flush but ledger completion fails | Inject failure at `complete_appointment_command`; close the session without commit and prove appointment, audit and claim all rolled back before one clean retry. |
| A rollback test passes only because it reuses the fixture session's uncommitted state | Commit fixture setup first, invoke confirmation in a separately owned SQLAlchemy session and verify through a fresh/expired observer session. |
| An event side effect broadens the claim | Keep the existing committed-event feature posture unchanged and claim only the appointment/audit/idempotency effects directly counted by the rehearsal. |
| Test code bypasses actor/practice scope | Resolve the ordinary authenticated synthetic user in the invoking database session or call the real FastAPI route with its existing role dependency; never construct cross-practice authority. |
| A test-only success is described as UI, provider or production readiness | Label evidence `provider_free_live_local_backend_postgresql_authored_synthetic` and keep every adapter, patient channel, provider and deployment gate closed. |
| A discovered source defect is silently repaired outside the frozen boundary | Preserve the failing scenario and require a separately named exact-source recovery amendment before product code changes. |

## Residual boundary

Passing `M1-M7` proves the existing update kernel for this exact combined-field
case in the isolated local PostgreSQL test environment. It does not prove
concurrent different-key serialisation, browser/editor composition, natural-
language interpretation, patient or assistant delegation, cross-family
atomicity, production roles/RLS, deployment or operational performance.
