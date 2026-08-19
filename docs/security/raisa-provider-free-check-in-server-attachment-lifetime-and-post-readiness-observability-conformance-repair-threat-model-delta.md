# Threat-model delta: check-in server attachment lifetime and post-readiness observability conformance repair

Date: 2026-08-20

Timestamp: 2026-08-20T03:29:08.3073070+10:00 (Australia/Brisbane)

Status: `frozen`

This delta authorises one provider-free two-path source repair and its exact
deterministic tests. It grants no Docker, database, product, ordinary-practice
or occupied recovery-attempt authority. One DeepSeek model worker is
conditionally admitted only through the separately bound native-Harness v2
WorkOrder, no-database interlock, custom runner and one-run latch.

## Assets and trust boundaries

- Immutable attempt-004 failure/envelope bytes and their exact full-Git source.
- The accepted base relay-free harness and two-path repair boundary.
- One controller-owned server attachment handle from credential delivery until
  final cleanup.
- Exact post-readiness running state and profile predicate names.
- Sanitized failure evidence, provider-free tests and independent readback.
- The broker-bound native Harness worker package and one consumed session.

Trust crosses the existing subprocess handle, Docker inspection abstraction,
closed predicate map, failure-evidence sanitizer and final cleanup owner. For
the worker only, trust also crosses the HMR custom runner and outer broker;
neither layer substitutes for the other.

## Threats and controls

| Threat | Fail-closed control |
|---|---|
| Stopping the attachment after readiness also stops or destabilizes the server | The handle remains live and controller-owned until the existing final teardown; fake-process sequence tests reject any early terminate, kill or wait. |
| The repair merely changes the error message | Tests prove later work begins while the same attachment remains unstopped and final cleanup stops it exactly once. |
| A stopped server is mistaken for an identity mismatch | Running state is checked first and has the distinct `server_not_running_after_readiness` coordinate. |
| Identity drift remains untraceable | Exact false predicate names are sorted, comma-joined and retained under `server_identity_mismatch_after_readiness`. |
| Inspection values or secrets leak through diagnostics | Evidence accepts names matching `[a-z_,]+` only; values, IDs, nonce, credentials and raw inspection are forbidden. |
| Malformed inspection bypasses the profile gate | Running shape fails closed first; malformed profile shape returns only `inspect_shape`. |
| Cleanup gains multiple owners or hides the primary error | The existing `finally` block is the sole attachment owner and primary-error preservation remains exact. |
| Attempt 004 is rerun or rewritten | Its namespace, failure and envelope are immutable and hash-bound; this operation has no Docker/database execution. |
| DeepSeek receives hidden execution authority | The exact tool view is only `edit`, `glob`, `read`; Sol alone runs no-database-admitted tests and owns Git/acceptance. |
| A worker failure causes repeated spend or authority drift | One-run latch, zero automatic retries/fallbacks, no resume and no Claude Code fallback. |
| Model output is treated as acceptance | Sol independently verifies bytes, diff, command admission and tests; Gemini later vetoes the exact deterministic candidate. |
| The repair changes product/API behavior | Owned-path checks and API Steward review keep GraphQL read-only and all REST, flag, route, schema, client and admission surfaces unchanged. |
| Governance adds another manual memory burden | Clockwork alone publishes canonical state after separate check/publish; machine-resolved full IDs and admission digests replace hand-completed fields. |

## API Spine boundary

GraphQL remains read-only. The existing REST-command rehearsal retains
practice scope, authorization, idempotency, atomic effect/receipt/audit and
default denial. No API Spine artifact, product route, event authority or
database schema changes.

## Residual limits

Provider-free fakes can prove control flow, ownership and diagnostic selection;
they cannot prove Docker CLI lifetime semantics on every platform, PostgreSQL
availability, transaction behavior, production reliability or that the hidden
attempt-004 cause was one particular branch. A later separately frozen attempt
is required for occupied evidence.

## Closed boundaries

No Docker object/start/attach, credential delivery, PostgreSQL, SQL, database,
attempt-004 retry, product/patient/appointment/clinical/historical/protected
data, ordinary-practice enablement, generic-status `Arrived`, feature-flag or
allowlist change, route, action grammar, first-party client, waiting-area
movement, product runtime, deployment, release, Pages, protected evidence or
protected-ref movement is authorised.
