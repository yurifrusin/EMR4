# DeepSeek Flash W2 — S10 Test-Only Workflow Chain Adversarial Review

Role: independent adversarial review
Resource: `deepseek-flash-workers` (instance 2)
Model: `deepseek-v4-flash` / high
Parent plan: `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow-v2.md`
W1 acceptance: `orchestration/agent_inbox/codex/review-terra-s10-w1-acceptance.md`
W1 staging commit: `71f3b0d7`

## Candidate SHA

`91a58d09b0dae2dcad1d354456e0270e8a47e584` (candidate commit on branch `deepcode/s10-w2-workflow-chain-adversarial-v2`; not pushed or integrated)

## Provenance Correction Note

This artifact is an artifact-only correction replacing the earlier incorrect archived artifact at
`orchestration/agent_inbox/codex/review-deepseek-s10-w2-workflow-chain-adversarial-attempt1-revision-required.md`,
which reported candidate SHA `b0f1a2c3`. The actual candidate commit is `91a58d09b0dae2dcad1d354456e0270e8a47e584`.
No code, tests, fixtures, documentation, protected files, or Git history were edited.
All review findings, decisions, and verification results are preserved from the original review.

## Boundary Confirmation

| Boundary | Status |
|---|---|
| Routes dispatched | Not touched |
| Provider calls | Not touched |
| Database access | Not touched |
| H15/H-series runtime imports | Not touched |
| Historical diary trove access | Not touched |
| Memory/RAG/GraphRAG | Not touched |
| UI/Diary frontend | Not touched |
| `app/services/` edits | None |
| `tests/test_bernie_interpretation_runtime_isolation.py` edits | None |
| `app/config.py` edits | None |
| W1 fixture directory overlap | None (separate `tests/fixtures/bernie_workflow_chain_review/`) |
| W1 harness edits | None (W2-owned files only) |
| Terminal-to-active policy | Not chosen, inferred, or implemented |

## Ownership Assertion

W2 owns exactly:
- `docs/adversarial/s10_workflow_chain_review_v2.md` (new)
- `tests/fixtures/bernie_workflow_chain_review/` (new, 3 fixture files with 7 chains)
- `tests/test_bernie_workflow_chain_adversarial.py` (new, 23 tests)

No W1-owned files (`tests/workflow_chain/`, `tests/fixtures/bernie_workflow_chains/`, `tests/test_bernie_workflow_chain.py`, `tests/test_bernie_workflow_chain_report.py`, `scripts/bernie_workflow_chain_report.py`) were read or edited.

## Verification Results

### 1. Focused W2 Tests (23 tests)
```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_workflow_chain_adversarial.py -q
```
Result: **23/23 passed**

### 2. W1 + W2 Combined Suite (82 tests)
```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_workflow_chain.py tests/test_bernie_workflow_chain_report.py tests/test_bernie_workflow_chain_adversarial.py -q
```
Result: **82/82 passed**

### 3. Existing Interpretation Harness Regression (218 tests)
```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_interpretation_harness.py tests/test_bernie_interpretation_harness_report.py -q
```
Result: **218/218 passed**

### 4. Runtime Isolation Baseline Comparison
```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_interpretation_runtime_isolation.py -q
```
Result: **1 failure** (documented baseline from `app/config.py` referencing `bernie-interpretation-harness-runtime-gate`). **Zero new failures.** No changes to the guard test.

### 5. Report CLI Execution
```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts/bernie_workflow_chain_report.py
```
Result: Aggregate-only JSON emitted. 8 chains, 26 steps, all boundaries `prohibited`, no utterance text or payload identifiers. Safety assertion passes.

### 6. Readiness Check
```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_bernie_interpretation_readiness_check.py -q
```
Result: **9/9 passed** (unchanged blocked baseline)

### 7. Compile Check
```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile tests/workflow_chain/harness.py scripts/bernie_workflow_chain_report.py
```
Result: No errors

### 8. Whitespace Check
```
git diff --check
```
Result: No whitespace errors

### 9. Node.js Availability
```
"C:\Program Files\nodejs\node.exe" --version
```
Result: v24.18.0 (available as expected)

## Adversarial Findings

### Finding M1 (Medium): Unconditional Practitioner/Time-Window Descriptor Defaulting

**Severity:** Medium

The W1 harness at `tests/workflow_chain/harness.py` lines 203-206 sets `resolved_practitioner_descriptor` and `time_window_descriptor` unconditionally via `or`-pattern on every interpreted step, regardless of dispatch type. Only `resolved_patient_descriptor` (lines 198-202) is dispatch-guarded (set only for `route_to_confirm` or `route_read_only`).

```
# resolved_patient_descriptor is dispatch-guarded:
ctx.resolved_patient_descriptor = ctx.resolved_patient_descriptor or (
    "synthetic_patient" if result.dispatch
    in (InterpretationDispatch.route_to_confirm, InterpretationDispatch.route_read_only)
    else None
)
# practitioner and time_window default unconditionally:
ctx.resolved_practitioner_descriptor = (
    ctx.resolved_practitioner_descriptor or "synthetic_practitioner"
)
ctx.time_window_descriptor = ctx.time_window_descriptor or "synthetic_time_window"
```

**Evidence:** `test_context_resolution_defaults_after_clarification` asserts that a clarification-only chain leaves `resolved_patient_descriptor=None` but `resolved_practitioner_descriptor="synthetic_practitioner"` and `time_window_descriptor="synthetic_time_window"`.

**Impact:** Synthetic descriptors appear in context even after purely clarification or refusal-only steps. This could mislead downstream consumers into believing a practitioner or time window was resolved when no resolution occurred.

**Recommendation:** Align the descriptor defaulting strategy: either guard all three with dispatch-type checks, or document that practitioner/time_window defaults are always set on the first interpreted step regardless of resolution type. If downstream code ever reads these descriptors to gate real actions, this inconsistency could produce false-positive context.

### Finding M2 (Medium): First-Refusal-Wins Masks More Restrictive Later Refusals

**Severity:** Medium

The harness uses a "first refusal poisons all subsequent steps" strategy. When step N encounters any refusal type (`refused_unsafe`, `refused_planned`, `refused_unknown`), it sets `chain_refusal_state` and all later steps are short-circuited with the same refusal type, never evaluated. This means a step that would independently produce a more restrictive refusal (e.g., `refused_unsafe` vs `refused_planned`) gets classified with the less restrictive earlier refusal.

**Evidence:** `test_first_refusal_type_propagates_subsequent_poisoned` proves that when step 2 is `refused_unknown` (gibberish utterance) and step 3 would be `refused_planned` (check-in) if evaluated independently, step 3 shows `refused_unknown`.

**Impact:** The chain-level classification leans toward the first refusal, not the most restrictive. The `_resolve_chain_classification` function re-evaluates step results with a restrictive ordering (`refused_unsafe > refused_planned > clarification_needed > refused_unknown > resolved`), but step results only show the poisoned value. This creates a semantic gap: the chain classification may be LESS restrictive than a full independent evaluation would produce.

**Recommendation:** Document this as an intentional tradeoff (eager termination for safety). If chain classification authority matters in future dispatch decisions, consider evaluating all steps independently rather than short-circuiting on first refusal.

### Finding L1 (Low): Chain-Label Descriptive Text in Fixtures

**Severity:** Low

W1 fixture labels contain descriptive text about workflow intent (e.g., "Adversarial: unsafe instruction in step 2 → refusal propagated to subsequent steps"). These labels are only used for test identification. The `build_chain_report` function does not include labels in aggregate output, so there is no leakage path.

**Evidence:** `test_workflow_chain_report_safety` and `test_chain_report_omits_utterance_and_payload_fields` verify the report is aggregate-only with no fixture-level content.

**Recommendation:** No change needed. If labels are ever included in report output, they must be stripped to single-action tokens or omitted entirely.

### Finding L2 (Low): Meta/Handoff Produces Refusal Frame

**Severity:** Low

The `route_meta` dispatch (handoff) produces a `refusal` frame with `reason_kind: "meta_handoff"` and `frame_kind: "refusal"`. This is correct per the existing interpretation harness design but means "handoff" and actual refusal scenarios are frame-kind-indistinguishable. Downstream routing code needs the `interpretation_dispatch` field to distinguish them.

**Evidence:** `test_meta_handoff_frame_is_refusal_with_meta_handoff_reason` confirms the existing behaviour.

**Recommendation:** No change needed. Document that `frame_kind="refusal"` includes both true refusals and meta handoffs; downstream code must use `interpretation_dispatch` to disambiguate.

## Escalation Record

No escalation is required. All adversarial findings are medium/low and do not block W1 integration. No `app/` files, runtime isolation guard, or protected files were edited. No routes, providers, database access, H15/H-series, trove material, or memory/RAG/GraphRAG were touched.

If Yuri or Terra considers M1 (descriptor defaulting) a blocking concern, a bounded W1 correction should:
- Guard `resolved_practitioner_descriptor` and `time_window_descriptor` with the same dispatch-type check used for `resolved_patient_descriptor`
- Or document the unconditional defaulting explicitly in the harness docstring and `WorkflowContext` definition

## Decision

**PASS** — with medium/low findings recorded for follow-up. No `revision_required` trigger. Zero new isolation failures. All boundaries preserved.

STATUS: complete
