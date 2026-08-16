# DeepSeek bounded mechanical correction — delete-confirm public schema exactness

Date: 2026-08-17

Timestamp: 2026-08-17T05:24:00+10:00 (Australia/Brisbane)

## Exact candidate

- Worktree: `C:\Users\sarashera\EMR4-worktrees\delete-confirm-http-route-convergence-deepseek-f78524b4`
- Branch: `codex/worker-delete-confirm-http-route-f78524b4`
- Exact clean HEAD: `45311f8c238d935716574abae96d9715a070782d`
- Original implementation commit: `abdbcd5f28d39d21084bbc86b22f7201217226b0`

The original worker result is preserved but not admitted. This is the plan's
sole permitted same-lane mechanical correction. Do not revisit route behavior
or any other file.

## Exact defects

1. The delete-confirm `200` response in
   `docs/api-spine/openapi/appointment-commands.yaml` still references generic
   `AppointmentConfirmResultEnvelope`, which exposes `appointment` and lacks
   the versioned minimal delete receipt. Add a dedicated exact delete-confirm
   public-envelope component and receipt component, and point only the delete
   confirm response at it. The generic component remains unchanged for other
   command families.
2. `AppointmentDeleteConfirmationReceipt` lacks `extra=forbid` and admits a
   non-null `waiting_area_id`. Make nested receipt extras fail, require
   `waiting_area_id` to be exactly null, retain cancellation max length 500,
   and keep the dedicated status/reason/warning semantics consistent with the
   canonical serializer.
3. Update API alignment metadata to record both status and delete canonical
   aliases mounted on 2026-08-17.
4. Add focused regression assertions proving the OpenAPI response uses only
   the dedicated schema, neither dedicated schema contains `appointment`,
   nested extras/non-null waiting-area values fail, and the deterministic
   reviewer detects regression. Regenerate its exact evidence/report.

## Owned files only

- `app/schemas/appointments.py`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `scripts/raisa_provider_free_delete_confirm_http_route_convergence.py`
- `tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py`
- `tests/test_raisa_provider_free_delete_confirm_http_route_convergence_plan.py`
- `tests/test_api_spine_appointment_openapi_drift_guard.py` only if its exact
  response-schema assertion belongs there
- `orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/provider-free-route-convergence-evidence.json`
- `orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/route-convergence-report.md`
- `orchestration/agent_inbox/deepseek/raisa-provider-free-delete-confirm-http-route-convergence-mechanical-correction-worker-receipt.json`

No other edit is permitted. Do not amend or erase prior commits/receipts.

## Checks

Use `C:\Users\sarashera\emr4\.venv\Scripts\python.exe` and run focused tests
with `--noconftest`, reviewer `--no-write`, Ruff over changed Python, compile,
`git diff --check`, exact changed-path verification and byte-identical evidence
regeneration. No database, Docker, SQL, network, provider or protected access.

Commit the correction separately and write a structured receipt naming the
exact before/after commits, changed paths, test counts, mutation count and the
four corrected invariants. Do not accept, integrate or push.
