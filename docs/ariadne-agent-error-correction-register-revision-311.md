# Ariadne agent error and correction register — revision 311

Date: 2026-08-16

Timestamp: 2026-08-16T17:18:00+10:00 (Australia/Brisbane)

## Result

Revision 311 preserves 358 bounded known incidents. All are corrected or
explicitly contained; none is open.

This revision adds AER-0358. During independent admission of the provider-free
delete-confirm response architecture, Sol used ordinary repository pytest and
then the serialized repository pytest launcher. Both load the autouse
`tests/conftest.py` database fixture. Three passing sessions therefore created,
truncated and dropped the local authored-synthetic `gp_pms_test` schema even
though the tranche explicitly closed database execution.

No product database, product/patient/clinical data, provider, credential,
external network or protected ref was accessed. The local test-schema teardown
completed after each session. The affected results are replaced by a distinct
provider-free profile.

The correction adds `scripts/ariadne_provider_free_pytest.py`. It accepts only
literal repository-relative `tests/*.py` paths, forces `--noconftest`, disables
plugin autoload and the pytest cache, clears inherited pytest options, omits
database/credential environment and invokes pytest with `shell=False`.
`evidence_led_workflow.yaml` now makes that entry point a hard control whenever
database authority is closed. Its focused controls and the replacement
architecture/profile population pass without the repository conftest lock
message or any database fixture.

## Boundary

This is a workflow-scope incident, not a product-data or provider event. It
does not weaken the ordinary repository database tests; it separates them from
static/provider-free tranches that have no authority to run them.
