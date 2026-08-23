# Historical Diary measured privacy probe — Yuri summary

Date: 2026-08-24

Timestamp: 2026-08-24T03:42:32.7376775+10:00 (Australia/Brisbane)

## Lay summary

The privacy gate has now been used on real historical Diary material and it
worked. One local run opened 80 snapshots, found clear minute-by-minute motion,
released no private value and cleaned up its private working files. It stopped
short of reuse because the first parser could not yet connect occupied cells
to appointment times.

This is a useful result rather than a failed idea: we now know the trove
contains recoverable workflow changes, and we know exactly which structural
piece is missing. The next tranche will improve only that time-axis mapping,
first with synthetic examples and then with at most one new bounded local run.

## Technical summary

- Decision: `revision_required` (`insufficient_time_mapping`).
- Snapshots: 80 opened, 80 parsed, 0 rejected.
- Structure: 1,120 cell observations, 40 stable records, 118 changes across 79
  adjacent transitions.
- Privacy: 0 source-value leakage; no raw text, filename, path, timestamp, key
  or mapping emitted.
- Linkability: 9/51 unique record shapes and 51/51 unique trajectories; no
  anonymity claim or downstream release.
- Cleanup: owned Word process complete; private manifest and incomplete
  projection removed; no persisted key or mapping.
- Verification: 36 new hostile tests plus 86 unchanged privacy/H5/H15 controls
  pass; one content run and zero automatic content retries.
- Workflow: five contained prepublication lapses are consolidated into one
  register incident rather than five expanded bureaucratic records.
- Authority: local ignored research only. No fixture, memory, provider, model,
  product, database, ordinary-practice, production, Pages or protected-ref
  authority opened.
