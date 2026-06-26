# plan-codex-codex-bernie-pilot-launch-context-guard

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-pilot-launch-context-guard` |
| Source Task | `codex-bernie-pilot-launch-context-guard` |
| Status | pending_plan_review |
| Created | 2026-06-27 09:29 +1000 |
| Source HEAD | `bf987c8` |

## Plan Summary

Cicero plan: fail-closed Bernie pilot launch context guard

## My Understanding

| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | codex/bernie-pilot-launch-context-guard |

The current Bernie staff-visible pilot launcher can show an eligible launch button and then POST `/appointments/proposals/bernie/supervised-booking` using fallback `practitioner_id=prac-1`, `patient_id=smoke-pat-1`, and a default reference date when ordinary staff context is absent. I will harden the frontend so ordinary pilot mode derives launch context from real diary state only and fails closed with a clear readiness/blocked message when practitioner or patient context is missing. Smoke/dev/query review paths may keep explicit fixture defaults, but normal staff-visible pilot mode must never synthesize smoke identifiers or call supervised-booking until real context is present. Confirm-Bernie remains a separate explicit approval step after a valid staff review.

## Intended Surface / Boundary

Affected surface: the diary Bernie supervised review sidebar/pilot launch path in `docs/diary/diary.html`, `docs/diary/diary.js`, and narrow diary CSS if a readiness banner needs styling. Nearby surfaces that must not change: diary grid slot/card layout, waiting-room/patient-flow panels, booking create/edit modal, appointment status controls, roster/resource admin, taskpane/Command Centre, backend routes, auth/config, migrations, and live booking write endpoints. Review harness changes will be limited to deterministic Playwright assertions in `review/test_diary_smoke.py` for Bernie launcher/readiness/write gating.

## Out Of Scope

No backend changes, no config/auth changes, no new live write path, no autonomous booking, no provider/LLM calls, no PHI, no taskpane/Command Centre/Office/resource admin/billing/SMS work, no diary grid visual redesign, no booking modal/status/waiting-room behaviour changes except any labels needed inside the Bernie sidebar/launcher readiness state.

## Files I Expect To Edit

Expected implementation files after approval: `docs/diary/diary.js`; possibly `docs/diary/diary.html` only if an extra static test id/readiness container is needed; possibly `docs/diary/diary.css` only for small Bernie readiness/banner styling; `review/test_diary_smoke.py` for focused deterministic tests. Plan-gate-only files now: `orchestration/agent_inbox/codex/codex-bernie-pilot-launch-context-guard.md` status/completion notes and the generated Codex plan/review packet.

## Implementation Steps

1. Introduce a small Bernie pilot context resolver that separates ordinary mode from explicit dev/smoke/query review mode; ordinary mode must return only real diary context and mark missing practitioner/patient/reference context as not ready.
2. Replace the fallback defaults in `loadBernieLiveReview()` and the `initBernieReview()` live path with the resolver so default `prac-1`, `smoke-pat-1`, and hard-coded reference date are allowed only in explicit smoke/dev/query harness paths, not ordinary pilot launch.
3. Render an eligible-but-context-missing readiness/blocked sidebar message with no confirm controls and no supervised-booking POST; keep the launch button visible only when eligibility allows, but make the panel explain what context staff must select/load.
4. Preserve explicit dev review behaviour: `bernie_dev_review=true` and smoke fixture/query harness URLs should continue to POST when explicit practitioner/patient/candidate parameters are supplied, and existing fixture states should remain read-only/confirm-gated.
5. Add focused Playwright tests proving ordinary eligible launch with missing context does not call supervised-booking or confirm-Bernie, does not use smoke/default identifiers, labels the state clearly, and still requires approval before confirm in valid explicit dev/smoke review paths.
6. Run the packet verification commands and inspect any failures without widening scope.

## Visual / Behavioural Acceptance Checks

Exact checks after implementation approval: `node --check docs/diary/diary.js`; `python scripts/check_frontend_versions.py` if `docs/diary/*.html|css|js` deployed asset references change; `pytest review/test_diary_smoke.py -q` or focused Bernie tests first then full `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`; `git diff --check`. Behavioural acceptance: in ordinary staff-visible pilot mode, clicking Bernie Pilot when real context is missing shows a clear readiness/blocked message, leaves confirm controls absent/disabled, sends zero supervised-booking requests, sends zero confirm-Bernie requests, and never emits `prac-1` or `smoke-pat-*` identifiers. Explicit smoke/dev/query review paths with provided IDs still work. Confirm-Bernie POST occurs only after the approval checkbox is checked and the confirm button is clicked.

## Risks / Ambiguities

Risk: the current diary may not yet expose a stable real selected patient/practitioner context for ordinary Bernie launch, so the safest implementation may be deliberately fail-closed until Ariadne assigns a later context-selection sprint. Risk: existing harnesses intentionally use smoke IDs; tests must distinguish explicit smoke/dev fixtures from ordinary pilot mode so legitimate review coverage is not removed. Risk: changing shared render functions could accidentally affect the review sidebar visual states; keep changes narrow and assert nearby blocked/candidate/confirmation states still render. Ambiguity: whether a practitioner-only context is ever sufficient; I will require all identifiers needed by supervised-booking before POSTing rather than guessing.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
