# Threat-model delta — unmounted status-confirm runtime convergence architecture

Date: 2026-08-12

Source HEAD: `fca97097eeca5070ad41e403aed9413eee45ccba`

## Scope

This delta covers a provider-free, non-executing architecture contract for the
status-only confirmation path. It consumes only the nine exact hash-bound
accepted artifacts named in the plan. `implementation_authorized: false` is an
invariant.

## Assets protected

- current practice, actor, role, active-user and opaque session authority;
- locked appointment state and its monotonic source version;
- explicit confirmation and exact warning acknowledgement;
- appointment mutation, attributable audit and canonical completed receipt;
- idempotency identity, request digest and replay/conflict confidentiality; and
- existing waiting-area behavior, which remains outside the new kernel.

## Threats and required controls

| Threat | Required fail-closed control |
|---|---|
| Transport asserts practice, actor, role or session authority | Accept those fields only from backend authority/session ingress; client duplicates are rejected. |
| Replay discloses a prior result after access was revoked | Lock practice and appointment, recheck current authority, then lock/classify idempotency before any disclosure. |
| Two paths acquire locks in different orders | Freeze the status subset as `practice -> appointment -> idempotency_record`; skip the unused schedule domain without reordering. |
| Waiting-area input enters the status kernel | Discriminate the proposal intent before kernel ingress and emit no request for the union sibling. |
| Signed evidence is reused after session or state change | Bind an opaque session digest and monotonic appointment state version and compare them under the lock. |
| Warning drift is hidden by concatenation | Require exact canonical set equality and reject missing, extra, duplicate or unknown codes. |
| Terminal policy is silently invented | Stop a terminal-to-different-status request as `transition_policy_deferred`. |
| Mutation commits without its audit or durable receipt | Stage mutation, attributable audit and correlated receipt in one transaction; any failure rolls all three back. |
| Initial and replay responses diverge | Render both from the same stored canonical receipt bytes and digest. |
| Response failure causes a duplicate effect | Mark delivery unknown, perform no server retry and require same-key client retry to disclose the stored receipt after authority recheck. |
| Architecture prose is mistaken for runtime proof | Keep every effect flag false, prohibit application/database imports and label the next gate unmounted. |
| Evidence expands into protected or unrelated files | Verify only the nine exact plan hashes; AER-0291 forbids broader content search. |

## Residual risks deliberately open

- physical appointment version storage, migration, backfill and compatibility;
- concrete ORM/service boundaries and transaction error mapping;
- actual PostgreSQL lock, isolation, rollback, race and unknown-commit behavior;
- mounted route parity and waiting-area regression protection;
- raw compatibility-route convergence and create schedule-domain fencing; and
- operational data, provider, deployment, production and release safety.

## Evidence and authority boundary

Only authored-synthetic JSON, deterministic validation and repository-local
tests are evidence. No patient, clinical, real-person or product-derived data;
route/database execution; provider/network call; credential; browser action;
tool; command; deployment; production; release; Pages; or protected-ref
movement is authorized. `docs/branding/` and unrelated untracked paths remain
excluded.
