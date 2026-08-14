# Independent veto packet — Reception One same-update-family multi-change kernel rehearsal

Date: 2026-08-15

Timestamp: 2026-08-15T00:26:47+10:00 (Australia/Brisbane)

Decision required: exactly one terminal `pass` or `revision_required`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\same-update-multi-change-review-0acc745a`
- Branch: `codex/review-reception-one-same-update-multi-change-0acc745a`
- Task baseline: `704f2827c7b914792c43c12f026149ce25f70882`
- Exact candidate: `3dd5f3b39ed98a2d562685d1d1567a359930c693`
- Protected local/remote `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Review only. The pre-dispatch receipt, exact worktree
preflight and this packet bind the candidate above.

## Purpose

Independently decide whether the existing appointment update proposal/confirm
kernel is adequately and accurately rehearsed for one authored-synthetic
request that changes practitioner, local time and duration together.

The required meaning is one provisional proposal and one explicitly confirmed
transaction—not three sequential field writes. Confirmation must recheck
current appointment truth, target availability and practitioner state, then
produce one correlated appointment update, audit and idempotency result. Exact
same-key replay must be mutation-free; different-body reuse must conflict; a
failure after update/audit flush but before commit must roll back every effect
before a clean same-key retry.

This tranche adds only tests and orchestration evidence. It adds no compound
editor, UI, product source, route, API schema, command family, migration,
provider or external patient/channel runtime.

## Closed command scope

Only literal named paths below may be opened. Do not use `rg`, `grep`, `find`,
`Get-ChildItem`, `git grep`, `git ls-files`, globbing, recursive traversal,
directory-root inputs or repository-wide content/path search. Do not inspect
any adjacent path. The exact baseline-to-candidate name-only and whitespace
commands below are the only diff enumeration allowed.

## Exact allowed review surface

- `AGENTS.md`
- `docs/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-plan.md`
- `docs/security/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-threat-model-delta.md`
- `tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py`
- `tests/test_appointment_update_proposal.py`
- `tests/test_api_spine_update_confirm_idempotency_route_contract.py`
- `tests/test_api_spine_artifacts.py`
- `app/schemas/appointments.py`
- `app/routers/appointments.py`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `orchestration/api_spine_adr.md`
- `orchestration/bernie_interaction_model.md`
- `orchestration/continuity/ariadne-active-operation-latch/current.json`
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`
- `orchestration/continuity/ariadne-agent-error-register/pattern-report.json`
- `tests/test_ariadne_agent_error_register.py`
- `tests/test_ariadne_active_operation_latch.py`
- `tests/test_ariadne_orchestrator_preflight.py`
- `docs/ariadne-agent-error-correction-register-revision-270.md`
- `docs/ariadne-agent-error-correction-register-revision-271.md`
- `docs/ariadne-agent-error-correction-register-revision-272.md`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-deepseek-egress-incident.json`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-integration-source-binding-incident.json`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-antigravity-help-incident.json`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-deepseek-packet.md`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-deepseek-result.json`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-deepseek-worktree-preflight.json`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-integrated-candidate-precommit-receipt.json`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-postcompaction-receipt.json`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-preintegration-receipt.json`
- `orchestration/agent_inbox/codex/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-preverifier-harness-recovery-precommit-receipt.json`

The three incident records are sanitized workflow-control evidence. Do not seek
or reconstruct any worker-internal content beyond the allowlisted result file.

## Required challenges

1. Verify exact HEAD, branch, clean checkout, protected refs and exact
   baseline-to-candidate changed paths before and after review.
2. Confirm the candidate changes no `app/**`, Diary UI, OpenAPI, GraphQL,
   migration or database-schema source.
3. Confirm `M1` proves one combined proposal containing practitioner, local
   date/time and duration while appointment, audit and idempotency counts do
   not change.
4. Confirm `M2` proves all three values commit together with exactly one update
   audit and one completed idempotency row correlated to the command outcome.
5. Confirm `M3` changes authoritative subject truth after proposal and the
   signed freshness check blocks the candidate without retained effects.
6. Confirm `M4` creates a new target-practitioner interval conflict after
   proposal and confirm-time re-proposal blocks without subject mutation.
7. Confirm `M5` deactivates the target practitioner after proposal and
   confirmation returns the exact inactive denial without candidate effects.
8. Confirm `M6` replays from a fresh database session, returns the exact stored
   response without revalidation or mutation, and rejects different-body key
   reuse as a typed conflict.
9. Confirm `M7` injects failure at `complete_appointment_command` after the
   update and audit have flushed but before commit, closes the failed session,
   proves transaction-wide rollback through fresh observation, then commits
   exactly once on clean same-key retry and replays mutation-free.
10. Confirm fixtures are committed before separately owned confirmation
    sessions where rollback semantics depend on transaction ownership.
11. Confirm practice/actor scope, signed evidence, exact command equality,
    target conflict checks, audit correlation and idempotency semantics use the
    ordinary existing kernel rather than a test-only bypass.
12. Confirm status is absent and no cross-family, implicit confirmation,
    automatic execution or delegated-channel authority is claimed.
13. Confirm the evidence label is limited to provider-free authored-synthetic
    local backend/PostgreSQL behavior, not browser, patient, provider,
    deployment or production evidence.
14. Confirm AER-0309 through AER-0311 are contained and do not supply
    self-acceptance; independently reconcile every claim from source and exact
    commands.
15. Run every exact command below in order and leave HEAD and worktree
    unchanged and clean.

## Exact commands

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-same-update-3dd5-core tests\test_appointment_update_proposal.py tests\test_api_spine_update_confirm_idempotency_route_contract.py tests\test_api_spine_artifacts.py tests\test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-same-update-3dd5-continuity tests\test_ariadne_active_operation_latch.py tests\test_ariadne_orchestrator_preflight.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-same-update-3dd5-register tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check tests\test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check tests\test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --name-only 704f2827c7b914792c43c12f026149ce25f70882..3dd5f3b39ed98a2d562685d1d1567a359930c693
git diff --check 704f2827c7b914792c43c12f026149ce25f70882..3dd5f3b39ed98a2d562685d1d1567a359930c693
git status --short --branch --untracked-files=no
git rev-parse HEAD
```

Expected pytest results are exactly 109 passed, 69 passed and 234 passed,
totalling 412 across the seven named modules. Ruff lint and format checks plus
Git whitespace must pass. The changed-path list must contain exactly the 32
bounded plan, test and orchestration paths frozen by the packet and no product
source.

## Forbidden actions

Do not edit, format, commit, push, install dependencies, create or delete files
inside the candidate worktree, contact a product/provider/network surface,
access patient, clinical, product-derived, historical Diary or protected data,
inspect `docs/branding/`, use a command not explicitly listed above, move refs
or accept your own output.

## Decision rule

Return `revision_required` for any P0-P2 finding, scenario/evidence gap,
incorrect rollback or replay proof, test-only authority bypass, product-source
change, overclaim, failed exact command or dirty postcondition. Otherwise
return exactly one `pass`, with findings, exact counts, candidate HEAD and
post-review cleanliness.
