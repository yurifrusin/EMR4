# Provider-free visible native Diary status-confirm wiring closeout

Date: 2026-08-13

Timestamp: 2026-08-13T15:42:33+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `bed49be3d78d79207857b3d3a044cebd334112dc`

Result: `raisa_provider_free_visible_native_diary_status_confirm_wiring_pass`

## Outcome

Reception One's existing staff appointment-status selector now presents the
accepted proposal/confirm command honestly. A routine safe status change checks
and saves without an extra dialog. Warning-tier and terminal changes show one
labelled dialog with the exact old-to-requested transition and explain that
current authority and current booking truth will be checked again on confirm.
A blocked proposal offers no commit action.

The selector is disabled and marked busy while a change is pending. Cancellation,
Escape, a stale proposal or a confirm rejection restores the prior displayed
status and reports that no change occurred. A successful command reloads Diary
truth and reports the committed status. The dialog contains keyboard focus,
Escape cancels, and focus returns to the initiating selector. The status and
error surfaces are explicit accessible live regions.

The native client still has no raw appointment-status fallback. The accepted
canonical `POST /api/v1/appointments/proposals/status/confirm` family remains
the only status commit path used by this control; the server still owns current
authority, current source truth, idempotency, audit, receipt and commit.

## Evidence

- The closed typed evidence records the authored-synthetic smoke client,
  `route_intercepted_browser` and repository-regression modes separately.
- The safe Booked-to-Arrived path commits with zero dialog; the terminal
  Arrived-to-Cancelled path exposes one confirmation dialog and the final
  current-truth boundary.
- Desktop 1280×720, tablet 768×1024 and phone 390×844 renders keep the dialog
  visible and usable. Escape restores the exact selector and its prior value.
- Browser console warning/error count is zero; no screenshot or browser state
  was persisted.
- Four focused route-intercepted status cases pass: safe signed confirmation,
  stale confirm rejection, terminal Escape/focus restoration and blocked
  no-commit.
- The complete native Diary browser review passes 144/144.
- The focused contract/API/security/latch packet passes 81/81.
- The canonical fast profile passes 193/193, together with Ruff, maintained
  Python source compilation, Diary JavaScript syntax and Git whitespace.

The sanitized result is
`orchestration/continuity/raisa-provider-free-visible-native-diary-status-confirm-wiring/visible-status-confirm-evidence.json`.

## Issues resolved

One historical security test still assumed that all seven existing confirm
callers invoked the endpoint allowlist inline. The source already had six
inline callers and one caller that first stored the allowlisted path; the test
now accounts for both forms and also rejects a direct unvalidated
`confirmEndpoint` call.

The first interactive reload retained the earlier JavaScript asset in the
local browser cache. The current source was rerun from a fresh loopback origin,
after which all transaction markers, live copy and responsive views passed.
Both task-owned local servers were stopped and the browser viewport and tabs
were cleaned up. Neither issue changed product authority or required a source
contract recovery.

## Claim boundary and next work

The smoke rendering proves authored-synthetic client behavior. The intercepted
browser cases prove exact UI request/response handling, not a live backend.
The already accepted source `b414eb256853c301099d9cf7797a69cd3ec077c5`
separately proves the canonical local HTTP/PostgreSQL status command. This
tranche does not prove real product-data operation, another command family,
restart/unknown-commit recovery, deployment or production.

The visible consumer boundary now makes the next planned durability step
specific. Under standing uninterrupted-development authority, the next safe
tranche is a fresh provider-free CF-D2 observability-first durable event/cue
plan. It must treat events only as acceleration hints, preserve command-time
current-truth correctness, define the smallest cues, positions, lag,
reconciliation and operator evidence the visible status flow needs, and open no
watcher runtime, database/source access or product data while the plan is being
frozen.

External patient clients/channels, real identity, other commands, product or
patient data, providers/ADC, credentials/IAM, external network, operational
watchers, deployment, production, release, Pages and protected refs remain
closed. `docs/branding/` and every unrelated untracked file remain preserved.
