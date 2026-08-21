# Threat-model delta: repaired-sentinel preactivation source-coordinate diagnosis

Date: 2026-08-21

## New evidence surface

The tranche reads a sanitized failed terminal, Python source, one accepted passing control, and pinned local rc.7 loader source. It writes deterministic source-coordinate evidence only.

## Threats and controls

- **Raw-stream reconstruction:** a stderr digest could be treated as an oracle for guessing the destroyed message. The implementation must never compare candidate messages with that digest or retain message, path, stack, environment or stream content.
- **Execution disguised as diagnosis:** a parser or import check could start Node or load the Harness. The implementation uses Python AST plus a bounded lexical-state scanner and records zero executable-Harness activity.
- **False uniqueness:** several lexical faults or binding drift could be collapsed into one convenient explanation. Acceptance requires exactly one earliest fatal coordinate and fails closed on zero or multiple coordinates.
- **Overclaim from a sufficient defect:** a proven preactivation defect does not prove it is the only later defect. Evidence must say that the coordinate is sufficient for this failure boundary and that later defects remain untested.
- **Control mismatch:** a different package or layout could make the comparison meaningless. Both failed and passing evidence are hash-bound to the same pinned rc.7 materialisation and their exact source authors.
- **Consumed-attempt replay:** the diagnosis must not retry, resume or reinterpret the consumed attempt. The consumed ledger remains immutable and the active contract permits no native process.
- **Workflow drift:** canonical continuity surfaces must be updated only by the clockwork tick, never manually.

## Unchanged boundaries

No product or clinical surface is opened. No provider request, live data, deployment, release, Pages action, protected-ref change or ordinary-practice enablement is authorised.
