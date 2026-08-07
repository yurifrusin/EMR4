# Normative validator and schema closure recovery worker packet

Source HEAD: `7ad40bd337ac6433bd6cc84653dd5883679ed13b`

Worktree: `C:\Users\sarashera\emr4`

Branch: `codex/ariadne-bernie-davida-parallel-seam`

## Read first

Read `AGENTS.md` sections 3-7, the active function/trigger-body plan, its four
normative recoveries, the exact veto, immutable parent, current generated child,
builder, validator, schema generator and architecture tests before editing.

## Owned files

- `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_validator.py`
- `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_schema.py`
- `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_normative_closure.py`
- `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-normative-closure-recovery-worker.md`

Do not edit any other path. Other workers share this worktree; preserve their
changes and do not stage or commit.

## Task

Implement R4 independently of whole-baseline equality.

- Semantic validation must bind the immutable parent digest and exact effective
  parent, all ordered twenty-six recovery operations and scalar values, exact
  type enum vocabularies, all twenty-two full signatures, thirteen trigger
  declarations, exact effective-role privileges, public-execute denial and
  body-summary/graph derivation.
- Every enum-typed `CONST` must be a member of its effective type catalogue.
- The schema must freeze critical normative scalar envelopes with ordered
  `const`/`prefixItems`: recovery operations, effective-parent summary,
  signatures, declarations, privileges, enums, renderer/artifact boundaries
  and body identity/order. Do not make entire body AST objects `const`.
- Add resealed/regenerated-schema attacks for owner outbox DELETE, REC19
  widening/invalid constant, producer owner swap and central event-proof
  removal. Each attack must be rejected by an independent semantic or critical
  scalar check before any baseline byte-equality helper could decide it.

The tests may import existing deterministic builder helpers but this lane may
not change the builder or generated contract/schema.

## Forbidden surfaces and checks

No SQL/DDL, database/source/provider/data, app/API/Diary/runtime, command,
deployment, Pages, protected refs, `docs/branding/**`, staging or commit. Run
only `py_compile`, focused Ruff and `git diff --check` on owned paths. Do not run
pytest during parallel work; Sol will run it serially.

## Durable result

Write the owned worker artifact naming exact changes, static checks and any
remaining issue. End with exactly one line:

`RESULT: candidate_ready`

or

`RESULT: blocked — <specific reason>`
