# Ariadne agent error and correction register revision 113

Date: 2026-08-08

Status: accepted register correction

Revision 113 adds AER-0136 and brings the register to 136 bounded incidents.

## AER-0136 - invalid adapter observation method

The first pre-dispatch state for the function-coordinate veto used descriptive
method `operator_selected_transport` for the Antigravity adapter instead of
the registered `agy_cli_observation` method. The deterministic receipt builder
returned `revision_required` and `worker_dispatch_permitted: false`; no
verifier or model call occurred.

The rejected state and receipt remain immutable. A distinct replacement copies
the exact method identifier from the accepted same-adapter pattern and must
pass before dispatch.
