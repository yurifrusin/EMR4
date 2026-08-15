# DeepSeek worker packet: delete-confirm conditional-command kernel rehearsal

Date: 2026-08-15

Timestamp: 2026-08-15T11:55:04+10:00 (Australia/Brisbane)

## Identity and workspace

- Worker: DeepSeek V4 Flash/high through Claude Code `--bare`.
- Worktree: `C:\Users\sarashera\EMR4-worktrees\delete-confirm-kernel-deepseek-717c1233`.
- Branch: `codex/worker-delete-confirm-kernel-717c1233`.
- Exact source HEAD: `717c1233046452abff7d83af68e9949a31cc29b5`.
- This is a bounded implementation/test package. You have no architecture,
  acceptance, integration, push, protected-ref or baton authority.

Read `AGENTS.md` completely, then read these frozen controlling files:

1. `docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-rehearsal-plan.md`;
2. `docs/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission.md`;
3. `docs/security/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission-threat-model-delta.md`;
4. `docs/raisa-reception-one-cancellation-command-path-readiness-review-closeout.md`;
5. `orchestration/agent_inbox/codex/raisa-reception-one-cancellation-command-path-readiness-review-sol-acceptance.md`;
6. `orchestration/api_spine_adr.md`;
7. `docs/api-spine/openapi/appointment-commands.yaml` only for its delete alignment, paths and delete schemas; and
8. the accepted status protocol analogue:
   `scripts/raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal.py` and
   `tests/test_raisa_provider_free_unmounted_status_transaction_kernel_protocol_rehearsal.py`.

Do not inspect protected holdouts or historical Diary/PHI.

## Owned files only

Create and edit only:

- `scripts/raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py`;
- `tests/test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py`;
- `tests/test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_plan.py`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission/contract.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission/contract.schema.json`; and
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-conditional-command-kernel-architecture-admission/provider-free-acceptance-evidence.json`.

Do not edit the frozen plan, architecture, threat delta, application source,
OpenAPI, AGENTS, implementation plan, continuity/Compass, other tests, worker
configuration or any existing artifact.

## Required implementation

Build one pure standard-library-plus-`jsonschema` Python module. It must not
import `app`, SQLAlchemy, a database driver, requests/httpx/socket/subprocess,
provider clients, browser tooling or runtime command code. The module should:

1. build a closed contract and JSON Schema;
2. bind exact SHA-256 hashes for all three frozen tranche documents, readiness
   closeout, readiness Sol acceptance, API Spine ADR and appointment OpenAPI;
3. model only dedicated `confirmAppointmentDeleteProposal` / `delete-confirm`
   ingress;
4. use the exact symbolic lock order `practice -> appointment ->
   idempotency_record`, with schedule-domain skipped;
5. check current authority after target lock and again with all locks held,
   before any replay disclosure;
6. validate `confirmed=true`, required warning acknowledgements, authentic and
   unexpired signed evidence, exact server-session/practice/actor/operation/
   target/state/waiting-area/existing-reason/proposed-reason/digest bindings;
7. require a current Cancelled reason code for new dedicated ingress and allow
   optional free text of at most 500 characters, preserving the admitted value
   exactly across appointment, audit and receipt;
8. simulate one atomic appointment/audit/completed-receipt write set, complete
   rollback at every pre-commit injection, and stored replay after lost
   response;
9. simulate overlapping different keys, same-key same/different digest,
   authority loss while waiting, stale state and separately authorised
   post-commit readback;
10. reject raw delete, status fallback, event evidence, model/channel
    confirmation and cross-practice/absent targets without effect or receipt
    disclosure; and
11. generate deterministic JSON artifacts with `--write`, otherwise print a
    compact evidence report and exit nonzero on failure.

Use only `syn-` identifiers, fixed UTC timestamps, fixed non-secret digests,
allowed cancellation codes and plainly fictional bounded cancellation text.

The closed packet must contain at least 24 decision scenarios and 12 transaction
schedules. At least 40 independent hostile mutations must each fail validation.
The evidence report must record scenario/schedule/mutation counts, zero admitted
hostile mutations, every effect-boundary flag false and
`runtime_or_command_authority_granted=false`.

## Required tests

Tests must prove at minimum:

- canonical contract/schema/evidence equality and exact source hashes;
- both authority checks and authority-before-replay non-disclosure;
- exact lock order on every schedule;
- structured-reason requirement, allowlist rejection, optional-text bound and
  exact cross-artifact preservation;
- waiting-area clearing in appointment, audit and receipt;
- every pre-commit injection rolls back appointment/audit/receipt and claim;
- lost-response retry is one commit plus one replay with no duplicate effect;
- same-key conflict and different-key overlap winner/loser behavior;
- post-commit readback is separately authorised;
- raw/status/event/model/channel ingress cannot self-confirm or execute;
- every hostile mutation fails closed;
- the script has no forbidden imports and all effect flags are false; and
- plan/architecture/threat text contains the frozen timestamp, boundaries,
  acceptance counts and next-gate claim.

Use the main environment interpreter for verification:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py --write
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py tests\test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_plan.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py tests\test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission.py tests\test_raisa_provider_free_unmounted_delete_confirm_conditional_command_kernel_architecture_admission_plan.py
git diff --check
```

## Forbidden surfaces

No mounted route/OpenAPI/GraphQL/database/product-client/UI edit; no application
import or execution; no database/source/watcher/event runtime; no provider call;
no patient/product/clinical/protected data; no credentials/IAM/network; no
product command/write; no deployment/production/release/Pages; no protected ref;
no broad staging; no `docs/branding/` or unrelated untracked file.

## Handoff

Stage only the six owned paths explicitly, commit them on the worker branch with
message `test: rehearse delete-confirm kernel contract`, and finish with:

```text
DECISION: pass|revision_required
COMMIT: <full sha or none>
TESTS: <exact summary>
FILES: <exact owned paths changed>
ISSUES: <none or exact bounded issue>
```
