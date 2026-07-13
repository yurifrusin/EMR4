# Bernie S25-S27 Accessible Booking Authority Tranche

Status: approved for implementation

## Goal

Make the existing deterministic, staff-authorized Bernie booking path usable
without sighted diary inspection. Accessibility changes the modality of review
and authorization; it does not weaken or replace backend authority.

## Authority Model

1. Bernie interprets and prepares a proposal.
2. The backend supplies typed patient, practitioner, time, duration, warning,
   freshness, and confirmation evidence.
3. An authenticated receptionist reviews and explicitly authorizes through an
   accessible control.
4. The REST confirmation command revalidates practice scope, entities, current
   schedule/conflicts, signed/session evidence, and idempotency before writing.
5. The backend returns an authoritative typed receipt for the committed result.
6. The diary announces and renders that receipt without requiring visual grid
   inspection.

The receptionist remains the authorizing principal. Bernie does not gain write
authority. A sighted human check is not an authority source.

## S25 - Typed Confirmation Receipt

Extend successful appointment-create confirmation responses with an additive
`appointment.confirmation_receipt.v1` object. It must contain:

- confirmed outcome and appointment identifier;
- patient, practitioner, date, local time, duration, status, and optional type;
- authenticated confirmer display and role;
- deterministic verification flags for actor authentication, practice scope,
  proposal revalidation, conflict checking, idempotency, audit recording, and
  whether signed evidence was verified;
- `visual_diary_check_required: false`.

Blocked responses must not carry a successful receipt. Populate the receipt on
both canonical staff and Bernie create-confirm routes because they share the
same command output contract. Do not add a new mutation route.

## S26 - Modality-Independent Diary Flow

- Parse the successful confirmation response before changing UI state.
- Build confirmed state from the backend receipt, not the staged preview.
- Announce a concise committed-result message with a semantic live region.
- Render receipt details and deterministic verification status in normal DOM
  text that is available to assistive technology.
- Keep the confirm action a native keyboard-operable button with an informative
  accessible name.
- On an HTTP 200 blocked body, do not claim success; announce the backend block
  and preserve a recoverable review state.
- Do not require locating the appointment visually in the diary grid.

## S27 - Evidence

Add deterministic route and browser tests proving:

- exactly one appointment and audit row accompany one successful receipt;
- receipt identity, schedule, actor, and verification fields come from the
  committed backend result;
- idempotent replay returns the same receipt and creates no second write;
- blocked confirmation has no successful receipt;
- keyboard activation can submit confirmation;
- confirmed UI copy and receipt details derive from the response body;
- success is exposed through status/live-region semantics;
- no candidate, confirmation, or visual-grid check is required after success.

Label route-intercepted browser evidence accurately. Run focused confirmation,
idempotency, API-spine, and diary smoke regressions.

## Closed Gates

This tranche does not open autonomous or model-to-database writes, hands-free
delegation, provider/live-provider wiring, GraphQL mutation, external clients,
schema/database migration, memory/RAG/GraphRAG, H15/H-series, historical diary
inputs, deployment, production, or release authority.
