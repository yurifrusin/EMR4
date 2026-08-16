# DeepSeek worker packet — provider-free delete-confirm HTTP route convergence

Date: 2026-08-17

Timestamp: 2026-08-17T04:36:29.1514011+10:00 (Australia/Brisbane)

## Exact workspace

- Worktree: `C:\Users\sarashera\EMR4-worktrees\delete-confirm-http-route-convergence-deepseek-f78524b4`
- Branch: `codex/worker-delete-confirm-http-route-f78524b4`
- Exact source HEAD: `f78524b41c909c74acc93b2818be8fc871ed8fd3`
- Model: DeepSeek V4 Flash/high through Claude Code `--bare`

Before editing, verify the exact HEAD, branch and clean tracked worktree. Read
the frozen plan, threat delta and contract/schema completely. The plan's exact
source allowlist applies; do not search the repository or protected paths.

## Task

Implement exactly the five frozen transition gaps in
`docs/raisa-provider-free-delete-confirm-http-route-convergence-plan.md`:

1. canonical delete-confirm path plus hidden historical alias over one handler;
2. server-minted opaque proposal-version binding and required carriage;
3. authenticated bearer/current user/command-session plus five server-derived
   domain-separated secrets into exactly one accepted adapter call;
4. the minimal versioned delete-confirm public response schema; and
5. canonical public-envelope bytes for committed/replay, never private
   `stored_response_bytes` as HTTP content.

Remove route-local claim/read/verification/mutation/audit/receipt/commit
behavior from `confirm_delete_proposal_route`. Preserve raw DELETE byte-for-byte
and do not edit the accepted adapter, composition or physical seam.

## Owned files

You may edit only:

- `app/routers/appointments.py`
- `app/schemas/appointments.py`
- `app/services/diary/confirm_actions.py`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `orchestration/api_spine_appointment_command_alignment_inventory.md`
- the exact existing narrow test-repair files marked in the plan, and only
  where an assertion must recognize the new canonical path, binding, adapter
  ownership or minimal response;
- `scripts/raisa_provider_free_delete_confirm_http_route_convergence.py`
- `tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py`
- `tests/test_raisa_provider_free_delete_confirm_http_route_convergence_plan.py`
- `orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/provider-free-route-convergence-evidence.json`
- `orchestration/continuity/raisa-provider-free-delete-confirm-http-route-convergence/route-convergence-report.md`
- `orchestration/agent_inbox/deepseek/raisa-provider-free-delete-confirm-http-route-convergence-worker-receipt.json`

Do not edit the plan, threat delta, contract/schema, latch, AGENTS.md, register,
Compass/Continuity, closeouts, Sol/Gemini artifacts or unrelated files.

## Required implementation invariants

- Add `delete_proposal_version_binding` to the safe proposal metadata and make
  it a required confirmation field.
- Mint signed evidence with the delete-specific evidence secret before minting
  the version binding from `appointment_state_version`.
- Use exact domains `emr4.delete-confirm.<purpose>.v1` for `evidence`,
  `proposal-version`, `authenticated-session`, `idempotency` and
  `stored-session-binding`.
- Keep the accepted adapter's own validation/outcome mapping intact.
- For success, serialize `result.body` through
  `canonical_delete_confirm_envelope_bytes`. `stored_response_bytes` may be
  checked for presence but must never be passed to `Response(content=...)`.
- Blocked/error adapter outcomes return their exact status and body with no
  fallback.
- Both decorators must bind `confirm_delete_proposal_route`; only the canonical
  decorator appears in generated OpenAPI.
- The public schema is exact, versioned, forbids extras, exposes `receipt` and
  never exposes `appointment` or mutable read-model fields.
- Keep raw `cancel_appointment` and `_apply_appointment_delete` unchanged.
- No database, Docker, SQL, source watcher, provider, network or protected
  evidence access.

## Deterministic evidence

Create a reviewer script which validates the frozen contract, exact pre-edit
hashes where applicable, all twelve `DHC-S*` scenarios, output shapes and at
least 100 meaningful hostile contract mutations. `--no-write` must perform the
same checks without changing artifacts. A write run must generate only the two
owned evidence/report files byte-deterministically; the report needs Date and
ISO Timestamp at the top.

Focused route tests must use `--noconftest`, in-memory dependency/adapter
stubs and no database connection. Use the repository interpreter explicitly:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest --noconftest -q tests/test_raisa_provider_free_delete_confirm_http_route_convergence.py tests/test_raisa_provider_free_delete_confirm_http_route_convergence_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest --noconftest -q tests/test_api_spine_appointment_openapi_drift_guard.py tests/test_api_spine_openapi_backend_alignment.py tests/test_api_spine_confirmation_contract_matrix.py tests/test_api_spine_confirmation_family_idempotency_checkpoint.py tests/test_api_spine_appointment_idempotency_route_integration_preflight.py tests/test_api_spine_appointment_command_alignment_inventory.py tests/test_api_spine_appointment_idempotency_gap.py tests/test_api_spine_delete_confirm_idempotency_preflight.py tests/test_api_spine_delete_confirm_idempotency_route_contract.py tests/test_api_spine_proposal_only_idempotency_preflight.py tests/test_api_spine_staff_create_confirm_idempotency_route_contract.py tests/test_diary_confirm_actions.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.raisa_provider_free_delete_confirm_http_route_convergence --no-write
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check <every changed Python file>
git diff --check
```

If a selected legacy test requires repository database fixtures, do not run it
under this worker envelope; report it for Sol's later ordinary regression pass.

## Finish

Inspect the exact diff, confirm no forbidden file changed, commit the owned
candidate, and write the receipt JSON with:

- `status`: `completed` or `blocked`;
- exact source and result commit IDs;
- exact changed paths;
- checks with exit codes and counts;
- hostile mutation count and twelve scenario outcomes;
- explicit booleans for no database/provider/network/protected access,
  private bytes not delivered, one handler/adapter call and raw DELETE
  unchanged; and
- any issue or narrow repair needed.

Do not accept or integrate your own work and do not push any ref.
