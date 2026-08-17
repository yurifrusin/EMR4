# DeepSeek V4 Flash/high canonical check-in product-adapter worker packet

Date: 2026-08-18

Timestamp: 2026-08-18T08:58:42+10:00 (Australia/Brisbane)

Source HEAD: `2b20e59c4a6c6584709f794e7ed4b5e6b1dc5b0b`

Assigned worktree:
`C:\Users\sarashera\EMR4-worktrees\check-in-product-adapter-deepseek-2b20e59c`

Assigned branch:
`codex/check-in-product-adapter-deepseek-2b20e59c`

## Authority

You are the DeepSeek V4 Flash/high implementation-and-test worker. Read
`AGENTS.md` completely before acting. Then follow the frozen plan and threat
delta exactly. You may create/edit only these two new files:

- `app/services/appointment_check_in_product_adapter.py` (maximum 750 lines);
- `tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py`
  (maximum 950 lines).

You may read only:

- `AGENTS.md`;
- `docs/raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal-plan.md`;
- `docs/security/raisa-provider-free-unmounted-canonical-check-in-product-adapter-extraction-rehearsal-threat-model-delta.md`;
- `app/routers/appointments.py`;
- `app/config.py`;
- `app/schemas/appointments.py`;
- `app/models/appointments.py`;
- `app/models/tenancy.py`;
- `app/models/diary.py`;
- `app/services/appointment_idempotency.py`;
- `app/services/diary_committed_events.py`;
- `app/services/appointment_status_product_adapter.py`;
- `docs/raisa-provider-free-read-only-arrival-check-in-command-family-convergence-review.md`;
- `docs/emr4-model-required-bureau-a5-b4-command-runtime-plan.md`; and
- `docs/api-spine/openapi/appointment-commands.yaml`.

Use exact literal-path reads only after `AGENTS.md`; do not use repository-wide
search, directory listing, protected paths or any file outside this allowlist
and your two owned outputs. Permission availability is not authority.

## Deliverable

Implement the plan's unmounted `compose_product_check_in` seam with typed
bounded helpers/results and injected dependencies. It must:

- exclude settings and the A5.1 feature/practice gate;
- require a current active exact-practice Receptionist supplied by the server;
- admit only the dedicated typed check-in confirmation family;
- preserve exact current-state, command-payload, target-area and 32-character
  freshness behavior;
- classify claim replay/conflict/in-progress/evidence-reuse before effects;
- verify opaque evidence through an injected verifier;
- enforce exact waiting-area assignment/preservation with no move/removal;
- order one status/area effect, audit, checked-in event, completion, commit and
  fresh readback through injected fake callbacks;
- roll back pre-commit failure and never release a false successful receipt;
- release no patient, clinical, raw evidence or raw idempotency material; and
- import no router, settings, `SessionLocal`, server or generic executor.

Use authored-synthetic in-process fakes only. Tests must cover the frozen
success/replay/failure matrix and reject at least 60 hostile mutations with
zero successful effect. Parametrization is encouraged.

Do not edit or import the adapter from the existing route. Do not weaken the
plan because an implementation choice is inconvenient. If an exact plan
responsibility is genuinely impossible within the two-file boundary, stop and
report the concrete blocker without editing another file.

## Allowed commands

- literal reads of the allowlist above and your two outputs;
- `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile app/services/appointment_check_in_product_adapter.py tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py`;
- `C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m scripts.ariadne_provider_free_pytest tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py`;
- `C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app/services/appointment_check_in_product_adapter.py tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py`;
- exact line counts for the two owned files;
- `git status --short --untracked-files=no`;
- `git diff --check --` followed by the two exact owned paths;
- `git diff --` followed by the two exact owned paths;
- `git add --` followed by the two exact owned paths;
- `git diff --cached --check`;
- `git commit -m "feat(check-in): extract unmounted product adapter"`;
- `git rev-parse HEAD`.

No package install, environment mutation, network/provider/database/server,
route call, protected ref, push, deployment or command outside this list.

## Terminal receipt

Return one compact result containing: status; exact files; line counts; focused
test, compile and Ruff results; hostile-mutation count; commit hash; boundary
attestation; and any genuine blocker. Do not claim acceptance or integration.
