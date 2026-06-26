# plan-codex-codex-bernie-slot-flow-review-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-slot-flow-review-harness` |
| Branch | `codex/bernie-slot-flow-review-harness` |
| Source Task | `codex-bernie-slot-flow-review-harness` |
| Status | pending_plan_review |
| Created | 2026-06-27 00:20 +1000 |
| Source HEAD | `7ef4713` |

## Plan Summary

Deterministic backend Bernie slot flow review harness

## My Understanding

Build a focused deterministic review harness for Bernie command normalization, normalized slot search, and slot-selection proposal flow before any final booking write bridge exists. The harness should prove the chain is non-mutating, avoids appointment/audit writes, and does not call Gemini/LLM/provider code.

## Intended Surface / Boundary

Backend test/review harness only around Bernie slot-flow endpoints and helpers. Affected product surface is API contract confidence for command-normalize-search-select; visually adjacent surfaces such as diary cards, slots in the diary grid, taskpane panels, Command Centre, waiting room, and booking status UI must not change.

## Out Of Scope

Diary UI, taskpane, Command Centre, Gemini/LLM parsing, autonomous runtime, final appointment write/confirmation bridge, audit mutation, migrations, billing, SMS, resource admin, broad refactors, unrelated test hygiene, and any master/handoff integration.

## Files I Expect To Edit

Expected after approval: tests/test_bernie_slot_flow_review_harness.py or the nearest existing Bernie endpoint test module; possibly tiny test fixtures/helpers only. Production app files only if a small testability-only helper extraction is strictly required and justified.

## Implementation Steps

1. Inspect existing Bernie normalize/search/select endpoint tests and fixtures. 2. Add deterministic fixtures for appointment slots/resources/patients without external provider calls. 3. Cover successful normalize -> normalized search -> slot selection proposal chain. 4. Cover no-match/conflict/unbookable paths. 5. Assert no appointment rows, audit rows, final booking writes, or LLM/provider calls occur. 6. Keep assertions structural and compact so the harness can run cheaply in future review loops. 7. Run focused pytest, py_compile for touched Python, and git diff --check.

## Visual / Behavioural Acceptance Checks

Focused backend tests pass; harness demonstrates normalized command input can produce search results and a proposal without mutating appointment/audit state or invoking LLM/provider code; conflict/no-match paths are deterministic; product behaviour and frontend surfaces remain unchanged.

## Risks / Ambiguities

Existing endpoint boundaries may already require DB fixture setup or dependency overrides; if no clean public endpoint chain exists, I will prefer test-only helpers over production refactors. Any production touch must be minimal and reported. Ambiguity: exact audit table/model used by Bernie flow will be confirmed before implementation.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
