# Independent Review and Veto Report: LC3 Composed Evaluator

**DECISION:** `DECISION: pass`

---

## 1. Metadata and Context

*   **Reviewed Commit:** `793b930008decc667fb4029bcb8ceec3d0bd315e` (fix(bernie): harden LC3 evaluation evidence)
*   **Workspace Root:** `C:\Users\sarashera\EMR4-worktrees\lc3-antigravity`
*   **Target Branch:** `antigravity/lc3-composed-evaluator-review`
*   **Review Agent:** Gemini 3.5 Flash (Medium)

### Files Reviewed
*   [`app/services/bernie/composed_evaluator.py`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/app/services/bernie/composed_evaluator.py)
*   [`app/services/bernie/composed_corpus_evaluator.py`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/app/services/bernie/composed_corpus_evaluator.py)
*   [`scripts/bernie_coverage_lattice.py`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/scripts/bernie_coverage_lattice.py)
*   [`docs/bernie-lc3-composed-evaluation-report.json`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/docs/bernie-lc3-composed-evaluation-report.json)
*   [`docs/bernie-lc3-composed-evaluation.md`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/docs/bernie-lc3-composed-evaluation.md)
*   [`tests/test_bernie_composed_corpus_evaluator.py`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/tests/test_bernie_composed_corpus_evaluator.py)
*   [`tests/test_bernie_coverage_lattice.py`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/tests/test_bernie_coverage_lattice.py)
*   [`tests/test_bernie_lc3_mutations.py`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/tests/test_bernie_lc3_mutations.py)
*   [`AGENTS.md`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/AGENTS.md)
*   [`docs/bernie-language-coverage-implementation-plan.md`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/docs/bernie-language-coverage-implementation-plan.md)
*   [`docs/bernie-t2-deterministic-behaviour-matrix.md`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/docs/bernie-t2-deterministic-behaviour-matrix.md)
*   [`docs/bernie-t3-shadow-evaluation.md`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/docs/bernie-t3-shadow-evaluation.md)

---

## 2. Verification Commands and Executable Results

### Command 1: Focused Test Executions
All tests covering the composed evaluator, mutations, and the coverage lattice were executed.

```powershell
# Running evaluator, lattice, and mutation tests
pytest tests/test_bernie_composed_corpus_evaluator.py tests/test_bernie_coverage_lattice.py tests/test_bernie_lc3_mutations.py
```

**Result:**
```text
======================================= 90 passed in 33.06s =======================================
```

### Command 2: Independent Adjudication & Provenance Tests
Additionally, the LC2 corpus generation and promotion-prevention rules were validated to confirm that Silver candidates are quarantined if there is an adjudication mismatch.

```powershell
# Running LC2 provenance and adversarial corpus tests
pytest tests/test_bernie_corpus_adversarial.py tests/test_bernie_corpus_tier.py
```

**Result:**
```text
======================================= 100 passed in 19.74s ======================================
```

### Command 3: Coverage Lattice Generation
Verified the candidate-aware coverage lattice output and gap calculations.

```powershell
# Run the coverage lattice script in candidate-aware mode
python scripts/bernie_coverage_lattice.py --candidate-dir tests/fixtures/bernie_corpus_candidates
```

**Result:**
The command completed successfully and generated the coverage lattice statistics showing:
*   `adjudicated_covered_cell_count`: 3
*   `adjudicated_empty_cell_count`: 152,061
*   `candidate_only_cell_count`: 7
*   `union_covered_cell_count`: 10
*   `union_empty_cell_count`: 152,054
*   `total_lattice_cells`: 152,064
*   `pending_candidates_do_not_reduce_adjudicated_gaps`: true

---

## 3. Evaluation of Adjudication and Falsification Claims

### Claim 1: Observed interpretation is derived from utterances and deterministic state, not copied from expected specs or branched on scenario IDs.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:** In [`composed_corpus_evaluator.py`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/app/services/bernie/composed_corpus_evaluator.py), `deterministic_interpret` processes dialogue turns entirely dynamically. It parses utterances using regular expression patterns (`_PATIENT_PATTERN`, `_PRACTITIONER_PATTERN`, `_DURATION_PATTERN`) and temporal parser APIs (`extract_natural_time_constraints` and `parse_time_fragment`). The scenario is only accessed to resolve relative clinic clocks (e.g. mapping "tomorrow" relative to `scenario.reference_date`). There are no branches on scenario IDs or copies of expected output fields.

### Claim 2: Lossless normalization and multi-turn correction preserve all uncorrected fields; exact/open/interval/approximate/unspecified relations cannot collapse silently.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:** `_extract_normalized_values` aggregates temporal constraints losslessly. Multi-turn correction (via `_detect_correction_turn`) is handled by a state reducer where a correction turn overrides only the specific target entity or temporal coordinate (e.g., updating the time field in a time correction turn) while carrying all other previously extracted fields forward. The extracted temporal relation maps directly to `exact`, `not_before`, `not_after`, `interval`, `approximate`, or `unspecified`, verifying that distinct temporal forms do not collapse.

### Claim 3: Replay is a deterministic offline T2-style policy projection, not a hidden provider/runtime route or an expected-outcome echo.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:** `deterministic_replay` uses an offline mapper (`_map_outcome`) checking the interpreted action, clarification needs, and mock diary state (such as `exact_duplicate`, `overlap`, `empty`) from the scenario spec. Write deltas are constructed from interpreted values (not expected spec deltas), and `is_simulated_confirmed_write` is flagged only when the scenario contract expects persistence, ensuring that replay acts as a query-only offline projection.

### Claim 4: Field, outcome, interpretation-tool, replay-tool, authority, clarification, appointment/audit delta, safety, and repeat variance scores are separately visible; simultaneous failure layers are not hidden by a dominant score.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:** `ComposedSampleResult` holds isolated result classes for each facet of correctness. The fail attribution helper `_attribute_all_failures` returns a complete list of failure layers (`FailureLayer`) in priority order: safety, interpretation, policy, and integration. In `build_corpus_summary`, each failure type is checked and aggregated independently, so a single sample failure containing both safety and integration violations is tallied under both metrics.

### Claim 5: Prohibited instructions retain the legitimate first-turn write but cannot cause a second write, claim completion, bypass confirmation, or promote pending Silver evidence.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:** In `deterministic_interpret`, if unsafe/bypass wording is detected, `action_semantics` is set to `prohibited`, `authority_claim` becomes `refuse`, and `claims_action_completed` is forced to `False`. The replay constructs delta logs representing only the legitimate first turn and enforces refusal on the second turn, preventing any second write or confirmation bypass. It does not trigger any promotion of pending Silver candidates.

### Claim 6: The 7 metamorphic and 9 mutation probes execute real relations/damage and would fail under plausible parser/scorer mutations; flag tautologies or checks that merely restate fixture expectations.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:** In [`test_bernie_lc3_mutations.py`](file:///C:/Users/sarashera/EMR4-worktrees/lc3-antigravity/tests/test_bernie_lc3_mutations.py), metamorphic classes (e.g. `TestMetamorphicParaphrase`, `TestMetamorphicMinimalPair`) test real data flow over candidates. The mutation tests deliberately corrupt the expected/observed fields (temporal relation, entity, outcome, tools, authority, clarification, deltas) and pass them to the scorer to verify that the scorer registers failures and attributes them to the correct layer. These are not tautological as they use real scenario files on disk and confirm scorer output.

### Claim 7: Two repeats genuinely exercise variance bookkeeping; the committed report regenerates exactly and its 18/36, 26/10, 7/7, 9/9, and layer/dimension counts match executable results.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:** The test `TestCommittedReportMatch` verifies that `evaluate_corpus()` matches the committed `bernie-lc3-composed-evaluation-report.json` exactly. The variance metrics track fingerprint differences across repeats. Since the evaluator is deterministic, variance is exactly 0. The report counts match executable results:
    *   18 scenarios × 2 repeats = 36 samples
    *   26 passed, 10 failed
    *   10 interpretation failures, 10 integration failures
    *   0 safety, 0 policy, 0 repeat variance

### Claim 8: Candidate-aware lattice arithmetic is correct, examples are unique cells, strict loading fails closed, and pending/quarantined evidence never reduces the 152,061 adjudicated gaps.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:**
    *   Total cells = 6 actions * 11 states * 6 entities * 6 temporal * 8 dialogue * 8 language = 152,064.
    *   Gold scenarios = 3, so adjudicated covered = 3.
    *   Adjudicated empty cells = 152,064 - 3 = 152,061 (gaps).
    *   Silver candidates = 15, covering 7 candidate-only cells.
    *   Union covered = 10 (3 gold + 7 candidate-only), leaving 152,054 union empty cells.
    *   Adjudicated empty cells (152,061) is preserved and never reduced by pending candidates.
    *   Loader validations fail closed if file counts, tiers, or adjudication structures are anomalous.

### Claim 9: T3.1-T3.4, interpretation/live-provider gates, T3.5 deferral, provider/data/route/DB/history/write boundaries, and no-self-certification rules remain intact.
*   **Status:** **Pass (Falsification failed)**
*   **Evidence:** The isolation test `test_isolation` parses the AST of `composed_evaluator.py` to assert that no database, route, or provider module is imported. The live gates check remains blocked in `docs/bernie-t3-live-replay-gate.json`, and no promotion logic or live model adapters are active.

---

## 4. Independent Arithmetic and Count Readback

We verify the Cartesian math of the coverage lattice:
$$\text{Total Cells} = |A| \times |S| \times |E| \times |T| \times |D| \times |L|$$

Where:
*   $|A|$ (Diary Actions) = 6
*   $|S|$ (Diary States) = 11
*   $|E|$ (Entity States) = 6
*   $|T|$ (Temporal Forms) = 6
*   $|D|$ (Dialogue Forms) = 8
*   $|L|$ (Language Forms) = 8

$$\text{Total Cells} = 6 \times 11 \times 6 \times 6 \times 8 \times 8 = 152,064$$

### Lattice Summary table:
| Metric | Expected Value | Observed Value | Match Status |
| :--- | :--- | :--- | :--- |
| **Total cells** | 152,064 | 152,064 | Match |
| **Adjudicated covered (Gold)** | 3 | 3 | Match |
| **Adjudicated empty (Gaps)** | 152,061 | 152,061 | Match |
| **Candidate-only covered (Silver)**| 7 | 7 | Match |
| **Union covered** | 10 | 10 | Match |
| **Union empty** | 152,054 | 152,054 | Match |

---

## 5. Explicit Authority and Gate Confirmation

The boundary verification passes:
1.  **Imports Isolation:** Verified by `validate_composed_evaluator_isolation()` which successfully checks that `app.routers`, `app.models`, `app.db`, `app.services.ai.providers`, `sqlalchemy`, and `alembic` are NOT imported.
2.  **No Writes:** Replay is strictly read-only unless `is_simulated_confirmed_write` is flagged based on scenario expectations.
3.  **Adjudication POSTURE:** All candidates retain their `silver`/`pending` status and cannot certify themselves.

---

## 6. Proposed Failing Probe (Mutated Priority Scorer)

If a developer mutated the priority scorer in `app/services/bernie/composed_evaluator.py` such that a safety failure was hidden by an interpretation failure, or the layers were ordered incorrectly, the following test outlines how to fail the mutation.

```python
def test_priority_scorer_safety_dominance_mutation():
    """Verify that a safety violation is always the dominant failure layer (first in the tuple),
    even when interpretation, policy, and integration failures are simultaneously present.
    """
    # 1. Arrange: Construct a scenario and heavily damaged observations containing ALL failure layers.
    scenario = SCENARIO_EXACT
    
    # Mutated interpretation has:
    # - wrong temporal_relation (interpretation failure)
    # - claims_action_completed = True (safety failure)
    # - selected_tool_sequence = ("wrong_tool",) (integration failure)
    bad_interp = _default_interp(
        scenario,
        temporal_relation="unspecified",
        claims_action_completed=True,
        selected_tool_sequence=("wrong_tool",),
    )
    
    # Mutated replay has:
    # - wrong downstream_outcome (policy failure)
    # - wrong tools_used (integration failure)
    bad_replay = _default_replay(
        scenario,
        downstream_outcome="appointment_created",
        tools_used=("wrong_tool",),
    )
    
    # 2. Act: Score the mutated pair
    result = score_interpretation_replay_pair(scenario, bad_interp, bad_replay)
    
    # 3. Assert: Verify all layers are identified and 'safety' is the DOMINANT layer (failure_layer)
    assert "safety" in result.failure_layers
    assert "interpretation" in result.failure_layers
    assert "policy" in result.failure_layers
    assert "integration" in result.failure_layers
    
    # If the prioritisation rules are damaged, this dominant layer assertion fails.
    assert result.failure_layer == "safety", (
        f"Expected dominant failure layer to be 'safety', got: '{result.failure_layer}'"
    )
```
