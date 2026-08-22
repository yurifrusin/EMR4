# Ariadne agent error and correction register — revision 632

Date: 2026-08-23

<!-- ariadne-agent-error-register-reading
revision: 632
incident_count: 1020
new_incident_ids: AER-1016,AER-1017,AER-1018,AER-1019,AER-1020
open_incident_count: 0
-->

## AER-1016 — Verification manifest named an undiscovered test path

Status: `closed_corrected`

The first small governance selection named a nonexistent current-Baton test
file. Pytest rejected the path before collection and no test or external
action ran. Repository discovery identified the exact current path,
`tests/test_current_baton_consistency.py`, and the corrected selection passed.

The durable control is to generate verification manifests from discovered
repository paths rather than recalled filenames.

## AER-1017 — Serial pytest invocation omitted its argument separator

Status: `closed_corrected`

The first serial-runner command placed `-q` before the runner's required
separator. Its argument parser rejected the command before collection. The
corrected typed form inserted the separator and the selected suite passed.

The durable control is to generate serial-runner invocations from a typed
command structure that owns the separator.

## AER-1018 — Yielded long-running test session was not retained

Status: `closed_corrected`

The first 164-test broader regression run yielded a session identifier inside
the complete execution result, but the orchestration wrapper retained only its
partial text output. The run continued to completion, yet its final exit could
not be read back, so one redundant full regression run was required. The
second run retained and polled the session identifier and passed all 164
tests.

The durable control is to route every potentially long command through one
typed controller that persists and polls the yielded session identifier.

## AER-1019 — Active latch was edited outside its clockwork owner

Status: `closed_corrected`

The orchestrator directly edited the active-operation latch at the diagnosis
plan checkpoint. The clockwork dry run rejected `canonical_drift` before any
publication. The exact previous canonical latch bytes were restored and the
successor state was returned to the clockwork closeout transaction.

The durable control is that every clockwork-owned canonical surface, including
the active latch at named checkpoints, changes only through the single
clockwork writer.

## AER-1020 — Canonical evidence readback rebound to live HEAD

Status: `closed_corrected`

The first postcommit diagnosis check rebuilt canonical evidence against the
new live HEAD rather than its stored full source object, so it rejected its own
previous bytes as drifted. The repair retains the stored 40-character source
binding, proves it remains an ancestor of current HEAD and rebuilds against
that exact object. The focused suite now contains 25 passing tests and
postcommit readback is idempotent.

The durable control is that canonical evidence readback validates its stored
full Git object by ancestry and never silently substitutes live HEAD.
