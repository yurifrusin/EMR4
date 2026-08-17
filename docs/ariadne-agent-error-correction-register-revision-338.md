# Ariadne agent error and correction register — revision 338

Date: 2026-08-17

Timestamp: 2026-08-17T16:55:41.3070627+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 338 retains 385 bounded known incidents. No incident is open.

- AER-0385 records a low-severity recurrence of the known configured-leverage
  vocabulary mismatch: the first compatibility-review preplanning state used
  invented value `positive_independence` for the reserved Gemini lane.
- The deterministic preflight returned `revision_required` before plan freeze,
  worker dispatch or product-source change. Its failed receipt is preserved.
- The corrected runtime state uses configured value `required_independence`;
  a distinct v2 receipt must pass and be read back before planning continues.

## Boundary

The correction changes orchestration evidence only. It grants no product,
data, provider, database, deployment, release, Pages or protected-ref
authority.
