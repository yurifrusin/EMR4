| Item | Value |
|---|---|
| To | codex |
| From | codex (DeepSeek Flash replacement for Claude's R30 plan lane) |
| Model | Current Codex session model |
| Branch | codex/r30-grammar-replay-consumer-plan |
| Source Task | claude-r30-action-grammar-replay-consumer (Claude lane replaced; plan produced by Codex via DeepSeek Flash protocol) |
| Status | pending_plan_review |
| Created | 2026-07-06 |

## Plan Summary

Build the smallest deterministic synthetic replay consumer that proves the R29 action grammar can be *consumed* by dispatch/routing logic without tautology. The replay consumer lives entirely in test helpers and synthetic fixtures (no production pp/ changes). It simulates consumer-side decisions — tier-based routing, implementation gates, staff-confirmation enforcement, envelope-name resolution, and affordance pre-check — against authored day/action scripts. No DB, no HTTP, no provider calls, no H-series semantic data. H15 stays closed.

## My Understanding

R29 delivered a typed DiaryActionVerb enum (11 verbs), DiaryActionVerbDescriptor with full domain contract bindings, DIARY_ACTION_GRAMMAR, ction_verb_for_envelope bridge, and ssert_grammar_consistency(), plus ~20 tests covering schema version, invariants, confirm-tier notes, mutation/meta rules, envelope name mapping, and H-series reference regression.

The existing 	ests/bernie_scenarios/ replay infrastructure tests booking-slot HTTP API endpoints (normalize ? search ? select ? confirm). It uses YAML fixtures, a TestClient, DB fixtures, and a forbidden-AI-provider guard. It proves backend route correctness, not grammar-contract consumption.

The **grammar replay consumer** is a fundamentally different kind of replay:
- Pure in-process contract consumption (no DB, no HTTP, no route)
- Tests how a consumer *interprets* grammar descriptors to make dispatch/affordance decisions
- Authored synthetic day scripts describe action sequences with expected consumer-side decisions
- No provider calls (trivially guaranteed by no i_service imports and no monkeypatch needed)

The tautology risk is the central design challenge. If the consumer only re-checks descriptor.mutating == True and descriptor.tier == BernieCapabilityTier.confirm, that's just ssert_grammar_consistency repeated at a different call site. Real consumer logic is **cross-field dispatch decisions** — the consumer must correctly answer "what do I do next?" based on the grammar contract, not "does the grammar contract hold?"

## Intended Surface / Boundary

- 	ests/action_grammar_replay/ — new test helper directory (mirrors 	ests/bernie_scenarios/ structure but pure domain, no HTTP/DB)
  - loader.py — loads synthetic day-action scripts
  - eplay.py — grammar replay consumer engine with consumer-side decision logic
  - 	est_grammar_replay.py — parametrized pytest harness
- 	ests/fixtures/action_grammar_replay/ — new synthetic-only JSON fixtures directory
  - 3–5 authored day-action scripts covering: full confirm day, read-only day, mixed day, planned-not-implemented refusal, unknown action graceful degradation
- docs/receptionist_review_r30.md — Antigravity/Gemini to produce after plan approval
- Coordination-only updates to packet status

**Surfaces that must NOT change:**
- pp/ (no production code edits)
- 	ests/fixtures/bernie_scenarios/ (existing booking scenario corpus)
- 	ests/fixtures/h_series_profiles/ (neutral profile layer)
- 	ests/bernie_scenarios/ (existing replay infrastructure)
- All existing test files in 	ests/ root
- Any docs/historical-diary-trove-* docs
- local_data/ (raw trove stays ignored)
- Routes, UI, taskpane, diary grid, migrations, provider code

## Out Of Scope

- Production pp/ changes (the consumer lives in test helpers, not in production dispatch code)
- Raw local_data, ignored JSON, H-series profiles, H15 gate edits
- Broad full-trove processing or -AllowLargeRun invocations
- Route/UI/taskpane changes
- Provider calls or AI service imports
- Backend DB writes
- Existing fixture or test modifications
- master or handoff/current movement

## Files I Expect To Edit / Create

### New: 	ests/action_grammar_replay/loader.py
Loads synthetic day-action JSON/JSON5 scripts from 	ests/fixtures/action_grammar_replay/.

### New: 	ests/action_grammar_replay/replay.py
The grammar replay consumer engine. Contains consumer-side decision logic that proves grammar consumption:
- esolve_action(raw_name) — calls ction_verb_for_envelope, then get_verb_descriptor; returns structured consumer state
- consumer_dispatch_decision(descriptor) — returns a typed enum covering: oute_to_confirm, oute_read_only, oute_meta, efuse_not_implemented, efuse_unknown_action
- consumer_confirm_prerequisites(descriptor) — returns what conditions must hold before a confirm endpoint may be called (requires_staff_confirmation, confirm_affordance_notes expectations)
- consumer_enforce_invariants(descriptor) — cross-field checks a real consumer would need (e.g., "is it an error if a confirm-tier verb is implemented but has no confirm_actions?", "is it normal that a read-only verb is not mutating?")
- un_day_script(script) — loads and executes each action through the consumer functions, collects structured decisions and evidence

### New: 	ests/action_grammar_replay/test_grammar_replay.py
Parametrized pytest tests that:
1. Load all synthetic day-action scripts from 	ests/fixtures/action_grammar_replay/
2. Run each through the consumer engine
3. Assert expected consumer decisions match the script's expected outcomes
4. Assert no provider calls (trivially satisfied since no ai_service import)
5. Assert no DB access (trivially satisfied since no model imports)

### New: 	ests/fixtures/action_grammar_replay/ directory
Synthetic-only JSON fixtures. Each fixture is a single authored day-action script:

**confirm_create_move_resize_day.json** — Full confirm day:
- Action sequence: create (via ction_verb_for_envelope bridge with confirm_booking), move, resize, cancel
- Expected: each resolves to a confirm-tier, implemented, requires_staff_confirmation verb
- Consumer must route each to oute_to_confirm

**ead_only_handoff_day.json** — Read-only day:
- Actions: slot_search, explain_schedule, handoff
- Expected: no mutating, no staff confirmation, read_only/meta tier
- Consumer must route each to oute_read_only or oute_meta

**mixed_day_with_refusals.json** — Mixed day:
- Actions: slot_search (read_only), check_in (not implemented ? consumer must refuse), waiting_area_move (not implemented ? refuse), create (confirm ? route)
- Expected consumer dispatch: refuse for check_in and waiting_area_move, route_to_confirm for create, route_read_only for slot_search

**unknown_actions_and_bridge.json** — Graceful degradation:
- Actions: "propose_booking" (unknown ? should get back None from bridge), "propose_edit" (unknown), "find_slots" (known alias ? slot_search)
- Expected: consumer handles unknown gracefully, returns efuse_unknown_action

**ffordance_gate_expectations.json** — Confirm affordance pre-check:
- Actions: create, move, status_change
- For each: verifies consumer extracts confirm_affordance_notes, interprets staff_confirmation requirement, and can enumerate the confirm_actions endpoints that back it

Each fixture has the format:
`json
{
  "id": "confirm_create_move_resize_day",
  "description": "...",
  "source": "authored_synthetic",
  "actions": [
    {
      "raw_name": "confirm_booking",
      "expected_verb": "create",
      "expected_tier": "confirm",
      "expected_dispatch": "route_to_confirm",
      "expected_mutating": true,
      "expected_implemented": true,
      "requires_staff_confirmation": true,
      "has_confirm_affordance_notes": true,
      "confirm_actions_non_empty": true
    }
  ]
}
`

### Coordination artifacts:
- orchestration/agent_inbox/codex/plan-r30-action-grammar-replay-consumer.md (this plan)
- orchestration/agent_inbox/claude/claude-r30-action-grammar-replay-consumer.md (update completion notes + status to reflect plan produced by Codex)

## Implementation Steps

### Step 1 — Create synthetic fixture directory and 5 authored scripts
Create 	ests/fixtures/action_grammar_replay/ with 5 JSON fixtures (described above). Each is purely synthetic — no H-series references, no appointment times, no patient/practitioner identities, no raw diary content. Just action names and expected consumer dispatch metadata.

### Step 2 — Build 	ests/action_grammar_replay/loader.py
A load_day_script(path) -> dict function that:
- Reads JSON from the fixture directory
- Validates required fields (id, source, actions list)
- Validates that source == "authored_synthetic" (guard against accidental H-series or real-data loading)
- Validates expected dispatch values against a known safe set
- Returns the parsed script dict

Schema validation: SCHEMA_VERSION = "action_grammar_replay.v1", KNOWN_DISPATCH_VALUES = {"route_to_confirm", "route_read_only", "route_meta", "refuse_not_implemented", "refuse_unknown_action"}.

### Step 3 — Build 	ests/action_grammar_replay/replay.py
Contains the consumer-side decision functions:

`python
class ConsumerDispatch(str, Enum):
    route_to_confirm = "route_to_confirm"
    route_read_only = "route_read_only"
    route_meta = "route_meta"
    refuse_not_implemented = "refuse_not_implemented"
    refuse_unknown_action = "refuse_unknown_action"

def resolve_action(raw_name: str) -> dict:
    # 1. Call action_verb_for_envelope(raw_name)
    # 2. If None: return {verb: None, dispatch: refuse_unknown_action}
    # 3. Call get_verb_descriptor(verb)
    # 4. Call consumer_dispatch_decision(descriptor)
    # 5. Return structured result dict

def consumer_dispatch_decision(descriptor: DiaryActionVerbDescriptor) -> ConsumerDispatch:
    # A real consumer's dispatch logic:
    # - not implemented ? refuse_not_implemented
    # - confirm tier ? route_to_confirm
    # - read_only tier ? route_read_only
    # - meta tier ? route_meta

def consumer_confirm_prerequisites(descriptor: DiaryActionVerbDescriptor) -> dict:
    # What a consumer must check before calling a confirm endpoint:
    # - requires_staff_confirmation
    # - confirm_affordance_notes summary
    # - confirm_actions endpoints
    # - Is the verb in an envelope-ready state?

def consumer_enforce_invariants(descriptor: DiaryActionVerbDescriptor) -> list[str]:
    # Cross-field checks a consumer should make:
    # - If confirm-tier + implemented: must have confirm_actions, must have notes
    # - If mutating: must have staff_confirmation
    # - If read_only: must not be mutating
    # Returns list of invariant violations (empty = all good)

@dataclass
class ActionResult:
    raw_name: str
    verb: Optional[DiaryActionVerb]
    descriptor: Optional[DiaryActionVerbDescriptor]
    dispatch: ConsumerDispatch
    prerequisites: dict
    invariant_violations: list[str]

@dataclass
class DayScriptResult:
    script_id: str
    action_results: list[ActionResult]
    passed: bool
    evidence: list[str]
    failures: list[str]

def run_day_script(script: dict) -> DayScriptResult:
    # Run each action through resolve_action
    # Compare each result's actual fields against script's expected_* fields
    # Collect evidence/failures
    # Return structured result
`

Key design choice: the replay engine **compares consumer decisions against expected script outcomes**, not against grammar-module values read a second time. If a script says "action 'confirm_booking' should dispatch to route_to_confirm", the engine resolves the action through the consumer's dispatch function and checks the result matches the script's expectation. The expected values in the script are **authored correct expectations** — they represent what a correct consumer should produce, not what the grammar module internally stores. This avoids tautology because the expected values are authored independently and tested against the consumer's decision logic, not pulled from the grammar.

### Step 4 — Build 	ests/action_grammar_replay/test_grammar_replay.py
Parametrized pytest harness:

`python
@pytest.mark.parametrize("script", _build_params())
def test_grammar_replay_consumer(script):
    result = run_day_script(script)
    # Assert result.passed
`

The _build_params() function discovers all fixtures from 	ests/fixtures/action_grammar_replay/, loads them with load_day_script(), and returns pytest params.

A standalone "no tautology" guard test:
`python
def test_consumer_dispatch_is_independent_of_grammar_enum_values():
    """Verify consumer dispatch uses descriptor fields, not enum identity."""
    # Construct a synthetic descriptor (not from DIARY_ACTION_GRAMMAR)
    # with mismatched tier/implemented/mutating to prove the consumer
    # reads the right fields independently.
`

### Step 5 — Run verification
`powershell
.venv\Scripts\python.exe -m py_compile tests\action_grammar_replay\loader.py tests\action_grammar_replay\replay.py tests\action_grammar_replay\test_grammar_replay.py
.venv\Scripts\python.exe -m pytest tests\action_grammar_replay\ -v --tb=short -p no:randomly
.venv\Scripts\python.exe -m pytest tests\test_diary_action_grammar.py -v --tb=short -p no:randomly
git diff --check
`

### Step 6 — Update coordination artifacts
Update the Claude R30 task packet's completion notes to record this plan. Update orchestration/parallel_workstreams.md status.

## How Replay Proves Grammar Consumption Without Tautology

### What would be tautological
- Re-running ssert_grammar_consistency() in a different test file (the R29 tests already call it)
- Testing that DIARY_ACTION_GRAMMAR[create].tier == Confirm again (already tested)
- Reading a descriptor field and asserting it equals the same constant the grammar was defined with

### What makes this non-tautological

1. **Authored expected values vs. programmatic re-read**: Each fixture's expected_* values are authored by hand (not programmatically derived from the grammar module). The consumer's consumer_dispatch_decision() function reads descriptor fields and produces a dispatch enum. The test compares that dispatch output against the authored expectation. If someone breaks the consumer logic while keeping descriptor fields correct, the test fails. If someone breaks descriptor fields (e.g., marks create as read_only), both the R29 consistency tests and the consumer tests fail — orthogonal coverage.

2. **Consumer-side decision logic**: consumer_dispatch_decision() implements dispatch branching that is not present in the grammar module. It reads 	ier, implemented, and mutating and produces a single ConsumerDispatch decision. This logic is the same kind of decision a real route or Bernie dispatch point would make. The R29 tests never exercise this branching — they only test individual descriptor field values and static invariants.

3. **Cross-field invariant enforcement**: consumer_enforce_invariants() applies consumer-side validation rules that a real dispatch handler would need. For example: "is it an operational error if a confirm-tier implemented verb has zero confirm_actions?" The grammar module's ssert_grammar_consistency() checks this statically, but a consumer must also handle dynamic cases where a descriptor is retrieved at runtime and could theoretically be corrupted or from an unexpected version.

4. **Graceful degradation path**: The consumer handles ction_verb_for_envelope returning None (unknown action names, "propose_*" names) with efuse_unknown_action. The grammar tests only verify the bridge returns None — they don't test what a consumer *does* with that None. The replay test proves the consumer handles it correctly in a workflow context.

5. **Synthetic unknown descriptor test**: The standalone "consumer dispatch is independent" test constructs a synthetic descriptor not from DIARY_ACTION_GRAMMAR to prove the consumer reads descriptor fields correctly rather than being tautologically correct because it processes the same object reference.

### Proof table

| What's tested | Tautological? | Why |
|---|---|---|
| Grammar has ssert_grammar_consistency() | N/A (R29 owns this) | Already tested in R29 |
| Consumer dispatch matches authored script expectations | **No** | Authored values ? programmatic re-read; consumer has independent branching logic |
| Consumer invariant enforcement catches violations | **No** | Consumer-side rules applied at runtime, not static module-level |
| Consumer handles unknown action names | **No** | Tests consumer's graceful degradation path, not bridge return value alone |
| Consumer correctly reads verb from synthetic descriptor | **No** | Test uses constructed descriptor not from grammar dict |

## Visual / Behavioural Acceptance Checks

1. All 5 synthetic day-action scripts load and pass through the consumer engine.
2. consumer_dispatch_decision returns oute_to_confirm for create/move/resize/cancel/status_change; efuse_not_implemented for check_in/waiting_area_move/link_patient; oute_read_only for slot_search/explain_schedule; oute_meta for handoff.
3. esolve_action("propose_booking") returns efuse_unknown_action (bridge returns None ? consumer degrades gracefully).
4. consumer_enforce_invariants() reports zero violations for canonical grammar descriptors.
5. The standalone synthetic-descriptor test proves the consumer reads descriptor fields independently of the grammar dict identity.
6. No existing test regresses (pytest tests/test_diary_action_grammar.py -q still passes).
7. git diff --check produces no whitespace errors.
8. No pp/ files changed. No H-series references in any new fixture or test file. No local_data references. No provider imports.

## Risks / Ambiguities

- **Risk: fixture file format overengineering.** Mitigation: use simple JSON with minimal schema validation. No YAML dependency needed since the consumer has no DB/HTTP context to configure. Avoid adding a new serialisation library.
- **Risk: the consumer logic appears too trivial.** Mitigation: document explicitly that the consumer's value is proving *consumption*, not sophistication. The consumer is intentionally minimal — it must be small enough to review and trust, but exercise enough branching to prove the grammar is consumable. A trivial consumer that still fails on a corrupted or unexpected descriptor is worth more than a complex one that is hard to reason about.
- **Risk: tautology accusation remains despite mitigation.** Mitigation: the 	ests/test_diary_action_grammar.py golden confirm-block test is different from the replay consumer's affordance pre-check — the golden test verifies the grammar descriptor has notes; the consumer verifies it can *interpret and act on* those notes in a dispatch context. Include this distinction in the implementation review.
- **Ambiguity: whether to add a consumer.py in pp/services/diary/ for production use.** Decision: not yet. The consumer lives in test helpers for R30. If it proves useful, later sprints may promote it to production dispatch code. This follows the Fable recommendation of "grammar first, consumer second, dispatch third."
- **Ambiguity: JSON vs YAML for fixtures.** Decision: JSON. The existing bernie_scenarios uses YAML because those fixtures have rich initial_state, 	urns, and nested expect structures. Grammar replay fixtures are flat action lists — JSON is simpler and avoids adding PyYAML as an implicit dependency (the existing project already has it, but the new fixtures should not rely on it).
- **Ambiguity: should the loader validate that expected_tier matches verb descriptor?** Decision: no — that's what the test assertion does. The loader only validates structure and format, not semantic correctness. Semantic comparison happens in the replay engine.
- **Risk: fixture source field may be forgotten.** Mitigation: loader validates source == "authored_synthetic" and rejects any fixture with a different or missing source. This prevents accidental loading of non-synthetic data in future sprints.
- **H15 gate**: remains closed. No semantic appointment data, no patient/practitioner identifiers, no diary times, no raw trove content in fixtures. The fixtures contain only action verb names and expected consumer dispatch values.
- **No provider calls**: proven by the absence of any i_service import in the replay engine or tests. No monkeypatch guard needed (unlike the bernie_scenarios replay which has DB/HTTP routes that could theoretically trigger AI provider calls).
- **No DB/HTTP writes**: proven by the absence of any DB model imports, HTTP client imports, or route URL constants in the new replay code.

## Verification

`powershell
# Compile check
.venv\Scripts\python.exe -m py_compile tests\action_grammar_replay\loader.py tests\action_grammar_replay\replay.py tests\action_grammar_replay\test_grammar_replay.py

# Grammar replay consumer tests
.venv\Scripts\python.exe -m pytest tests\action_grammar_replay\ -v --tb=short -p no:randomly

# R29 grammar tests still pass
.venv\Scripts\python.exe -m pytest tests\test_diary_action_grammar.py -v --tb=short -p no:randomly

# Broader diary-domain regression (confirm_gate, confirm_actions, capabilities)
.venv\Scripts\python.exe -m pytest tests/test_diary_confirm_gate.py tests/test_diary_confirm_actions.py -v --tb=short -p no:randomly

# Whitespace hygiene
git diff --check

# Verify no production app/ changes
git diff --stat -- app/

# Verify no H-series references in new fixtures
Select-String -Path "tests\fixtures\action_grammar_replay\*.json" -Pattern "h_series|trove|large_unexplained_delta|no_structural_change|small_content_delta|time_grid_delta|pilot_0" | ForEach-Object { Write-Error "H-series reference found: " }
`

## Merge Criteria

1. All verification steps pass.
2. No pp/ files changed.
3. No existing test regressions.
4. The standalone synthetic-descriptor test proves consumer dispatch is independent of DIARY_ACTION_GRAMMAR identity.
5. All fixture source fields equal "authored_synthetic".
6. No H-series, trove, or raw-diary references in any new file.
7. git diff --check clean.
8. Ariadne has reviewed the diff and run verification.
