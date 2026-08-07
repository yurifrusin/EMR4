# R6 coordinator and recovery-anchor implementation worker packet

## Assignment

Implement only R6A and R6B as frozen in
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-third-exact-veto-recovery.md`.

- Worktree: `C:/Users/sarashera/emr4`
- Branch: `codex/ariadne-bernie-davida-parallel-seam`
- Source HEAD: `2b3798f8`
- Role: bounded implementation worker; no acceptance or integration authority

## Owned files

1. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
2. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_third_veto_entry_anchor.py`
3. `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r6-entry-worker.md`

Do not modify any other file. Do not stage, commit or push.

## R6A construction contract

- Keep only binding, barrier, generation, checkpoint and exact retained
  admission/receipt evidence before route selection.
- Move source-position and dependent anchor/frame/watermark/obligation reads
  into only the active or conflict/rebase branches that require them.
- Exact `RECEIPT_REPLAYED` and `TERMINAL_REPLAYED` paths must not contain or
  inherit a source-outbox read or unrelated branch-dependent reads.
- Add candidate-independent path-walking tests which prove the replay effect
  sets and fail after hostile read hoisting or unconditional selection.

## R6B construction contract

- Reject requested revision zero with `F_ANCHOR`; registration owns and proves
  that baseline.
- At the requested current revision, independently select exactly one lifecycle
  row and the exact branch evidence frozen in R6B.
- DECISION rebase: exact audit, zero receipt, recompute and compare
  `checkpoint_rebase_digest_v1` plus checkpoint/lifecycle/audit state.
- DECISION receipt: exact audit, receipt, one matching PRIMARY and zero
  CONFLICT, rederive `classified_receipt_digest_v1`, recompute and compare
  `checkpoint_apply_digest_v1`, plus receipt/audit/lifecycle/checkpoint fields.
- KEY_ROTATION: zero audit/receipt, exact lifecycle-named key interval and
  immediately previous anchor, recompute and compare `key_rotation_digest_v1`
  with lifecycle, generation schedule and checkpoint integrity.
- Derive the recovery-anchor digest only after applicable proof. Exact replay
  compares every anchor field; no partial repair or checkpoint advance.
- Add focused hostile tests for omitted/substituted evidence, wrong
  cardinality/branch/digest, revision zero, and replay field substitution.

Use only existing typed DSL primitives and types unless a missing primitive is
strictly necessary. If it is, stop with `revision_required` and describe the
minimal shared change; do not edit the builder or validator.

## Forbidden surfaces

No builder, validator, schema source, generated artifacts, existing tests,
plan/design/threat/AER, app/API/Diary/migration files, SQL/DDL, database,
source/feed/watcher/listener, provider/network/browser, patient/product data,
runtime, credential, command/write, deployment, production, release, Pages,
protected refs, branding or unrelated untracked files.

## Verification and result

Do not run repository pytest or generation while parallel lanes are active.
Run Ruff only on the two owned Python paths. Inspect only the owned diff and
write the result file last with exact source HEAD, changed paths, R6A/R6B
summary, Ruff result, unresolved integration needs, forbidden-surface
confirmation and exact terminal `RESULT: candidate_ready` or
`RESULT: revision_required`.
