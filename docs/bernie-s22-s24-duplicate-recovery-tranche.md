# Bernie Duplicate Recovery Tranche

| Item | Value |
|---|---|
| Tranche | S22-S24 |
| Trigger | Live receptionist diary use, 2026-07-13 |
| Boundary | Read-only classification and proposal/UI recovery |
| Status | Approved for bounded implementation |

## Goal

When a recognized patient's active booking already satisfies the requested
date, practitioner, and time semantics, Bernie must explain that the requested
booking already exists and ask whether staff want another time or day. It must
not continue to generic candidate selection, expose a confirm affordance, or
create another appointment.

Candidate recovery must preserve the normalized requested date and time bounds.
Removing or widening a time bound remains a typed suggestion requiring an
explicit subsequent staff action.

## Deterministic Classification

Before supervised slot search, classify active appointments for the same
practice, patient, and requested date as:

- `exact_duplicate`: requested practitioner matches; the existing start time is
  exactly the sole lower bound or falls inside the supplied bounded start-time
  window; and any supplied appointment type, location, and duration match;
- `overlapping_same_patient`: the patient's appointment overlaps the requested
  temporal window but does not satisfy all exact-duplicate fields;
- `same_day_distinct`: an active same-day appointment exists outside the
  requested temporal match;
- `none`: no applicable active appointment exists.

Completed, Cancelled, NoShow, and DNA appointments do not qualify. A source
appointment supplied for reschedule/extend is excluded. Missing temporal
evidence must never be treated as an exact duplicate.

Only `exact_duplicate` short-circuits this tranche. The other classifications
retain existing advisory behavior and do not grant or remove booking authority.

## Sprint Split

- **S22:** add the practice-scoped, read-only classifier and exhaustive unit
  tests, including source exclusion and terminal-status cases.
- **S23:** short-circuit supervised booking before slot search with a typed
  `existing_booking_found` result/outcome, structured non-PHI-broadening booking
  summary, no candidates, no confirm affordance, and change-time/day
  suggestions. Add a live-report golden regression and candidate-bound tests.
- **S24:** render the typed existing-booking result in the diary with no
  candidate cards or confirm button and accessible change-time/day actions.

## Authority Boundary

- Classification reads current database state; it does not depend on model
  confidence, provider prose, or the capped patient-context display list.
- The result is non-confirmable and performs no appointment or audit write.
- Confirmation routes, signed evidence, idempotency, raw compatibility routes,
  provider configuration, and model-to-database authority remain unchanged.
- No migration, GraphQL mutation, H15/historical-diary input, memory/RAG/
  GraphRAG, deployment, or production gate is opened.

## Allocation

- DeepSeek V4 Pro: coordinator review only.
- DeepSeek V4 Flash: classifier, schema/outcome, supervised route, and backend
  regression tests.
- Gemini 3.5 Flash through Antigravity: diary rendering and focused UI tests
  after the backend contract is committed.
- Sol: contract correction, independent review/tests, protected-master
  integration, commit, push, and closeout.

## Acceptance

- exact duplicate produces `existing_booking_found` before slot search;
- response contains no candidates, staged proposal, confirm endpoint, or confirm
  payload and reports that no new booking was created;
- missing/blank temporal evidence cannot produce exact duplicate;
- source appointment and terminal appointments cannot self-trigger;
- every returned candidate remains inside the normalized date/time bounds;
- exact-duplicate route call changes neither appointment nor audit counts;
- diary UI exposes the explanation and accessible next actions while hiding
  candidate and confirmation controls;
- existing collision, booking outcome, supervised booking, and confirmation
  regressions remain green.
