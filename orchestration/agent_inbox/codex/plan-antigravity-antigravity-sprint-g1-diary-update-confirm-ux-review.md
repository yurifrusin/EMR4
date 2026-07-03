# plan-antigravity-antigravity-sprint-g1-diary-update-confirm-ux-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-g1-diary-update-confirm-ux-review` |
| Status | integrated |
| Created | 2026-07-04 06:37 +1000 |
| Source HEAD | `5eb771b` |

## Plan Summary

Plan to move human UI and Bernie-authored appointment updates/extensions to a unified, evidence-gated confirmation flow. Human updates will POST to a confirmation endpoint (carrying signed proposal/freshness evidence) instead of direct bypassable PUT requests. Happy-path (safe, warning-free) moves will auto-confirm in the background to preserve a fast, modal-free UI. Bernie-authored extensions will use the same confirm schema.

## My Understanding

Currently, human Diary updates (e.g. resize, drag/drop) run a proposal check and then invoke direct PUT /appointments/{id}. Bernie extensions run tool-intent checks and invoke direct PUT /appointments/{id}. Neither flow enforces backend evidence/signature gating. We need to transition the client to obtain a proposal with confirm_payload/confirm_endpoint evidence and execute updates/extensions by POSTing the confirmed payload to confirm_endpoint, preventing direct PUT write bypass.

## Intended Surface / Boundary

The affected surfaces are the Diary grid slots and appointment cards (during drag/drop/resize), the human update confirmation overlay (identity-confirm-panel), and the Bernie review sidebar panel (specifically the tool intent proposal card and confirmation button). Nearby surfaces like waiting room columns, staff rosters, patient search, and consultation/billing panels must remain unaffected.

## Out Of Scope

Out of scope: Database schema mutations, backend implementation of the unified confirmation endpoint, Alembic migrations, GraphRAG or session table storage, and handling other appointment actions (like creation or deletion) beyond updates/extensions.

## Files I Expect To Edit

docs/diary/diary.js: Update handleMoveResize, showStatusProposalDialog, and confirmBernieToolIntentChange to support the unified confirm payload/endpoint contracts, including background auto-confirm for safe actions. docs/diary/diary.css: If styling is needed for staleness warnings or blocked states.

## Implementation Steps

1. Modify confirmBernieToolIntentChange to POST the confirmation payload to the returned confirm_endpoint. 2. Refactor handleMoveResize to execute proposal check, extract confirm_endpoint and confirm_payload, and perform background auto-confirmation if the proposal is safe (no warning, no block). 3. Update showStatusProposalDialog to consume structured review payloads, rendering blocks/warnings properly, disabling confirm buttons when blocked, and POSTing to confirm_endpoint on confirm click. 4. Implement staleness and conflict alerts (e.g. 409 conflict, 404 slot-taken).

## Visual / Behavioural Acceptance Checks

1. Safe human drag/drop or resize updates the diary instantly without showing a modal, and network traffic confirms it went through the confirm endpoint. 2. Conflicting human moves trigger the confirmation modal showing warnings; clicking Cancel snaps the card back to its original slot. 3. Blocked human moves render a blocked overlay dialog with explanation copy and only a 'Close' button. 4. Bernie-authored extensions render a proposal card with a 'Confirm change' button, and clicking it POSTs to the confirm endpoint. 5. Stale proposals display a warning and disable the confirmation button.

## Risks / Ambiguities

1. Latency: Sequential HTTP calls (proposal check followed by confirm write) for every single drag/drop could introduce minor latency; mitigated by optimistic UI and loading states. 2. Backward compatibility: We must mock or handle fallbacks if backend integration is running in parallel and not yet ready.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
