# Idempotency Continuity Index

Date: 2026-07-19

Tranche: S19-S21

## Purpose

This index links the appointment command metadata preflight to the current
idempotency runtime checkpoints. The S19-S21 tranche opens syntactic header
enforcement on the four canonical proposal routes without granting replay or
write authority.

It answers one narrow question: for each OpenAPI appointment command path, what
is the current idempotency continuity status?

## Continuity Table

| OpenAPI path | Kind | Runtime status | Source sprint | Source test |
|---|---|---|---:|---|
| `/appointments/proposals/create` | proposal | `syntactic_only` | S19-S21 | `tests/test_appointment_proposals.py` |
| `/appointments/proposals/create/confirm` | confirm | `ledger_wired` | 145 | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `/appointments/proposals/update` | proposal | `syntactic_only` | S19-S21 | `tests/test_appointment_update_proposal.py` |
| `/appointments/proposals/update/confirm` | confirm | `ledger_wired` | 145 | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `/appointments/proposals/status` | proposal | `syntactic_only` | S19-S21 | `tests/test_appointment_update_proposal.py` |
| `/appointments/proposals/status/confirm` | confirm | `ledger_wired` | 145 | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `/appointments/proposals/delete` | proposal | `syntactic_only` | S19-S21 | `tests/test_appointment_status_mutations.py` |
| `/appointments/proposals/delete/confirm` | confirm | `ledger_wired` | 145 | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `/appointments/proposals/slot-search/normalize` | read | `read_no_idempotency` | 199 | `tests/test_api_spine_idempotency_audit_metadata.py` |
| `/appointments/proposals/slot-search` | read | `read_no_idempotency` | 199 | `tests/test_api_spine_idempotency_audit_metadata.py` |
| `/appointments/proposals/slot-search/select` | read | `read_no_idempotency` | 199 | `tests/test_api_spine_idempotency_audit_metadata.py` |

Status meanings:

- `ledger_wired`: existing source-level checkpoint records that the confirmation
  route family requires `Idempotency-Key`, calls the appointment command ledger
  helper before writes, and completes the ledger after appointment/audit success.
- `syntactic_only`: runtime requires a nonblank `Idempotency-Key`, but the
  non-mutating proposal does not claim durable replay or write authority.
- `read_no_idempotency`: command-style read surface with `X-Correlation-Id` only;
  it must not be treated as a replayable write command.

The runtime confirmation-family checkpoint records five wired backend families
because it includes the Bernie create-confirm backend variant. The OpenAPI
continuity table above intentionally covers only the eleven canonical OpenAPI
`paths` entries: four confirm paths, four proposal-only paths, and three
slot-search command-style read paths.

Legacy compatibility writes and Bernie backend variants are outside this index
unless and until they become canonical OpenAPI `paths` entries. Their current
posture remains tracked by the existing source checkpoints and blocked-gate
notes rather than by this static OpenAPI continuity table.

## Stage 2 Bernie Create-Confirm Checkpoint

The existing backend variant
`POST /api/v1/appointments/proposals/create/confirm-bernie` now has bounded
local synthetic runtime evidence beyond the canonical declaration table:

- the ledger claim is one PostgreSQL `INSERT ... ON CONFLICT DO NOTHING`
  followed by a row lock on the single actor/practice/operation/key identity;
- two independent same-key confirmation transactions return one stored result
  and create exactly one appointment, audit, completed ledger, and confirmation
  outcome;
- an injected failure after the appointment, audit, and session events are
  flushed but before command completion/commit rolls every effect back;
- the same key then succeeds once, and a fresh database session replays the
  stored response without another write; and
- raw command and session-event idempotency keys are HMAC-hashed rather than
  persisted.

This checkpoint does not change the four canonical `ledger_wired` rows or their
status counts. It applies only to the already approved Bernie appointment-create
variant and does not grant durable replay to proposals, slot search, other
compatibility writes, or new appointment actions.

## Closed Gates

This index does not authorize:

- proposal-only durable replay-ledger enforcement;
- raw compatibility `PUT`, `PATCH`, or `DELETE` idempotency enforcement;
- slot-search reservation or replay semantics;
- provider calls or live provider gates;
- runtime FGA clients;
- external patient clients;
- GraphQL mutations;
- H15/H-series runtime imports;
- memory/RAG/GraphRAG runtime wiring;
- broad historical diary trove mining;
- model-to-database writes outside REST command handlers.

## Boundary

The canonical index rows and their static source tests do not prove runtime
concurrency behavior for every command family, network-loss behavior, or
production deployment readiness. The Stage 2 checkpoint separately proves
transaction concurrency, rollback, and fresh-session replay for the one bounded
local synthetic Bernie create-confirm variant; it is not a production or broad
command-family claim.

`tests/test_api_spine_idempotency_continuity_index.py` validates this index by
parsing only this markdown file and
`docs/api-spine/openapi/appointment-commands.yaml`.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_continuity_index.py -q
```
