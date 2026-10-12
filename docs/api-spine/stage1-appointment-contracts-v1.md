# Stage 1 appointment contract convergence — inert source candidate

This is a synthetic, source-only contract proposal. It does not mount a route,
authenticate a person, query an appointment, invoke a model, or authorise a
write. The accepted `appointment.list_projection.v1` functions and example keep
their original wire shape and behavior. The new list v2 and move intent v1
require separate admission and integration before product use.

## Existing command authority remains separate

Patient request submission, staff create confirmation, and staff move
confirmation are three distinct decisions. The existing backend
`/api/v1/appointments/proposals/create` and
`/api/v1/appointments/proposals/create/confirm` form the create path;
`/api/v1/appointments/proposals/update/{appointment_id}` and
`/api/v1/appointments/proposals/update/confirm` form the update path. This
candidate creates no command endpoint. The future move adapter may submit only
an explicitly chosen date and local start time to the existing update proposal
path, then let the authenticated backend perform its own current-state,
availability, signed-confirmation, idempotency and transaction checks. It must
never use the raw compatibility PUT as an equivalent confirmation route.

`AppointmentMoveTimeIntentIn` is a closed transport shape for the intended
delta: version, tenant/actor/role, selected appointment identity, source state
version, query source revision, target date/local start, and `proposal_only`.
Extra patient, practitioner, type, duration, location, notes, status, command,
route or write fields are rejected. The separate trusted context supplied by a
future server adapter contains the selected appointment's current identity,
status, date/local start, patient, practitioner, type, duration, location,
source revision, state version, capture/as-of instants and practice timezone.
`validate_move_intent` requires exact actor, tenant, appointment and revision
association; a source no older than 300 seconds; a `Booked` or `Confirmed`
appointment; valid date and local clock; a changed time coordinate; and a
synthetic timezone from `Australia/Brisbane` or `Australia/Sydney`.
`move_review(raw, trusted_context)` revalidates and emits before, after and
unchanged facts from a frozen validated snapshot, with disabled command
affordances. Invalid input
raises a fixed non-disclosing code and releases no partial review.

The pure move intent is **not** a current-availability result or confirmation.
`source_state_version` identifies the selected appointment revision;
`source_revision` identifies the associated read source and has different
meaning. Neither is inferred from an audit-count event revision. A later
server adapter must resolve the local clock in the practice timezone, including
daylight-saving ambiguity or gaps; re-fetch the selected row; preserve its ID
and non-time fields; verify actor/tenant authority; use the supported
self-overlap rule; and reconcile an uncertain command/result before retrying.
The review text explicitly says availability and source state may change.

## Exact lifecycle vocabulary

The domain statuses are `Booked`, `Confirmed`, `Arrived`, `InConsult`,
`Completed`, `Cancelled`, `NoShow`, and `DNA`. `domain_status` accepts only these
exact names. The existing `reception.one.bureau.plan-input.v1` accepts only
`booked`, `arrived`, `completed`, and `dna`; `bureau_status` maps only `Booked`,
`Arrived`, `Completed`, and `DNA` respectively. Other domain states, including
`Cancelled`, fail closed with `STATUS_UNSUPPORTED`; none default to `booked`.
The reception runtime now wraps this as a constant
`unsupported_appointment_status` error. Extending the Bureau vocabulary
requires its own versioned protocol review.

## Complete list projection v2

`appointment.list_projection.v2` keeps the accepted v1 validator and renderers
untouched. A trusted context has exactly `tenant_id`, `actor_id`, `role`,
`read_capability`, `source_id`, `source_revision`, `as_of`,
`practice_timezone`, and `expected_total`. The role is `reception` and the
capability is `appointments.read`; this is a claimed caller-supplied context
until a future server adapter actually authenticates it. The raw envelope
matches tenant, actor, role, source ID and revision, has `read_only` authority,
a UTC capture instant within 300 seconds and never in the future, and an exact
practice timezone. `is_complete=true`, `total_count=expected_total=len(items)`
and a maximum of 32 rows prevent a silently truncated display. A query that
could contain more than 32 rows must fail rather than claim completeness.

Every row has only ID, practice ID, positive appointment source version, UTC
start/end, **exact domain status**, fixed ordinal display/accessibility labels,
and allowed warning codes. Rows are ordered by `(start_time, id)` with unique
IDs. The only current warning code is `TIME_UNCONFIRMED`. No notes, reasons,
patient identifiers or names may appear. The timezone label is structural;
the candidate does not convert UTC instants into local display time or prove a
rendered accessible surface. It does not imply a complete appointment history.
The source adapter must define the bounded query and supply an honest count.

`render_view_v2` emits only a fully frozen validated snapshot; a later raw
mutation cannot enter the view. `render_fallback_v2` revalidates raw input by
the same path. On valid input, normal and fallback contain identical facts,
warnings, ordering, labels, source metadata and disabled affordances. On any
rejection, fallback is a generic empty, read-only view with
`PROJECTION_UNAVAILABLE`, no source metadata and no rejected rows. A missing,
unknown, stale, future, cross-actor/tenant, incomplete, inaccessible or
overprivileged envelope is never partially displayed.

The worked synthetic input and exact normal/fallback/rejection expectations
are in `stage1-appointment-contract-example-v1.json`. These structures do not
establish app wiring, rendered keyboard/screen-reader behavior, real actor
authentication, database readback, model interpretation or a completed Stage 1
journey. The later integrated create and move tests must establish those facts
under their own reviewed execution scope.
