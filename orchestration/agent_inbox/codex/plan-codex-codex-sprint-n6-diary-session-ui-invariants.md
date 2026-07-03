# plan-codex-codex-sprint-n6-diary-session-ui-invariants

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/current` |
| Source Task | `codex-sprint-n6-diary-session-ui-invariants` |
| Status | integrated |
| Created | 2026-07-03 22:47 +1000 |
| Source HEAD | `6ec3298` |

## Plan Summary

Plan focused N6 Diary session UI invariants and review harness checks

## My Understanding

Sprint N6 should make the Diary Bernie panel render from the N5 server-owned session endpoint without letting browser memory become authority. Antigravity owns the primary UI implementation in docs/diary/diary.js; this Codex worker lane owns invariant review points and focused deterministic harness additions. The plan should prove active-session/new-session/refetch/append wiring remains presentational, stale 409 conflicts are visible and recoverable, idempotent retry is not shown as duplicate conversation truth, confirm evidence survives the session-render path, and browser storage does not persist PHI or session authority.

## Intended Surface / Boundary

Affected surface for the later implementation is the Bernie panel inside the native Diary page, especially docs/diary/diary.js state/session helpers and the route-intercepted review harness in review/test_diary_smoke.py. Visually adjacent surfaces that must not change: the diary grid appointment cards, booking modal, waiting-area/status tabs, time ruler, room/location selectors, taskpane, Command Centre, and backend session/confirm route contracts except for reading existing endpoint shape.

## Out Of Scope

No production code during this plan gate. Later implementation should not own Antigravity's main UI composition, CSS redesign, diary.html layout, backend route/schema changes, database migrations, GraphRAG/practice-knowledge wiring, auto-mode, taskpane/Command Centre behavior, appointment write endpoints, or broad live-provider testing. Existing localStorage uses for auth token and non-PHI UI preferences are not part of this lane unless new session/PHI authority storage is introduced.

## Files I Expect To Edit

Expected later edits: review/test_diary_smoke.py for route-intercepted server-session invariants; optionally a tiny helper/checklist artifact under orchestration/agent_inbox/codex if Ariadne wants review notes. docs/diary/diary.js is review target and may need only narrow testability hooks or data-testid additions after plan approval; primary UI implementation remains Antigravity's lane. No app/, migrations, diary.html/css, taskpane, or Command Centre files unless Ariadne explicitly expands scope.

## Implementation Steps

1. Review Antigravity's approved N6 UI plan/submission before coding and mark overlap boundaries. 2. Add route-intercepted smoke cases for GET /api/v1/appointments/bernie/sessions/active, POST /new, and POST /{session_id}/events with captured request bodies. 3. Assert active-session load renders latest server session/events while empty local client state cannot invent session_id, revision, confirm readiness, or transcript turns. 4. Assert append requests echo the server session_id, surface_id, expected_revision, event_id/idempotency_key, and PHI-minimised payloads; raw instruction/patient name must not be sent to the session event endpoint. 5. Add stale 409 case for stale_session_revision: visible calm conflict/refetch copy, confirm action suppressed or disabled, refetch/new-session path available, and the current server snapshot replaces stale UI state. 6. Add idempotent retry case: replay of the same idempotency key/result renders one logical staff/Bernie turn and does not duplicate chat bubbles, pending spinners, or confirmations. 7. Add confirm evidence preservation case: a server-rendered confirmation_ready snapshot keeps confirm_endpoint, confirm_payload, turn_ref/freshness ids/signed evidence fields through render and into the confirm POST unchanged except confirmed=true. 8. Add storage assertions using page.evaluate over localStorage/sessionStorage keys and values after session render/append/conflict: fail if raw PHI-like names/instructions, session revision, confirm payload/evidence, or authoritative session snapshots are persisted. 9. Keep checks structural and route-intercepted; use selectors/data-testid and captured network bodies, not broad screenshots. 10. Run static and smoke verification and record any Antigravity overlap for Ariadne.

## Visual / Behavioural Acceptance Checks

Plan acceptance: complements Antigravity by owning invariant tests/review harness rather than UI implementation. Later implementation acceptance: node --check docs/diary/diary.js passes; pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q passes; targeted N5 backend route regressions pass if any endpoint assumptions change; git diff --check passes; storage assertions prove no new localStorage/sessionStorage PHI/session authority; route captures prove expected_revision/idempotency and confirm evidence preservation; stale 409 UX is visible/recoverable without permitting confirm from stale evidence.

## Risks / Ambiguities

The current diary has a substantial client-side BernieSession class and existing localStorage for token/location/break UI preferences, so tests must distinguish allowed existing storage from forbidden PHI/session authority. If Antigravity changes selectors or DOM shape, harness checks may need a small data-testid coordination pass. The N5 endpoint event payload deliberately rejects raw_instruction, so the UI may need a separate non-PHI event reference model; this lane should flag any need for backend changes instead of making them. Confirm evidence can be nested and versioned, so preservation checks should compare captured payload fields rather than fragile full-object text.

## Codex Plan Review

- Review result: Accepted and integrated locally by Ariadne.
- Required changes before implementation: Coordinate with the amended Antigravity plan so the harness verifies PHI-minimised server-session participation without requiring server-rendered transcripts before server outcome events exist.
- Approved to proceed: yes.
