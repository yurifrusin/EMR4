# Reception One cancellation command-path readiness review closeout

Date: 2026-08-15

Timestamp: 2026-08-15T11:33:02+10:00 (Australia/Brisbane)

Status: accepted

Accepted reviewed source: `bb36e19c774eb1bc4ace8cafc6ae2b5c35bc8735`

Result: `raisa_reception_one_cancellation_command_path_readiness_review_pass`

## Lay summary

The existing cancellation path is substantially safer and more complete than
a raw delete button: it prepares a proposal, requires a distinct staff
confirmation, verifies signed evidence, prevents same-request duplication,
records an audit and returns the resulting appointment.

Reception One should nevertheless not reuse it unchanged yet. Two matters need
to be resolved first:

- the dedicated cancellation transaction does not yet lock the appointment and
  freshly recheck the staff member's current authority at the final write
  boundary; and
- the ordinary Diary has an older fallback that changes cancellation into a
  status update and loses any free-text cancellation reason.

No unsafe live behavior or production exploit was proved. This tranche has
identified the exact assurance work needed before cancellation becomes a fifth
Reception One action.

## Technical result

The review inventoried five surfaces: dedicated delete proposal, dedicated
delete confirm, raw compatibility delete, native delete-to-status fallback and
Reception One's absent cancellation bridge.

The dedicated confirm path already preserves explicit confirmation, signed
practice/actor/command/current-state evidence, freshness, waiting-area
revalidation, structured and free-text reasons, idempotency, audit and result
readback. Its current `_get_appointment()` read is not locked, the route has no
explicit in-transaction current-authority recheck, and its differently-keyed
"concurrency" test is serial rather than overlapping.

The native fallback retains explicit confirmation and signed status confirm,
but it intentionally omits `cancellation_reason` and changes command, audit and
idempotency vocabulary. The OpenAPI draft also differs from mounted runtime in
both proposal and confirm path/payload shape.

The accepted next prerequisite is one provider-free, unmounted delete-confirm
conditional-command kernel architecture and admission rehearsal. It will
define the future locked/current-authority transaction without changing any
mounted route, database, client or UI.

## Verification

- Seven focused readiness assertions passed.
- The combined cancellation, audit, reason-policy and API Spine packet passed
  all 188 tests.
- The canonical fast profile passed Ruff, compilation of 209 maintained Python
  sources, 196 tests, Diary JavaScript syntax and Git whitespace.
- Gemini 3.6 Flash/high independently passed all ten challenges and reproduced
  all 188 tests at unchanged clean source.
- The non-PHI Pushover closeout notification succeeded with request
  `001a6d8a-b5fc-42fa-8a1d-385d6b0296e2` and status `1`.
- Evidence label: `repository_static_authored_synthetic`.

## Parallelism efficacy

- DeepSeek was declined because no stable mechanical artifact existed in this
  tightly coupled command-semantics review.
- Native subagents were declined because no bounded package exceeded briefing
  and reconciliation cost.
- Gemini supplied the planned fresh independent veto and had positive leverage.
- Sol retained source reconciliation, acceptance, continuity and Git authority.

## Deliberately closed

No cancellation control or product behavior changed. No route, OpenAPI,
GraphQL, schema, database, event, watcher, command, provider or UI source
changed. Raw compatibility delete remains mounted. Patient/product/clinical
data, protected evidence, external channels, provider/ADC, credentials/IAM,
deployment, production, release, Pages and protected refs remain closed.

## Next tranche

Begin the provider-free unmounted delete-confirm conditional-command kernel
architecture and admission rehearsal under standing uninterrupted-development
authority. User attention is not required.
