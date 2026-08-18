# Threat-model delta — ordinary-practice canonical check-in admission-readiness review

Date: 2026-08-18

Timestamp: 2026-08-18T22:34:05.3641972+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `8fe889764e778c21bd051f30549f77c8db425e7c`

## New seam

The review classifies whether an accepted authored-synthetic, default-off
mutation path has enough explicit controls and evidence to permit a later
ordinary-practice admission candidate. The review itself is static evidence;
it has no route, configuration, data, provider or runtime authority.

## Assets protected

- unchanged default denial and empty ordinary-practice posture;
- the separate authored-synthetic allowlist semantics;
- exact REST/OpenAPI request, response, operation and error contracts;
- authenticated and transaction-time Receptionist authority;
- tenant locks, forced RLS evidence, idempotency and one-use evidence;
- atomic effect, append-only audit, patient-free event/receipt and rollback;
- future rollout, observability and operational-evidence gates; and
- protected refs, sealed evidence and unrelated untracked files.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Treating accepted synthetic route tests as ordinary-practice authority | The exact verdict must remain `not_ready_for_ordinary_practice_admission` while any blocking or operational-evidence gap exists. |
| Reusing the synthetic allowlist for an ordinary practice | Classify the absence of a separate ordinary admission control as a blocking gap; the successor remains architecture-only and default-off. |
| Mistaking default-off safety for a rollout mechanism | Require separate rollout state, selected-practice admission, kill-switch and rollback-runbook evidence. |
| Ignoring runtime database-role uncertainty because table RLS exists | Record forced-RLS structure as present while retaining the non-owner/NOBYPASS and exact runtime-role proof as an operational-evidence gap. |
| Treating 503 unknown-commit behavior as operational recovery | Preserve no-false-success behavior while requiring an ordinary-practice retry/readback/runbook and alert proof before admission. |
| Calling audit/event evidence observability | Keep command audit/event evidence distinct from aggregate non-PHI attempts, denials, replay, latency, unknown-commit and alerting telemetry. |
| Widening the API contract during review | Bind exact source hashes; no product or API Spine file is editable. |
| Importing application code and opening runtime side effects | Reviewer uses text reads only and must prove no `app` import, route, database, Docker, SQL, browser, provider or network operation. |
| Letting client readiness force backend enablement | Keep ordinary admission and later atomic two-client cutover as distinct gates; no client or waiting-area movement changes. |
| Losing the live operation during transition | Update only the exact latch fixture for the named in-progress successor and retain all predecessor assertions. |
| Moving protected refs or user files | Verify all four protected refs and `docs/branding/`; explicit-path staging only. |

## Residual boundary

The expected result exposes three missing designs and three missing operational
proofs. A later architecture tranche may specify default-off admission control,
observability, runtime-role proof and rollback prerequisites only. It cannot
enable an ordinary practice, edit product code/configuration, call a route, use
product data or advance deployment/production.
