# S11 Protected-Master Integration Manifest

Source branch: `codex/s10-terra-staging`
S11 source commit range: `7624392b..c7765584`
Candidate code commit: `c7765584`

## Expected Diff Scope

- `tests/test_api_spine_confirmation_contract_matrix.py`
- S11 plan, worker packet, W1 review artifacts, and manifest evidence only

No production router, schema, model, migration, OpenAPI, policy, provider, or
deployment file may be included in the protected-master integration.

## Required Tests

```powershell
.venv\Scripts\python.exe -m pytest tests\test_api_spine_confirmation_contract_matrix.py tests\test_api_spine_confirmation_family_idempotency_checkpoint.py tests\test_api_spine_appointment_idempotency_route_integration_preflight.py tests\test_api_spine_artifacts.py -q
git diff --check
```

The matrix, confirmation-family checkpoint, and API-spine artifacts pass. The
route-integration preflight has one documented pre-existing failure because the
existing create-proposal `Idempotency-Key` binding falls inside its broad
non-confirm span. This S11 commit does not change that route or test.

## Clean/Conflict-Free Precondition

Before Sol authorizes protected-master integration:

1. Refresh `origin/master` and confirm this source branch is clean.
2. Confirm the expected diff scope above, with no unrelated commits.
3. Resolve or explicitly accept the unchanged pre-existing preflight failure.
4. Confirm merge is conflict-free against the then-current `origin/master`.
5. Do not push or modify protected master before Sol authorization.
