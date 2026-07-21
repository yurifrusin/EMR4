# Sol acceptance — Reception One availability reconciliation

**Decision:** `reception_one_availability_reconciliation_pass`  
**Accepted candidate:** `41ecb386bcb0a6f25a56febbc9fe754ebd7af1d3`  
**Date:** 2026-07-21

## Acceptance finding

The frozen plan and threat delta are satisfied. The existing patient-free
`diary.appointment_rescheduled` signal now drives deterministic fresh-read
reconciliation for one active-practitioner availability, selection or non-
committing proposal projection. A surviving time retains state with a fresh raw
candidate; an occupied time clears selection/proposal, handoff and affected Back
history; unselected material changes refresh; irrelevant and no-consequence
events remain silent.

The client remains read/proposal-only. It creates no event, appointment command,
confirmation, automatic repair or acknowledgement. Event payload time is not
display truth. Projection identity, close and interruption guards prevent stale
async overwrite, and privacy/live-region/cue behavior remains bounded and
memory-only.

## Evidence disposition

- Real Chromium/UI/FastAPI/PostgreSQL evidence passes at five required
  viewports with no interception, no browser write, clean console/network, zero
  overflow and no undersized enabled control.
- Two signed support reschedules produce exactly two audits, idempotency rows
  and patient-free correlated events; one replay deduplicates; RLS and append-
  only probes pass; the exact database and role are removed.
- Exact and inherited populations pass at 13, 165, 211 and 139 cases as
  documented in the closeout.
- Two over-broad legacy location nodes reproduce at untouched source head and
  are not candidate regressions.
- Fresh Gemini 3.5 Flash High returned `pass`, no material finding, and reran 55
  allowed tests plus Node and Ruff.

## Boundary disposition

No API/database/OpenAPI/event-producer or schema surface changed. Other event
families, GraphQL mutation/subscription, provider, PII, protected/historical,
Stage 3B, representative usability, voice, external transport, persistence,
production, deployment, release and autonomous action remain closed.

The Ariadne contract may now change from `gap` to `satisfied`; that records
evidence only and grants no new authority.

