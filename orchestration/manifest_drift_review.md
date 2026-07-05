# Bernie Manifest Drift & Domain Policy Review - Sprint R19

This review records the Gemini/Antigravity domain-policy critique for hardening
the Bernie Diary Capability Manifest before Bernie consumes it in production.

## Core Recommendation

Keep a hard boundary between authoritative backend policy and display-only
frontend copy. Bernie may read outcome names, reason-code policy, and staff
explanations, but the backend must remain the sole validator of diary
mutations.

## Outcome-Copy Drift

- Backend booking-turn outcomes are defined by
  `app.services.diary.outcomes.BernieBookingOutcomeKind`.
- Diary UI copy is spread across `BERNIE_STATUS_COPY`,
  `BERNIE_HEADLINE_COPY`, hardcoded review-copy branches, and schedule
  explanation copy.
- New backend outcome kinds could otherwise fall through to generic frontend
  copy, so R19 adds a deterministic outcome-copy drift guard.
- `interpreted_ready` remains an explicit transient exception: it is a proceed
  outcome normally consumed before staff see a stable review state.

## Reason-Code Drift

Gemini identified a stronger risk in status-specific reason codes:

- The frontend restricted `Cancelled`, `DNA`, and `NoShow` reason-code options,
  but the backend previously accepted any code from the flat
  `STATUS_REASON_CODES` set for any status.
- The frontend omitted legitimate cancellation options that already existed in
  backend labels and taxonomy: `PATIENT_RESCHEDULED`, `PATIENT_UNWELL`, and
  `CLINIC_RESCHEDULED`.
- Before Bernie consumes the manifest, the backend should provide the
  source-of-truth policy and the frontend should mirror it.

## R19 Integration Decision

- Accepted: add backend `STATUS_SPECIFIC_REASON_CODE_POLICY` and schema
  validators for status/reason-code combinations.
- Accepted: align `docs/diary/diary.js` so the `Cancelled` dropdown includes
  `PATIENT_RESCHEDULED`, `PATIENT_UNWELL`, and `CLINIC_RESCHEDULED`.
- Accepted: add a frontend-drift test proving `STATUS_SPECIFIC_REASON_CODE_OPTIONS`
  matches backend policy.
- Deferred: requiring non-null reason codes for all `Cancelled`, `DNA`, and
  `NoShow` transitions. R19 preserves null/grandfathering semantics to avoid
  changing legacy or partially populated write paths without a migration plan.
- Deferred: deprecating frontend schedule copy catalogs in favour of backend
  schedule-explanation payloads. This is a larger UX copy-source migration.

## Bernie-Facing Safety Notes

- Bernie must not treat display copy as policy.
- Bernie must target exact backend `AppointmentStatus` values, not visual state
  names.
- Bernie must not invent status/reason-code combinations; future prompt/context
  material should cite `STATUS_SPECIFIC_REASON_CODE_POLICY`.
- Bernie must understand that null reason codes are still technically accepted
  for grandfathering, but staff-facing UI should prefer explicit reason capture.
