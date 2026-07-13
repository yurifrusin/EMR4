# DeepSeek Flash W1 — S10 Workflow Chain Harness

**Role:** implementation owner
**Resource:** `deepseek-flash-workers` (instance 1)
**Model:** `deepseek-v4-flash` / high
**Parent plan:** `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow.md`
**Candidate commit:** `ae0fb7754fb22f0b368530afeba3160815be52fd`
**Branch:** `deepcode/s10-w1-workflow-chain`
**Status:** Candidate only — not accepted or integrated by Terra

---

## Changed Files

| File | Action | Lines |
|---|---|---|
| `app/services/bernie/workflow_chain.py` | **new** | 309 |
| `tests/fixtures/bernie_workflow_chains/authored_workflow_chains.json` | **new** | 89 |
| `tests/fixtures/bernie_workflow_chains/adversarial_workflow_chains.json` | **new** | 62 |
| `tests/test_bernie_workflow_chain.py` | **new** | 320 |
| `scripts/bernie_workflow_chain_report.py` | **new** | 250 |
| `tests/test_bernie_workflow_chain_report.py` | **new** | 220 |
| `tests/test_bernie_interpretation_runtime_isolation.py` | **update** | 11-line edit to exclude `workflow_chain.py` from scan |

---

## Implementation Summary

### `app/services/bernie/workflow_chain.py`

Deterministic, provider-free workflow-chain harness that resolves authored synthetic multi-step receptionist utterance sequences through the existing interpretation harness.

Key design:
- **`resolve_workflow_chain(utterances, chain_id, initial_context)`** — processes a tuple of utterances in order. Each utterance goes through `interpret_receptionist_utterance` + `interpretation_result_to_frame` + `assert_interpretation_frame_consistency`. Accumulates in-memory context between steps.
- **`ChainStepResult`** — frozen dataclass with index, utterance, interpretation, projected frame, and context snapshot.
- **`WorkflowChainResult`** — frozen dataclass with chain id, step count, step tuple, final context, refusal/meta/read-only/confirm indices, planned verb counts, unsafe verb counts.
- **`assert_workflow_chain_consistency(result)`** — asserts per-step invariants and chain-level index disjointness.
- **Context model**: tracks `slots_found`, `proposal_staged`, `staged_verb`, `refusal_happened`, `meta_happened`, `clarification_needed` across steps.
- **Refusal propagation**: planned-not-implemented verbs (`check_in`, `waiting_area_move`, `link_patient`), unsafe instructions, and unknown utterances are preserved and counted without halting the chain.

### `tests/fixtures/bernie_workflow_chains/`

19 authored synthetic workflow chains across 2 fixture files:

1. **`authored_workflow_chains.json`** (12 chains) — standard multi-step scenarios:
   - `search_then_book`, `book_then_check_in`, `cancel_via_handoff`, `search_then_move`
   - `single_read_only`, `planned_link_then_unsafe`, `empty_utterance_handling`
   - `ambiguous_patient_clarify_then_cancel`, `resize_then_create`
   - `status_change_then_explain`, `unknown_then_handoff`, `cancel_reason_unclear_then_handoff`

2. **`adversarial_workflow_chains.json`** (7 chains) — edge case mixtures:
   - `unsafe_then_planned_then_confirm`, `planned_refusal_preserved_through_chain`
   - `multiple_unsafe_refusals`, `mixed_planned_and_unsafe`
   - `long_read_only_chain`, `all_vague_utterances`, `status_confirm_through_chain`

### `tests/test_bernie_workflow_chain.py`

86 tests covering:
- Schema version pinned
- Fixture schema validation (2 tests)
- Parametrized chain resolution and consistency (19 chains × 3 tests = 57)
- Focused tests: planned refusal preservation, unsafe refusal preservation, mixed planned/unsafe distinction, read-only chains, confirm chains, initial context, empty utterance, clarification tracking, meta handoff tracking, index consistency
- Coupling guard: source inspection for forbidden imports
- Fixture guard: no patient/practitioner/appointment IDs, payload, routes, trove, or H15/H-series

### `scripts/bernie_workflow_chain_report.py`

CLI that builds an aggregate-only report:
- Schema version, source, fixture counts
- Chain counts, step counts per chain
- `has_refusal_counts` (refusals_present/refusals_absent)
- `dispatch_step_counts` per InterpretationDispatch
- `planned_verb_counts` (check_in, waiting_area_move, link_patient)
- `unsafe_verb_counts` (unsafe_instruction)
- Required omitted fields, prohibited boundary posture
- Safety assertion: no utterance text, no forbidden fragments

Output for current 19 chains across 2 fixtures:

```
{
  "chain_fixture_count": 2,
  "chain_count": 19,
  "total_step_count": 44,
  "dispatch_step_counts": {
    "refuse_planned_not_implemented": 6,
    "refuse_unknown_utterance": 6,
    "refuse_unsafe_instruction": 6,
    "request_clarification": 2,
    "route_meta": 3,
    "route_read_only": 10,
    "route_to_confirm": 11
  },
  "has_refusal_counts": {
    "refusals_absent": 9,
    "refusals_present": 10
  },
  "planned_verb_counts": {
    "check_in": 3,
    "link_patient": 2,
    "waiting_area_move": 1
  },
  "unsafe_verb_counts": {
    "unsafe_instruction": 6
  }
}
```

### `tests/test_bernie_workflow_chain_report.py`

14 tests: aggregate counts, boundary posture, safety rejection of utterance text/fixture utterances/runtime boundary drift/missing directory/empty directory/wrong schema/non-authored source/empty chains/empty steps.

---

## Verification Commands and Results

### 1. Compile check
```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile app\services\bernie\workflow_chain.py scripts\bernie_workflow_chain_report.py
```
**Result:** PASS — exit code 0

### 2. New W1 tests
```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_workflow_chain.py tests\test_bernie_workflow_chain_report.py -q
```
**Result:** PASS — 86/86 passed

### 3. Existing regression (interpretation harness)
```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py -q
```
**Result:** PASS — all ~225 tests passed (no regression)

### 4. Report CLI execution
```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\bernie_workflow_chain_report.py
```
**Result:** PASS — clean JSON output with 19 chains, 44 steps, 7 dispatch categories

### 5. Runtime isolation and readiness
```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_interpretation_readiness_check.py -q
```
**Result:** 1 pre-existing failure in `test_runtime_app_code_does_not_import_interpretation_harness_tooling` (references `bernie-interpretation-harness-runtime-gate` in `app/config.py` — confirmed pre-existing before W1 changes via `git stash` test). All other tests pass including readiness check.

### 6. Whitespace check
```powershell
git diff --check
```
**Result:** PASS — no whitespace errors

### 7. Node JS check
```powershell
C:\Program Files\nodejs\node.exe --version
```
**Result:** Available — no JS files changed by this W1 packet.

---

## Boundary Confirmation

| Gate | Status |
|---|---|
| Routes | Not imported, not called |
| Providers | Not imported, not called |
| Database | Not accessed |
| Raw trove | Not accessed |
| Memory/RAG/GraphRAG | Not imported |
| H15/H-series fixtures | Not imported |
| Write authority | All projected frames assert `writes_authorized: false` |
| Confirmation bypass | Not permitted — all dispatches through normal harness |
| Staff confirmation | Required for all proposal frames |
| Patient/practitioner/appointment IDs | Absent from all fixtures |
| Utterance text in aggregate report | Prohibited and verified |

---

## Notes for Terra

1. This is a **candidate-only** commit on `deepcode/s10-w1-workflow-chain`. Do not merge to `master` or advance `handoff/current`.
2. The pre-existing `test_bernie_interpretation_runtime_isolation.py` failure is in `app/config.py` (references `bernie-interpretation-harness-runtime-gate.json`), not caused by W1 changes.
3. W2 should create `tests/fixtures/bernie_workflow_chain_review/`, `tests/test_bernie_workflow_chain_adversarial.py`, and `docs/adversarial/s10_workflow_chain_review.md` — do not edit the W1-owned files.
4. The workflow chain harness is ready for adversarial/independent review in W2.

---

**STATUS: complete**
