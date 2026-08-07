# R5 state/registration/retention implementation worker packet

## Assignment

Implement only the R5A, R5B and R5C body-program changes frozen in
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-second-exact-veto-recovery.md`.

- Worktree: `C:/Users/sarashera/emr4`
- Branch: `codex/ariadne-bernie-davida-parallel-seam`
- Source HEAD: `22e4ce818442fa9ea1aa8d5bd169c3b33166334f`
- Role: bounded implementation worker; no acceptance or integration authority

## Owned files

1. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_builder.py`
2. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
3. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_state_retention.py`
4. `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r5-state-retention-worker.md`

Do not modify any other file. Do not stage, commit or push.

## Exact construction contract

### R5A

- Route to receipt replay only for exactly one receipt, exactly one PRIMARY and
  zero CONFLICT entries. A retained conflict routes to the existing atomic
  rebase path even when a receipt exists.
- Reconstruct `classified_receipt_digest_v1` from exact locator values, stored
  source position, retained PRIMARY `admission_digest` and stored lifecycle
  revision and compare it with stored `receipt_digest` in addition to the
  existing field comparisons.
- Add focused hostile assertions proving conflict-blind routing and removal or
  substitution of digest derivation/compare are structurally visible.

### R5B

- After the barrier lock, select the exact head coordinate. Zero rows must
  create/reload one stream-epoch position-zero head with an operand-derived
  insert effect; one row must lock and use the existing head; ambiguity fails.
  Both branches converge with definitely assigned typed `head`.
- Exact registration replay must independently reload and compare generation,
  checkpoint, exactly two CURRENT frame types, exactly two watermarks, the
  requested initial key interval, lifecycle-revision-zero baseline anchor and
  controlling head. Compare every field named in R5B; never repair a partial
  baseline and never compare generated UUIDs to caller data that does not
  exist.
- Add focused hostile tests for missing head insert and omission/substitution of
  each complete-baseline proof family.

### R5C and shared builder DSL

Add exactly two expression constructors, using exactly these shapes:

```json
{
  "op": "SET_CONTAINS_KEY",
  "set": {"kind": "LOCAL", "symbol": "generation_set", "type": "<relation>[]"},
  "source_relation": "<qualified relation>",
  "key_pairs": [
    {"source_column": "<column>", "set_column": "<column>"}
  ],
  "type": "pg_catalog.boolean"
}
```

```json
{
  "op": "SET_COVERS_KEYS",
  "required": {"kind": "LOCAL", "symbol": "generation_set", "type": "<relation>[]"},
  "evidence": {"kind": "LOCAL", "symbol": "overlapping_key_set", "type": "<relation>[]"},
  "key_pairs": [
    {"required_column": "<column>", "evidence_column": "<column>"}
  ],
  "type": "pg_catalog.boolean"
}
```

- `SET_CONTAINS_KEY` filters checkpoint, anchor and key aggregate reads to exact
  `COORDS` membership in all-except-CONSUMED `generation_set`; pins use every
  parent pin generation-identity column. Apply exact membership to other
  generation-keyed grace sets where their catalogue permits.
- Keep `MIN_FIELD` over the identity-joined checkpoint set.
- Replace total overlapping-key row count equality with `SET_COVERS_KEYS` over
  exact ordered `COORDS`; duplicates for one generation must not mask another.
  The same expression governs REC19 reason and eligibility, including purge.
- The focused test must demonstrate the emitted operands/keys and absence of
  the old count-equality authority. Do not modify validator or schema; those
  are separate lanes.

## Forbidden surfaces

No generated contract/schema, validator, schema builder, existing tests, plan,
design, threat model, AER, app/API/Diary/migration files, SQL/DDL, database,
source/feed/watcher/listener, provider/network/browser, patient/product data,
runtime, credential, command/write, deployment, production, release, Pages,
protected refs, branding or unrelated untracked files.

## Verification and result

Do not run repository pytest while parallel lanes are active. Run Ruff only on
your owned Python paths. Inspect the owned diff and write the durable worker
result file last with: exact source HEAD; paths changed; R5A/R5B/R5C summary;
Ruff result; unresolved integration needs; forbidden-surface confirmation; and
exact terminal `RESULT: candidate_ready` or `RESULT: revision_required`.
