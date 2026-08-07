# R7 final exact-HEAD independent veto packet

Date: 2026-08-08

Candidate HEAD: `a93d07405ad35d7d6c0603065625c17ec14ab23e`

Candidate contract:
`sha256:f71287f266a3252d2a0736e511287600939a40bc70397710600c12581e24d4f3`

Review worktree: `C:/Users/sarashera/EMR4-worktrees/r35`

Review branch:
`codex/review-durability-function-trigger-body-r7-a93d0740`

Model allocation: fresh Antigravity project, exact
`gemini-3.6-flash-high`, explicit high reasoning.

## Authority and exclusions

This is a repository-code-only, read-only, exact-HEAD architectural veto. Do
not edit, stage, commit, push, fetch, merge, create or move refs, install
anything, open a browser/database/source/feed/watcher/listener/product runtime,
render or execute SQL/DDL, create a migration/object, touch credentials, or
access patient, product, protected or historical-PHI data. Use only the clean
review worktree and the allowlisted commands below. Do not read the main dirty
worktree or any prior independent-review conclusion artifact. Tests may use the
repository's local serial-test lock but must not contact PostgreSQL or any
external product system.

GPT Sol retains acceptance, recovery, integration and Git authority. Return
one veto decision only and do not self-repair.

## Required reading

Read completely from the review worktree:

- `AGENTS.md`;
- `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-plan.md`;
- `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-design.md`;
- `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-fourth-exact-veto-recovery.md`;
- `docs/security/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-threat-model-delta.md`;
- the accepted parent contract only where needed for
  `anchor_fences_next_transition_v1` and the recovery-anchor/generation/
  checkpoint shapes;
- the entry-program builder, validator, generated child contract/schema and
  the fourth-veto test module; and
- the exact Git diff `0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d..a93d07405ad35d7d6c0603065625c17ec14ab23e`.

Do not use the earlier R6 reviewer conclusion as evidence.

## Required challenge

Challenge rather than restate these claims:

1. The new-effect branch of `rotate_observation_key_v1` locks exactly one
   current anchor, immediately asserts exactly four checkpoint-state
   equalities and seven controlling-generation-digest equalities with
   `F_ANCHOR`, then and only then locks the prior key or uses the anchor digest
   in any effect.
2. Locator equality, row locking and `anchor_digest` presence cannot substitute
   for the eleven field-level comparisons. Independently mutate or remove each
   class of comparison, alter row symbol/relation/operator/failure family and
   move digest use/effect before the fence; each must be rejected even after
   candidate evidence is resealed.
3. Identical-key replay is detected before the new-effect branch and remains
   inert: no anchor/prior-key lock, lifecycle/key/generation/checkpoint effect,
   or new anchor-fence dependency occurs on replay.
4. The R7 delta does not regress the previously reviewed R6A branch-local
   source-independent replay, R6B complete anchor append, R6C duplicate-free
   set pairs or R6D unique contiguous coordinator lock order. Verify this from
   the exact diff and at least one independent structural/path check; do not
   rely only on stored summaries.
5. Parent, API Spine, application, migration, Diary, provider/data/runtime,
   SQL/DDL/command/deployment and protected-ref boundaries remain unchanged.

Passing tests are necessary but do not override a reproduced semantic gap.
Report all P0-P3 findings with exact file/line or contract path.

## Allowlisted commands

Run from the review worktree only:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:RUFF_NO_CACHE='true'
git rev-parse HEAD
git status --short
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m scripts.raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder --check
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_normative_closure.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_state_retention.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_fourth_veto_rotation_anchor.py tests/test_api_spine_artifacts.py tests/test_ariadne_agent_error_register.py tests/test_ariadne_autonomous_continuation.py tests/test_model_required_bureau_standing_continuation.py
C:/Users/sarashera/emr4/.venv/Scripts/python.exe -m ruff check scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_plan.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_normative_closure.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_state_retention.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_validator.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_schema.py tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_fourth_veto_rotation_anchor.py tests/test_api_spine_artifacts.py tests/test_ariadne_agent_error_register.py
git diff --check 0bfd3e7545dfa1a7431f856b5eaf2aac32a9292d a93d07405ad35d7d6c0603065625c17ec14ab23e
git status --short
git rev-parse HEAD
```

You may use read-only `rg`, `git show`, `git diff`, `Get-Content` and short
in-memory Python expressions inside the review worktree for the required
counterexamples. Do not create files or caches.

## Terminal response

Return exactly one structured terminal decision supported by the report:

- `pass`; or
- `revision_required`.

Before the decision, report exact HEAD/status postflight, test count, builder
hash, Ruff result, counterexamples attempted and every finding by severity.
