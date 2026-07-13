# Task Packet: LC1 DW2 — Scenario Contract + Normalization + Seed + Gap

Role: DeepSeek Flash Worker (implementation owner)
Model: `deepseek-v4-flash` / high
Branch: `codex/lc1-dw2-scenario-contract`
Source Plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-lc1-semantic-foundation-v2.md`

## Mission

Introduce the canonical `ReceptionScenarioSpec` contract, lossless language
normalization, adapted T1/T2 seed scenarios, a coverage lattice gap report,
and the supporting tests. Do not implement product code beyond these test/
harness artifacts.

## Boundary

- All new code is test/harness-only: no routes, no provider calls, no DB
  writes, no mutation/confirmation authority, no live prompts.
- Do not touch: `app/services/diary/temporal.py` (DW1),
  `app/services/bernie/normalizer.py` (existing slot-normalizer facade),
  `app/services/bernie_slot_normalizer.py`, `app/schemas/appointments.py`,
  T3 eval code, migrations, routes.
- New modules must use distinct names:
  `app/services/bernie/scenario_spec.py` for the contract and
  `app/services/bernie/language_normalization.py` for normalization.

## Implementation Steps

### Step 1: Create `app/services/bernie/scenario_spec.py`

Define a Pydantic `ReceptionScenarioSpec` model with these fields:

| Field | Type | Description |
|---|---|---|
| `spec_version` | `Literal["lc1.v1"]` | Version marker |
| `scenario_id` | `str` | Unique ID referencing source T1/T2 scenario |
| `provenance` | `Literal["gold", "silver", "bronze"]` | Evidence tier |
| `adjudication` | `Literal["adjudicated", "pending", "quarantine"]` | Review state |
| `family` | `str` | Scenario family label |
| `description` | `str` | Human-readable scenario description |
| `dialogue_turns` | `list[dict]` | Original receptionist utterances, one per turn |
| `reference_date` | `date` | Deterministic clinic-local clock date |
| `intended_action` | `str` | Diary action verb (create, move, resize, cancel, status_change, explain_schedule) |
| `temporal_relation` | `Literal["exact", "not_before", "not_after", "interval", "approximate", "unspecified"]` | Temporal operator semantics |
| `earliest_time` | `Optional[str]` | HH:MM normalized earliest |
| `latest_time` | `Optional[str]` | HH:MM normalized latest |
| `source_spans` | `dict[str, str]` | Field → original utterance substring |
| `duration_minutes` | `Optional[int]` | Appointment duration |
| `practitioner_semantics` | `Literal["exact", "ambiguous", "omitted", "negated"]` | How practitioner is referenced |
| `patient_semantics` | `Literal["exact", "ambiguous", "omitted", "negated", "provisional"]` | How patient is referenced |
| `initial_diary_state` | `dict` | Synthetic diary state before interpretation |
| `expected_outcome_kind` | `str` | e.g. `interpreted_ready`, `existing_booking_found`, `clarification_required` |
| `expected_tool_sequence` | `list[str]` | Ordered tool calls expected |
| `expected_appointment_deltas` | `list[dict]` | Appointment rows expected to change |
| `forbidden_outcomes` | `list[str]` | Outcomes that must not occur |
| `forbidden_tool_calls` | `list[str]` | Tool calls that must not occur |
| `expected_clarification` | `Optional[str]` | Expected clarification question |
| `clarification_choices` | `list[str]` | Acceptable clarification responses |

Export the model and any helper validation functions from `__init__` if needed.

### Step 2: Create `app/services/bernie/language_normalization.py`

Implement lossless normalization as a pure function:

```python
def normalize_utterance(original: str) -> NormalizedUtterance:
    """Preserve the original utterance and produce a derived matching view."""
```

`NormalizedUtterance` dataclass:

| Field | Type | Description |
|---|---|---|
| `original` | `str` | The untouched original utterance |
| `normalized` | `str` | Unicode NFKC, whitespace-collapsed, case-folded, punctuation-normalized |
| `time_forms` | `dict[str, str]` | Detected time fragments → HH:MM canonical form |
| `number_forms` | `dict[str, str]` | Detected number words → digit form |
| `source_spans` | `dict[str, tuple[int, int]]` | Field → (start, end) in original string |

Processing rules:
1. Unicode NFKC normalization
2. Collapse runs of whitespace to single spaces
3. Case folding (lowercase)
4. Normalize multiple punctuation: `..` → `.`, `!!` → `!`
5. Detect time forms: `3pm`, `3 pm`, `3.00pm`, `15:00`, `3:00` → HH:MM
6. Detect number words: `fifteen` → `15`, `thirty` → `30`, etc.
7. Preserve operator words: `at`, `before`, `after`, `from`, `to`, `not`,
   `without`, `around`, `about`, `between`, `and` — never remove these.
8. No stop-word removal, stemming, or lemmatization.

### Step 3: Create adapted T1/T2 seed fixtures

Under `tests/fixtures/bernie_scenario_spec/`, create three JSON fixtures:

1. **`booking_create_then_exact_duplicate.json`** — Adapted from T1.1:
   - First turn: create a booking at a specific time
   - Second turn: request a booking at the same exact time
   - `temporal_relation: "exact"`
   - `expected_outcome_kind: "existing_booking_found"`
   - `forbidden_outcomes: ["appointment_created"]`

2. **`booking_overlap_not_exact_duplicate.json`** — Adapted from T1.2:
   - Existing booking at 15:00
   - Request booking within overlapping window but not exact time
   - `temporal_relation: "not_before"` or `"interval"`
   - `expected_outcome_kind: "clarification_required"` or `"candidate_selection_required"`
   - Must NOT produce `existing_booking_found` because relation is not `exact`

3. **`interpret_clarify_temporal_bounds.json`** — Interpret-clarify with
   temporal bounds:
   - Ambiguous or partial temporal instruction
   - `expected_outcome_kind: "clarification_required"`
   - `expected_clarification` populated
   - `clarification_choices` populated

Each fixture must:
- Reference a valid T1/T2 scenario ID in `scenario_id`
- Use `provenance: "gold"`
- Have `adjudication: "pending"` (Sol adjudicates)
- Include all required `ReceptionScenarioSpec` fields
- Use synthetic patient/practitioner/appointment IDs from the Bernie test
  fixture namespace (e.g. `"p-001"`, `"pr-001"`, `"apt-001"`)

### Step 4: Create `tests/fixtures/bernie_scenario_spec/README.md`

Document:
- Provenance: adapted from authored T1/T2 golden scenarios
- Tier: Gold (adjudication pending)
- Adjudication authority: Sol (Conductor)
- Family labels and their meanings
- How to add new scenarios
- What makes a scenario Gold vs Silver vs Bronze

### Step 5: Create `tests/test_bernie_scenario_spec.py`

Tests covering:
1. **Contract validation:** `ReceptionScenarioSpec` validates with all
   required fields; rejects missing required fields; validates enum literals.
2. **Seed fixture validation:** All three seed .json files parse as valid
   `ReceptionScenarioSpec` instances.
3. **Seed semantics:** Each seed fixture has correct `temporal_relation`,
   correct `expected_outcome_kind`, correct `forbidden_outcomes`.
4. **Normalization:** `normalize_utterance` preserves original, produces
   correct normalized form, detects time forms, preserves operator words.
5. **Normalization edge cases:** Unicode variants, multiple spaces, mixed
   case, punctuation variants.
6. **Normalization no-ops:** Stop words are NOT removed; stemming is NOT
   applied; `at`, `before`, `after` are preserved.

### Step 6: Create `scripts/bernie_coverage_lattice.py`

A CLI script that:
1. Discovers all committed scenario fixtures under
   `tests/fixtures/bernie_scenario_spec/`.
2. Builds a coverage lattice across dimensions:
   - diary_action: create, move, resize, cancel, status_change,
     explain_schedule
   - diary_state: empty, exact_duplicate, overlap, same_day_distinct,
     terminal, stale, concurrent, roster_absent, break, no_slots,
     elapsed_window
   - temporal_form: exact, not_before, not_after, interval, approximate,
     unspecified
   - dialogue_form: one_shot, clarification, correction, reversal,
     ellipsis, anaphora, repeated, session_restart
   - language_form: plain, paraphrase, filler, abbreviation, typo,
     speech_like, punctuation_variant, adversarial
3. Prints JSON to stdout with:
   - Total scenario count
   - Per-dimension counts
   - Explicit list of empty cells (cell = tuple of dimension values with
     zero scenarios covering it)
   - Per-family summary
4. Accepts `--fixture-dir` to override the default path.
5. Returns exit code 0 on success even when empty cells exist (empty cells
   are information, not failure).

### Step 7: Create `tests/test_bernie_coverage_lattice.py`

Tests covering:
1. Script runs and produces valid JSON.
2. JSON has required top-level keys: `scenario_count`, `dimensions`,
   `empty_cells`, `family_summary`.
3. Empty cells list is non-empty (proves the lattice shows gaps).
4. Each empty cell has `diary_action`, `diary_state`, `temporal_form`,
   `dialogue_form`, `language_form` fields.
5. Script fails with non-zero exit when fixture directory is missing.
6. Script fails with non-zero exit when fixture directory is empty.

## Out of Scope

- Temporal parser changes (DW1).
- Independent review (DW3).
- Routes, provider calls, DB writes, confirmation authority.
- `app/services/bernie/normalizer.py` (the slot-normalizer facade).
- `app/services/diary/temporal.py`.
- `app/schemas/appointments.py`.
- T3 evaluation code.
- `app/services/bernie_slot_normalizer.py`.

## Acceptance Checks

```powershell
# 9-11. All scenario spec tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_scenario_spec.py -q

# 12. Coverage lattice emits valid JSON with explicit empty cells
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_coverage_lattice.py

# 13. Coverage report tests pass
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_coverage_lattice.py -q
```

## Submit Instructions

When complete, from this worktree run:

```powershell
python scripts\agent_worktrees.py submit --agent deepcode --commit-message "LC1 DW2: scenario contract + lossless normalization + adapted T1/T2 seeds + coverage lattice gap report" --message "ReceptionScenarioSpec contract, lossless language normalization preserving operator words, three adapted T1/T2 gold seed fixtures, and machine-readable coverage lattice with explicit empty cells. All test/harness only."
```
