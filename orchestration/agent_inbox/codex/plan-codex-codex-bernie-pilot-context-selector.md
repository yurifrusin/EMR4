# plan-codex-codex-bernie-pilot-context-selector

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-pilot-context-selector` |
| Source Task | `codex-bernie-pilot-context-selector` |
| Status | pending_plan_review |
| Created | 2026-06-27 09:57 +1000 |
| Source HEAD | `6befea1` |

## Plan Summary

Sprint 62 plan: Bernie pilot explicit context selector

## My Understanding

Role | codex-worker
Worker Name | Cicero
Worker Branch | codex/bernie-pilot-context-selector

I will add a narrow Bernie pilot readiness/context selector so ordinary staff-visible pilot mode cannot POST /appointments/proposals/bernie/supervised-booking until the user has explicitly provided a non-default practitioner and patient context. Smoke/dev/query harness paths may keep explicit harness defaults, but ordinary pilot mode must not silently use smoke/default identifiers and must not call confirm-Bernie before the approval checkbox is explicitly checked.

## Intended Surface / Boundary

Affected surface: docs/diary Bernie Pilot launch affordance, the Bernie Booking Review sidebar panel, and the small context/readiness controls inside that review/sidebar flow. Nearby surfaces that must not change: diary grid layout, appointment cards/slots, waiting room flow panel, status controls, booking modal, dev fixture selector semantics, taskpane, Command Centre, backend APIs, and live write routes.

## Out Of Scope

No backend changes, no config/auth changes, no patient search/autocomplete backend, no autonomous booking, no PHI, no provider/LLM calls, no taskpane/Command Centre/Office/resource admin/billing/SMS work, no live writes in tests, no broad diary redesign, and no unrelated test refactors.

## Files I Expect To Edit

Expected implementation files after approval only: docs/diary/diary.html for a minimal context selector/form container; docs/diary/diary.css for constrained Bernie context form styling; docs/diary/diary.js for context collection/readiness gating and supervised-booking payload construction; review/test_diary_smoke.py for route-intercepted acceptance checks; possibly review/checks_diary.json only if a stable structural smoke assertion is useful; docs/diary/diary.html cache-bust/version references if runtime assets require it. Plan-gate files now: orchestration/agent_inbox/codex/plan-codex-codex-bernie-pilot-context-selector.md and source packet status/notes only.

## Implementation Steps

1. Locate current Bernie pilot launch/readiness logic and preserve smoke/dev/query review behavior behind its existing explicit flags.
2. Add a small context selector/form in the Bernie review/sidebar flow that is shown for eligible ordinary pilot launch and asks for practitioner and patient identifiers before review preparation.
3. Make ordinary pilot mode treat empty, smoke-like, or default practitioner/patient identifiers as not ready; render blocked readiness evidence locally and return without POSTing supervised-booking.
4. Only after explicit non-default practitioner and patient context is supplied, build the supervised-booking request body with that context and POST to the existing route.
5. Keep confirm-Bernie disabled until the existing explicit approval checkbox is checked, and prove no confirm route is called before approval.
6. Add focused Playwright/pytest route-intercepted tests for missing context block, explicit non-default context success, no pre-approval confirm, and smoke/dev/query regression paths.
7. Run the required static/frontend/review checks and only then submit implementation after approval.

## Visual / Behavioural Acceptance Checks

Exact acceptance checks after approval: node --check docs/diary/diary.js; python scripts/check_frontend_versions.py if docs/diary asset references change; pytest review/test_diary_smoke.py -q focused to new Bernie tests first; pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q if focused checks pass; route-intercepted proof that ordinary pilot launch with missing practitioner/patient makes zero supervised-booking POSTs; route-intercepted proof that ordinary pilot launch with explicit non-default practitioner and patient makes exactly one supervised-booking POST carrying those identifiers; route-intercepted proof that confirm-Bernie POST count stays zero until the approval checkbox is checked; regression proof that existing smoke/dev/query Bernie review paths still render and use their allowed harness behavior; git diff --check.

## Risks / Ambiguities

Risks / ambiguities: the repo already has partial ordinary-mode missing-context guards, so the implementation must extend rather than bypass them; there may be no real patient search surface yet, so a typed non-PHI identifier field is likely safer than implying backend autocomplete; practitioner context can come from query/template columns or an explicit selector, but must not fall back to prac-1 in ordinary mode; patient context validation must distinguish smoke/default IDs without blocking legitimate future backend IDs accidentally; visual space in the diary header is tight, so the context controls should live in the Bernie sidebar/review flow rather than changing grid/slot layout; route interception must avoid real writes and should fail closed on unexpected POSTs.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
