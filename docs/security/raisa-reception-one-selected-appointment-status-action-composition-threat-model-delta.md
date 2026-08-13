# Reception One selected-appointment status-action threat-model delta

Date: 2026-08-13

Timestamp: 2026-08-13T21:51:25+10:00 (Australia/Brisbane)

Status: `frozen`

Parent authority: accepted visible native Diary status-confirm interaction and
post-CF-D2 programme orientation

## Changed surface

This tranche adds one internal staff affordance to Reception One. It does not
add write authority. The affordance delegates to the ordinary Diary's existing
status interaction, whose REST/OpenAPI proposal/confirm path and backend
transaction remain the sole owners of admission and commit.

## Threats and required controls

| Threat | Required control |
|---|---|
| Reception One becomes a second command implementation | The bridge validates only id and existing status vocabulary, resolves the current client appointment, and calls `setAppointmentStatus`; mechanically reject bridge-local `fetch`, `apiFetch`, proposal, confirm or raw compatibility mutation code. |
| A selected card or dropdown value is mistaken for current truth | Label selection as staff input, keep the old status until commit, and rebuild the exact projection after the ordinary Diary reload before showing success. |
| A stale or out-of-scope appointment is acted upon | Resolve the exact id from the current authoritative client snapshot immediately before delegation; fail closed when absent; rely on the backend's final practice/actor/current-truth recheck before commit. |
| A stale Back projection survives a committed status change | Clear projection history on commit and reconstruct the current root scope from fresh reads; reselect only the matching fresh appointment. |
| A terminal or warning change bypasses explicit confirmation | Reuse the existing status dialog and its signed proposal evidence unchanged; do not special-case a Reception One confirm path. |
| Escape closes Reception One behind the status dialog | Suppress the workspace-level Escape close while the existing modal is present; let the modal own cancellation and focus restoration. |
| Blur or visibility interruption starts duplicate work or loses the outcome | Latch one status action busy, start no second action, enter privacy mode, and reconcile after the one terminal result before enabling another action. |
| Failure or cancellation leaves optimistic status or ambiguous focus | Restore the prior visible value, report a patient-free blocked/cancelled/failed state, clear busy state and focus the initiating Reception One control. |
| Status feedback leaks patient information | Use fixed administrative status-only copy in the polite-live region; never copy proposal summaries, patient names, ids, reasons, raw errors, tokens or receipts into it. |
| Authored-synthetic browser proof is described as live | Mark interception as `route_intercepted_browser` and smoke rendering as `authored_synthetic_client_fixture`; make no live backend/database/provider claim. |

## API Spine preservation

The change is a REST-command UI consumer. GraphQL remains read-only. The
existing status proposal/confirm family retains actor, practice, confirmer,
freshness, version binding, idempotency, audit and receipt semantics. Events
remain optional acceleration hints and are not confirmation evidence.

## Residual boundary

Client freshness and good interaction design cannot make a stale command safe.
Correctness still comes from the backend's command-time authority and source-
truth recheck. This tranche proves only provider-free authored-synthetic client
composition. Real product operation, another status/command family, durable
event delivery, restart/unknown-commit handling, deployment and production
remain unproved and closed.
