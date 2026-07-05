# Implementation Plan: Sprint R11 — Nullable Status Reason Code Substrate

| Item | Value |
|---|---|
| Sprint | Sprint R11 (Sprint 11 - Reason Code Substrate) |
| Worker | DeepSeek Flash via Codex subagent |
| Branch | `codex/sprint-r11-reason-code-backend-plan` |
| Role | implementation |
| Plan Status | Awaiting Codex/User approval |

## My Understanding

The R10 governance policy defines a taxonomy of 12 cancellation/status-change reason codes grouped into Patient-initiated, Clinic-initiated, Administrative, Attendance, and Fallback categories. These need to be threaded through the existing appointment delete/cancel and status-change mutation pathways as an **optional, validated application-level field** — not as a database enum.

The implementation must:
- Add a shared reason-code allow-list and validator (app-level, not DB constraint)
- Add optional `status_reason_code: Optional[str]` to status and delete schemas
- Persist the code to the `Appointment` model and `AppointmentAuditLog` (nullable, non-breaking for legacy data)
- Pass the code through proposal payload display and freshness-ID computation
- Include the code in signed evidence payloads
- Reject invalid codes with a clear error
- Preserve existing `cancellation_reason` free-text field unchanged

## Intended Surface / Boundary

### Affected Surfaces

| Surface | Change |
|---|---|
| `app/schemas/appointments.py` | Add shared `STATUS_REASON_CODES` allow-list, validator helper. Add `status_reason_code: Optional[str]` to `AppointmentStatusUpdate`, `AppointmentStatusProposalIn`, `AppointmentStatusCommand`, `AppointmentDeleteIn`, `AppointmentDeleteCommand`, `AppointmentOut`. |
| `app/models/appointments.py` | Add nullable `status_reason_code` column to `Appointment` and `AppointmentAuditLog`. |
| `app/routers/appointments.py` | Thread status_reason_code through status/delete proposal, confirm, and write pathways. Validate via shared helper. Include in freshness-ID and signed evidence. |
| `tests/test_appointment_audit.py` | Valid-code persistence, invalid-code rejection, nullable legacy, audit-log exposure, proposal display. |

### Adjacent Surfaces That Must NOT Change

- Diary grid (`docs/diary/`) — no frontend changes
- Taskpane (`EMR4-Sidebar/`) — dropdown comes in a later sprint
- Appointment create route — no change to creation schema
- Appointment generic update route (`PUT /appointments/{id}`) — no change
- Waiting-area proposal/confirm — not a status transition
- Bernie proposals, sessions, interpret — no Bernie changes
- Past-date / same-day elapsed slot-write guards — not altered
- Database enum / reference table — not introduced
- Alembic migrations — not until Ariadne approves

## Out of Scope

- UI / taskpane dropdown controls
- Database enum or reference table creation
- Alembic migration (plan-gate assumption: no migration needed at plan stage)
- Past-date or same-day elapsed slot-write policy changes
- Bulk historical backfill or heuristic classification
- Requiring reason code on any mutation path (stays optional)
- Bernie session or interpret changes
- Waiting-area proposal/confirm routes
- Create or generic-update appointment routes
- Existing `cancellation_reason` free-text field removal

## Files Expected

```
app/schemas/appointments.py
app/models/appointments.py
app/routers/appointments.py
tests/test_appointment_audit.py
```

## Implementation Steps

### 1. Add shared reason-code allow-list in `app/schemas/appointments.py`

```python
STATUS_REASON_CODES: Final[frozenset[str]] = frozenset({
    "PATIENT_CANCELLED", "PATIENT_RESCHEDULED", "PATIENT_UNWELL",
    "PATIENT_TRANSPORT", "PRACTITIONER_UNAVAILABLE", "CLINIC_OPERATIONAL",
    "CLINIC_RESCHEDULED", "ADMIN_ERROR", "DUPLICATE_BOOKING",
    "DID_NOT_ATTEND", "LEFT_WITHOUT_SEEN", "OTHER", "LEGACY_UNCLASSIFIED",
})
```

Add `validate_status_reason_code(value: Optional[str]) -> Optional[str]`:
- Returns `None` if `None`
- Returns uppercased value if in `STATUS_REASON_CODES`
- Raises `ValueError` otherwise

### 2. Extend schemas with optional `status_reason_code`

- `AppointmentStatusUpdate`: add `status_reason_code: Optional[str] = None` with `field_validator`
- `AppointmentStatusProposalIn`: add `status_reason_code: Optional[str] = None` with validator
- `AppointmentStatusCommand`: add `status_reason_code: Optional[str] = None` (constructed from validated input)
- `AppointmentDeleteIn`: add `status_reason_code: Optional[str] = None` with validator
- `AppointmentDeleteCommand`: add `status_reason_code: Optional[str] = None`
- `AppointmentOut`: add `status_reason_code: Optional[str] = None`

### 3. Extend SQLAlchemy models

- `Appointment.status_reason_code`: `Column(String(50), nullable=True)`
- `AppointmentAuditLog.status_reason_code`: `Column(String(50), nullable=True)`

### 4. Thread through status proposal flow

- `propose_status_update`: include `status_reason_code` in `AppointmentStatusCommand` when supplied
- `_appointment_status_command_payload`: add `status_reason_code` when set
- `_appointment_status_state_payload`: add `status_reason_code` from DB

### 5. Thread through status confirm/write

- `_apply_appointment_status_update`: write `body.status_reason_code` to `appt.status_reason_code` when in `model_fields_set`; pass to `_write_audit`
- `_write_audit`: accept optional `status_reason_code`, write to `audit_log.status_reason_code`
- `confirm_status_proposal_route`: pass command's `status_reason_code` through

### 6. Thread through delete proposal flow

- Delete proposal builder: include `status_reason_code` in `AppointmentDeleteCommand`
- `_appointment_delete_command_payload`: add `status_reason_code`
- `_appointment_delete_state_payload`: add `status_reason_code`

### 7. Thread through delete confirm/write

- `_apply_appointment_delete`: write to `appt.status_reason_code`; pass to `_write_audit`
- `confirm_delete_proposal_route`: pass command's `status_reason_code` through

### 8. Signed evidence payloads

- `_status_signed_confirmation_payload` and `_delete_signed_confirmation_payload`: include `status_reason_code` from command payload

### 9. Tests

Add to `tests/test_appointment_audit.py`:

- `test_status_update_with_valid_reason_code` — each valid code persisting
- `test_status_update_with_invalid_reason_code` — 422 on bad code
- `test_status_update_without_reason_code_nullable` — no regression
- `test_delete_with_valid_reason_code` — each valid code
- `test_delete_with_invalid_reason_code` — 422 on bad code
- `test_delete_without_reason_code_nullable` — no regression
- `test_status_proposal_displays_reason_code` — code in proposal out
- `test_status_confirm_persists_reason_code` — code in DB after confirm
- `test_delete_confirm_persists_reason_code` — code in DB and audit log
- `test_reason_code_unchanged_on_no_supply` — no mutation when omitted

## Acceptance Checks

1. `py_compile` on all touched files passes
2. `pytest tests/test_appointment_audit.py -q` passes (existing tests + new)
3. Existing `DELETE /appointments/{id}` without body continues to work
4. Existing `PATCH /appointments/{id}/status` without `status_reason_code` continues to work
5. Invalid reason code returns 422 with clear error

## Risks / Ambiguities

| Risk | Mitigation |
|---|---|
| **Freshness-ID churn**: adding `status_reason_code` to payloads changes hashes. In-flight frontend proposals stale. | Acceptable — hash salt version stays unchanged (backward-compatible optional field). In-flight proposals stale naturally. |
| **Column nullable + no default**: existing rows have NULL. | `Optional[str]` in Pydantic + `nullable=True` in SQLAlchemy ensure safe handling. |
| **No migration at plan gate**: production DB lacks columns. | Tests using `db_create_all()` pick up columns automatically from model metadata. Ariadne approves migration step separately. |
| **Proposal freshness hash includes code**: changing code requires new proposal. | Desirable — proposal should reflect intended reason. |

## Dissent / Alternatives

1. **Separate reference table**: Rejected — app-level `frozenset` is reversible and matches R10 governance recommendation.
2. **Single shared field with free-text fallback**: Adopted — `status_reason_code` is nullable, sits alongside existing `cancellation_reason`.
3. **Schema-level vs route-level validation**: Schema-level Pydantic validator provides earliest rejection with clear error attribution.
4. **Database Enum**: Rejected per R10 governance — app-level allow-list keeps first step reversible.

## Completion Notes (pre-filled for submit)

- Files changed: `app/schemas/appointments.py`, `app/models/appointments.py`, `app/routers/appointments.py`, `tests/test_appointment_audit.py`
- Verification run: py_compile + `pytest tests/test_appointment_audit.py -q`
- Remaining risks: Freshness-ID hash change may stale in-flight proposals; no migration until Ariadne approves
