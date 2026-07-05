# Bernie Diary Capability Manifest v1 - Domain Review

Sprint R18 reviewed the idea of making Bernie/Gemini deeply literate in the
native Diary schema while keeping all authority in deterministic EMR4 code.

## Core Recommendation

Bernie should receive a compact, versioned, read-only capability manifest rather
than raw codebase context. The manifest can make Bernie fluent in the Diary's
entities, states, transitions, reason-code rules, roster semantics,
patient-link semantics, freshness evidence, and confirmation boundaries, but it
must not grant write authority or replace backend validation.

## What Bernie Should Know

- The canonical appointment statuses, booking channels, diary template fields,
  waiting-area fields, and Bernie session states/events.
- The declared capability tiers: `read_only`, `propose`, `confirm`, and `meta`.
- Which actions produce non-mutating proposals and which require staff
  confirmation through a signed server evidence gate.
- Which statuses require reason codes and which schedule-explanation reason
  codes can explain blocked or constrained diary movement.
- That patient/practitioner recognition can be linked, provisional, ambiguous,
  or insufficient, and that uncertainty should drive clarification rather than
  silent binding.
- That roster, break, collision, freshness, and availability facts are produced
  by deterministic backend services, not inferred by the model.

## What Bernie Must Not Decide

- Bernie must not decide RBAC, availability, collision override, roster truth,
  patient identity binding, signed evidence validity, or mutation authority.
- Bernie must not construct or claim confirm-grade evidence such as
  `audit_evidence`, `proposal_freshness_id`, `staff_confirmed`,
  `confirmed_at`, or `confirmed_by_user_id`.
- Bernie must not treat frontend display copy as a source of backend truth.
- Bernie must not receive raw patient rows, live diary rows, or executable
  runtime code through this manifest.

## Acceptance Criteria

- The manifest is source-derived from backend enums, registries, statecharts, and
  deterministic policy constants.
- The manifest is JSON-serializable and free of PHI, credentials, database rows,
  executable code, and write tokens.
- Golden tests prove source parity for statuses, reason codes, session states,
  capability rows, outcomes, and confirmation boundaries.
- Tests prove only staff-confirmed confirmation envelopes can carry
  `writes_authorized=True`.
- Drift risks are named explicitly rather than hidden from Bernie-facing
  prompt/context design.

## R18 Findings To Preserve

- `allowed_authors` in the current capability registry is a declared contract,
  not yet route-enforced policy.
- Frontend outcome copy and backend `BernieBookingOutcomeKind` can drift unless
  future guardrails bind them.
- Frontend status-specific reason-code option lists are display policy until
  promoted into backend source-of-truth policy.
- Patient/practitioner confidence bands should eventually become shared typed
  enums before they are represented as authoritative manifest facts.
