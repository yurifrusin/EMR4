# Reception One committed-event vertical — Sol acceptance

**Decision:** `reception_one_committed_event_vertical_pass`
**Date:** 2026-07-21
**Accepted candidate:** `705582b7719bce6f1c5fe5833c1703354b5fa1a3`
**Source:** `be5e01d00b23ef43f7aab8b30f6dbdfa6e858c45`

## Acceptance finding

I accept the bounded Reception One committed-event vertical for the exact
scope Yuri authorized. One actual appointment start/duration change confirmed
through the existing signed update path can append one patient-free
`diary.appointment_rescheduled` event in the same PostgreSQL transaction as
appointment truth, update audit and idempotency completion. A default-off,
authenticated, practice-scoped read feed and a fresh-read client consumer can
then produce one quiet controllable cue in an active patient-timeline or
focused-practitioner projection.

## Gate decisions

| Gate | Result | Evidence |
|---|---|---|
| Frozen plan and threat delta | pass | Exact event, transaction, cursor, privacy, evidence and closed-boundary semantics are implemented without a material fork |
| Atomicity and replay | pass | Success correlation, idempotent replay and injected event-failure rollback tests |
| Database authority | pass | Exact schema constraints, practice-qualified appointment/command/audit links, forced RLS and append-only rejection |
| Delivery boundary | pass | Authenticated GET-only feed, limit 20, signed practice-bound opaque cursor, empty-history first-event coverage and default-off setting |
| Client freshness and relevance | pass | Active-projection membership, fresh appointment plus projection reads, deterministic revision/dedup and unrelated suppression |
| Attention and privacy | pass | Nonmodal bounded memory state, dismiss/snooze/mute/show-context, patient-free live region, masking and Escape focus restoration |
| Real browser | pass | No interception; desktop, tablet and smartphone evidence; zero overflow/small controls; clean console/network |
| Database readback and cleanup | pass | Two exact reschedules, two correlations, one replay, RLS 2/0, append-only rejection, exact marker-verified database and role removal |
| Regression | pass | 20 focused, 213 current combined and clean 139/139 Diary; baseline comparison separates unchanged obsolete historical nodes |
| Independent veto | pass | Fresh Gemini 3.5 Flash High, clean candidate, no material finding, 20 focused rerun plus Node/Ruff |
| Scope | pass | No provider, PII, protected/historical, Stage 3B, voice, new action, external transport, production, deployment or release opening |

No failed acceptance gate was overridden.

## Claim calibration

The browser evidence is `live_local_browser_backend_postgres`; the two existing
update support commands are `live_local_backend_postgres`; stored examples are
`authored_synthetic_local`. This is not provider, production, representative
usability, deployment or release evidence.

The API Spine exception is narrow. GraphQL remains read-only, and there is no
new appointment command, acknowledgement endpoint, subscription, broker,
worker, WebSocket, autonomous action or additional event family.

## Residual boundaries and handoff

This acceptance does not prove availability/selection/proposal invalidation
when a committed reschedule occupies or frees a candidate slot. That is the
recommended next bounded nervous-system proof if Yuri prefers it over the
deferred Reception One visual/interaction synthesis. Both require a fresh
decision. All broader event, participant, provider, data, production,
deployment and release gates remain closed.

Sol High may now complete the check-gated task-branch closeout, protected
integration and baton realignment under the frozen plan.
