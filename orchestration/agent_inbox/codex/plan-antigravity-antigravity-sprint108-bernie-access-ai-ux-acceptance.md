# plan-antigravity-antigravity-sprint108-bernie-access-ai-ux-acceptance

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint108-bernie-access-ai-ux-acceptance` |
| Status | pending_plan_review |
| Created | 2026-07-06 23:51 +1000 |
| Source HEAD | `7581696f` |

## Plan Summary

Sprint 108: Minimal staff-visible acceptance coverage for Bernie booking-instruction interpretation routed through Access AI, ensuring honest provider labeling in debug modes and calm, no-write copy in ordinary modes.

## My Understanding

Under Sprint 108, we must ensure that Bernie's booking-instruction interpretation routed through Access AI (the single backend entry point) preserves honest provider, mode, and live_provider labeling in the user interface (when debug/dev parameters are enabled).
We also need to guarantee that staff-visible outputs in the main UI remain calm, do not call route-intercepted or fake-provider flows live under ordinary conditions, and never imply booking completion or availability unless evidence exists.
Specifically, the rendering of the `bernie-interpret-provider` element (which only displays when `bernie_debug=true` or `bernie_dev_review=true`) should accurately display both the `provider` name and the `mode` plus the `live_provider` status rather than using mode as the provider name.

## Intended Surface / Boundary

- **Diary Side Panel UI (docs/diary/diary.js)**: Modify the rendering of the provider metadata element (`.bernie-interpret-provider`) to honestly reflect both the provider name and the mode.
- **Review Harness (review/test_diary_smoke.py)**: Add a deterministic route-intercepted test verifying the correct rendering of the honest provider/mode/live_provider label when debug parameters are active.
- **Nearby surfaces**: Nearby surfaces like the main diary grid, patient flow cards, and modal inputs are unaffected.

## Out Of Scope

- No changes to backend route/schema logic.
- No enabling of live providers or external patient clients.
- No mutations to appointment or diary DB tables.
- No RAG/GraphRAG or H15 database queries.

## Files I Expect To Edit

- [docs/diary/diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js)
- [review/test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)
- [docs/diary/diary.html](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.html) (for cache-busting asset versions)

## Implementation Steps

1. **Diary JS Update**: In `docs/diary/diary.js`, locate `renderBernieInterpretPreview` where `metadata` is processed. Update the string formatting for `provider.textContent` to show:
   `Provider: ${metadata.provider || "fake"} (${metadata.mode || "mocked"}${metadata.live_provider ? " live" : " non-live"})`
2. **Diary HTML Cache Buster**: In `docs/diary/diary.html`, bump the asset cache-buster version for `diary.js` to ensure the new rendering takes effect immediately.
3. **Write/Extend Review Test**: Add a test in `review/test_diary_smoke.py` called `test_bernie_debug_provider_metadata_honest`. This test will navigate to the diary with `bernie_debug=true`, intercept `/interpret-booking-instruction` to return mock provider metadata, submit a dummy instruction, and assert that `bernie-interpret-provider` is visible and matches the expected format showing the provider name and live status.

## Visual / Behavioural Acceptance Checks

- When `bernie_debug` is not in the URL parameters, the provider debug block is hidden.
- When `bernie_debug=true` or `bernie_dev_review=true` is set, the debug block appears with the exact formatted text: e.g. "Provider: fake (mocked non-live)" or "Provider: gemini_vertex (live live)".
- The main receptionist instruction entry and confirmation flow remain functional, calm, and do not make unintended live-provider calls.

## Risks / Ambiguities

- We must make sure the test does not require a live network connection or attempt to call GCP APIs. This is mitigated by route interception.
- Playwright is not pre-installed in the local virtual environment. This limits our ability to run `review/test_diary_smoke.py` locally without installing playwright. Since we are in the plan phase, we will request permission to install playwright or run check validation.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
