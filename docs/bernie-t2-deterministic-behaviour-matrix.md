# T2 Deterministic Bernie Behaviour Matrix

Status: T2.2 complete; T2 continues

Date: 2026-07-13

## Outcome

T2 turns the deterministic diary policy into a broad regression matrix so
manual receptionist testing becomes exploratory evidence rather than the main
way defects are discovered.

## T2.1 Allocation

The existing repository already has a substantial authored golden corpus for
booking classification, route outcomes, confirmation/idempotency, tenancy, and
candidate bounds. T2.1 therefore adds only missing independent surfaces:

- a generated boundary/invariant matrix over interval edges, duration edges,
  active/terminal statuses, date boundaries, ordering, and mutation absence;
- independent authored golden cases that are not generated from the production
  classifier's branching logic; and
- focused E3 UI-contract evidence for no-slots, roster-unavailable, and
  clarification outcomes, including keyboard/focus/live-region semantics and
  absence of confirmation authority.

DeepSeek V4 Flash owns the backend generated matrix. Antigravity/Gemini 3.5
Flash owns the browser/accessibility slice. Sol retains scope, correction,
integration, and protected-master authority. No Conductor or verifier is needed
because the approved roadmap fixes the tranche and the two surfaces are
disjoint.

## Invariants

- no deterministic classifier, proposal, search, or clarification step writes
  an appointment or audit row;
- no candidate lies outside normalized date/time bounds or overlaps an occupied
  practitioner interval;
- half-open interval boundaries remain stable: touching endpoints do not
  overlap, while one-minute intersections do;
- terminal appointments do not create duplicate/overlap authority;
- exact duplicate, overlap, same-day-distinct, roster-unavailable, no-slots, and
  clarification remain distinguishable;
- no blocked/advisory/clarification UI state exposes a confirmation control or
  authoritative-success copy; and
- provider calls, autonomous writes, runtime consultant/triage, deployment, and
  production gates remain closed.

## Evidence Boundary

Backend route replay is E1. Route-intercepted Playwright is E3 UI-contract
evidence and is not E2 non-intercepted backend transport evidence. Generated
tests supplement but do not replace the independent authored T1/T2 golden
corpus.

## T2.1 Result

T2.1 is the first hundreds-scenario deterministic gate. It executes:

- 260 generated half-open interval combinations spanning five existing start
  times, four existing durations, and thirteen requested windows;
- 15 independently authored boundary, date, ordering, route-bound, and
  read-only cases from the DeepSeek worker review;
- the existing 57 classifier and slot-search regression cases; and
- three focused route-intercepted Playwright scenarios for no-slots,
  roster-unavailable, and clarification states.

The generated cases run inside one test node through a query-only session. The
classifier still executes for every combination, any attempted session write
fails immediately, and labelled assertion messages identify the failing
combination. This reduced the generated gate from about 100 seconds with full
DB fixture setup per case to about five seconds without reducing its 260
scenario executions. DB-backed read-only and route truth remain independently
covered by the authored E1 tests.

The UI review exposed and corrected three product defects:

- asynchronous results could leave keyboard focus on the document body;
- the Edit request action targeted the nonexistent
  `bernie-pilot-instruction` element instead of `bernie-instruction-input`;
- a canonical UI view model could collapse `roster_unavailable` into the
  generic blocked state.

Returned results now receive programmatic focus, Edit request restores focus to
the instruction field, and roster-unavailable remains distinct through the
canonical view-model path. No blocked, advisory, no-slot, roster, or
clarification state gained confirmation authority.

## Next Slice

T2.2 should extend the economical generated matrix beyond interval geometry to
terminal/active status, practitioner/location, roster/break, normalized bounds,
and stale-proposal axes. Keep each broad generated matrix fast, and retain
separate authored DB-backed golden cases for semantic and persistence truth.

## T2.2 Allocation

T2.2 concentrates on interactions not covered by the single-axis authored
tests:

- DeepSeek V4 Flash owns a fast exact-match precedence matrix combining
  practitioner, appointment type, location, duration, and temporal-evidence
  axes through the public classifier;
- Antigravity/Gemini 3.5 Flash owns route-intercepted Playwright checks for
  stale, failed, and confirmation-pending proposal states; and
- Sol owns gap analysis, product corrections, integration, protected-master
  authority, and the final decision about whether T2 needs another slice.

Existing DB-backed tests remain authoritative for terminal-status filtering,
roster/break/location query behavior, normalized candidate bounds, stale
confirmation revalidation, audit deltas, and tenancy. Generated query-only
cases must not pretend to replace those persistence and route boundaries.

## T2.2 Result

The exact-match precedence matrix executes 486 labelled combinations across:

- matching or mismatching practitioner;
- omitted, matching, or mismatching appointment type;
- omitted, matching, or mismatching location;
- omitted, matching, or mismatching duration; and
- nine temporal-evidence modes covering both bounds, earliest-only,
  latest-only, no bounds, inside, outside, and endpoint cases.

Together with T2.1, the routine service-level gate now executes 746 generated
classifier combinations in two test nodes. The query-only sessions expose no
write methods, while separate DB-backed tests retain authority for filtering,
persistence, audit, tenancy, and route behavior.

Three new route-intercepted Playwright cases cover stale, failed, and
confirmation-pending proposal states. They prove distinguishable state/copy,
status-region focus, keyboard recovery for stale/failed states, and absence of
confirm controls, requests, success receipts, or completion claims. This is E3
UI-contract evidence, not E2 backend transport evidence.

No product correction was required. Central review corrected an evidence-tier
label and a prose description of a touching-endpoint case; the executable
oracle had already classified that endpoint correctly as non-overlap.

## T2.3 Direction

T2.3 should exercise the remaining persistence-backed route interactions rather
than add another query-only classifier matrix. Combine active/terminal
appointment status, same/other location conflicts, roster presence/absence,
break warnings, and normalized time bounds in a compact DB-backed table. Keep
stale-confirm revalidation as an authored stateful golden case and prove every
search/proposal combination remains non-mutating.
