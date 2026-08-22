# Ariadne agent error and correction register — revision 633

Date: 2026-08-23

<!-- ariadne-agent-error-register-reading
revision: 633
incident_count: 1023
new_incident_ids: AER-1021,AER-1022,AER-1023
open_incident_count: 0
-->

## AER-1021 — Preplanning prose repeated machine-owned Git objects

Status: `closed_corrected`

The first repair preplanning state manually repeated the task and protected Git
objects in its free-form ref note. The orchestrator preflight rejected both
before plan writing or implementation. Removing the prose identities allowed
the same authority state to pass from the builder's exact machine snapshot.

The durable control is already executable: continuation receipts require zero
manually supplied Git objects and source exact ref values only from the machine
snapshot.

## AER-1022 — New conformance CLI lacked its direct-script import bootstrap

Status: `closed_corrected`

The first direct-path conformance check stopped at sibling-package import. No
evidence, provider, Docker or database action occurred. The CLI now inserts the
repository root before sibling imports and has a direct-path regression test;
the corrected command and focused suite pass.

The durable control is to include the established import bootstrap and a
direct-path smoke test in every new sibling-importing repository CLI.

## AER-1023 — Serial runner received a nested Python command

Status: `closed_corrected`

The first broader invocation put `python -m pytest` after the serial runner's
separator. Pytest treated `python` as a path and rejected the request before
collection. The corrected pytest-only remainder acquired the lock and passed
all 83 selected tests.

The durable control is a typed serial-runner command with runner options, one
separator and a pytest-only remainder vector.
