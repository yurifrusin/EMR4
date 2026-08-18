# DeepSeek V4 Flash/high default-off check-in route-adapter worker packet

Date: 2026-08-18

Timestamp: 2026-08-18T12:18:37+10:00 (Australia/Brisbane)

Source HEAD: `4daa2d772ffcf64e55f69917d2fb21802e959673`

Assigned worktree:
`C:\Users\sarashera\EMR4-worktrees\check-in-route-adapter-deepseek-4daa2d77`

Assigned branch:
`codex/check-in-route-adapter-deepseek-4daa2d77`

## Authority

You are the DeepSeek V4 Flash/high implementation-and-test worker. Read
`AGENTS.md` completely before acting. Then follow the frozen plan and threat
delta exactly. You may create or edit only:

- the bounded A5.1 import/binder/mapper/confirmation-handler region in
  `app/routers/appointments.py`;
- the single idempotency-before-envelope ordering seam in
  `app/services/appointment_check_in_product_adapter.py`;
- one narrow regression in
  `tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py`;
  and
- new `tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py`.

You may read only:

- `AGENTS.md`;
- `docs/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-plan.md`;
- `docs/security/raisa-provider-free-default-off-canonical-check-in-route-adapter-convergence-rehearsal-threat-model-delta.md`;
- the four owned files above;
- `app/config.py`;
- `app/schemas/appointments.py`;
- `app/models/appointments.py`;
- `app/models/tenancy.py`;
- `app/models/diary.py`;
- `app/services/appointment_idempotency.py`;
- `app/services/diary_committed_events.py`;
- `tests/test_model_required_bureau_a5_1_check_in_runtime.py`;
- `docs/api-spine/openapi/appointment-commands.yaml`;
- `docs/raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal-plan.md`;
- `docs/raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal-closeout.md`; and
- `orchestration/agent_inbox/codex/raisa-canonical-check-in-product-adapter-sol-acceptance.md`.

Use exact literal-path reads only after `AGENTS.md`; do not perform repository-
wide search, directory listing, protected-path access or reads outside this
allowlist. Permission availability is not authority.

## Deliverable

Implement the frozen plan exactly:

1. Keep `_a5_check_in_gate_open` first and idempotency normalization before any
   adapter dependency work.
2. Bind `CheckInDependencies` to the existing dedicated claim, exact-practice
   locked appointment, exact-practice active Receptionist reload, exact waiting-
   area lookup, evidence verifier, typed effect, existing audit/event/completion,
   commit/rollback and one post-commit readback.
3. Treat the accepted adapter's typed plans as authoritative. Do not add a
   generic executor or recompute command meaning.
4. Change the adapter only enough to classify replay/conflict/in-progress before
   envelope validation. A newly started invalid envelope must roll back. Every
   other accepted adapter invariant stays intact.
5. Make the confirmation handler call `compose_product_check_in` exactly once,
   with no direct claim, lock, mutation, audit, event, completion or commit
   fallback.
6. Preserve the exact existing 200 blocked, 404, 409 and 503 response families,
   patient-free success envelope and server-error posture for internal or
   uncertain failures.
7. Add self-contained authored-synthetic/static tests for the exact dependency
   and result mappings, the one-call/no-fallback handler, default gate ordering,
   unchanged route/schema/OpenAPI identities and idempotency precedence.

Do not edit the proposal route, settings, schemas, models, OpenAPI, other
command families or existing A5.1 runtime test. Do not execute a live route,
database, server, provider or external network. If the frozen response contract
is impossible within the four-file boundary, stop and report the exact blocker
without editing anything else.

## Allowed commands

- literal reads of the allowlist above and the four owned paths;
- `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile app/routers/appointments.py app/services/appointment_check_in_product_adapter.py tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py`;
- `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.ariadne_provider_free_pytest tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py`;
- `C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app/routers/appointments.py app/services/appointment_check_in_product_adapter.py tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py`;
- exact line counts for the three changed and one new file;
- `git status --short --untracked-files=no`;
- `git diff --check --` followed by the four exact owned paths;
- `git diff --` followed by the four exact owned paths;
- `git add --` followed by the four exact owned paths;
- `git diff --cached --check`;
- `git commit -m "feat(check-in): converge default-off route adapter"`;
- `git rev-parse HEAD`.

No package install, environment mutation, database/server/browser/provider call,
network access, protected ref, push, deployment or command outside this list.

## Terminal receipt

Return one compact result containing: status; exact files; focused test,
compile and Ruff results; commit hash; exact route/adapter boundary attestation;
and any genuine blocker. Do not claim acceptance, integration or broader
product authority.
