# plan-codex-codex-bernie-confirmed-flow-review-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-confirmed-flow-review-harness` |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-confirmed-flow-review-harness` |
| Source Task | `codex-bernie-confirmed-flow-review-harness` |
| Status | pending_plan_review |
| Created | 2026-06-27 01:12 +1000 |
| Source HEAD | `54314fa` |

## Plan Summary

Sprint 45 Bernie confirmed full-flow review harness plan

## My Understanding

| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-confirmed-flow-review-harness` |

Build, after approval only, a deterministic backend review harness that exercises the full supervised Bernie path: command normalization, normalized slot search, supervised candidate selection, and explicit create confirmation. The harness should prove every pre-confirmation step is non-mutating, blocked/unconfirmed confirmation is non-mutating, successful confirmation creates exactly one appointment plus bounded audit evidence, and the chain never invokes Gemini/LLM/provider code.

## Intended Surface / Boundary

Tests/review-harness surface only. Expected affected surface is backend pytest coverage around appointment proposal endpoints (`/slot-search/normalize`, `/slot-search/normalized`, `/slot-search/selection`, `/create/confirm-bernie`). Visually adjacent but untouched surfaces: diary grid/cards/slots panels, taskpane, Command Centre, waiting room UI, booking modals, and any runtime/autonomous Bernie interface.

## Out Of Scope

No production/runtime expansion unless a tiny compatibility fix is strictly needed after approval and reported. No UI changes, no migrations, no autonomous booking, no new natural-language execution, no Gemini/LLM parsing, no SMS/billing/resource-admin work, no broad audit or appointment redesign, and no unrelated test hygiene.

## Files I Expect To Edit

Expected after approval: add one focused full-flow backend test module, likely `tests/test_bernie_confirmed_flow_review_harness.py`. Reuse existing helpers/patterns from `tests/test_bernie_slot_flow_review_harness.py`, `tests/test_bernie_confirm_create_proposal.py`, `tests/test_slot_search_normalized_execution.py`, `tests/test_slot_selection_proposal.py`, `tests/test_slot_search_proposal.py`, and `tests/test_appointment_proposals.py`. Production files should remain untouched unless a strict compatibility blocker appears.

## Implementation Steps

1. Reuse the existing deterministic fixtures and endpoint helpers for auth, row counts, and forbidden AI-provider guards.
2. Add a success-path full-chain test: normalize -> normalized search -> select first candidate -> assert no appointment/audit writes so far -> confirm true -> assert exactly one appointment and exactly one bounded audit row/evidence.
3. Add blocked/unconfirmed-path assertions in the same harness or focused tests: no writes when confirmation is false and no writes when confirmation revalidation is blocked, while preserving existing Sprint 40-44 contracts.
4. Add source/provider guard assertions to prove the full chain does not instantiate AI providers, call Gemini/generate_content, or perform autonomous natural-language execution.
5. Keep assertions compact and deterministic, avoiding UI/browser review and avoiding broad fixture churn.
6. Run the required focused verification suite and `git diff --check`, then submit for Ariadne review.

## Visual / Behavioural Acceptance Checks

The final implementation must demonstrate: pre-confirm normalize/search/select writes no appointments or audit rows; blocked or unconfirmed confirmation writes no appointment/audit rows; successful explicit confirmation writes exactly one appointment and one bounded audit row; audit evidence remains limited to expected Bernie/proposal evidence; no Gemini/LLM/provider calls occur; no UI/runtime behavior changes; all required focused tests pass.

## Risks / Ambiguities

The main risk is duplicating existing Sprint 43/44 tests instead of adding a coherent full-chain review harness; I will keep the new test focused on end-to-end evidence across steps. Another risk is brittle source-inspection assertions; I will prefer provider monkeypatch guards plus narrow source checks matching existing tests. If existing endpoint helpers already cover a case, I will reference/reuse rather than broadening production code.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
