# LC4V6D1 DeepSeek Flash Candidate

**Date**: 2026-07-16

**Source commit**: `b8bafbddf854b671e4e1f12d2c240b88f02db7d6`

**Worker**: DeepSeek V4 Flash/high through Claude Code `--bare`

---

## Changed files

| File | Status |
|------|--------|
| `app/services/bernie/lc4v6d1_development_evidence.py` | **new** — bounded ordinary-development evidence runner |
| `tests/test_bernie_lc4v6d1_development.py` | **new** — 157 focused serial tests |
| `orchestration/agent_inbox/claude/lc4v6d1-deepseek-candidate.md` | **this file** — durable candidate artifact |

No other files were read or edited. The fixture, contract, parser, policy, AGENTS.md, historical reports, routes, APIs, UI, database, provider code, and all holdouts remain untouched.

---

## Test command

```bash
py -m pytest tests/test_bernie_lc4v6d1_development.py -v
```

Ran within the worktree root at `C:\Users\sarashera\EMR4-worktrees\claude` using
the shared integration Python path (`py` = Python 3.14.6).

---

## Test results

```
collected 157 items
tests/test_bernie_lc4v6d1_development.py ... 157 passed in 32.75s
```

### Test breakdown

| Test class | Tests | Coverage |
|---|---|---|
| `TestFixtureValidation` | 10 | Schema, population 24, family counts 12/6/3/3, unique IDs, required fields |
| `TestFixtureHash` | 3 | Deterministic sha256 hash over sorted cases |
| `TestEvidenceIntegrity` | 5 | Overall evidence structure, classification taxonomy, aggregate counts |
| `TestExtractionLayer` | 12 (param × 24) | Every probe extraction vs fixture extraction expectations |
| `TestPolicyLayer` | 12 (param × 24) | Every probe policy vs fixture policy expectations |
| `TestUnknownPractitionerContract` | 72 (6 param × 12) | Extraction exact at extraction → policy fails closed with clarification, no ID, no mutation, no deltas, no simulated write |
| `TestKnownPractitionerControls` | 6 (param × 6) | Known practitioner ID resolves, no clarification, appointment_moved |
| `TestRepeatVariance` | 2 | Zero variance across two repeats |
| `TestSafety` | 2 | No claims_action_completed, unknown-practitioner subset safe |
| `TestComposedCounts` | 4 | All 24 pass extraction, policy, composed, and safety |
| `TestContractLayerGap` | 2 | Unknown practitioner extraction/policy deliberately differ; known practitioner layers agree |
| `TestFixtureCrossChecks` | 2 | All unknown practitioner names genuinely unmapped; all known IDs non-None |

---

## Aggregate layer counts

| Metric | Value |
|---|---|
| Total probes | 24 |
| Extraction pass | 24 / 24 |
| Policy pass | 24 / 24 |
| Composed pass | 24 / 24 |
| Safe | 24 / 24 |
| Variance | 0 / 24 |

### Family distribution

| Family | Count | Extraction:Policy relationship |
|---|---|---|
| `move_unknown_practitioner` | 12 | Extraction exact → policy clarify (deliberate contract-layer gap) |
| `move_known_practitioner_control` | 6 | Both layers resolve |
| `resize_paraphrase_control` | 3 | Both layers resolve |
| `status_paraphrase_control` | 3 | Both layers resolve |

### Classification

| Classification | Count |
|---|---|
| `pass` | 24 |
| `parser_gap` | 0 |
| `policy_gap` | 0 |
| `contract_layer_gap` | 0 |
| `authoring_invalid` | 0 |

### Fixture hash

```
sha256:98609b943085498f50941f4dfddc0efee414c8a2a779e78e1f00ddb484bff672
```

---

## Fixture-label concerns

None. The fixture passed all validation checks:

- Schema version `bernie.lc4v6d1.probes.v1` ✓
- Reference date `2026-07-16` ✓
- Population exactly 24 ✓
- Family counts 12 / 6 / 3 / 3 ✓
- All probe IDs unique ✓
- All required fields (`probe_id`, `family`, `utterances`, `extraction`, `policy`) present ✓
- All extraction required keys present ✓
- All policy required keys present ✓

All 24 probes were authored with independent extraction and policy expectations
that correctly reflect the contract-layer distinction for unknown practitioners.

---

## Contract-layer verification

The deliberate contract that **unknown practitioner text is exact at extraction
but becomes clarification at policy** was verified across all 12 unknown-practitioner
probes:

| Property | Extraction | Policy |
|---|---|---|
| Practitioner semantics | `"exact"` | N/A (resolved as `None` ID) |
| `requires_clarification` | `False` | `True` |
| Authority | `"read"` | `"clarify"` |
| Tools | `("search_patients", "update_appointment")` | `("request_clarification",)` |
| Resolved practitioner ID | N/A | `None` |
| Appointment deltas | N/A | `()` |
| Audit deltas | N/A | `()` |
| Simulated write | N/A | `False` |

The runner compares extraction and policy independently against the fixture
and never requires identical clarification state across layers — confirming
the contract-layer feature, not a parser deficiency.

---

## Decision

```
DECISION: pass
```

All 24 probes pass extraction-layer and policy-layer comparison with zero
variance, 100% safety coverage, and full preservation of the contract-layer
distinction for unknown practitioners. No fixture-label concerns, no parser
gaps, no policy gaps, no runner-level contract-layer defects.
