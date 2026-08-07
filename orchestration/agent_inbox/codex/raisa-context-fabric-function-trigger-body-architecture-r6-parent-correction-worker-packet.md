# R6 parent-constraint and audit-chain correction worker packet

## Assignment

Correct only the rejected R6 entry-program worktree candidate under the
corrected R6B in
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-third-exact-veto-recovery.md`.

- Worktree: `C:/Users/sarashera/emr4`
- Branch: `codex/ariadne-bernie-davida-parallel-seam`
- Recovery-control source HEAD: `2b3798f8`
- Rejected uncommitted contract:
  `sha256:49db11e74a46d1056e694614a970037cf021e174d71114f5262e950b9075b01f`
- Role: bounded correction worker; no acceptance or integration authority

## Owned files

1. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
2. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py`
3. `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r6-parent-correction-worker.md`

Do not modify the earlier worker result. Do not modify any other file. Do not
stage, commit or push.

## Exact correction

1. In `rotate_observation_key_v1`, write lifecycle `source_position` as typed
   NULL exactly as required by the immutable parent branch constraint. Preserve
   the existing checkpoint position unchanged.
2. In the anchor KEY_ROTATION proof, require lifecycle `source_position IS
   NULL`, require both key-interval bounds present and ordered, and prove
   checkpoint position/observation equality only against the immediately
   preceding anchor.
3. Independently close audit-head continuity without adding a new DSL
   primitive:
   - load the exact revision-zero baseline anchor;
   - for DECISION, use the current audit `prior_audit_digest` to select zero or
     one matching earlier audit head; if zero, prove there are no earlier audits
     and it equals the baseline anchor digest; if one, load it exactly and prove
     there is no later audit revision before the requested revision;
   - for KEY_ROTATION, apply the same proof using the unchanged checkpoint
     `audit_head_digest` as the expected latest earlier audit head;
   - any duplicate match, rollback to a non-latest head, missing baseline or
     unexpected audit fails `F_ANCHOR`.
4. For DECISION prove lifecycle source position present and positive and key
   bounds absent. For every nonzero kind prove checkpoint `updated_at` equals
   lifecycle `created_at`.
5. Keep R6A branch-local replay, complete replay-field comparison, schema lane
   work and every prior recovery requirement unchanged.

Focused tests must directly compare the rotation producer with the immutable
parent branch constraint and challenge NULL substitution, latest-audit rollback
across rotation, missing/duplicate prior audit, missing baseline and checkpoint
timestamp mismatch. Keep hostile validation bounded: avoid repeatedly rebuilding
or semantically validating the entire candidate when direct candidate-independent
AST assertions establish the same property.

## Forbidden surfaces

No builder, validator, schema source, generated artifacts, other tests,
plan/design/threat/AER, app/API/Diary/migration files, SQL/DDL, database,
source/feed/watcher/listener, provider/network/browser, patient/product data,
runtime, credential, command/write, deployment, production, release, Pages,
protected refs, branding or unrelated untracked files.

## Verification and result

Do not run pytest or generation. Run Ruff only on the two owned Python paths.
Inspect only the owned diff and write the correction result last with exact
recovery-control HEAD, changed paths, parent/audit corrections, Ruff result,
unresolved integration needs, forbidden-surface confirmation and exact terminal
`RESULT: candidate_ready` or `RESULT: revision_required`.
