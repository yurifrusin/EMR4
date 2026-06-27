# plan-codex-codex-bernie-interpret-review-ui-adapter

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Role | codex-worker |
| Worker Name | Cicero |
| Worker Branch | `codex/bernie-interpret-review-ui-adapter` |
| Branch | `codex/bernie-interpret-review-ui-adapter` |
| Source Task | `codex-bernie-interpret-review-ui-adapter` |
| Status | integrated |
| Created | 2026-06-27 12:49 +1000 |
| Source HEAD | `ad6f8f0` |

## Plan Summary

Plan Bernie interpret review UI adapter

## My Understanding

Role codex-worker; Worker Name Cicero; Worker Branch codex/bernie-interpret-review-ui-adapter. I will connect a structured Bernie booking-instruction interpretation envelope into the existing dev/pilot supervised Bernie review panel so staff can see interpreted intent before the existing supervised booking review. The implementation should use fake/mocked or route-intercepted data only, stay behind existing smoke/dev/pilot gates, and must not enable live provider calls, autonomous booking, backend writes, or backend changes.

## Intended Surface / Boundary

Only the diary Bernie supervised review surface is affected: the small right/sidebar Bernie Booking Review panel and its dev/pilot launch flow in docs/diary. The diary grid, booking slot cards, waiting room/flow panel, appointment cards, taskpane, Command Centre, Word surfaces, backend appointment contracts, and existing confirm-Bernie approval path must not visually or behaviorally change except for the added interpreted-intent preview inside the Bernie review panel before supervised review content.

## Out Of Scope

No app/ backend edits, no migrations, no live Gemini/Vertex/provider calls, no service-account/auth setup, no production default exposure, no autonomous appointment creation, no direct appointment/proposal/confirm writes, no changes to slot-search or supervised-booking backend contracts, no broad diary redesign, no taskpane/Command Centre/Word changes, and no runtime docs/config changes beyond necessary asset version bumps if runtime assets change after approval.

## Files I Expect To Edit

Expected after approval: docs/diary/diary.js for query-gated mocked/route-interceptable interpretation envelope request/normalization and render hooks; docs/diary/diary.html only if a tiny static placeholder/control is cleaner than dynamic DOM creation; docs/diary/diary.css only if a compact interpreted-intent panel needs styling; review/test_diary_smoke.py for route-intercepted Playwright checks. No production-code edits during this plan gate.

## Implementation Steps

1. Re-read the current Bernie pilot/dev review path and choose the narrowest hook before loadBernieLiveReview/initBernieReview posts supervised-booking. 2. Add a dev/pilot-gated interpretation preview adapter that accepts a structured envelope from mocked fixtures or an intercepted endpoint only after explicit launch/context, normalizes interpreted/clarification/blocked states, and renders it at the top of the existing Bernie review panel. 3. Preserve existing supervised-booking request shape and confirm-Bernie checkbox/write gating; do not call confirm-Bernie until explicit approval. 4. Keep default diary loads hidden/no-call, and ensure non-dev/non-pilot URLs do not expose the control or request interpretation. 5. Add route-intercepted review harness coverage for interpreted, clarification, and blocked interpretation states, plus no-live-provider/no-write assertions and existing dev/query review regression checks. 6. Run node --check on changed JS, targeted pytest review checks, frontend version integrity if assets change, and git diff hygiene.

## Visual / Behavioural Acceptance Checks

Visual/behavioural checks: the interpreted intent appears only inside the Bernie Booking Review panel, above or immediately before supervised booking review content; blocked/clarification states are clearly review-only and prevent supervised review progression where appropriate; interpreted state can precede existing candidate/confirmation review without changing slot cards or diary grid layout; launch requires explicit smoke/dev/pilot context; route intercepts prove no live provider endpoint is called and no confirm-Bernie POST occurs before checkbox approval; existing blocked/candidate/confirmation_ready review states and ordinary pilot context behaviour continue to pass.

## Risks / Ambiguities

Ambiguity: the exact frontend URL/endpoint name for the interpretation envelope may not yet exist, so I will prefer a clearly dev-gated mocked/route-interceptable adapter rather than inventing a backend contract. Risk: adding another preview area could visually crowd the review panel, so styling should be compact and isolated. Risk: current smoke/dev review already has several gates; tests must prove the new interpretation request does not fire on default diary load or bypass real-context protection. Dissent: if Ariadne wants zero new runtime URL parameters, this can be implemented purely as a test-intercepted pilot branch instead, but a dev flag is more inspectable.

## Codex Plan Review

- Review result: Accepted; scoped to gated diary Bernie review UI and deterministic route-intercepted tests.
- Required changes before implementation: None.
- Approved to proceed: yes
