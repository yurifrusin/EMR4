# Reception One selected-appointment status-action composition closeout

Date: 2026-08-13

Timestamp: 2026-08-13T22:46:00+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33`

Result: `raisa_reception_one_selected_appointment_status_action_composition_pass`

## Outcome

Reception One can now apply one existing appointment-status transition to one
selected current appointment without leaving its focused projection. The new
modeless action panel uses the existing status vocabulary and delegates through
the existing `setAppointmentStatus` proposal/confirm interaction. It contains
no second command implementation and no raw-write fallback.

Committed outcomes trigger a fresh Diary read and rebuild of the current
projection. The selected card is rebound to fresh truth when it remains in
scope, or cleared with an explanation when it no longer does. Stale Back
history is discarded. Cancellation, blocking, stale rejection, failure and
mid-command interruption remain fail-closed and do not create a duplicate
command.

## Implementation

- `docs/diary/diary.js` owns one immutable shared status-option vocabulary,
  preserves the current `Confirmed` label, reports patient-free lifecycle
  phases and exposes a local bridge that resolves the exact current appointment
  before delegating to `setAppointmentStatus`.
- `docs/diary/meta-grid.js` renders the selected-appointment action, holds its
  busy/reconciliation latch, returns focus, suppresses competing workspace
  Escape handling while terminal confirmation owns Escape, and rebuilds from a
  fresh read after terminal outcomes.
- `docs/diary/meta-grid.css` and versioned Diary assets provide responsive,
  keyboard-visible desktop, tablet and phone behavior.
- `review/test_reception_one_status_action.py` proves route-intercepted safe,
  cancel, blocked, stale, interruption and responsive cases with authored-
  synthetic client fixtures.

## API Spine review

This is a consumer-only composition over the accepted status proposal/confirm
family. GraphQL remains read-only and unchanged; REST remains the existing
proposal/confirm command surface; the bridge performs no network operation.
There is no new OpenAPI operation, GraphQL mutation, adapter method, database
object or generated client to update. Backend authority, current-truth,
idempotency, audit and receipt ownership are unchanged.

## Verification

- The dedicated rendered acceptance passes 8/8 cases.
- The full native Diary browser suite passes 144/144 cases.
- The focused UI, API Spine, latch and regression packet passes 171/171 tests.
- The canonical fast profile passes Ruff, maintained-source compilation, its
  193/193 API Spine/handover/maintenance tests, Diary JavaScript syntax and Git
  whitespace.
- Direct JavaScript syntax checks pass for `diary.js` and `meta-grid.js`.
- Rendered in-app inspection passed at 1280x720, 768x1024 and 390x844 with no
  horizontal overflow, framework overlay, console error or warning.
- Typed evidence is schema-valid and bound to exact source
  `b6c6a983c4936c1f0bd5e9daf03924bbcd4ddd33`.

One rendered defect was found and repaired during the frozen loop: a refreshed
patient timeline could duplicate the possessive heading suffix. The repair is
covered by the final rendered and regression results.

Closeout validation also rejected the first Continuity projection because its
contract evidence was path-shaped rather than typed, then exposed stale
current-node assertions in two general baton/Compass tests. Those evidence-
wiring assertions were advanced without changing product source; the final
Continuity, baton and canonical gates pass.

## Next tranche

Run a fresh provider-free, read-only Compass and baton orientation over the
newly completed visible status-action seam. It may choose the next
dependency-satisfied product tranche already supported by repository evidence,
but it may not infer authority for another command family, event family,
patient channel, participant cohort or runtime.

Yuri's attention is not presently required.

## Claim boundary

This proves repository-local authored-synthetic client composition and
route-intercepted rendered behavior. It does not prove a backend, database,
deployed, production, real-user or patient-data operation. Protected evidence,
historical Diary/PHI, patient/product/clinical data, external patient channels,
source/watcher/persistence, providers/ADC, credentials/IAM/network, new routes
or command families, deployment, production, release, Pages and protected-ref
movement remain closed.
