# R5 semantic-validator implementation worker packet

## Assignment

Implement only semantic validation for the two R5C set primitives and R5D
field-independent exact signature/trigger-declaration closure.

- Worktree: `C:/Users/sarashera/emr4`
- Branch: `codex/ariadne-bernie-davida-parallel-seam`
- Source HEAD: `22e4ce818442fa9ea1aa8d5bd169c3b33166334f`
- Role: bounded implementation worker; no acceptance or integration authority

## Owned files

1. `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py`
2. `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_second_veto_validator.py`
3. `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-r5-validator-worker.md`

Do not modify any other file. Do not stage, commit or push.

## Exact semantic contract

### Set expressions

Admit exactly `SET_CONTAINS_KEY` and `SET_COVERS_KEYS` with the object shapes
frozen in the second recovery and state/retention packet.

- Both output exactly `pg_catalog.boolean`.
- Every set operand must be a declared definitely assigned LOCAL whose type is
  exactly `<qualified-relation>[]`.
- `SET_CONTAINS_KEY.source_relation` must equal the current typed selection
  source where the expression is used.
- Key-pair arrays are ordered, non-empty and duplicate-free. Every named column
  must exist in its exact relation and paired column types must match.
- `SET_CONTAINS_KEY` must expose its source-row key columns in derived reads.
  Set-member columns remain bound to the previously selected complete set.
- Unknown keys, relation substitution, partial generation identity, scalar
  locals, mismatched types, empty pairs and generic/arbitrary expressions fail.

### Exact independent R5D maps

Add static candidate-independent exact field maps for the support signature,
nine entry-point signatures, thirteen trigger signatures and thirteen trigger
declarations. The maps may be transcribed from the frozen effective parent at
source HEAD but must be literal validator authority and must never be read from
the candidate during validation.

For every signature independently compare exact position/id, ordered inputs,
output type/cardinality, language, owner, executor, strictness, volatility,
parallel safety, security-definer, fixed search path, PUBLIC execute denial and
invariant IDs. For every trigger declaration compare exact position/function,
relation, timing, row level, ordered events, deferrability and
initially-deferred value. Emit field-specific issue codes; canonical
`normative_section_mismatch` may coexist but cannot be the sole finding.

Focused resealed hostile tests must mutate at least producer owner,
security-definer, volatility, one trigger timing and one deferrability value and
prove each receives a non-`normative_section_mismatch` semantic issue. Also test
both set operators' invalid shapes and type/key/relation substitutions.

## Forbidden surfaces

No body programs, builder DSL, structural schema, generated artifacts, existing
tests, plan/design/threat/AER, app/API/Diary/migration files, SQL/DDL, database,
source/provider/network/browser, patient/product data, runtime, credential,
command/write, deployment, production, release, Pages, protected refs,
branding or unrelated untracked files.

## Verification and result

Do not run repository pytest while parallel lanes are active. Run Ruff only on
owned Python paths. Inspect the owned diff and write the durable worker result
last with exact source HEAD, paths changed, semantic controls added, Ruff
result, integration dependencies, forbidden-surface confirmation and exact
terminal `RESULT: candidate_ready` or `RESULT: revision_required`.
