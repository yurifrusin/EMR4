# Reception One availability reconciliation threat-model delta

**Status:** frozen for bounded local implementation  
**Date:** 2026-07-21  
**Parent controls:** `docs/security/bernie-reception-one-committed-event-threat-model-delta.md`  
**Authorised event:** `diary.appointment_rescheduled` only

## Scope

This delta covers the client-side extension from appointment-present attention
to a fresh-read reconciliation of the already accepted combined availability,
selection and non-committing proposal flow. It adds no producer, route, event
family, database artifact or mutation authority.

## Threats, controls and evidence

| Threat | Required control | Acceptance evidence |
|---|---|---|
| Event payload is treated as availability truth | Payload is only a signal; obtain the current appointment and rerun the exact authorised slot-search before comparing candidates | Focused source tests and real network trace showing appointment plus slot-search reads |
| A move out of the time window frees a slot but is missed because the event contains only the new time | Prefilter by exact active practitioner after a fresh appointment read; decide consequence only by fresh candidate-set comparison | Same-practitioner moved-window scenario and fresh alternatives evidence |
| Other-practitioner or same-practitioner irrelevant changes create alert noise | Other practitioners are rejected; an unchanged candidate set reconciles silently | Suppression tests and zero-cue browser assertions |
| Freshness-token churn is mistaken for a changed slot | Compare canonical date/start/duration/practitioner/location coordinates rather than freshness token alone | Deterministic candidate identity tests |
| A stale raw candidate survives after a fresh read | If the slot survives, replace the selected raw candidate with the fresh backend candidate before proposal preparation | Surviving-selection state and later proposal-input assertions |
| Occupied selected or proposed slot remains actionable | Clear selected item and proposal result, remove proposal handoff, return to fresh availability and explain that the time is no longer available | Selection and proposal invalidation browser/tests |
| A proposal is automatically rebuilt or confirmed from an event | Event reconciliation performs reads only and may never call proposal preparation, handoff or confirmation | Network allowlist and client primitive guards |
| Slow reconciliation overwrites a newer root, Back action, close or interruption state | Capture initiating projection identity and open/visibility state; discard results if current state changed before completion | Controlled async-race tests |
| Replay, order or burst creates repeated visible effects | Retain accepted event-id/revision deduplication, serial polling, one cue and coalescing | Replay and coalescing assertions |
| Cross-practice disclosure | Existing authenticated practice-scoped feed, signed cursor and forced RLS remain unchanged; fresh appointment and availability reads retain ordinary authorization | Inherited RLS tests and exact database readback |
| Shared-screen cue reveals patient or time | Privacy mode masks patient/time and disables detail reveal; live region remains patient-free | Desktop and smartphone privacy evidence |
| Availability attention becomes a command tunnel | No new bridge operation or endpoint; selection/proposal remain non-authoritative; backend confirmation remains separate and uncalled | API Spine assertions and forbidden-request evidence |

## Residual bounded posture

- Any same-practitioner reschedule can cause one extra bounded availability read
  because the current event deliberately omits its previous time. Unchanged
  candidate results stay silent. Adding previous-time payload fields would be a
  new schema/API decision and is not necessary for this proof.
- Polling latency and in-memory attention controls remain local-proof behavior,
  default-disabled outside the exact harness.
- Candidate comparison proves slot consequences for the current requested
  window only. It is not a general database watcher or production scheduler.
- The backend confirmation path remains the final conflict authority even after
  a candidate survives this reconciliation.

## Stop conditions

Stop and return to Yuri if implementation requires another event family,
previous-time payload expansion, a new API/database artifact, automatic proposal
execution, any appointment mutation, external transport, persistence, provider,
PII/real data, protected/historical evidence, Stage 3B, voice, production,
deployment or release.
