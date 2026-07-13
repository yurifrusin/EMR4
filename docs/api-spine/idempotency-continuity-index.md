# Idempotency Continuity Index

Date: 2026-07-13

Sprint: 200

## Purpose

This index links the static appointment command metadata preflight to the
existing idempotency runtime checkpoints without opening any new enforcement
surface.

It answers one narrow question: for each OpenAPI appointment command path, what
is the current idempotency continuity status?

## Continuity Table

| OpenAPI path | Kind | Runtime status | Source sprint | Source test |
|---|---|---|---:|---|
| `/appointments/proposals/create` | proposal | `syntactic_only` | 200 | `tests/test_appointment_proposals.py` |
| `/appointments/proposals/create/confirm` | confirm | `ledger_wired` | 145 | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `/appointments/proposals/update` | proposal | `syntactic_only` | 200 | `tests/test_appointment_update_proposal.py` |
| `/appointments/proposals/update/confirm` | confirm | `ledger_wired` | 145 | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `/appointments/proposals/status` | proposal | `syntactic_only` | 200 | `tests/test_appointment_update_proposal.py` |
| `/appointments/proposals/status/confirm` | confirm | `ledger_wired` | 145 | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `/appointments/proposals/delete` | proposal | `syntactic_only` | 200 | `tests/test_appointment_status_mutations.py` |
| `/appointments/proposals/delete/confirm` | confirm | `ledger_wired` | 145 | `tests/test_api_spine_confirmation_family_idempotency_checkpoint.py` |
| `/appointments/proposals/slot-search/normalize` | read | `read_no_idempotency` | 199 | `tests/test_api_spine_idempotency_audit_metadata.py` |
| `/appointments/proposals/slot-search` | read | `read_no_idempotency` | 199 | `tests/test_api_spine_idempotency_audit_metadata.py` |
| `/appointments/proposals/slot-search/select` | read | `read_no_idempotency` | 199 | `tests/test_api_spine_idempotency_audit_metadata.py` |

Status meanings:

- `ledger_wired`: existing source-level checkpoint records that the confirmation
  route family requires `Idempotency-Key`, calls the appointment command ledger
  helper before writes, and completes the ledger after appointment/audit success.
- `documented_gap`: OpenAPI declares `Idempotency-Key`, but proposal-only runtime
  enforcement remains deliberately deferred and separately tracked.
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

## Closed Gates

This index does not authorize:

- proposal-only route idempotency enforcement;
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

This is a documentation continuity artifact. It does not prove runtime concurrency
behavior, network-loss replay behavior, backend handler correctness,
database transaction durability, audit-log append-only semantics, or production
deployment readiness.

`tests/test_api_spine_idempotency_continuity_index.py` validates this index by
parsing only this markdown file and
`docs/api-spine/openapi/appointment-commands.yaml`.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_idempotency_continuity_index.py -q
```
