# Threat-model delta — unmounted default-off ordinary-practice canonical check-in admission-control kernel rehearsal

Date: 2026-08-19

Timestamp: 2026-08-19T03:47:11.9420134+10:00 (Australia/Brisbane)

Status: frozen provider-free unmounted rehearsal; no enablement

Parent architecture: `752b521c59f5b44bf46de0cf776a33ac74b8134d`

## Scope

This delta covers only a pure in-memory evaluator, disable-biased transition
kernel, command-envelope validator and deterministic authored-synthetic
scenario reducer. There is no route, application import, persistence,
environment, product data, provider or deployment surface.

## Assets and trust boundaries

Protected assets are default denial, exact authored-synthetic semantics,
ordinary-lane separation, zero active ordinary records, kill-switch dominance,
the no-resume/disable-only graph, full Git identity, command requirements,
unknown-commit no-success and the no-mount boundary.

The only new trust boundaries are the immutable pure input values, kernel
functions, normative JSON contract, deterministic runner and derived evidence.
None has a product or filesystem-write capability.

## Threats and controls

| Threat | Failure mode | Required fail-closed control |
|---|---|---|
| Executable ordinary enablement | A hypothetical active record releases ordinary admission. | Rehearsal profile freezes activation authority false; every ordinary lane denies and canonical active-record count is zero. |
| Synthetic privilege confusion | Synthetic allowlisting is treated as an ordinary record. | Distinct lane types and inputs; overlap denies; no cross-lane fallback. |
| Precedence reordering | Lane admission occurs before snapshot, feature or kill-switch checks. | One exact ordered evaluator; named scenarios assert the first closed reason. |
| Stale or malformed fallback | Invalid input reuses a prior good result. | Pure call has no cache; missing, invalid, stale, unresolved or multiply-current snapshot denies. |
| Kill-switch bypass or clear | Engagement is ignored or a retry clears it. | Engagement dominates both lanes; executable switch graph contains only `clear -> engaged`. |
| Activation through transition | `prepare` produces `active`. | `prepared -> active` is represented but denied; no executable transition may output `active`. |
| Resume or rollback activation | Suspension resumes or withdrawal restores an old active version. | No resume operation; suspended can only withdraw; withdrawal is terminal and disable-only. |
| Hostile active input confused with authority | A negative scenario is treated as a persisted active record. | Inputs are authored-synthetic immutable values; evaluator denies active ordinary input and the evidence reports zero canonical active records. |
| Command-envelope omission | Missing role, version, audit, digest or scope is accepted. | Fourteen exact required fields and closed semantic checks; each one receives a negative scenario. |
| Git abbreviation | Seven characters are accepted as the reviewed source. | Lowercase 40-character regex plus resolved flag; no prefix expansion. |
| Unknown-commit false success | Uncertainty releases success or triggers blind retry. | Bounded result has `success_released=false`, `readback_required=true`, `retry_allowed=false`. |
| Product import or accidental mount | Pure module gains application/database/network capability. | Standard-library import allowlist, exact owned paths and source tests reject `app`, router, ORM, HTTP and environment imports. |
| Contract drift | Code, schema, evidence and prose describe different graphs. | One closed normative contract; deterministic semantic comparison and hostile mutations fail before evidence release. |
| Clockwork authority escalation | Digest/tick provenance is interpreted as admission permission. | Clock status remains shadow-only; no broker code changes or calls; workflow receipt is never a product authority input. |
| Bureaucratic-weight regression | New controls add fixtures and reruns without reducing mistakes. | Later clockwork migration must measure manual fields, commands, retries, maintained surface and escapes before adoption; this product kernel makes no efficacy claim. |

## Data and API posture

Inputs contain no patient, appointment, practitioner, user, token, note, reason
text or product payload. Synthetic practice and record identifiers remain local
test values and never enter telemetry. The kernel emits only bounded enum,
generation and digest fields.

No REST/OpenAPI operation is mounted. The five architecture operation IDs are
classification inputs only. GraphQL remains read-only by architecture and is
not changed or invoked. Async events, models, agents and the DeepSeek broker
have no write or activation authority.

## Residual risk and closed authority

The three operational-evidence gaps remain blocking. Concurrency, persistence,
real runtime role, audit storage, secret posture and unknown-commit behavior
are simulated contracts only. Passing this tranche cannot justify a product
mount or ordinary enablement.

No `app/**`, configuration, OpenAPI/GraphQL, database, runtime role, route,
generic-status `Arrived`, client, waiting area, product/patient/clinical data,
provider/network, deployment, release, Pages, live clockwork or protected-ref
change is authorized.
