# Appointment list projection v1 — isolated offline candidate

Status: **unactivated, synthetic design candidate**. This file and its Python
module are not a service route, database query, UI, admission, or permission to
execute. The canonical checkout used for vocabulary is historical relative to
accepted G2 source `6fe523c`; integration must reconcile exact selected paths.

## Contract and authority

`appointment.list_projection.v1` is one read-only projection family. A future
backend adapter must authenticate the actor, establish tenant and role, grant
`appointments.read`, supply current source revision and deterministic `as_of`,
and construct the projection from current tenant-scoped truth. The pure module
cannot authenticate or grant any of these facts. It accepts a separately
supplied trusted context solely to check the candidate envelope. It never
constructs a route, callback, command, event, proposal, confirmation, receipt,
or audit record.

The **intent** for this example is `view_appointment_list`; the **command** is
absent and no command envelope is accepted; the **event** is absent and no event
log is read or emitted; the **projection envelope** is the JSON object below.
This read example does not establish a second command plane. Future writes
remain under the existing backend proposal/confirmation and current-truth
authority. A stale projection must never authorise one.

The trusted context is an exact object with `tenant_id`, `actor_id` (canonical
lowercase UUID strings), `role` exactly `reception`, `read_capability` exactly
`appointments.read`, positive integer `source_revision`, and `as_of` in strict
UTC seconds form `YYYY-MM-DDTHH:MM:SSZ`. The projection has exactly
`schema_version`, `tenant_id`, `actor_id`, `role`, `source_revision`,
`captured_at`, `authority`, `heading`, `columns`, `items`, and `warnings`.
Version is exactly `appointment.list_projection.v1`; authority is exactly
`read_only`; identity and revision match context. Capture time must be no later
than `as_of` and at most 300 seconds old. Unsupported versions, extra fields,
missing fields, mismatches and stale or future captures fail closed.

Heading is exactly `Appointments`; columns are the ordered list `Start`, `End`,
`Status`, `Appointment`. These are mandatory structural accessibility text.
There are at most 32 rows. Each row has exactly `id`, `practice_id`,
`start_time`, `end_time`, `status`, `display_label`, `accessibility_label`, and
`warnings`. `id` and `practice_id` are canonical lowercase UUIDs and practice
matches trusted tenant. Times use strict UTC seconds, end is after start and
within eight hours. Status is the deliberately narrow projection vocabulary
`scheduled` or `cancelled`; mapping from the application status enum requires
separate integration review. `display_label` must be exactly `Appointment 1`,
`Appointment 2`, and so on, derived from the row's one-based position in the
canonical `(start_time, id)` order. The caller cannot supply any alternative
label, including a name or identifier. The required
accessibility label is exactly
`{display_label}; starts {start_time}; ends {end_time}; status {status}`.
The resulting rows are ordered by `(start_time, id)` and IDs are unique.
Top-level warnings are sorted unique values from `TIME_UNCONFIRMED`, at most
four; each row may have zero or one such warning. This fixed code has no
payload. All data is synthetic in the worked example; a future adapter must
decide what warning can be derived from real authoritative state.

The candidate uses `id`, `practice_id`, `start_time`, `end_time`, and `status`
from the existing `AppointmentOut` naming vocabulary. It intentionally omits
patient identifiers, reason, notes, practitioner, waiting details, and other
unrelated data. Unknown fields are rejected rather than ignored.

## View and fallback

`render_view(raw, context)` validates the entire input into a frozen snapshot of
all emitted row facts and warning codes. It constructs the result only from
that snapshot, never rereading raw input after validation. The result has
heading, ordered columns and rows, warning codes, and four
disabled affordances (`create`, `update`, `cancel`, `confirm`). It raises a
`ProjectionRejected` with only a fixed error code; no rejected value is echoed.
`render_fallback(raw, context)` calls the same path and revalidates raw input.
For valid input its complete view value equals the normal view. For any
contract rejection it returns a fixed empty view with no rows or warnings,
the same disabled affordances, and `PROJECTION_UNAVAILABLE`. It never shows a
partial rejected projection. It has no callbacks or route data.

Error codes: `STRUCTURE_INVALID`, `IDENTITY_INVALID`, `TIME_INVALID`,
`CONTEXT_UNAUTHORIZED`, `REVISION_INVALID`, `VERSION_UNSUPPORTED`,
`AUTHORITY_INVALID`, `SCOPE_MISMATCH`, `REVISION_MISMATCH`,
`FUTURE_PROJECTION`, `STALE_PROJECTION`, `ACCESSIBILITY_INVALID`,
`WARNINGS_INVALID`, `SIZE_INVALID`, `DUPLICATE_ID`, `STATUS_INVALID`,
`LABEL_INVALID`, `ORDER_INVALID`. These codes report categories only. The
fallback reason is always `PROJECTION_UNAVAILABLE` for a rejected input.

The standalone tests are authored but not run here. They load the isolated
source file directly and use `unittest`, avoiding application imports and the
repository test configuration. The JSON worked example is review material,
not execution evidence. Accessibility is structural here: no service read,
rendering, assistive technology, or AI-off interaction has been proven.
