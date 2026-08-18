# Ariadne agent error and correction register — revision 400

Date: 2026-08-18

Timestamp: 2026-08-18T17:50:47.8378516+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 400 carries forward AER-0454 through AER-0460 and adds AER-0461.

AER-0461 preserves the first rejected Continuity 320 / Compass 302 updater
run. The new node's inherited contract paths were not duplicated into its own
evidence inventory, and the updater named the existing profile-contract test
with an extra `worker` filename segment. Compass validation rejected the state
before rendered-report admission. The graph and Compass JSON had reached the
new revision through the updater's deterministic write path, while its
reentrant revision-320 branch remained available for correction.

The correction adds every inherited contract evidence path to the node's
evidence inventory and binds the exact existing
`tests/test_deepseek_native_harness_emr4_profile_contract.py` path. No provider,
candidate, external runtime or protected ref changed.

## Population

- incidents: 461;
- corrected or explicitly contained: 461;
- open: 0;
- latest id: `AER-0461`.
