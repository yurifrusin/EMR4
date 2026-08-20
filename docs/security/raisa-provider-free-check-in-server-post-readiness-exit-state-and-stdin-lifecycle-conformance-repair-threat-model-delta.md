# Threat-model delta: check-in server post-readiness exit state and stdin lifecycle conformance repair

Date: 2026-08-20

Timestamp: 2026-08-20T14:50:08.3884319+10:00 (Australia/Brisbane)

Status: `frozen`

This delta authorises one provider-disabled and initially Docker/database-
nonexecuting lifecycle repair. It grants no attempt-006, product, ordinary-
practice or occupied DeepSeek authority. One separately gated native Harness
process may exercise only the provider-disabled `agents.create({setup})` mount
path and must stop before a model request or turn.

## Assets and trust boundaries

- Immutable attempts 001-005 and the consumed worker terminal.
- The exact server credential delivered through attached stdin.
- The controller-owned stdin pipe and attachment process lifetime.
- Closed OCI state and host-process projections.
- The pinned rc.7 package, exact bounded preset and provider-disabled native
  mount probe.
- Machine-generated Git, dependency, bounded-text, artifact-role and changed-
  path readings.
- Sanitized evidence, independent veto and clockwork publication.

Trust crosses the Python subprocess pipe, Docker inspection abstraction,
failure-evidence builder and final cleanup owner. The provider-disabled probe
also crosses the HMR loader, agent factory, preset service, scoped tool view and
sanitized stage ledger. No raw exception or model/provider boundary is trusted.

## Threats and fail-closed controls

| Threat | Control |
|---|---|
| Parent stdin closes immediately after credential delivery and sends an unintended EOF | Write and flush exactly once, keep the pipe open through post-readiness work, and close it exactly once under the final attachment cleanup owner. |
| Keeping stdin open leaks or duplicates a credential | No second payload copy, output reader, log sink or evidence field is added; tests inspect write/flush/close counts without secret values. |
| Cleanup blocks because stdin remains open | Cleanup closes the parent write handle before polling/terminate/wait and retains the bounded kill fallback. |
| Server exit remains opaque | A fixed nine-key projection records only admitted state classes, booleans, bounded integers and null/unknown forms. |
| Raw Docker error or identity data leaks | `State.Error` becomes one boolean; unknown status collapses to `unknown`; IDs, names, timestamps, paths, logs, output, exceptions, credentials and nonce are forbidden. |
| Malformed state is mistaken for valid evidence | Any invalid type/range or unreadable host handle sets `projection_valid` false and substitutes only closed null/unknown values. |
| Host attachment exit is confused with OCI server exit | OCI and host readings have separate typed fields and are never acceptance substitutes for each other. |
| Native preset failure is confused with server failure | Evidence uses disjoint `native_harness/preset_mount` and `server/post_readiness` coordinate families. |
| Native mount diagnosis invents a substage from an opaque exception | Ordered entry/pass markers determine the first missing stage; unavailable safe instrumentation returns only `PRESET_SUBSTAGE_INSTRUMENTATION_UNAVAILABLE`. |
| Provider-disabled probe accidentally calls DeepSeek | Provider credential is absent, broker requests are disabled/count-checked, no turn is created, and any model/provider/network attempt is terminal failure. |
| A failed probe triggers another expensive run | One checkpoint, one process start, zero retries, zero fallback and no resume. |
| Historical attempt or accepted Harness evidence is rewritten | Exact hashes and owned-path checks bind every predecessor as read-only. |
| Another memory checklist creates more reruns | Full Git IDs, dependency closure, bounded text, artifact roles and changed paths are emitted once from typed schema-owned builders. |
| Byte-identical placeholders are reported as model edits | Changed paths are derived only from before/after SHA-256 map differences. |
| Dependency omission consumes a worker | Future sparse closure is derived from the admitted command and explicit dependency manifests before dispatch. |
| Product/API scope expands during harness repair | Owned-path and forbidden-surface tests reject product, API Spine, config, route, client, flag, allowlist and waiting-area changes. |
| A verifier becomes implementer or acceptor | Gemini is read-only and candidate-gated; Sol independently owns source, tests, acceptance and Git. |

## Residual limits

Deterministic fakes prove control flow and sanitized projection, not Docker or
PostgreSQL runtime success. One provider-disabled native process can identify
the safe failing/passing mount stage for rc.7, but cannot prove DeepSeek model
quality, provider reliability, a complete coding session or future package
versions. Attempt 006 needs a new exact plan and checkpoint.

## Closed boundaries

No attempt 006, Docker object/start/attach, PostgreSQL, SQL, database, live
DeepSeek request, product/patient/appointment/clinical/historical/protected
data, ordinary-practice enablement, generic-status `Arrived`, feature-flag or
allowlist change, route, API/OpenAPI/GraphQL/schema/migration, action grammar,
first-party client, waiting-area movement, production runtime, deployment,
release, Pages, protected evidence or protected-ref movement is authorised.
