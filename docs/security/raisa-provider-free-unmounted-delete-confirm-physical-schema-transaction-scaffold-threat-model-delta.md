# Threat-model delta — delete-confirm physical schema-and-transaction scaffold

Date: 2026-08-15

Timestamp: 2026-08-15T21:08:13+10:00 (Australia/Brisbane)

Source HEAD: `0a01e93319f302256f2b8af0aa74e494256808a8`

Status: `frozen_for_provider_free_unmounted_implementation`

## Scope

This delta covers additive ORM mapping, one inert migration, pure receipt
helpers and an unmounted ordered transaction seam. It proves source
representability only and processes no product, patient or clinical data.

## Threats and controls

| Threat | Frozen control |
|---|---|
| Application or client selects authority generation | PostgreSQL trigger forces insert one, ignores direct submitted updates and owns every qualifying advance. |
| A grant changes without invalidating an old proposal | Capability insert/delete must first advance and lock the exact parent generation in the same transaction. |
| An unrelated nested trigger impersonates the grant-owned generation advance | PostgreSQL exposes depth but not parent-trigger identity, so admission is closed-world: the exact `public` grant function is the sole migration source containing the authority generation, runtime DDL/function/trigger mutation remains closed, a maintained source-inventory regression rejects another writer, and the next catalogue gate must verify the exact installed set. |
| A duplicate `INSERT ... ON CONFLICT DO NOTHING` advances authority despite changing no grant | The capability trigger locks the parent first, detects an already-present exact row and returns without a generation update; a semantic static mutation must reject removal or weakening of this guard. |
| Capability identity is reassigned in place | Capability update is rejected; delete then insert advances each affected parent. |
| Role, wildcard, JSON or model output synthesizes authority | Only exact closed grant rows count; both authority checks also require active exact membership, admitted server role and signed current generation. |
| Existing users receive implicit power | Migration creates an empty grant table and no provisioning path or consumer. |
| Synthetic application-auth data becomes product authority | The seam imports and locks only the product `User` mapping and exact product grant relation. |
| Revocation races a command | The parent `FOR SHARE` lock conflicts with every user/grant generation advance; two checks run while ordered locks remain held. |
| Overflow wraps or reuses an old generation | Positive BIGINT constraints and trigger guards reject the whole transaction at the maximum. |
| Practice or actor is substituted | Server-owned composite user identity, composite grant FK and exact practice-scoped target are enforced. |
| Target or receipt probing leaks existence | User and appointment locks plus first full authority check precede idempotency access or classification. |
| Concurrent keys create two effects | Appointment remains locked while insert-on-conflict selects and locks the one unique idempotency winner. |
| Wait budget resets at each lock | One monotonic 2000 ms deadline is created once; only positive remaining time is applied before each blocking access. |
| NOWAIT, skip-locked or retry changes winner semantics | The seam contains none of them and performs no server effect retry. |
| A status receipt is broken by the new family | The database constraint retains the exact status-confirm branch and adds only one closed delete-confirm disjunct. |
| Another family claims receipt v1 | Version one is admitted only for the exact status or delete operation/route branches. |
| Legacy receipt gains new meaning | New authority/audit fields remain null and no legacy row is backfilled or replayed as v1. |
| Stored JSON changes replay bytes | Canonical bytes are delivery authority; lowercase SHA-256 is checked in constant time before release. |
| Full appointment or patient data leaks | The helper can construct only the six-field patient-free response; public response transition remains unmounted and separately gated. |
| Raw session identity becomes durable | Only a domain-separated length-framed 32-byte HMAC digest is represented. |
| Cancellation reason is weakened | The helper requires one exact dedicated code, preserves nullable text independently and rejects overlength text. |
| Human warnings and internal evidence are merged | Distinct JSON-array audit columns remain separate; legacy merged content is not reinterpreted. |
| Partial effect commits | The seam stages no effect itself and requires a future complete appointment/audit/receipt set before context exit or rolls back. |
| Scaffold is mistaken for executable proof | Migration and transaction text receive static/provider-free verification only; no engine or route executes. |
| Downgrade erases adopted authority meaning | Downgrade fails when any grant, delete receipt or delete audit v1 exists and otherwise restores the prior status-only constraint. |
| Events or readback become command proof | Events remain cues; readback remains separately authorised reconciliation and is not added here. |
| Protected or user-owned evidence is absorbed | Exact-file hashes and explicit-path staging exclude protected evidence, `docs/branding/` and all unrelated untracked paths. |

## Residual risks

- PostgreSQL parsing/catalogues, trigger behavior, actual locks and wait timing,
  RLS, concurrency, rollback, restart and unknown-commit recovery remain
  unproved until separately admitted disposable rehearsals.
- The source-only closed-world writer inventory does not prove production role
  privileges or future deployed catalogue state; those remain closed and must
  be re-established by later migration/catalogue and deployment gates.
- The scaffold deliberately does not verify signed proposal evidence, stage a
  cancellation, create an audit row, complete a receipt, mount a route, or
  provision a grant.
- Exact internal audit-evidence vocabulary and the public six-field response
  version transition remain future kernel/API gates; this scaffold only keeps
  their storage separate and fail-closed.
- Operational migration cost, capability administration, observability,
  performance, production recovery and rollout remain outside this tranche.

## Authority boundary

No route/schema/OpenAPI edit or call, migration/DDL/SQL/database execution,
real lock, capability provisioning, product/patient/clinical data, provider,
ADC, credential/IAM/browser/network action, watcher/event authority, product
command, deployment, production, release, Pages or protected-ref movement is
authorised. All unrelated untracked files remain preserved and excluded.
