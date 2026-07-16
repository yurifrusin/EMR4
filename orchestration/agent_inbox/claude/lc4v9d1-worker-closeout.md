# LC4V9D1 Worker Closeout

**Date:** 2026-07-16
**Worker:** DeepSeek V4 Flash/high through Claude Code `--bare`
**Worktree:** `C:\Users\sarashera\EMR4-worktrees\lc4v9d1-dw1`
**Branch:** `claude/lc4v9d1-noncreate-identity-diagnostic`
**Source head:** `2e8cf77745f4bb54fe18d2759d878fb3a7170271`

## Source Head

The dispatch commit in `git rev-parse HEAD` is:
```
2e8cf77745f4bb54fe18d2759d878fb3a7170271
```

## Owned Files (created)

| File | Purpose |
|------|---------|
| `app/services/bernie/lc4v9d1_development_evidence.py` | Diagnostic evidence runner - loads fixture, validates fail-closed, runs extraction then policy, projects 14 fields, derives semantics, classifies |
| `tests/fixtures/bernie_lc4v9d1_development/probes.json` | 30-probe synthetic Gold fixture (6 per non-create action, no create probes) |
| `tests/test_bernie_lc4v9d1_development.py` | 69 focused tests for counts, balance, Gold contradictions, oracle separation, projection, variance, hashes, safety |
| `orchestration/agent_inbox/claude/lc4v9d1-worker-closeout.md` | This closeout |

## Commands / Counts

```
python -m pytest tests/test_bernie_lc4v9d1_development.py -v
```

- **69 tests collected, 69 passed, 0 failed**
- **0 variance** over 60 observations (30 probes x 2 repeats)
- **30 safe** (all 30)
- **All natural time tests preserved** (no regression)

## Fixture / Report Hashes

| Artifact | Hash |
|----------|------|
| Raw fixture file | `sha256:4727ded84b333142a3f0ca08d955bac88b52fac2b2bc148f3160876a27461de4` |
| Canonical fixture | `sha256:5aaf3972546a56b717998b73a11247756f24fb3336dbf8e6c3ef3b3ba90f71ad` |
| Evidence report | `sha256:fcc816aa50b3d93240bb7be9e35f8a3b84cad29fe808a467f9c34b67b854ccdf` |
| Non-pass selection | `sha256:e0005f99b49814a3a99cc5af5886436115d35bdd28cc170988a2fa3695c623ed` |

## Observed Class Counts

| Classification | Count | Description |
|----------------|-------|-------------|
| `pass` | 15 | All layers match Gold |
| `extraction_gap` | 6 | Uppercase action verb captured as part of patient name by `_extract_patient` |
| `policy_gap` | 9 | Non-possessive patient forms: `extract_final_patient` returns None, so `resolved_patient` is null in 14-field projection |
| `authoring_invalid` | 0 | All Gold is internally consistent |
| **Total** | **30** | |

### Per-action breakdown

| Action | pass | extraction_gap | policy_gap |
|--------|------|----------------|------------|
| move | 1 | 2 | 3 |
| resize | 3 | 1 | 2 |
| cancel | 3 | 1 | 2 |
| status_change | 2 | 2 | 2 |
| explain_schedule | 6 | 0 | 0 |

### Language structure coverage

All 6 required structures present per action:
1. direct_named_patient
2. appointment_for_patient
3. possessive_patient
4. patient_first_word_order
5. polite/safe_negated or polite_speech_like
6. two_turn_additive_unsafe or two_turn_additive_context

### Negated/unsafe per mutation action

| Action | Safe negated | Unsafe bypass/refusal |
|--------|-------------|----------------------|
| move | v9d1-move-005 | v9d1-move-006 |
| resize | v9d1-resize-004 | v9d1-resize-006 |
| cancel | v9d1-cancel-003 | v9d1-cancel-004 |
| status_change | v9d1-status-003 | v9d1-status-005 |

## Scope Incident Record

- **None.** No protected V9 evidence, holdout files, or forbidden surfaces were accessed.
- Only the 8 named files were read (AGENTS.md, sol-contract.md, semantic_extraction.py, language_normalization.py, lc4v4d3_policy_resolution.py, lc4v8d1_development_evidence.py, test_bernie_lc4v8d1_development.py, probes.json).
- No recursive listing, broad filename search, or repository-wide grep was performed.
- No parser/policy/product code was edited or repaired.
- No protected refs were pushed.

## Diagnostic Findings

1. **Verb-in-name extraction gap:** When a non-create action verb (Move, Cancel, Mark, Resize) starts the utterance with an uppercase letter, `_extract_patient` captures the verb as part of the patient name (e.g., "Move Amara Osei" instead of "Amara Osei"). 6 probes exhibit this pattern.

2. **Policy patient identity loss:** For non-possessive patient forms (without `'s appointment`), `extract_final_patient` in the policy module returns None, causing `resolved_patient` to be null in the 14-field canonical projection. 9 probes exhibit this policy gap. Possessive forms (`'s appointment`) correctly resolve patient identity via `_MUTATION_PATIENT_CAPTURE`.

3. **Both findings validate the V9 hypothesis** that non-create language may lose patient identity during extraction or policy projection.

---

**DECISION: candidate_ready**
