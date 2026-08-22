# Ariadne agent error and correction register — revision 634

Date: 2026-08-23

<!-- ariadne-agent-error-register-reading
revision: 634
incident_count: 1024
new_incident_ids: AER-1024
open_incident_count: 0
-->

## AER-1024 — Provider-free verification loaded the database autouse conftest

Status: `closed_corrected`

Six otherwise-passing ordinary pytest sessions loaded `tests/conftest.py`.
Its session engine and autouse cleanup fixture therefore created, truncated and
dropped the local authored-synthetic `gp_pms_test` schema even though this
tranche closed database authority. No product, patient or clinical data was
used, and no occupied rehearsal ran, but the six results are not provider-free
evidence and are excluded.

The exact 83-test candidate profile and complete register suite were rerun
through `scripts.ariadne_provider_free_pytest`, which disables repository
conftest, plugin autoload, inherited pytest options and database configuration.
Both replacement profiles passed.

The durable control repeats the accepted AER-0358 rule: when database authority
is closed, every test command must use the provider-free entry point. Ordinary
or serial pytest is inadmissible even when the selected files appear pure.
