# DeepSeek Review - Sprint 204 Legacy Compatibility Write Deprecation Map

DeepSeek reviewed the current API Spine appointment route/read-model artifacts
for a narrow legacy compatibility write deprecation/read-model boundary map.

## Sources Reviewed

- `docs/api-spine/appointment-read-model-route-inventory.md`
- `tests/test_api_spine_appointment_openapi_drift_guard.py`
- `orchestration/api_spine_adr.md`
- `docs/api-spine/blueprint-first-model-second-boundary.md`
- `app/routers/appointments.py`

## Findings Integrated

- The four raw appointment compatibility writes already have proposal/confirm
  equivalents:
  - `create_appointment` uses `raw_compat_create` and maps to create proposal
    plus create confirm, including the Bernie create-confirm variant.
  - `update_appointment` uses `raw_compat_update` and maps to update proposal
    plus update confirm.
  - `update_appointment_status` uses `raw_compat_status` and maps to status or
    waiting-area proposal plus status confirm.
  - `cancel_appointment` uses `raw_compat_delete` and maps to delete proposal
    plus delete confirm.
- The existing `_raw_compat_evidence_and_headers()` helper supports
  `audit`, `header`, and `off` modes through
  `settings.appointment_raw_compat_mode`; the default is `audit`.
- The safest Sprint 204 increment is a static declaration-continuity artifact
  plus markdown/source parser tests, not a route/config/runtime behavior change.

## Risks Preserved

- Unknown compatibility-route consumers could break if raw routes are removed
  before client parity is proven.
- `appointment_raw_compat_mode=off` suppresses both raw compatibility evidence
  and deprecation headers, so future changes to that mode need explicit review.
- Raw compatibility routes still do not become proposal-confirm/idempotency
  equivalents by documentation alone.
- Existing deprecation headers are generic and do not yet carry migration or
  sunset details.

## Review Result

Accepted. Ariadne incorporated the raw compatibility tags, default mode
assertion, and map-only posture into
`docs/api-spine/legacy-compatibility-write-deprecation-map.md` and
`tests/test_api_spine_legacy_compatibility_write_deprecation_map.py`.
