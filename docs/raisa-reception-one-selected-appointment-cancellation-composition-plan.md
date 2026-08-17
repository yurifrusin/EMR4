# Reception One selected-appointment cancellation composition plan

Date: 2026-08-17

Timestamp: 2026-08-17T13:49:00.3722917+10:00 (Australia/Brisbane)

Status: `frozen_for_provider_free_implementation`

Task baseline: `36edc1e5b36b83a54f6af28c9519853290e4189b`

Target result: `raisa_reception_one_selected_appointment_cancellation_composition_pass`

Reasoning level: Extra High. This tranche exposes a destructive scheduling
command in the visible first-party client. It preserves the already accepted
backend command meaning but freezes a new staff interaction, strict public
receipt and post-command truth-display boundary.

## Objective

Add one fifth, visually distinct `Cancel appointment` choice to Reception
One's selected-action console. The action must use only the accepted dedicated
delete proposal and canonical delete-confirm REST/OpenAPI family, always stop
for explicit staff confirmation, accept only the versioned minimal public
delete receipt, and rebuild the current projection from a fresh authorised
Diary read after every terminal outcome.

This is not a second cancellation mechanism. It must not call the raw
compatibility `DELETE`, route through status cancellation, reuse the ordinary
booking editor's 404-to-status fallback, or interpret a confirm response as an
appointment read model.

## API Spine classification

- **Read surface:** the current scoped Reception One projection and a fresh
  appointment-list projection read after any terminal proposal/confirm result.
- **Command surface:** existing
  `POST /api/v1/appointments/proposals/delete/{appointment_id}` followed only
  by canonical
  `POST /api/v1/appointments/proposals/delete/confirm`.
- **GraphQL:** read-only and unchanged.
- **Response:** exact
  `raisa.delete_confirm_public_envelope.v1` with optional exact
  `appointment.delete_confirmation_receipt.v1`; never `AppointmentOut`.
- **Backend ownership:** authenticated practice/actor authority, current source
  version, grant/revocation, warning acknowledgement, idempotency, transaction,
  audit, private receipt and atomic effect remain wholly backend-owned.

No OpenAPI, Pydantic, router, service, migration or database change is
authorised.

## Adapter-neutral projection rule

Reception One is the first-party reference rendering of an adapter-neutral
semantic contract. Raisa supplies a typed, purpose-limited projection/action
envelope rather than raw rows. A rendering engine or external adapter may vary
layout, wording, visual hierarchy, speech turn-taking or device affordance, but
it may not change:

- displayed fact values or provenance;
- whether a value is current, proposed, committed or unavailable;
- action identity or consequence;
- required warnings and blocks;
- the explicit confirmation boundary;
- authority/current-truth recheck meaning; or
- the strict receipt and fresh-reconciliation requirement.

Accordingly, this native HTML composition is one implementation of the
contract, not a claim that every future client must reproduce its pixels.
Siri-like clients may own speech UX; Raisa still owns the typed cancellation
semantics and accepts only a conforming confirmed command packet.

## Frozen visible interaction

1. `activeSelectedAction` becomes exactly one of `null`, `status`, `time`,
   `duration`, `practitioner` or `cancel`.
2. Opening, closing or drafting the cancellation editor performs zero HTTP
   requests. The existing four choices and shared-editor behavior remain.
3. The cancellation editor contains one required administrative reason select
   over exactly these ten dedicated values:
   `PATIENT_CANCELLED`, `PATIENT_RESCHEDULED`, `PATIENT_UNWELL`,
   `PATIENT_TRANSPORT`, `PRACTITIONER_UNAVAILABLE`, `CLINIC_OPERATIONAL`,
   `CLINIC_RESCHEDULED`, `ADMIN_ERROR`, `DUPLICATE_BOOKING`, `OTHER`.
4. It may contain one optional administrative note, trimmed and capped at 500
   characters. The draft is provisional, patient-minimised and never displayed
   as current truth.
5. `Review cancellation` is disabled without one exact current appointment,
   one allowed reason, a non-stale projection or while any selected action,
   confirmation dialog, interruption or reconciliation latch is active.
6. Submission resolves the exact selected appointment and sends one dedicated
   delete proposal. No status or raw-write fallback is permitted for any HTTP
   status, network error or malformed response.
7. A blocked proposal exposes only typed safe copy and no confirm action. Every
   otherwise admissible proposal opens the existing contained confirmation
   dialog, even if it has no warning. The dialog says the whole appointment
   will be cancelled and that current authority and source truth will be
   checked again.
8. Escape or `Cancel` sends no confirm request, discards no current truth and
   returns focus to the cancellation control.
9. Confirm uses only the proposal's exact canonical endpoint, cloned prepared
   payload, `confirmed=true`, acknowledged proposal warning codes and the
   existing delete-confirm idempotency derivation.
10. Success is admitted only when the recursively closed public envelope has
    the exact schema/intent, `safe=true`, `requires_confirmation=false`,
    `autonomy_tier=confirmed_write`, no blocks and an exact receipt matching
    the selected appointment, `status=Cancelled`, chosen reason, optional note,
    null waiting area and only the sorted unique optional
    `waiting_area_cleared` warning.
11. Unknown top-level, issue or receipt fields; widened enums; a returned
    `appointment`; mismatched identity/reason; missing receipt; or malformed
    audit labels fail closed. Private receipt bytes or appointment read-model
    fields are never rendered or retained.
12. After success, blocked confirmation, staff cancellation, stale/current-
    authority denial, transport failure or malformed response, Reception One
    rebuilds the exact scoped projection from a fresh authorised list read.
    Cancelled appointments disappear because the projection contract excludes
    them. Proposed values never stand in for that read.
13. If fresh reconciliation fails, the console enters
    `reconciliation_required`, disables every action and offers the existing
    refresh control. It must not claim either success or non-commit.
14. Busy reselection, blur/visibility interruption, palette switching and
    workspace Escape retain the accepted exclusion and focus rules.

## Source boundary

Sol may edit only:

- `docs/diary/diary.js` at baseline SHA-256
  `0c69253df5428df3007182c31e9c1b2efd98591a7fc632609d9d1ca060acf1e7`;
- `docs/diary/meta-grid.js` at baseline SHA-256
  `9c09ea90e7846d9fdee1a912fc9b7d72e1fdd7f7990549d7dd8768b22c73ce5e`;
- `docs/diary/meta-grid.css` at baseline SHA-256
  `54f1e5aa1dbfa913376e06fe3af682315e0bef61d13b91fef7f8b3da28c436f0`;
- the three matching cache references in `docs/diary/diary.html` at baseline
  SHA-256
  `42314b5febe364a09eaff46b4ac1d791caea2bf386adbb24976b03a3120edb06`;
- tranche-local deterministic tests, typed evidence, review, continuity,
  acceptance and closeout artifacts.

`app/schemas/appointments.py`, `app/routers/appointments.py`, every delete
service, migration and `docs/api-spine/openapi/appointment-commands.yaml` are
read-only semantic controls.

## Frozen bridge contract

`docs/diary/diary.js` may add one
`EMR4DiaryMetaGridBridge.cancelAppointment` operation. It validates the exact
current appointment, reason code and note, performs the dedicated proposal and
confirm calls, emits only patient-free lifecycle states, validates the strict
public envelope and returns a minimal frozen outcome. It contains no raw
`DELETE`, status-proposal fallback, optimistic appointment mutation or public
receipt widening.

The old ordinary booking-modal `deleteBooking()` remains outside this tranche
and may not be called by the bridge. Its historical fallback is neither
accepted nor copied; converging that separate compatibility consumer is future
work.

## Acceptance scenarios

The provider-free authored-synthetic packet must prove:

1. palette open/collapse/switch and cancellation drafting issue zero routes;
2. safe cancellation issues exactly one dedicated proposal, one canonical
   confirm after a visible explicit dialog, zero status proposals and zero raw
   writes, then removes the appointment only after a fresh scoped read;
3. Escape/Cancel issues no confirm, restores current truth and returns focus;
4. a blocked proposal offers no confirm and performs fresh reconciliation;
5. a stale/current-authority denial performs no fallback or optimistic change;
6. malformed/widened public envelopes, receipt identity/reason mismatches and
   injected appointment/read-model fields fail closed and reconcile freshly;
7. simulated success/replay envelopes produce the same visible outcome without
   a second effect claim;
8. interruption and busy reselection cannot switch action or appointment and
   require fresh reconciliation before another action;
9. native keyboard operation, contained dialog/Escape, one polite atomic live
   region, 44-pixel targets and no horizontal overflow pass at 1280x720,
   768x1024 and 390x844; and
10. source guards prove no raw `DELETE`, no cancellation status fallback, no
    GraphQL mutation, no new route/schema and no use of `deleteBooking()` or
    `applySignedDeleteProposal()` by the Reception One bridge.

Browser evidence is labelled `route_intercepted_browser`; it is never live
backend or database evidence.

## Parallelism-efficacy allocation

- **Sol:** owns destructive semantics, adapter-neutral contract, product
  source, integration, deterministic admission, recovery and acceptance.
- **DeepSeek V4 Flash/high:** after this freeze, owns exactly one new bounded
  `review/test_reception_one_cancellation_action.py` route-intercepted browser
  test artifact. It receives no product-source, plan, acceptance, Git publish
  or live-system authority. Sol product implementation may overlap that
  separable test work.
- **Gemini 3.7 Flash/high:** reserved for one fresh exact-candidate read-only
  veto after deterministic admission.
- **Native subagents:** declined because current developer policy prohibits
  proactive native delegation.

Shared browser execution and repository pytest remain serial. Reassess at
DeepSeek predispatch/return, material recovery, pre-verifier admission and
closeout.

## Verification and claim boundary

Run the new browser artifact, the existing selected-action/status/update
browser packet, exact source/API Spine guards, JavaScript syntax, the canonical
fast profile, Ruff, maintained-source compilation and Git whitespace. Use the
repository serial pytest wrapper whenever `tests/conftest.py` loads. Admit one
fresh clean Gemini veto only after these gates pass.

Passing proves only provider-free, authored-synthetic first-party client
composition and route-intercepted browser behavior over an already accepted
command contract. It does not prove live browser/backend/PostgreSQL operation,
representative usability, external adapter interoperability, product/patient/
clinical data, deployment or production.

No provider/ADC, credential/IAM, external network, executable model tool,
database/source/watch access, migration, product/patient/clinical/historical
data, deployment, production, release, Pages or protected-ref movement is
authorised. `docs/branding/` and every unrelated untracked file remain
preserved; staging is explicit-path only.
