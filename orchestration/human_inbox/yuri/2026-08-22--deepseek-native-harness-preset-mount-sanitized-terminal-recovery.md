# DeepSeek native Harness sanitized-terminal result

Date: 2026-08-22

Timestamp: 2026-08-22T07:43:26.3147932+10:00 (Australia/Brisbane)

## Lay summary

The experiment achieved something useful even though it did not reach the exact
new checkpoint we wanted. One real native DeepSeek Harness process was kept
inside the deterministic cage: it made no DeepSeek model call, started no
worker task, touched no product data and returned a finite named failure instead
of disappearing into an opaque timeout.

Our outer controller then rejected that valid bounded result because its schema
name did not match the name emitted by the runner, and a second controller bug
interrupted cleanup. I recovered the result without rerunning the Harness,
removed the exact leftover disposable directory, and added regression controls.

The honest conclusion is that substantial orchestrator control is emerging,
but the new preset-mount bridge is not yet proved inside the native runtime.

## Technical summary

- Consumed native candidate:
  `c1ae13df334dfdffefb229c3ae5a502a7251451c`.
- Accepted recovery source:
  `05a721a075a96a5e248818371d7bdfc8e136c792`.
- Native terminal: `preset_composition_failure_attributed` /
  `EFFECTIVE_TOOL_COMPOSITION_UNCLASSIFIED`.
- Native process count: one; retry/resume: zero.
- Turn, worker, model/provider, network, database, Docker and target counts:
  zero.
- Recovery process count: zero Node/native Harness processes.
- Cleanup: zero retained diagnostic roots and zero owned Node processes.
- Register: revision 608, 907 bounded incidents, none open.

Next I will reconcile the exact generated and installed composition sources
without starting another native process. That should identify the narrowest
source-owned correction before any later separately authorised rehearsal.
