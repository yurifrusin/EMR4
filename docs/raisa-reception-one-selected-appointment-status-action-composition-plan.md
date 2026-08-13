# Reception One selected-appointment status-action composition plan

Date: 2026-08-13

Timestamp: 2026-08-13T21:51:25+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_execution`

Task baseline: `9a1401665bc6163145bbcbbb53d06ce3f4abd036`

Target result: `raisa_reception_one_selected_appointment_status_action_composition_pass`

Reasoning level: High. The accepted orientation has already selected this
user-visible behaviour. This plan freezes its narrow implementation and
evidence boundary without revising API or authority semantics.

## Objective

Let an internal staff user select one current appointment in a focused
Reception One projection, choose one existing Diary status and submit that
choice through the ordinary native Diary's existing `setAppointmentStatus`
interaction.

Reception One remains a projection and interaction surface. The existing
status proposal/confirm family remains the only commit path, and the backend
continues to own practice and actor authority, current source truth,
proposal admission, warnings and blocks, confirmation evidence, idempotency,
audit, receipt and atomic commit.

## Boundary classification

- **Read surface:** the existing scoped appointment snapshot and a fresh
  post-action projection read.
- **Command surface:** the existing REST/OpenAPI appointment-status
  proposal/confirm interaction only.
- **UI composition:** a modeless selected-appointment status action within
  Reception One and a small same-page bridge to the existing interaction.
- **Not opened:** GraphQL mutation, new REST route, raw compatibility write,
  database object, event delivery, provider, external patient client or new
  command family.

## Frozen implementation

1. Reuse one shared client status-option helper for the ordinary Diary and
   Reception One. Its values remain exactly `Booked`, `Arrived`, `InConsult`,
   `Completed`, `Cancelled`, `NoShow` and `DNA`; retain `Confirmed` only when it
   is the current accepted status, matching the existing ordinary control.
2. Keep appointment selection separate from action. Only one current
   non-synthetic-placeholder appointment may be selected; the status action
   names no patient and is unavailable when the bridge cannot resolve the
   exact appointment from the current authoritative client snapshot.
3. Add one bridge operation that validates the appointment id and requested
   status, resolves the exact current appointment, and delegates to
   `setAppointmentStatus`. It must contain no `fetch`, proposal, confirm,
   compatibility-route or mutation implementation of its own.
4. Present a modeless status selector and explicit `Review status change`
   button for the selected appointment. A status choice is staff input only;
   the visible action stays disabled when no real transition is selected or
   another status transaction is in progress.
5. Surface the existing transaction phases in Reception One through an
   administrative, patient-free polite-live region: checking, confirmation
   required, saving, cancelled, blocked, stale/failure and committed.
6. Preserve the ordinary status dialog for warning-tier and terminal changes.
   Its focus containment, Escape cancellation, explicit confirm button and
   current-authority/current-truth explanation remain authoritative. Reception
   One's own Escape handler must not close the workspace while that dialog is
   open.
7. On every non-commit outcome, retain the selected current appointment,
   restore its displayed status and return focus to the initiating control.
   On success, reload the ordinary Diary, rebuild the exact current Reception
   One projection, discard stale Back history, re-resolve the selected
   appointment and show only the freshly read status. If the appointment is no
   longer in scope, clear selection and explain that result.
8. During blur or visibility interruption, enable privacy and allow the one
   already-started interaction to reach its existing terminal result; start no
   second action. Reconcile from a fresh projection before any later action.
9. Add responsive styling only for the new modeless action panel at the
   existing desktop, tablet and phone breakpoints. No wider visual redesign.

## Acceptance scenarios

The authored-synthetic provider-free packet must prove:

1. **Safe transition:** select one appointment, choose `Arrived`, submit, see
   no extra dialog, observe one existing proposal/confirm sequence, then see a
   fresh selected card with committed `Arrived` status.
2. **Terminal cancellation:** choose `Cancelled`, observe the existing labelled
   dialog, press Escape or Cancel, commit nothing, retain the old status and
   selected appointment, and restore focus inside Reception One.
3. **Blocked proposal:** the existing blocked proposal displays no confirm
   action; closing it leaves current status unchanged and reports `blocked`.
4. **Stale/current-truth rejection:** a confirm rejection or stale result
   commits nothing, restores the current displayed status and reports that no
   change occurred; no raw fallback request is made.
5. **Interruption:** blur or visibility loss during the one in-flight action
   exposes no patient details, starts no duplicate command and requires fresh
   reconciliation before another action.
6. **Responsive and keyboard:** desktop 1280x720, tablet 768x1024 and phone
   390x844 keep the selected-card action usable; selection, selector, button,
   dialog, Escape and focus return work from the keyboard.

Intercepted browser cases are labelled `route_intercepted_browser`, never
live. Smoke rendering is labelled `authored_synthetic_client_fixture`.
Repository/API Spine/static checks prove delegation and closed surfaces; they
do not prove live product operation.

## Verification

- Add deterministic source guards for the exact shared vocabulary, bridge
  delegation, no bridge-local network/write, phase feedback, reconciliation,
  focus and interruption rules.
- Add a task-scoped real-browser route-intercepted acceptance driver with
  sanitized typed evidence and no saved credentials, headers, traces or
  patient/product data.
- Run the complete existing native Diary/Reception One browser packet affected
  by the change, the status-confirm/API Spine/security packet, JavaScript
  syntax, canonical fast profile and Git whitespace.
- Do not run PostgreSQL, provider, external network, product source or
  deployment actions for this tranche.

## Recovery and stop

Correct mechanical selector, focus, styling, request-fixture or evidence
defects inside this boundary and rerun the affected deterministic cases. Stop
only if implementation would require a new route/command/status value, real
data, database/source access, provider use, protected evidence, deployment or
a non-inferable user-owned interaction choice.

## Closed surfaces

No FastAPI, GraphQL, OpenAPI, database/migration/RLS, event/cue runtime,
watcher, product/patient/clinical data, historical Diary/PHI, external patient
identity/client/channel, provider/ADC, credential/IAM/network, executable
model tool, new command/write, deployment, production, release, Pages or
protected-ref action is opened. `docs/branding/` and every unrelated untracked
file remain preserved; staging is explicit-path only.
