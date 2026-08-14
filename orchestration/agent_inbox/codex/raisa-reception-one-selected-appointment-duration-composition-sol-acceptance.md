# Sol acceptance — Reception One selected-appointment duration

Date: 2026-08-14

Timestamp: 2026-08-14T11:55:58+10:00 (Australia/Brisbane)

Decision: accept

Accepted source: `f397a3706f3b870b8436eb3993bd90c6c0c742a8`

Result: `raisa_reception_one_selected_appointment_duration_composition_pass`

## Acceptance reasoning

The exact candidate satisfies the frozen duration-only boundary. One selected
current appointment can choose a bounded target from 15 through 480 minutes,
provided the change is a whole 15-minute delta and the derived end remains on
the same date. The bridge reads exact current truth, fixes the start delta at
zero, retains the current practitioner and delegates once to the existing
`handleMoveResize` interaction.

The existing update proposal/confirm family remains the sole command path.
Visible staff confirmation, backend warnings and blocks, opaque signed
evidence, command-time authority and source-truth revalidation, idempotency,
audit and atomic commit remain backend owned. Reception One has no network,
route, proposal, confirmation, signature, idempotency or raw-write code.

The twelve paired traces agree on all eight normalized truth fields and exact
route counts across safe, cancelled, blocked, stale, failed and committed
outcomes. Invalid, unchanged and out-of-day choices start no route. Terminal
UI phases cannot outrun the bridge's exact fresh read, reconciliation failure
remains fail closed, and status/time/duration actions are mutually exclusive.

DeepSeek's recovered test artifact and native read-only seam analysis both
found material risks. Gemini's fresh read-only review returned `pass` with
68/68 tests at the unchanged clean candidate. The expected and actual worker
mix therefore agree, with Sol correctly retaining all recovery, integration
and acceptance authority.

## Authority finding

No backend, OpenAPI, GraphQL mutation, database, event, watcher, product or
patient data, provider/product call, new route, command family, deployment,
release, Pages or protected ref was used or authorised. `docs/branding/` and
all unrelated untracked files remain outside the candidate.

The next safe descendant is same-date, same-start, same-duration
practitioner-only reassignment through the same existing update interaction.
Standing uninterrupted-development authority applies; no user-attention
condition is present.
