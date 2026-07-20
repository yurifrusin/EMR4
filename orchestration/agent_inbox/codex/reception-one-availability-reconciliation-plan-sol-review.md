# Reception One availability reconciliation plan — Sol review

**Decision:** `plan_pass`  
**Date:** 2026-07-21  
**Source:** `e469fd60d37ab536152eda8e2cc4997431817110`

## Finding

The plan is implementable inside Yuri's explicit authorization and the merged
baton. It reuses the exact accepted `diary.appointment_rescheduled` producer,
authenticated feed and existing appointment/availability/proposal reads. It
adds no API route, event family, database artifact, appointment action or
confirmation authority.

The material reconciliation rules are sufficiently deterministic:

- current practitioner match permits only a fresh availability read;
- canonical candidate comparison, never the event payload, determines visible
  consequence;
- unchanged results remain silent;
- a surviving selection/proposal remains intact and its selected raw candidate
  is refreshed where applicable;
- an occupied selected/proposed time clears invalid state and returns to fresh
  alternatives; and
- async results cannot overwrite newer user or interruption state.

The required threat delta, real browser/database evidence, fresh independent
veto, Ariadne gap-to-satisfaction transition and protected integration gates
are explicit. Provider, PII, protected/historical, Stage 3B, voice, broader
events, external transport, production, deployment and release boundaries
remain closed.

Sol may proceed with bounded implementation after a passed preimplementation
receipt. Any requirement for a new event schema, producer, route, migration or
automatic proposal action is a stop condition rather than an implementation
detail.
