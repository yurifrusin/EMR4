# Ariadne agent error and correction register — revision 633

Date: 2026-08-23

<!-- ariadne-agent-error-register-reading
revision: 633
incident_count: 1027
new_incident_ids: AER-1021,AER-1022,AER-1023,AER-1024,AER-1025,AER-1026,AER-1027
open_incident_count: 0
-->

## AER-1021 — Preplanning prose repeated machine-owned Git objects

Status: `closed_corrected`

The first receipt rejected two manually repeated objects before plan writing.
The corrected state leaves exact identities solely to the machine snapshot.

## AER-1022 — New conformance CLI lacked direct-script import bootstrap

Status: `closed_corrected`

The first direct check stopped at sibling imports. The CLI now inserts the
repository root before imports and a direct-path regression test passes.

## AER-1023 — Serial runner received a nested Python command

Status: `closed_corrected`

Pytest treated the forwarded `python` token as a path and collected nothing.
The corrected pytest-only remainder passed all 83 selected tests.

## AER-1024 — Provider-free verification loaded database autouse conftest

Status: `closed_corrected`

Six ordinary-pytest sessions created, truncated and dropped the local authored-
synthetic test schema despite closed database authority. Their results are
excluded. The exact 83-test profile and complete register suite passed through
the no-conftest provider-free entry point.

## AER-1025 — Clockwork-owned incident register was drafted directly

Status: `closed_corrected`

The orchestrator committed a direct register/pattern-report draft before
recognising the ownership violation. A Git revert restored the exact prior
canonical bytes. All incident intake is now supplied only in the clockwork
closeout intent.

## AER-1026 — Post-publication Baton test was selected before publication

Status: `closed_corrected`

The larger pre-closeout suite included `current_baton_consistency`, which
correctly rejected the old live register revision before clockwork publication.
The result is excluded; the test is reserved for the post-publication gate.

## AER-1027 — Revert command manually expanded a short Git object

Status: `closed_corrected`

The first revert command used a manually completed full object that did not
exist. Git changed nothing. The exact object was then copied from `git
rev-parse HEAD`, and the revert succeeded.

The durable control is the one Yuri previously requested: no displayed prefix
is ever completed from memory. Commands that require a commit consume a
machine-resolved full object value.
