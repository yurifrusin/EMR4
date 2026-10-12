# Appointment command, event, and projection linkage — source preparation v1

This note binds the existing appointment contracts to the frozen Stage 1
synthetic read and move contracts. Its `v1` suffix identifies this **document
revision**, not a new command or event wire version. It creates no route,
authority, event, renderer, or accepted G3 criterion. The source basis is the
accepted `5f56c186d144a173c576824fbfd8c08950b9f8a0` tree; the frozen Stage
1 source candidate is separate and remains unactivated. The independent
remaining-criteria review is
`g3-remaining-criteria-review-v1.json` SHA-256
`b1443e64ebfac913b33ca49219936a69ed808f1d45bdbbb6cb861ea230a7380d`.

## Existing links and their actual version claims

| Meaning | Existing source | Link and limit |
| --- | --- | --- |
| Staff create proposal and command | `app/schemas/appointments.py` lines 283–324; `app/routers/appointments.py` lines 1192, 1728–1811 | The accepted router is under `/api/v1/appointments`. `AppointmentCreateCommand` is typed but has **no per-message `schema_version` field**. A proposal carries it with safety, warning, freshness, and signed-confirmation evidence. `POST /proposals/create/confirm` requires authenticated mutating role, explicit confirmation, an idempotency claim, signed evidence, and freshness. The namespace and exact typed/signed payload are current version/compatibility evidence; this note does not decide whether they fully satisfy the G3 criterion. |
| Create result | `app/schemas/appointments.py` lines 344–381; `app/routers/appointments.py` lines 1866–1915 | Successful create returns `ConfirmationReceipt` with wire `appointment.confirmation_receipt.v1`, appointment ID, optional correlation/audit IDs and server-derived verification flags. The route stores the response against the claimed idempotency command before committing. Blocked responses carry no receipt; replay uses the stored decision path. There is no create diary-committed event in the named event source. |
| Staff update proposal and command | `app/schemas/appointments.py` lines 384–462; `app/routers/appointments.py` lines 1918–1988, 1991–2217, 2504–2677 | `AppointmentUpdateCommand` and `AppointmentConfirmUpdateProposalOut` are typed inside the `/api/v1/appointments` namespace without per-message version fields. The confirm route claims idempotency, locks the tenant-scoped appointment row, verifies signed evidence and freshness, re-proposes, compares the command, and stores the confirmed response and audit ID in the same transaction. Its response has no create-style `ConfirmationReceipt` or public command/event revision; exact response compatibility still needs independent assessment. |
| Reschedule event | `app/services/diary_committed_events.py` lines 16–20, 26–73; `app/schemas/diary_events.py` lines 26–66; `app/models/diary_events.py` lines 20–68 | A temporal update can append `diary.appointment_rescheduled.v1` with appointment/time window, reason code, actor, command ID, audit ID, and correlation ID. The typed event/feed shapes are versioned. `aggregate_revision` is the count of appointment audit rows at emission, constrained positive; it is **not** an appointment entity version or list revision. The update helper emits this event only when the committed-event feature is enabled, a command ID exists, and start or duration changed. |
| Synthetic move intent | Frozen `app/services/appointment_lifecycle.py` lines 122–232, SHA-256 `c84581d7a3fde7e80288d21b08d24e61fd210d281435e9d281bf121253539bd6` | `appointment.move_time_intent.v1` binds a selected appointment ID, selected state version, read-source revision, tenant/actor/role, and target local date/time to caller-supplied trusted context. It permits only a proposed time delta and emits a non-writing review. It does not mint the existing update command or authenticate its context. |
| Synthetic read projection | Frozen `app/services/appointment_list_projection.py` lines 220–410, SHA-256 `05e102af145ac8561c209108f8fb6e865d7b48a4fb598c9a5274c10d26e980d9` | `appointment.list_projection.v2` has one versioned read envelope, exact domain status, bounded complete row count, a query `source_id`/`source_revision`, per-row `source_version`, and matching normal/fallback semantics. The supplied context is not yet server-authenticated and no rendered surface is proved. |

The existing `AppointmentOut` (`app/schemas/appointments.py` lines 231–259)
does not expose `appointment_state_version`. A future trusted read adapter
cannot derive list v2's per-row `source_version` from that response alone.
Likewise, `_appointment_update_state_payload` (`app/routers/appointments.py`
lines 8058–8073) and its signed freshness construction (lines 8093–8132) omit
`appointment_state_version`. `_apply_appointment_update` (lines 5339–5465)
does not explicitly increment it. The permitted sources do not establish
whether a database trigger increments it on a date/time change. That fact
requires an exact approved migration or bounded database proof before a move
adapter treats the version as an enforceable compare-and-swap predicate.

## Required association for the next adapters

A read adapter must obtain the authenticated actor and practice scope from the
server, not the projection or move payload. Under one consistent bounded read,
it must establish the query identity/revision, capture instant, practice
timezone, complete count, and selected appointment's current state version.
It must reject a query that cannot prove completeness within 32 rows. It may
then give the frozen list validator its separate trusted context. The list
`source_revision` describes **that read source**; it must not be copied from
the event `aggregate_revision`, idempotency record, audit count, or row
`source_version` without a separately established rule. A missing or uncertain
version/revision means no authorised projection, with the existing generic
empty fallback.

For a staff move, the frozen pure review identifies one selected appointment
and one intended local date/time delta; the adapter must preserve the same
appointment ID, patient, practitioner, type, location, duration, and status.
It must resolve timezone ambiguity or gaps, re-fetch current server state,
check the selected entity version **and** exact temporal preimage under the
tenant-scoped row lock, and use only the existing update proposal and signed
confirmation route. The existing route's command contains a full resolved
appointment state; it must not treat client-supplied unchanged fields as
authoritative. Its self-overlap check, availability revalidation, idempotency
claim, audit, and transaction remain server-owned. A mismatch returns to a
fresh proposal; an uncertain result is reconciled before any retry. This is a
future integration predicate, not a claim that the current route already
enforces the frozen intent's state version.

The command ID, audit ID, optional reschedule-event ID/revision, entity state
version, and read-source revision have different owners and lifetimes. A
successful update response plus its stored idempotent result proves the
confirmed command result; a conditional reschedule event is a separate
projection signal. Neither event presence nor its audit-count revision proves
that list v2 was refreshed. The next read must re-establish its own source
revision and per-row versions from authoritative state.

## Minimum remaining implementation footprint

No new pure schema or test is authored here. The existing `/api/v1/appointments`
transport namespace, exact typed create/update payloads, signed-confirmation
inputs, idempotent results, `appointment.confirmation_receipt.v1`, and
`diary.appointment_rescheduled.v1` are the version and linkage evidence to
freeze together for the G3 criterion. This document's `v1` suffix is only its
revision. Absence of a `schema_version` member on every legacy command is
**not by itself** a missing version contract. Independent review must inspect
the actual typed schemas, route namespace, signature coverage, compatibility
and update-result/event association before deciding whether a narrow adapter
or additive field is necessary. Any change to signed payloads needs a
demonstrated gap and an exact compatibility rule; this preparation makes no
new wire-version or G3 acceptance claim.

After separate admission, the first read-only batch should own one bounded
server source adapter and one read endpoint or existing read seam, plus focused
tests for authenticated practice/actor binding, complete-count refusal,
freshness, status/identity ordering, version provenance, and no write effects.
The next supported local render profile should own the smallest actual read
surface and focused rendered accessibility/fallback parity checks. Structural
`accessibility_label` fields alone do not prove accessible names or interaction.
Create/move mutation and Diary/Word parity remain the later G4 journey; this
preparation neither starts nor accepts them.

Source pins for the accepted tree: `app/schemas/appointments.py` blob
`4f617dbf706a532e9bde31b32b003a77de887a26`;
`app/routers/appointments.py` blob
`dc1c0ba3a24fd135498408c7bc3f2692aa67289d`;
`app/services/diary_committed_events.py` blob
`ecc3d4f7431f184bf2201c6ddc621ef53969bea2`;
`app/schemas/diary_events.py` blob
`f99c88a73ec9585dc257bd89d314fbc7d3a8c9ae`;
`app/models/diary_events.py` blob
`6a796f52a56c8deff3b326f4c5385cbcac760d0f`.
