# plan-codex-codex-bernie-wrapper-confirmation-review-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-wrapper-confirmation-review-harness` |
| Branch | `codex/bernie-wrapper-confirmation-review-harness` |
| Source Task | `codex-bernie-wrapper-confirmation-review-harness` |
| Status | pending_plan_review |
| Created | 2026-06-27 02:13 +1000 |
| Source HEAD | `a1844f6` |

## Plan Summary

Plan deterministic Bernie wrapper confirmation review harness

## My Understanding

Role codex-worker; Worker Name Cicero; Worker Branch codex/bernie-wrapper-confirmation-review-harness. Sprint 47 should add a deterministic backend-only review harness proving Sprint 46 supervised Bernie wrapper confirmation_ready output can be explicitly confirmed through the existing confirm-Bernie endpoint. The success path must require confirmed=true and produce exactly one appointment plus bounded audit evidence; confirmed=false, stale/conflicting evidence, candidate_selection_required, blocked normalization, and any non-ready wrapper output must remain non-mutating. The harness must also prove no LLM/provider calls happen.

## Intended Surface / Boundary

Backend appointments proposal/review harness only. Expected affected surface after approval is pytest coverage around /appointments/proposals/bernie/supervised-booking and /appointments/proposals/create/confirm-bernie, likely through FastAPI TestClient and existing test fixtures. The visual/UX surfaces named in the packet are deliberately not affected: diary grid, booking slot rendering, appointment cards, stacking/overlap lanes, panels, waiting room/status UI, taskpane, and Command Centre must not change.

## Out Of Scope

No production code during the plan gate. After approval: no diary UI, taskpane, Command Centre, natural-language parsing, autonomous runtime execution, new write routes, schema redesign, migrations, SMS, billing, resource admin, broad appointment/audit redesign, or Sprint 40-46 semantic changes unless the focused harness exposes a verified contract bug requiring a tiny production fix.

## Files I Expect To Edit

Expected after approval: add or update a focused backend test/review harness, likely tests/test_bernie_wrapper_confirmation_review_harness.py. I may read adjacent tests such as tests/test_bernie_supervised_booking_wrapper.py, tests/test_bernie_confirm_create_proposal.py, tests/test_bernie_confirmed_flow_review_harness.py, and appointment fixtures. Production files are not expected to change; if a real contract gap appears, any tiny fix would likely be confined to app/routers/appointments.py or app/schemas/appointments.py and would trigger the expanded adjacent regression set.

## Implementation Steps

1. Inspect the existing wrapper, confirm-Bernie, and Sprint 45 flow harness tests to reuse fixtures/helpers instead of inventing a parallel path.
2. Add a deterministic wrapper-to-confirm review harness that calls supervised-booking, asserts confirmation_ready evidence, then posts that evidence to confirm-Bernie with confirmed=true and proves exactly one appointment plus exactly one expected audit/write trail.
3. Add negative cases for confirmed=false, stale conflict revalidation, candidate_selection_required, blocked normalization, and non-confirmation-ready evidence, each asserting zero appointment writes and zero audit mutations.
4. Add a no-LLM/provider guard by monkeypatching provider/LLM entry points to fail if touched, while keeping the route path deterministic.
5. Keep production code unchanged unless the harness reveals a genuine contract gap; if so, make the smallest backend-only fix and expand adjacent regression tests accordingly.
6. Run py_compile for touched Python/tests, the focused new pytest, existing wrapper/confirm/confirmed-flow suites, adjacent slot-search/selection/create-proposal tests if production code changes, and git diff --check.

## Visual / Behavioural Acceptance Checks

Plan-gate acceptance: plan packet exists at orchestration/agent_inbox/codex/plan-codex-codex-bernie-wrapper-confirmation-review-harness.md and includes Role codex-worker, Worker Name Cicero, and Worker Branch codex/bernie-wrapper-confirmation-review-harness. Implementation acceptance after approval: wrapper confirmation_ready evidence can be explicitly confirmed through confirm-Bernie only with confirmed=true; candidate-only, blocked, stale/conflicting, and confirmed=false paths are non-mutating; success creates exactly one appointment and expected audit evidence; no LLM/provider call is possible; no UI/visual surface changes occur.

## Risks / Ambiguities

The main ambiguity is whether existing confirm-Bernie accepts the wrapper evidence shape directly or requires minor evidence-shape adaptation. If the shape is incompatible, I will treat that as a contract gap only if the existing Sprint 46/Sprint 44 semantics imply direct compatibility. Counting audit writes may depend on existing fixture helpers; I will prefer existing audit assertions to avoid brittle implementation-detail coupling. No dissent with the task direction.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
