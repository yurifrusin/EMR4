# plan-codex-codex-bernie-supervised-review-payload-contract

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-supervised-review-payload` |
| Branch | `codex/bernie-supervised-review-payload` |
| Source Task | `codex-bernie-supervised-review-payload-contract` |
| Status | pending_plan_review |
| Created | 2026-06-27 02:33 +1000 |
| Source HEAD | `89096d6` |

## Plan Summary

Plan deterministic Bernie supervised review payload

## My Understanding

| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | codex/bernie-supervised-review-payload |

I need to add, after explicit approval, a deterministic backend-only staff-review payload for the supervised Bernie booking wrapper. The payload should summarize wrapper outcomes for later reception/UI review without creating appointments, writing audit rows before confirmation, or calling Gemini/LLM/provider code. It must preserve the existing wrapper discriminators and Sprint 40-47 contracts while adding stable review fields for blocked, candidate_selection_required, and confirmation_ready outcomes.

## Intended Surface / Boundary

Backend contract surface only: appointment/Bernie schemas, router/service/helper code that builds wrapper responses, and focused backend tests. The affected product surface is the future staff-review data contract returned by the backend; no visual diary cards, panels, waiting-room rows, taskpane views, Command Centre windows, or diary grid/booking-slot rendering will change in this sprint.

## Out Of Scope

Diary UI, taskpane, Command Centre, natural-language parsing, Gemini/LLM/provider calls, autonomous execution, direct appointment writes outside the existing explicit confirm-Bernie path, migrations unless a truly unavoidable schema need appears, SMS, billing, resource admin, broad appointment redesign, and changes to the confirm-Bernie write contract.

## Files I Expect To Edit

Likely: app/schemas/appointments.py, app/routers/appointments.py, and/or a small existing appointment/Bernie helper module if the wrapper logic is already factored there; tests/test_bernie_supervised_booking_wrapper.py plus a focused new or updated Bernie supervised review payload test. Possibly adjacent tests/test_bernie_wrapper_confirmation_review_harness.py only if the payload needs compatibility assertions. I do not expect to edit frontend files, migrations, taskpane/diary assets, or runtime docs.

## Implementation Steps

1. Inspect existing Bernie wrapper, selection, create-proposal, and confirm-Bernie schemas/tests to identify the current response discriminators and evidence payloads.
2. Define a compact deterministic review payload shape that is additive and stable: headline/status, staff_action_required, selected/candidate slot summary, warnings/evidence summary, confirmation readiness, and confirm payload/evidence when applicable.
3. Thread the review payload into supervised wrapper outcomes for blocked, candidate_selection_required, and confirmation_ready without changing existing discriminators or confirm-Bernie input/write semantics.
4. Add focused tests for all three outcomes proving payload shape, no appointment/audit mutation before explicit confirmation, no LLM/provider calls, confirmation-ready evidence compatibility, and preservation of existing result fields.
5. Rerun focused Bernie wrapper/confirmation test suites plus py_compile/git diff checks listed in the packet.

## Visual / Behavioural Acceptance Checks

Behavioural checks only, not visual UI checks: blocked outcomes expose a clear non-actionable review payload with warnings/evidence and no confirm payload; candidate_selection_required outcomes expose candidate slot summaries and staff action to select/confirm a slot; confirmation_ready outcomes expose selected slot summary, readiness=true, and the exact confirm payload/evidence required by the existing confirm-Bernie endpoint. Existing response discriminators remain unchanged. No diary grid cards, booking-slot visuals, stacking, waiting-room status panels, taskpane, or Command Centre behaviour changes.

## Risks / Ambiguities

Main ambiguity is whether to place the review payload as an additive field on every wrapper result or as a helper-derived field only on specific outcome models; I will choose the smallest additive schema that keeps backward compatibility. Another risk is duplicating confirm payload evidence instead of referencing the existing create-proposal/confirmation evidence cleanly; tests should pin compatibility without reshaping confirm-Bernie. If current wrapper code is not well factored, I will keep extraction minimal and avoid broad appointment refactors.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
