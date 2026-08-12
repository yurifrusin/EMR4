# Provider-free read-only status-confirm runtime-gap admission review

Date: 2026-08-12

Source HEAD: `1a26b49c0c3af84e8e8d2b6456268b7fff0d25f6`

Result: `raisa_provider_free_read_only_status_confirm_runtime_gap_admission_review_pass`

Runtime verdict: `not_admitted`

## Decision

The existing status-confirm route is not admitted to receive the accepted
adapter/kernel contract unchanged. Its one-transaction mutation/audit/receipt
shape and signed freshness evidence are useful foundations, but seven blocking
gaps and two partial gaps remain. This decision authorises no implementation.

## Exact gap matrix

| Dimension | Classification | Current observation | Narrowest prerequisite |
|---|---|---|---|
| Practice, appointment and idempotency lock order | `blocking_gap` | The route claims and locks the idempotency record before loading the appointment; _get_appointment performs no FOR UPDATE and no practice lock is present. | Specify one transaction-owned status kernel that locks practice, appointment and idempotency in the accepted order before disclosure or effect. |
| Current authority and server session ingress | `blocking_gap` | FastAPI dependencies check active user and role before the handler, but the route has no server-session binding or post-wait in-transaction authority recheck before mapping replay. | Define server-only authority/session ingress and an in-transaction recheck that precedes every idempotency outcome disclosure. |
| Status-only discrimination from waiting-area union | `blocking_gap` | The confirmation schema accepts a status-or-waiting-area union and the same route currently confirms a waiting-area write. | Freeze an explicit status-only runtime discriminator or separate route before kernel admission, retaining waiting-area behavior outside this kernel. |
| Fail-closed terminal re-transition policy | `blocking_gap` | The proposal emits only an already_terminal warning and the shared update helper contains no terminal guard; the out-of-tree guard expects blocking but is intentionally not current executable evidence. | Keep terminal re-transition outside the kernel until an explicit policy is accepted; the convergence architecture must make the admitted path fail closed. |
| Exact warning acknowledgement | `blocking_gap` | The route concatenates proposal warning codes and submitted confirmed_warnings; it does not compare exact sets before effect. | Specify one exact warning-set equality check after locked current-state recomputation and before request construction. |
| Signed evidence and freshness under current truth | `partial_gap` | Signed evidence binds practice, staff user, command, current status fields and freshness, but no session or durable source version is present and the state is read without the accepted lock order. | Extend the server-only binding to session and locked source version while retaining the existing practice/actor/command/current-state proof. |
| Atomic mutation, audit and receipt correlation | `blocking_gap` | The route stages mutation, audit and completed idempotency response before one commit, but it discards the created audit identifier and status completion is not constrained to durable audit correlation. | Return the staged audit identity into the kernel receipt and require status completed-write rows to bind target and audit before commit. |
| Authority-first replay and conflict disclosure | `blocking_gap` | The idempotency service may return a completed stored response and the route returns the mapped result before loading/locking current appointment state or rechecking authority inside the transaction. | Move replay/conflict classification behind the ordered current-authority and target lock boundary without weakening same-key identity. |
| Canonical stored-receipt delivery | `partial_gap` | The service stores response JSON plus a canonical hash and replay returns the stored JSON, but initial success returns the separately held Pydantic response and no explicit unknown-commit delivery contract exists. | Define one stored receipt serializer used by initial and replay responses plus a typed post-commit delivery-failure recovery contract. |

## Evidence boundary

All 11 exact non-protected source hashes matched; all 15 structural assertions passed; all 37 hostile mutations were rejected.
The out-of-tree terminal guard was read but not executed or counted as passing
evidence because its accepted fixture date is elapsed.

No application import/edit, route/database execution, provider call, product
or patient data, command, deployment, release, Pages or protected-ref action
occurred.

## Next safe candidate

Freeze a provider-free unmounted status-confirm runtime-convergence
architecture for the exact prerequisite set. It must remain non-executing and
must not choose terminal product policy or alter the mounted route.
