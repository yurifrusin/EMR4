# Normative validator and schema closure recovery worker result

Date: 2026-08-07

Source HEAD: `7ad40bd337ac6433bd6cc84653dd5883679ed13b`

## Exact changes

- The semantic validator now independently binds the exact immutable-parent
  path/digest/authority rule; the ordered REC01-REC26 recovery envelope and
  every scalar within it; the complete effective-parent signatures,
  declarations and role matrix; the qualified catalogue; typed-IR vocabulary;
  trigger return matrix; renderer order; and unmounted artifact boundary.
- Targeted privilege checks separately reject direct outbox `DELETE`, product
  DML, runtime product reads, runtime trigger execution and any missing
  `PUBLIC`-execute denial across the support plus twenty-two body signatures.
- Every enum-typed `CONST` and `ARRAY_CONST` is checked against the exact
  effective enum catalogue, including exact REC19 retention reasons.
- The producer's central event-membership assertion is independently bound by
  its exact typed-node digest, so removing or substituting it cannot pass by
  resealing the contract and recomputing derived summaries.
- The schema generator now refuses a drifted R4 normative envelope before
  emission, freezes critical scalar meaning recursively with scalar `const`
  and ordered `prefixItems`, and keeps body ASTs structurally typed rather than
  whole-object constants.
- Enum constant schema branches bind each enum type to its exact values while
  keeping non-enum constants structurally typed.
- The focused hostile packet covers resealed owner outbox-delete widening,
  REC19 widening, invalid retention-reason constants, producer-owner swap and
  central event-proof removal without using whole-baseline equality as the
  deciding control.

## Static checks

- `py_compile` passed for the validator, schema generator and focused hostile
  test.
- Focused Ruff passed for the same three Python paths.
- `git diff --check` passed for all four owned paths.
- Pytest was not run, exactly as required while parallel work remains active;
  Sol retains serial pytest ownership.

## Remaining issue

No static issue remains in this lane. Aggregate generated-artifact rebuilding,
serial pytest and cross-lane acceptance remain Sol-owned.

RESULT: candidate_ready
