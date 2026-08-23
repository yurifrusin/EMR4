# Ariadne agent error and correction register — revision 648

<!-- ariadne-agent-error-register-reading
revision: 648
incident_count: 1132
new_incident_ids: AER-1131,AER-1132
open_incident_count: 0
-->

## AER-1131

The first postpublication combined suite compared the newly advanced live
operation latch with the prior tranche's committed preplanning latch. The
production projection and canonical live-state reading remained valid. The
safety-equivalence test now derives both receipt paths from the same current
latch and retains the historical runtime state only as its size baseline; all
42 focused and 162 combined tests pass after correction.

## AER-1132

The first semantic publication invocation used the system Python launcher
instead of the repository-bound virtual-environment interpreter. The clockwork
rejected `active_interpreter_mismatch` before executing verification or
attempting publication, leaving lease 217 and all canonical files unchanged.
The corrected invocation is bound to `.venv/Scripts/python.exe` and proceeds
only from a new source containing this incident evidence.
