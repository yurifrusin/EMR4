# Ariadne agent error and correction register — revision 625

Date: 2026-08-22

Status: `accepted_closed_reading`

<!-- ariadne-agent-error-register-reading
revision: 625
incident_count: 984
new_incident_ids: AER-0983,AER-0984
open_incident_count: 0
-->

This revision records two bounded post-terminal control-plane omissions from
the preceding materialization closeout. Both are corrected and neither is
open.

## AER-0983 — idempotent readback omitted the failure-terminal branch

The materialization controller's provider-free readback validated a passing
evidence file but rejected its schema-valid consumed failure terminal. The
first post-closeout focused check exposed the omission. The readback now
validates either mutually exclusive accepted evidence or consumed failure plus
the exact consumed/process envelopes, without starting a process.

## AER-0984 — guessed a second nonexistent clockwork mode

After already correcting `--execute` to the closed `--publish` vocabulary, the
orchestrator later guessed `--check-live`. Argument parsing rejected before any
state mutation. The correction is to use the typed latch and clockwork tests
for live-state validation and never invent CLI modes outside the parser-owned
`--check`, `--publish`, `--rollback` set.
