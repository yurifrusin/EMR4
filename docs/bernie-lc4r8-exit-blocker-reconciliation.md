# LC4R8 Exit-Blocker Reconciliation

**Date:** 2026-07-15

**Conductor, sprint planner, architecture/acceptance owner, recovery owner, and
protected integrator:** GPT Sol.

**Worker:** DeepSeek V4 Flash/high through Claude Code `--bare`.

**Revision:** Accepted replacement for rejected candidate `0378b8b5`.

## Summary

LC4R8 reconciles the two exit blockers from the LC4R7 Silver/pending queue:

1. **Clarification decision surface** (53 `requires_adjudication` scenarios):
   Produces a deterministic blocker-class taxonomy showing that every scenario
   has at least one upstream semantic contract defect, so zero records are
   decision-ready for policy adjudication.

2. **Replay/delta contract audit** (51 `non_language_contract_mismatch` scenarios):
   Applies a frozen priority order to classify each mismatch. 11 cases are
   `audit_change_type_vocabulary_only` and authorized for generator-backed
   contract repair; the remaining 40 require further contract reconciliation.

No scenario was silently decided. No protected holdout, provider, route,
database, UI, historical diary, memory/RAG, or write surface was opened.

## Clarification Decision Surface

The 53 `requires_adjudication` scenarios are classified by examining the
semantic fields that fail alongside `requires_clarification`:

| Blocker class | Count | Hash |
|---|---|---|
| `normalization_contract_blocked` | 3 | `db484a50adc0b601` |
| `entity_and_normalization_contract_blocked` | 6 | `ff20612b3c9e276e` |
| `temporal_and_normalization_contract_blocked` | 20 | `910950860133d8b9` |
| `temporal_entity_and_normalization_contract_blocked` | 24 | `7cfaa6e4ddefc172` |
| `isolated_clarification_policy_choice` | 0 | `e3b0c44298fc1c14` |

Every record shows `decision_readiness: blocked_by_upstream_contract_defect`.
No scenario is decision-ready.

Action distribution with frozen selection hashes:

| Action | Count | Hash |
|---|---|---|
| create | 13 | `1839c8c567e44922` |
| move | 13 | `ec7e009f37f0834a` |
| resize | 14 | `e49785ce6f8922e5` |
| cancel | 13 | `830386f883de7fd0` |

## Replay/Delta Contract Audit

Applied frozen priority order:

1. **Negated surface vs create contract** (1): interpreter negates the action
   but contract expects `appointment_created`.
2. **Clarification tool without clarification contract** (11): expected tool
   sequence is only `request_clarification` but no expected clarification.
3. **Audit change-type vocabulary only** (11): all other replay dimensions
   pass; only the audit delta field fails. Authorized for generator-backed
   contract repair.
4. **Creation expectation vs replay policy** (28): contract expects
   `appointment_created`, replay yields no outcome, tool sequences agree.
5. **Genuine replay integration defect** (0): remainder.

## Exit Status

```
blocked_pending_generator_repair_and_contract_reconciliation
```

| Metric | Count |
|---|---|
| Clarification policy decision-ready | 0 |
| Genuine replay integration defects | 0 |
| Generator-backed contract repair authorized | 11 |
| Upstream clarification contract blockers | 53 |
| Remaining replay contract reconciliation blockers | 40 |

## Semantic Baseline, Safety, and Variance

The development corpus
(`sha256:aa2d946b60694eab96846ed77e885273c807e127f8998981a8cf8ff20ebae647`)
preserves the LC4R7 contract baseline over 1,152 scenarios / 2,304 samples:

| Metric | Observed | Expected | Match |
|---|---|---|---|
| Intended action | 880/1152 | 880/1152 | ✓ |
| Action semantics | 814/1152 | 814/1152 | ✓ |
| Temporal relation | 628/1152 | 628/1152 | ✓ |
| Normalized values | 101/1152 | 101/1152 | ✓ |
| Entity semantics | 300/1152 | 300/1152 | ✓ |
| Clarification | 782/1152 | 782/1152 | ✓ |
| Safety (all safe) | 1152/1152 | 1152/1152 | ✓ |
| Variance (deterministic) | 0/2304 | 0/2304 | ✓ |

## Protected Evidence and Authority

No protected holdout v1 evidence was opened, enumerated, imported, loaded,
regenerated, evaluated, hash-checked, inferred from, or tuned against. No
historical diary material was inspected. No provider inference, T3.5 adapter,
route/API, database, UI, deployment, memory, RAG/GraphRAG, confirmation, or
write authority was used.

## Revision Notes

- Initial worker pass (`0378b8b5`) briefly created and then removed the
  temporary root `bernie_lc4r8_output.json`; that commit was rejected.
- This revision adds: `build_from_variants` entry point, action selection
  hashes, semantic baseline/safety/variance sections in the report, observed
  exit counts computed from classified artifacts (not copied from constants),
  strengthened `run_check` with schema validation and record equality checks,
  and comprehensive fail-closed mutation tests (84 total).
- Exit counters 0/0/11/53/40 and all frozen 53/51 class counts and hashes,
  record hashes, and combined hash are retained unchanged.

## Files Changed

- `scripts/bernie_lc4r8_exit_blocker_reconciliation.py` — revised helper
- `tests/test_bernie_lc4r8_exit_blocker_reconciliation.py` — focused tests (84)
- `docs/bernie-lc4r8-clarification-decision-surface.json` — 53 redacted records
- `docs/bernie-lc4r8-replay-contract-audit.json` — 51 redacted records
- `docs/bernie-lc4r8-exit-blocker-report.json` — aggregate report
- `docs/bernie-lc4r8-exit-blocker-reconciliation.md` — this note
- `orchestration/agent_inbox/codex/lc4r8-dw1-completion.md` — provenance
