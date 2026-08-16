# Provider-free delete-confirm HTTP route convergence report

Date: 2026-08-17
Timestamp: 2026-08-17T04:36:29.1514011+10:00

Status: provider-free route convergence candidate

## Scope

- Canonical `POST /api/v1/appointments/proposals/delete/confirm` and hidden historical `/proposals/delete-confirm` alias over one handler.
- Server-minted opaque `raisa.delete_proposal_version_binding.v1` carried and required.
- Authenticated bearer/current-user/command-session and five domain-separated secrets into exactly one accepted adapter call.
- Versioned minimal public delete-confirm response schema; no appointment read model.
- Canonical public-envelope bytes for committed/replay; private `stored_response_bytes` never HTTP content.
- Raw `DELETE /api/v1/appointments/{appointment_id}` and non-delete command families unchanged.

## Checks

| Check | Passed | Details |
|---|---|---|
| contract_schema | yes | jsonschema validation passed |
| pre_edit_hashes | yes | 11 read-only inputs verified |
| DHC-S01 | yes | canonical endpoint, signed evidence and opaque positive-version binding carried |
| DHC-S02 | yes | exactly one adapter call with server-owned ingress and no route-local behavior |
| DHC-S03 | yes | both paths bind one handler; alias absent from OpenAPI |
| DHC-S04 | yes | byte-identical public bytes; private stored bytes differ and are never HTTP content |
| DHC-S05 | yes | exact receipt envelope admitted; forbidden/extra fields rejected |
| DHC-S06 | yes | all five hostile binding variants rejected |
| DHC-S07 | yes | all invalid contexts returned closed 403 adapter outcomes |
| DHC-S08 | yes | blank idempotency returned 409 idempotency_key_required; route missing/blank maps to 400 |
| DHC-S09 | yes | route carries no warning/stale/source-version logic; adapter owns it |
| DHC-S10 | yes | invalid envelopes fail closed; route has no write and never serves stored bytes |
| DHC-S11 | yes | router, OpenAPI, inventory, Diary descriptor and drift guard agree |
| DHC-S12 | yes | raw DELETE route and all non-delete confirm families remain present |
| hostile_contract_mutations | yes | 113/134 hostile contract mutations rejected |
| hostile_envelope_mutations | yes | 36/36 hostile envelope mutations rejected |

## Scenario outcomes

| Scenario | Outcome |
|---|---|
| DHC-S01 | passed |
| DHC-S02 | passed |
| DHC-S03 | passed |
| DHC-S04 | passed |
| DHC-S05 | passed |
| DHC-S06 | passed |
| DHC-S07 | passed |
| DHC-S08 | passed |
| DHC-S09 | passed |
| DHC-S10 | passed |
| DHC-S11 | passed |
| DHC-S12 | passed |

Hostile contract mutations rejected: 149 (>=100 required).

## Containment booleans

- database_opened: false
- docker_used: false
- network_opened: false
- provider_used: false
- protected_evidence_accessed: false
- sql_executed: false
- private_bytes_not_delivered: true
- one_handler_adapter_call: true
- raw_delete_unchanged: true

Result: raisa_provider_free_delete_confirm_http_route_convergence_pass
