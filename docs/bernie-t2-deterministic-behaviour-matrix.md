# T2 Deterministic Bernie Behaviour Matrix

Status: T2.1 in progress

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
