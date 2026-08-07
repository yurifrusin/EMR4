# R6 final exact-HEAD independent veto packet

Date: 2026-08-08

Candidate HEAD: `0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d`

Candidate contract:
`sha256:c8d27c85def134056598be7ef12cda3ae7b509b3d06b16a536459baea51bc24b`

Review worktree: `C:/Users/sarashera/EMR4-worktrees/r34`

Review branch:
`codex/review-durability-function-trigger-body-r6-0bfd3e75`

## Authority and exclusions

This is a provider-free, read-only, exact-HEAD architectural veto. Do not edit,
stage, commit, push, fetch, merge, create or move refs, install anything, open a
browser/network/provider/model/database/source/feed/watcher/listener, render or
execute SQL/DDL, create a migration/object, touch runtime/credentials, or access
patient, product or protected data. Do not read the main dirty worktree or any
untracked file there. Use only the clean review worktree and the allowlisted
commands below. Tests may use the repository's local serial-test lock but must
not contact PostgreSQL or any external system.

## Required review

Read `AGENTS.md` completely, then the plan, design, threat delta and all three
exact-veto recovery documents. Inspect the exact diff from
`5a3c5b5118f80153d545bf30ae9db99acb187cd7` to the candidate, the builder,
entry/trigger programs, validator, schema, generated contract/schema and all
body-architecture tests.

Challenge rather than restate these claims:

1. R6A: every receipt-replay and terminal-replay path is source-independent and
   cannot read anchor, frame, watermark or obligation evidence; conflict and
   active paths read only their branch-local relations.
2. R6B: every non-zero recovery anchor is derived from the exact lifecycle
   branch and complete committed evidence. DECISION and KEY_ROTATION shapes,
   immediate predecessor anchor, latest prior audit across intervening
   rotations, timestamp equality, strict key interval, digest provenance and
   exact replay must all fail closed under omission or substitution.
3. R6C: both set-key-pair structural branches require unique items and a
   duplicate otherwise-valid pair is rejected after contract digest resealing.
4. R6D: every terminal coordinator path has one unique, contiguous, increasing
   lock sequence. Primary/conflict paths lock one current anchor at ordinal 4
   before admission at 5 and reuse it; admission-missing rebase takes one local
   anchor; replay-only paths remain anchor-free.
5. The correction preserves the immutable parent, exact API Spine classification
   and all forbidden provider/data/runtime/database/DDL/command/deployment and
   protected-ref boundaries.

Try at least one candidate-independent counterexample for each claim, including
control-flow path traversal rather than relying on aggregate effect summaries.
Passing tests are necessary but do not override a reproduced semantic gap.

## Allowlisted commands

Run from the review worktree only:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:RUFF_NO_CACHE='true'
git rev-parse HEAD
git status --short
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder --check
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_normative_closure.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_state_retention.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_schema.py tests/test_api_spine_artifacts.py tests/test_ariadne_agent_error_register.py tests/test_ariadne_autonomous_continuation.py tests/test_model_required_bureau_standing_continuation.py
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m ruff check scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_normative_closure.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_state_retention.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_schema.py tests/test_api_spine_artifacts.py tests/test_ariadne_agent_error_register.py
git diff --check 5a3c5b5118f80153d545bf30ae9db99acb187cd7 0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d -- docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-design.md docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-plan.md docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-third-exact-veto-recovery.md docs/security/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-threat-model-delta.md scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema.py orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.json orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.schema.json tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_schema.py
git status --short
git rev-parse HEAD
```

You may use read-only `rg`, `git show`, `git diff`, `Get-Content` and short
in-memory Python expressions inside the review worktree for the required
counterexamples. Do not create files or caches.

## Terminal response

Return exactly one terminal line after all work is complete:

`RESULT: pass`

or

`RESULT: revision_required`

Before that line, report exact HEAD/status postflight, test count, builder hash,
Ruff result, counterexamples attempted and every finding by severity with exact
file/line or contract path. Do not self-repair.
