# Audit Correlation Continuity Index

Date: 2026-07-19

Sprint: 201

## Purpose

This index links the GraphQL audit/read-model declarations to the OpenAPI
appointment command audit and correlation metadata without opening any runtime
surface.

It answers one narrow question: which audit and correlation concepts are shared
between the read graph and command plane, and which are intentionally
read-model-only or command-plane-only?

## Action Bridge

| GraphQL AppointmentAuditAction | OpenAPI AuditIntent.audit_action | Continuity status | Notes |
|---|---|---|---|
| `PROPOSAL_STAGED` | `appointment_proposal_prepared` | `bridged` | Proposal preparation appears as read-model staged state and command audit intent. |
| `CONFIRMED_CREATE` | `appointment_created` | `bridged` | Confirmed create writes are command-owned and read through appointment audit models. |
| `CONFIRMED_UPDATE` | `appointment_updated` | `bridged` | Confirmed update writes are command-owned and read through appointment audit models. |
| `CONFIRMED_STATUS_CHANGE` | `appointment_status_changed` | `bridged` | Confirmed status writes are command-owned and read through appointment audit models. |
| `CONFIRMED_WAITING_AREA_MOVE` | `appointment_status_changed` | `bridged` | Waiting-area movement currently folds through the status command family. |
| `CONFIRMED_CANCEL` | `appointment_deleted` | `bridged` | Delete/cancel confirmation maps to the command-plane delete audit intent. |
| `DIRECT_COMPATIBILITY_WRITE` | `none` | `read_model_only` | Legacy compatibility writes remain visible in read models but outside the canonical OpenAPI proposal-confirm envelope. |
| `READ` | `none` | `read_model_only` | Read audit entries are GraphQL read-model vocabulary, not appointment command audit intent. |
| `none` | `slot_search_normalized` | `command_plane_only` | Slot-search normalization is a command-style read audit intent, not an appointment audit action. |
| `none` | `slot_search_proposed` | `command_plane_only` | Slot-search proposal is a command-style read audit intent, not an appointment audit action. |
| `none` | `slot_selected_for_proposal` | `command_plane_only` | Slot selection prepares create-proposal evidence and remains command-plane metadata. |

## Correlation Bridge

| GraphQL surface | OpenAPI surface | Continuity status | Notes |
|---|---|---|---|
| `AuditEvent.correlationId` | `X-Correlation-Id` | `bridged` | Generic audit read-model correlation id corresponds to the command request header. |
| `AppointmentAuditEvent.correlationId` | `ConfirmationAuditEvent.correlation_id` | `bridged` | Appointment audit read model and confirmation audit event both expose the propagated correlation id. |
| `AuditFilter.correlationId` | `CommandMeta.correlation_id` | `bridged` | Read-side filtering and command metadata share the same correlation concept. |

## Target-Kind Bridge

| GraphQL AuditTargetType | OpenAPI AuditIntent.target_kind | Continuity status | Notes |
|---|---|---|---|
| `APPOINTMENT` | `appointment` | `bridged` | Appointment is the shared audit target for proposal/confirmation workflows. |
| `none` | `slot_search` | `command_plane_only` | Slot-search audit intent is command-plane metadata, not a generic GraphQL target type yet. |
| `none` | `proposal` | `command_plane_only` | Proposal audit intent is command-plane metadata, not a generic GraphQL target type yet. |
| `PATIENT` | `none` | `read_model_only` | Patient audit reads are part of the broader read graph, not this appointment command schema. |
| `DIARY` | `none` | `read_model_only` | Diary audit reads are part of the broader read graph, not this appointment command schema. |
| `PRACTICE` | `none` | `read_model_only` | Practice audit reads are part of the broader read graph, not this appointment command schema. |
| `ACCESS_AI` | `none` | `read_model_only` | Access AI audit reads remain read-model vocabulary while provider gates stay closed. |
| `DIRECTORY` | `none` | `read_model_only` | Directory audit reads are outside the appointment command audit schema. |

## Command-Plane Fields

GraphQL audit read models must not acquire command-plane-only fields such as
`idempotencyKey`, `idempotency_key`, or `confirmer`. Those fields remain in
OpenAPI command and confirmation metadata, where command handlers own
idempotency, confirmer identity, evidence, and write authority.

## Stage 2 Local Synthetic Runtime Checkpoint

The approved Stage 2 appointment-create variant adds a runtime-proven, server-
owned correlation chain without changing GraphQL or adding a GraphQL mutation:

| Durable coordinate | Exact linkage | Runtime status |
|---|---|---|
| appointment command ledger id | `appointment_command_idempotency.id = appointment_audit_log.command_id = confirmation_receipt.correlation_id` | `local_synthetic_runtime_proven` |
| appointment target | `appointment_command_idempotency.target_appointment_id = appointment_audit_log.appointment_id = confirmation_receipt.appointment_id` | `local_synthetic_runtime_proven` |
| audit event | `appointment_command_idempotency.audit_log_id = appointment_audit_log.id = confirmation_receipt.audit_event_id` | `local_synthetic_runtime_proven` |
| Bernie session | retained opaque `bernie_session_id` agrees across command, audit, and receipt | `local_synthetic_runtime_proven` |

This checkpoint applies only to the existing
`POST /api/v1/appointments/proposals/create/confirm-bernie` local synthetic
vertical. The receipt `correlation_id` is the server-owned command-ledger UUID;
it is deliberately not a claim that the draft `X-Correlation-Id` header is
implemented or propagated by this route. Audit rows are append-only, while
expired detailed session/event rows may be purged without erasing the opaque
session coordinate from the durable command/audit/receipt chain.

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

This declaration index alone does not prove runtime correlation-id propagation,
resolver implementation, or production deployment readiness. The bounded Stage
2 checkpoint separately proves local synthetic database durability, direct
command/audit/receipt correlation, and append-only audit enforcement only for
the named Bernie create-confirm variant. It does not generalize those claims to
the draft request header, other command families, external clients, production,
or deployment.

`tests/test_api_spine_audit_correlation_continuity_index.py` validates this
index by parsing only this markdown file,
`docs/api-spine/graphql/appointment-diary-read.graphql`, and
`docs/api-spine/openapi/appointment-commands.yaml`.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_audit_correlation_continuity_index.py -q
```
