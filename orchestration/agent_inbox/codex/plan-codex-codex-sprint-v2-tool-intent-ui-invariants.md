# plan-codex-codex-sprint-v2-tool-intent-ui-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-v2-tool-intent-ui-invariants` |
| Status | integrated |
| Created | 2026-07-04 06:19 +1000 |
| Source HEAD | `0297f3a` |

## Plan Summary

Protocol-stopped Codex worker Planck produced an invariant plan after `python` was blocked by the Windows app-execution alias in the Codex mirror. Ariadne captured the substantive plan here rather than asking the worker to work around the protocol failure.

## My Understanding

V2 wires Diary "Ask Bernie" to the V1 non-mutating tool-intent route for explicit appointment-extension requests. Friendly Bernie copy may explain or suggest, but it must never create write authority. Confirm controls may appear only when backend proposal evidence exists.

## Intended Surface / Boundary

Affected surface: `docs/diary/` Bernie panel, especially latest response, history, proposal rendering, and guarded appointment-extension confirmation.

Nearby surfaces not to change: diary grid geometry, booking modal create/edit flow, waiting-room panel, status controls, taskpane, Command Centre.

## Out Of Scope

Auto-mode writes, persisted PHI/session tables, GraphRAG retrieval changes, broad API rewrite, arbitrary move/create/status/write tool intents, and production edits by the Codex worker.

## Files I Expect To Edit

Likely implementation: `docs/diary/diary.js`, `docs/diary/diary.html`, `docs/diary/diary.css`, and `review/test_diary_smoke.py`.

Likely tests: existing Bernie/tool-intent backend tests, deterministic Diary smoke fixtures, frontend asset checks.

## Implementation Steps

1. Add a tool-intent call path from Ask Bernie when the text looks like an explicit appointment-extension request.
2. Send visible `diary_day_booking` context frames including `appointment_id`; do not infer hidden appointment ids from display text alone.
3. Render latest Bernie response states for `proposal_ready`, `clarification_required`, `blocked`/`unsupported`, and plain advisory outcomes.
4. Render extension proposal details only from backend `proposal`, not from model/staff text.
5. Show no confirm/update affordance unless the backend response contains a valid deterministic proposal contract.
6. Clear stale proposal/no-slot/booking-prep UI before each new Ask Bernie request and when date/room/context changes.
7. Preserve response history visibly, but ensure only the latest valid proposal can drive an actionable affordance.

## Visual / Behavioural Acceptance Checks

- Friendly text cannot create authority: phrases like "I can extend that" are display-only unless `proposal` exists.
- Staff text cannot smuggle authority: "confirm this now" in the prompt must not create confirm UI.
- No stale bleed: a prior booking/no-slot/proposal card must disappear when the next response is unsupported, ambiguous, blocked, or loading.
- Latest wins: history may remain visible, but old proposal controls must be inert or absent.
- Extension boundary: V2 supports extension proposal display only, not arbitrary move/create/status/write tools.
- One visible target only: ambiguous visible appointment matches must produce clarification, not proposal UI.
- No backend evidence, no confirm affordance.

## Recommended Tests

- `node --check docs\diary\diary.js`
- `.\.venv\Scripts\python.exe scripts\check_frontend_versions.py`
- `.\.venv\Scripts\pytest.exe tests\test_bernie_tool_intent.py tests\test_appointment_update_proposal.py tests\test_diary_confirm_gate.py -q`
- `.\.venv\Scripts\pytest.exe review\test_diary_smoke.py -q`
- Add or extend smoke cases for stale proposal clearing, unsupported request after proposal, ambiguous extension request, and history/latest separation.
- `git diff --check`

## Risks / Ambiguities

The worker could not run the formal plan/submit protocol because the `python` alias failed, so this packet is Ariadne-captured from the subagent notification. The implementation must still be reviewed through normal integration checks.

## Codex Plan Review

- Review result: Accepted as invariant guidance and folded into Ariadne's V2 implementation.
- Required changes before implementation: Use backend proposal evidence as the sole source of confirmability; do not let friendly copy or staff text create authority.
- Approved to proceed: implemented by Ariadne
