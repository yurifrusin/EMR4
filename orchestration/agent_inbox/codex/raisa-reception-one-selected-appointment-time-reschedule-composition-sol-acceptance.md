# Sol acceptance — Reception One selected-appointment time reschedule

Date: 2026-08-14

Timestamp: 2026-08-14T09:50:00+10:00 (Australia/Brisbane)

Decision: accept

Accepted source: `d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`

Result: `raisa_reception_one_selected_appointment_time_reschedule_composition_pass`

## Acceptance reasoning

The exact candidate satisfies the frozen time-only boundary. One selected
current appointment can choose one 15-minute-aligned same-day start time. The
bridge resolves the exact current appointment, fixes duration delta at zero,
keeps the practitioner unchanged and delegates once to the existing
`handleMoveResize` interaction. It contains no route, network, proposal,
confirmation, idempotency, signature or raw-write implementation.

The existing update proposal/confirm family remains the sole command path.
Visible staff confirmation, backend warnings and blocks, opaque signed evidence,
command-time authority/source-truth revalidation, idempotency, audit and atomic
commit remain backend owned. Every terminal result is reconciled from a fresh
read, and a committed Reception One card receives its coordinate only from the
exact fresh appointment response.

The 12 paired renderer/outcome traces agree on all eight frozen kernel-owned
field groups and exact command counts. Invalid/no-op input starts no route;
interruption starts no duplicate; dialog Escape and focus return pass; and all
three responsive viewports avoid horizontal overflow.

DeepSeek's one-file test candidate was integrated under Sol recovery and exposed
the fresh-coordinate race repaired in the final product. Gemini's fresh
read-only review returned one `pass` at the unchanged exact candidate. The
packet's incorrect 35-test estimate is not used: independently reproduced
collection and execution prove 51/51.

The expected and actual worker mix is therefore DeepSeek completed, Gemini
completed after the serial deterministic gate, and native subagents declined
because they offered no distinct remaining artifact or veto surface. The new
mandatory parallelism-efficacy receipt control preserves this three-lane
decision across every future task-window continuation.

## Authority finding

No backend, OpenAPI, GraphQL mutation, database, event, watcher, provider,
product/patient data, new route, new command family, deployment, release,
Pages or protected ref was used or authorised. `docs/branding/` and all
unrelated untracked files remain outside the candidate.

The next safe descendant is duration-only composition through the same
existing update interaction, with date, start time, practitioner and every
other field frozen. Standing uninterrupted-development authority applies; no
user-attention condition is present.
