# Threat-model delta — delete-confirm route convergence and Ariadne Git-object resolution

Date: 2026-08-16

Timestamp: 2026-08-16T15:21:37.9387937+10:00 (Australia/Brisbane)

Status: `frozen`

Parent controls: API Spine command ownership, accepted delete-confirm physical
design/scaffold/serial behavior, Ariadne active-operation latch and risk-weighted
workflow hard controls.

## Product review threats

| ID | Threat | Required control |
|---|---|---|
| `DRC-001` | Literal route mounting is misreported as physical-seam convergence. | Separate mounting, composition and runtime classifications in a closed matrix. |
| `DRC-002` | Legacy idempotency replay discloses a body before current authority and target truth are rechecked. | Classify route-local replay ownership as blocking until the physical seam owns disclosure. |
| `DRC-003` | Authenticated role membership is mistaken for current cancel capability. | Require server-owned positive generation plus exact `appointment.cancel.confirm` grant in the command transaction. |
| `DRC-004` | Freshness or waiting-area checks use an unlocked stale appointment. | Require locked-state evidence and proposal-version re-admission before effect authority. |
| `DRC-005` | Cancellation, audit or private receipt can be partially committed or weakly correlated. | Require one physical transaction and exact audit/receipt correlation. |
| `DRC-006` | The six-field minimized receipt is silently treated as the full public confirmation envelope. | Name the response transition as blocking and require one byte-authoritative replay design. |
| `DRC-007` | Canonical and compatibility paths acquire different handlers or operation identities. | One future handler; canonical path plus hidden compatibility alias only. |
| `DRC-008` | Raw compatibility DELETE inherits dedicated-kernel authority or idempotency semantics. | Preserve it as a separately governed legacy ingress. |
| `DRC-009` | Settled PostgreSQL behavior is reopened as route-review ceremony. | Consume exact Continuity 303 evidence without runtime execution. |
| `DRC-010` | Read-only review imports application code or reaches configuration/data. | Exact hashes, literal text inspection only, no `app` import or route/database execution. |

## Git-object control threats

| ID | Threat | Required control |
|---|---|---|
| `GOR-001` | A manually completed but nonexistent full object ID enters a receipt. | Resolve the exact structured source as a commit before pass. |
| `GOR-002` | An abbreviated, uppercase or malformed ID is accepted. | Existing latch shape check plus exact lowercase forty-hex resolver input. |
| `GOR-003` | A blob, tree, tag indirection or different commit satisfies a loose revision check. | Use `<id>^{commit}` and require byte-exact resolved output equality. |
| `GOR-004` | A valid unrelated commit is used as current operation provenance. | Require the resolved source commit to be an ancestor of machine-observed HEAD. |
| `GOR-005` | Runtime content becomes a shell or revision-expression injection. | Fixed Git argv, `shell=False`, validated literal object ID, exact repository root. |
| `GOR-006` | Git failure, timeout or malformed output is treated as absence of evidence but the receipt passes. | Closed failure reasons, `revision_required`, dispatch false, no fallback. |
| `GOR-007` | The repository-aware check mutates Git or overrides a pre-existing failed receipt. | Read-only command allowlist; failure can only add reasons and narrow authority. |
| `GOR-008` | Machine-observed IDs remain buried in prose and are copied incorrectly later. | Emit a typed `git_object_resolution` receipt projection with full IDs. |

## Residual boundary

Passing the review does not make the delete route ready. Passing the resolver
does not prove the semantic correctness of a chosen source commit; it only
proves exact commit existence, ancestry and machine-observed identity. Plan,
acceptance and protected-ref controls remain independently mandatory.

No product route/database, patient or clinical data, provider/credential,
deployment, release, Pages or protected-ref authority is introduced.
