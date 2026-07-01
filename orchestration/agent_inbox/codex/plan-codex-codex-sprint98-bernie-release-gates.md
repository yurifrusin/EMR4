# plan-codex-codex-sprint98-bernie-release-gates

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint98-bernie-release-gates` |
| Source Task | `codex-sprint98-bernie-release-gates` |
| Status | integrated |
| Created | 2026-07-01 12:17 +1000 |
| Source HEAD | `ca8b293` |

## Plan Summary

Plan Sprint 98 Bernie release gates for practitioner-id leaks, slot-change path, and generic confirm Not Found failures

## My Understanding

Sprint 98 needs release gates, independent of the backend/UI implementation branches, that would have blocked the exact screenshot regressions Yuri reported after Sprint 97: the ordinary Margaret Thompson / Dr Shera flow surfaced raw Missing Practitioner Id even though Dr Shera was resolved, the receptionist had no clear path back from a staged/selected slot to choose another slot, and Confirm booking failed as a generic Not Found instead of a typed/reception-safe failure. The gate must preserve the existing distinction between route-intercepted/smoke checks and live checks, and must treat the ordinary prompt as blocking release evidence.

## Intended Surface / Boundary

Primary surface: release/review gates for Bernie booking, spanning backend contract tests, deterministic Diary smoke harness checks, smoke interpreter script assertions, and release-gate documentation. Affected behaviour vocabulary is limited to the Bernie panel, candidate booking slots, staged proposed appointment card, and Confirm booking action. Nearby surfaces that must not change: main diary grid geometry/stacking, waiting room cards/status controls, appointment create/edit modal, taskpane/Command Centre, and production backend/UI implementation files until implementation is explicitly approved.

## Out Of Scope

No production backend fixes, no Diary UI implementation, no GraphQL/API-spine work, no migrations, no broad architecture rewrite, no live phone/Medicare/OPV/PVM integration, and no attempt to mark route-intercepted checks as live. The plan should not depend on Claude or Antigravity implementation details beyond their public contracts.

## Files I Expect To Edit

Likely touched after approval: orchestration/bernie_release_gates.md to extend the standing gate with Sprint 98 screenshot blockers; review/test_diary_smoke.py to add route-intercepted end-to-end Diary assertions for ordinary prompt -> candidates -> choose slot -> change slot -> confirm; possibly review/checks_diary.json only if a declarative check is better than code; scripts/smoke_bernie_interpreter.py and tests/test_smoke_bernie_interpreter_script.py to add expectation flags for resolved practitioner/patient IDs without leaking UUIDs; a focused new backend test file such as tests/test_bernie_sprint98_release_gates.py, or small additions to tests/test_bernie_supervised_booking_wrapper.py and tests/test_bernie_confirm_create_proposal.py, to assert typed failure envelopes and no generic 404/Not Found on malformed/stale confirm payloads; orchestration/sprint_closeout.md only at integration closeout.

## Implementation Steps

1. Add a Sprint 98 section to bernie_release_gates.md naming the three screenshot blockers as closeout blockers: raw missing_practitioner_id after practitioner evidence/name resolution, no change-slot affordance/path after selecting a candidate, and generic Not Found from Confirm booking.
2. Add a backend contract gate for the ordinary prompt pipeline using deterministic/fake provider data: resolved Dr Shera must carry a real practitioner_id into normalized/supervised booking; if a practitioner is resolved in evidence, missing_practitioner_id must not be shown in staff_review blocks or ordinary-mode copy. Assert no appointment/audit mutation until confirm.
3. Add a confirm endpoint gate that posts stale, missing, or invalid confirm payloads through the real FastAPI route and asserts a typed 200/4xx envelope or structured detail appropriate to the API contract, never bare {detail: Not Found} and never raw internal IDs/codes in the staff-facing review path. Include a success path that still writes exactly one appointment.
4. Add a route-intercepted Diary smoke test for the exact receptionist loop: open Bernie, submit the Margaret Thompson / Dr Shera ordinary prompt, assert identity/practitioner evidence is human-readable, assert no raw UUID/snake_case Missing Practitioner Id leak, click a candidate, assert staged proposed appointment card and Confirm booking are visible, use the planned Change/Back/choose-another-slot path, assert candidates reappear and a different candidate can be selected, then intercept confirm to assert the UI calls the configured confirm endpoint and renders typed success/failure copy rather than generic Not Found.
5. Extend smoke_bernie_interpreter only for non-mutating interpreter assertions: add optional expectations such as --expect-practitioner-id-present and --expect-patient-id-present while continuing to redact compact output. Do not make it search slots or confirm bookings.
6. Document closeout commands separating deterministic route-intercepted checks from live checks: targeted backend pytest, smoke interpreter fake/provider readiness, node --check for diary JS when UI changes land, full review/test_diary_smoke.py, frontend version/deploy checks, and one residual live Diary check only for non-intercepted deployed browser/backend/provider behaviour.
7. CI/local review should fail on generic Not Found and raw ID leaks via explicit text-negative assertions: no visible 'Missing Practitioner Id' in resolved-practitioner confirmation/candidate states, no visible 'practitioner_id', UUID pattern, or bare 'Not Found' in ordinary receptionist panel/card failure states.

## Visual / Behavioural Acceptance Checks

Blocking deterministic checks: focused pytest proves resolved Dr Shera cannot regress to missing_practitioner_id in the wrapper/review contract; confirm-bernie malformed/stale paths return typed safe failure and no writes, while valid confirm writes one appointment; smoke_bernie_interpreter fake prompt parses 14:00-15:45 and can assert resolved IDs without printing them. Blocking route-intercepted UI checks: review/test_diary_smoke.py proves the ordinary prompt renders candidate slots, selecting a booking slot stages the proposed appointment card, a visible path returns to candidate choice, choosing another slot updates the staged card, Confirm booking calls /api/v1/appointments/proposals/create/confirm-bernie, and ordinary UI never shows raw UUIDs, 'practitioner_id', snake_case missing_practitioner_id, or generic Not Found. Live checks: only a clearly labelled non-intercepted deployed/local Diary check can be called live; if it cannot be run, closeout must say live readiness not proven and cannot use route-intercepted evidence as a substitute. Merge criteria: plan remains release-gate/test/docs only, does not implement backend/UI fixes, and would have blocked the three Yuri screenshot failures before closeout.

## Risks / Ambiguities

The route-intercepted UI gate may need stable selectors for the slot-change affordance that the UI worker has not yet implemented; the release-gate worker should phrase selectors around intended data-testid names and adjust after implementation review. Backend confirm failure semantics may be 200 safe=false or a structured 4xx; Ariadne should choose one accepted contract before approving implementation to avoid brittle tests. Live provider/provider-backed evidence can remain flaky due to credentials/quota, so deterministic gates must block screenshot regressions while live checks are labelled readiness evidence, not a replacement for route/backend contract coverage. There is a small risk of overlap if this worker edits review/test_diary_smoke.py while Antigravity also edits it; keep changes narrowly in new tests/helpers and let Ariadne integrate conflicts.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
