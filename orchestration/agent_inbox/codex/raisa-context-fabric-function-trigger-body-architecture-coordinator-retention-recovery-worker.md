# Coordinator and retention exact-veto recovery worker result

Date: 2026-08-07

Source HEAD: `7ad40bd337ac6433bd6cc84653dd5883679ed13b`

Worktree: `C:\Users\sarashera\emr4`

Branch: `codex/ariadne-bernie-davida-parallel-seam`

## Owned changes

- Replaced the collapsed coordinator fallback with explicit typed receipt
  replay, stored terminal replay, ambiguous/retained-conflict/missing admission,
  source-cardinality, stream-epoch, gap, predecessor, key-membership,
  anchor-integrity and dependent-state branches.
- Added operand-derived coordinator effects for the PRIMARY apply path:
  minimized decision lifecycle and audit rows, immutable receipt insertion,
  checkpoint/generation state, ordered frame and watermark locks, one-way frame
  retirement, watermark advancement, and insert-or-coalesce reassembly
  obligations. Rebase branches now store exact closed observation reason,
  lifecycle/audit/generation/checkpoint state and return the ordered
  `durability_transition_result_v1` composite without fabricating a PRIMARY.
- Corrected entry-program enum operands exposed by exact closure in this owned
  module, including observation-digest reuse, ACTIVE checkpoint state and the
  two exact frame-type values; removed the non-catalogued registration
  lifecycle value.
- Changed retention generation selection to exact `lifecycle_state !=
  CONSUMED`, preserving ACTIVE, REBASE_REQUIRED and REVOKED.
- Scoped checkpoint, anchor, active-pin, key, source, receipt and audit reads to
  the same practice/source/stream and added a complete-generation `FOR_EACH`
  proof binding checkpoint, current anchor, overlapping keys and active pins to
  each census generation identity.
- Kept the slowest checkpoint as `MIN_FIELD` over the complete checkpoint set.
  Added operand-derived source, receipt/checkpoint, audit and key-overlap grace
  comparisons against `transaction_timestamp()`, plus interval-start/end
  overlap predicates at the derived through-position.
- Replaced the three out-of-contract retention constants and closed every
  retention result to exactly REC19: `ELIGIBLE`, `EXECUTION_DISABLED`,
  `CHECKPOINT_LAG`, `ACTIVE_PIN`, `KEY_OVERLAP`, `GRACE_PENDING`,
  `AMBIGUOUS_CENSUS` and `NO_NON_CONSUMED_GENERATION`.
- Added focused source-level assertions independent of the generated whole
  contract. Hostile copies demonstrate rejection of an ACTIVE-only census, an
  out-of-REC19 reason, an unscoped checkpoint set, omitted grace/key proof and
  omitted coordinator state/effect nodes.

## Static checks

- `python -m py_compile` on both owned Python paths: pass.
- focused Ruff on both owned Python paths: pass.
- `git diff --check` on all three owned paths: pass.
- Pytest was not run, as required while parallel lanes are active. Sol retains
  the serial complete-suite and generated-contract reconciliation gate.

## Boundary and remaining gate

No SQL/DDL was rendered or executed. No contract was regenerated. No database,
source/feed/watcher/listener, network, provider, product/patient/protected data,
runtime, command, deployment, release, Pages or protected-ref surface was
opened. No file outside the three owned paths was edited, staged or committed;
unrelated worktree changes and `docs/branding/` remain preserved.

No lane-local implementation issue remains. The source is an unaccepted
candidate until Sol reconciles the parallel lanes, regenerates the contract
and schema, runs the complete serial deterministic suite and obtains the
required fresh exact-HEAD independent veto.

RESULT: candidate_ready
