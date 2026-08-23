# Governance clockwork typed serial-continuation state projection rehearsal

Date: 2026-08-23

Timestamp: 2026-08-23T19:41:32.8076827+10:00 (Australia/Brisbane)

Result: `accepted_pending_semantic_publication`

## Conclusion

Retain the typed serial projection. It replaces the repeated complete runtime
state with a 14-line intent while preserving the existing receipt and its hard
safety projections.

The live candidate reduced caller leaves from 114 to 9 (92.1 percent). The
complete intent-plus-receipt pair fell from 327 to 135 lines (58.7 percent) and
from 16,191 to 6,330 bytes (60.9 percent). No expanded runtime-state file was
written.

## Safety equivalence

The typed and manual paths produce equal status, settings fingerprint,
five-source inventory, active-operation projection, terminal guard, dispatch
decision, lane ID/disposition/leverage reading, machine Git binding, Git
snapshot and Git-object resolution.

The compact interface cannot express worker dispatch, a positive worker
assignment, free-form lane rationale, a caller-authored latch or caller-authored
Git evidence. It derives all declared adapter observations and managed empty
worker-slot shapes, then sends the complete in-memory state through the existing
validator. The historical full-state path remains available for non-serial or
occupied work.

## Honest build cost

The one-time implementation added 390 source lines net and 295 test lines. That
is a real maintenance cost. Against the observed saving of 188 input lines per
serial receipt, the source-only cost is recovered after roughly two ordinary
serial continuation events; the stronger justification is removal of 105
repeated caller choices at every event.

Forty-two focused preflight tests, the combined 162-test orchestrator/governance
suite and Ruff pass without a correction round. No product rerun, provider call,
worker dispatch or protected-ref movement occurred.

## Harness lesson retained

The DeepSeek work supplied the right abstraction boundary: synchronize
orchestrator and worker harnesses at coarse lifecycle readings, not at every
turn or tool call. This projection improves the orchestrator side of that
boundary without claiming that the native Harness is currently qualified for
occupied EMR4 work.

## Next observation

Use the projection at ordinary serial continuation events and retain their
compact intents plus receipts. After three live events, compare rejection rate,
pair size and any missing non-default decision with this baseline. Only then
decide whether to adjust the preset or separately study full-suite cadence.

All worker/provider, product, patient/clinical data, runtime, deployment,
release, Pages, protected-evidence and protected-ref surfaces remain closed.
