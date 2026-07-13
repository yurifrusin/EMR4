# S11 DeepSeek Flash — Confirmation Contract Matrix Review

## Artifact

| Item | Value |
|---|---|
| **Worker** | DeepSeek Flash via Deep Code |
| **Track** | S11 confirmation contract matrix |
| **Commit** | `ead8c23982e9111e348af83aea20a5304d506133` |
| **Branch** | `deepcode/s11-confirmation-contract-matrix` |
| **New file** | `tests/test_api_spine_confirmation_contract_matrix.py` |

## Scope

Derives a compact matrix over the five existing REST appointment confirmation
handlers. Does not edit production code, schemas, OpenAPI, models, migrations,
policies, or existing tests. Does not issue HTTP commands or writes.

## Confirmation Contract Matrix

The matrix in `tests/test_api_spine_confirmation_contract_matrix.py` defines
five wired confirmation families:

| Family | Handler | Route | Operation ID | Route Family | Base Evidence |
|---|---|---|---|---|---|
| Staff create | `confirm_create_proposal_route` | `POST /proposals/create/confirm` | `confirmAppointmentCreateProposal` | `create-confirm` | `_STAFF_CONFIRM_CREATE_BASE_EVIDENCE` |
| Bernie create | `confirm_bernie_create_proposal` | `POST /proposals/create/confirm-bernie` | `confirmAppointmentCreateProposal` | `create-confirm-bernie` | `_BERNIE_CONFIRM_CREATE_BASE_EVIDENCE` |
| Update | `confirm_update_proposal_route` | `POST /proposals/update/confirm` | `confirmAppointmentUpdateProposal` | `update-confirm` | `_BERNIE_CONFIRM_UPDATE_BASE_EVIDENCE` |
| Status | `confirm_status_proposal_route` | `POST /proposals/status-confirm` | `confirmAppointmentStatusProposal` | `status-confirm` | `_STATUS_CONFIRM_BASE_EVIDENCE` |
| Delete | `confirm_delete_proposal_route` | `POST /proposals/delete-confirm` | `confirmAppointmentDeleteProposal` | `delete-confirm` | `_DELETE_CONFIRM_BASE_EVIDENCE` |

### Assertions per handler (20 tests)

All five handlers pass deterministic source-inspection assertions for:

1. **Idempotency-Key header binding** — `Header(None, alias="Idempotency-Key")` parameter and `_normalize_idempotency_key()` call
2. **Operation id constant** — Each handler's operation id constant exists with the correct value
3. **Route family constant** — Each handler's route family constant exists with the correct value
4. **`claim_appointment_command()`** — Called before any write, with operation_id, route_family, request_body, and shared secret/stale_after
5. **`complete_appointment_command()`** — Called before `db.commit()` with `result_kind="confirmed_write"`
6. **Request-body idempotency binding** — `request_body=body.model_dump(mode="json")`
7. **Idempotency decision handling** — `_handle_create_confirm_idempotency_decision(decision)` with `mapped_decision is not None` guard
8. **Audit evidence** — Each handler starts with its base evidence list and includes `audit_evidence` in its response body
9. **confirmed=true guard** — `body.confirmed is not True` check blocks unconfirmed requests
10. **Completion before commit** — `complete_appointment_command()` appears before `db.commit()` in every handler

### Exclusion assertions (7 tests)

Proposal-only routes (`propose_create_appointment`, `propose_update_appointment`,
`propose_status_update`, `propose_delete_appointment`) and raw compatibility
routes (`update_appointment`) are verified to NOT use:

- `claim_appointment_command()`
- `complete_appointment_command()`
- Full `Idempotency-Key` header ledger (proposal-only create has proposal-level key normalization only, without claim/complete)

Read-only/list/non-confirm surfaces also exclude the confirmation idempotency ledger.

### Handler delegation note

`confirm_update_proposal_route` delegates the confirm body check and audit
evidence setup to the `confirm_update_proposal()` helper function. The matrix
resolves this by inspecting the helper body when testing the update handler.

## Test Results

```
Module                                                          Passed  Failed
─────────────────────────────────────────────────────────────── ────── ──────
test_api_spine_confirmation_contract_matrix.py                     20      0  (new)
test_api_spine_confirmation_family_idempotency_checkpoint.py        7      0
test_api_spine_appointment_idempotency_route_integration_preflight.py 4    1  (pre-existing*)
test_api_spine_artifacts.py                                        31      0
─────────────────────────────────────────────────────────────── ────── ──────
Total                                                              63      1
```

\* The single failure (`test_current_router_wires_only_approved_confirmation_families`)
is pre-existing and unrelated to this sprint. It fails because
`propose_create_appointment` has a `Idempotency-Key` header parameter (for
proposal-level key normalization), which appears in the "rest" zone that the
existing test expects to be free of the string `"Idempotency-Key"`. This was not
introduced by the new contract matrix module.

## Verification

- Production code, schemas, OpenAPI, models, migrations, policies: **untouched**
- Existing tests: **not edited**
- HTTP commands or writes: **none issued**
- Node JavaScript checks: not applicable (Python-only test module)

## STATUS: complete
