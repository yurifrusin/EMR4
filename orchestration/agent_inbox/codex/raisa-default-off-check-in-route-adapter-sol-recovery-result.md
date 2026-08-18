# Sol recovery result — default-off canonical check-in route-adapter convergence

Date: 2026-08-18

Status: deterministic candidate ready for exact-source admission

## Provenance

The DeepSeek V4 Flash/high worker returned no receipt, source or commit. Its
isolated worktree remained clean at frozen source
`4daa2d772ffcf64e55f69917d2fb21802e959673`; no late worker adoption is
permitted. GPT Sol authored this candidate under the explicit recovery lease.

## Candidate

- the unchanged default-off A5.1 confirmation route calls
  `compose_product_check_in` exactly once after the existing feature/allowlist
  gate and idempotency-key normalisation;
- one route-owned `CheckInDependencies` binder delegates the accepted adapter
  to the existing claim, lock, reauthorization, evidence, effect, audit, event,
  completion, commit, rollback and committed-readback primitives;
- the response mapper preserves existing 200 blocked/success/replay shapes,
  404 missing-appointment behavior, exact 409/503 idempotency details and the
  existing 500 posture for internal transaction failures;
- the adapter now preserves the mounted route's legacy ordering: same-key
  replay/conflict is classified before semantic envelope validation, and the
  body evidence token takes precedence over the proposal copy before exact
  server-side verification;
- no flag, allowlist, schema, OpenAPI, proposal route, generic status route,
  action grammar, first-party client or waiting-area command changed.

## Deterministic evidence before commit

- Python compilation: passed for both changed source files and both focused
  test files;
- Ruff: passed for both changed source files and both focused test files;
- self-contained adapter plus route-convergence suites: 103 passed;
- database-backed A5.1 runtime suite excluding one unrelated pre-existing stale
  Alembic-head assertion: 35 passed;
- the three first-run evidence-code mismatches were corrected by the frozen
  body-token-precedence amendment and passed on rerun;
- `test_migration_keeps_one_alembic_head` remains a baseline failure because it
  expects obsolete head `v1w2x3y4z5b6` while accepted repository history is at
  `x3y4z5a6b7c8`. No migration or baseline-test change is included in this
  tranche.

Gemini 3.7 Flash/high remains mandatory against one clean exact candidate.
