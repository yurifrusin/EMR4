# Reception One multi-change request atomicity architecture

Date: 2026-08-14

Timestamp: 2026-08-14T20:37:05+10:00 (Australia/Brisbane)

Status: `selected_for_provider_free_rehearsal`

Source inspected: `0eec51f419d955461696e8b986f7fb7e4dd20ab5`

Decision: `typed_inert_candidate_then_one_family_owned_command`

## Decision

The four visible Reception One buttons are controls for an authorised human
receptionist. They are not actuators made available to Raisa or to a provider
model. Their small vocabulary is nevertheless useful to Raisa: it is a
semantic keyboard whose keys have precise meanings that can be proposed in a
typed form without being pressed.

A future conversation, email, SMS, WhatsApp, voice or external-chatbot adapter
may produce an inert `AppointmentActionCandidate`. That candidate has no DOM,
session, confirmation, route or write authority. Deterministic admission must
resolve one target, reject contradictions and unsupported fields, bind the
current principal and practice, and classify all requested changes by the
backend command family that owns them. Only then may the product present a
review. Explicit human confirmation and a fresh kernel command remain separate
later facts.

The resulting chain is:

`message or utterance -> typed inert candidate -> deterministic admission ->`
`human review projection -> explicit human confirmation -> one kernel command ->`
`fresh authoritative readback`

No layer may inherit the authority of the layer to its right.

## Exact existing kernel map

| Fact | Exact ordinary source | Evidence classification |
|---|---|---|
| The update proposal accepts an optional closed patch containing patient, provisional name, practitioner, appointment type, location, date, local time, duration, reason and notes. Status is absent. | `app/schemas/appointments.py:373-384`; OpenAPI `appointment-commands.yaml:824-858` | Structural contract |
| Supplied update fields are merged over the current practice-scoped appointment and the combined result is checked for identity, practitioner activity, conflicts, breaks and temporal validity. | `app/routers/appointments.py:1888-2028` | Structural contract, with focused tests for individual and combined cases |
| A safe proposal emits one full `AppointmentUpdateCommand`, freshness digest, signed evidence and an explicit confirm payload without mutating. | `app/routers/appointments.py:2045-2103` | Directly tested for date, time and duration together at `tests/test_appointment_update_proposal.py:140-181` |
| Update confirmation claims an idempotency record, locks the practice-scoped appointment row, verifies current signed evidence and freshness, re-proposes the full command, exact-matches it, then performs one update/audit/command completion and commit. | `app/routers/appointments.py:1815-1885`, `2390-2552`, `5096-5222`, `7979-8002` | Structural transaction path; successful date/time/duration write and one audit are directly tested at `tests/test_appointment_update_proposal.py:184-226` |
| Changed practitioner activity is checked again at confirmation and blocks with no appointment or audit write if it changed. | `app/routers/appointments.py:2483-2516` | Directly tested at `tests/test_appointment_update_proposal.py:857-898` |
| Status has its own input, command, signed version binding, proposal route and status-only confirm route. | `app/schemas/appointments.py:477-524`, `555-570`; `app/routers/appointments.py:2702-2815`, `2970-3006`; OpenAPI `appointment-commands.yaml:232-279`, `870-939` | Separate-family contract, with one-write and tamper-denial tests at `tests/test_appointment_status_mutations.py:681-747` |
| The current browser console exposes four human buttons. Opening one selects only an editor; the four existing bridges remain distinct. | `docs/diary/meta-grid.js:3754-3825`; `docs/diary/diary.js:7297-7571` | Accepted product composition; no compound UI exists |

The successful combined update evidence covers date, local time and duration.
The source structurally carries practitioner, time and duration through one full
command, one revalidation and one apply path, and a blocked practitioner-plus-
time-plus-duration proposal is tested. It does **not** yet directly prove a
successful confirmation that changes practitioner, time and duration together,
nor a dedicated same-key replay/rollback matrix for that exact combination.
Those claims remain deliberately unproved.

## Candidate vocabulary

An `AppointmentActionCandidate` contains only:

- an origin kind and correlation reference;
- one provisional appointment target or a typed missing/ambiguous target state;
- zero or one provisional value for each allowlisted semantic field;
- a classification and presentation outcome; and
- explicit `none` values for DOM, confirmation, route and write authority.

The first semantic fields are `time`, `duration`, `practitioner` and `status`.
Their values remain provisional and must never be displayed as current truth.
More than one value for a field, an unresolved target, an unsupported field, an
unknown principal or an absent capability produces clarification or a typed
block. Provider confidence and list order never settle a contradiction.

Authentication, channel possession, patient recognition, authenticated
principal, confirmer identity and command authority are distinct. A future
authenticated Siri-like bot may carry a user's words; it does not thereby
become that user's confirmer.

## Atomicity matrix

| Candidate | Classification | Permitted representation | Execution meaning |
|---|---|---|---|
| One or more of time, duration and practitioner | `same_update_family` | One combined update patch, one proposal and one review packet | At most one explicit update confirmation and one update transaction; never a sequence of field writes |
| Status only | `status_family` | One status proposal and review packet | At most one explicit status confirmation through the distinct status kernel |
| Status plus any update-family field | `cross_family` | One non-executable review plan that clearly separates the parts | No current all-or-nothing command; no automatic sequencing and no rollback implication |
| Contradictory, ambiguous, unsupported or unauthorised request | `clarification_required` or `blocked` | Explanation and the minimum clarifying question | Zero proposal, zero confirmation and zero write |

If staff deliberately performs separate cross-family actions, each later action
must be freshly proposed after readback of the preceding result. The first
successful command remains committed if a later command is blocked. The UI must
show those as two outcomes, never one concealed partial success.

## Complex semantic keys

A future more complex button is a typed presentation macro, not a generic tool.
It may group several values only when deterministic classification maps all of
them to one existing command family and that family has a proven one-command
contract. The macro itself cannot call a route, confirm or write.

An all-or-nothing key spanning status and update would require a new kernel-
owned command with its own closed schema, capability, current-truth/conflict
domain, row-locking order, idempotency, audit, rollback and database proof. It
must not be simulated by a client loop.

This lets the semantic keyboard grow without confusing Raisa: complexity is
added by defining new safe keys, not by giving the model a more powerful hand.

## Adapter and interruption contract

- Email, SMS, WhatsApp, voice and external chatbot channels remain transports
  and presentation surfaces only.
- Replay, duplicate delivery or delayed channel messages must create at most a
  candidate for fresh admission; they cannot replay a confirmation.
- A stale candidate is discarded or reinterpreted. A stale signed proposal is
  blocked by the kernel and must be rebuilt from current truth.
- An interruption before confirmation leaves no write. An interruption after
  one separately confirmed cross-family action must show that committed truth
  before offering the remaining action again.
- Events may prompt a refresh but are not current truth, authority or command
  evidence.
- Provider or channel failure produces an unavailable/clarification outcome,
  never a deterministic guess or fallback command.

## Next tranche

The next safe descendant is
`raisa_reception_one_same_update_family_multi_change_kernel_rehearsal`.
It should use authored-synthetic, provider-free data to exercise the existing
update proposal/confirm path with a changed time, duration and practitioner in
one command, plus stale-current-truth, conflict, idempotency, audit and rollback
checks. It should change no UI and should prefer tests over new product code.

Only after that rehearsal passes should a multi-field Reception One editor or
conversation-to-editor composition be considered.

## Claim boundary

This is `repository_static_authored_synthetic` architecture evidence. It proves
the exact current source shape and selects fail-closed semantics; it does not
prove a new UI, a live adapter, patient identity, voice safety, provider
behavior, successful three-field update execution, a cross-family transaction,
deployment or production readiness.
