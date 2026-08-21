# Ariadne agent error and correction register — revision 602

Date: 2026-08-22

Timestamp: 2026-08-22T03:42:19.3682524+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 602
incident_count: 873
new_incident_ids: AER-0868,AER-0869,AER-0870,AER-0871,AER-0872,AER-0873
open_incident_count: 0
-->

This revision binds six corrected incidents from the accepted native agent-
factory closed-subcoordinate diagnostic and its prospective closeout. The
clockwork owns the canonical JSON register and pattern report; this note
supplies the prospective human-readable reading for one atomic projection.

## AER-0868

The generated Markdown report used a guessed static timestamp that was still
in the future when the single attempt completed. Its exact bytes remain
preserved, but the timestamp field is rejected by a typed metadata-rejection
artifact. The machine-recorded launch time in the evidence remains
authoritative, and the terminal/counter/cleanup claims are unchanged. Future
generated narrative timestamps must come from the creation clock or reuse an
already typed evidence timestamp; they may not be guessed.

## AER-0869

The first prospective clockwork intent placed ordinary file-path strings in
the graph's structured `contract_evidence` field. Projection validation
rejected before commands or publication and canonical state remained
unchanged. The contract/schema paths remain in `evidence.artifacts`, while
`contract_evidence` is empty. Future closeouts route ordinary paths through the
artifact inventory and reserve `contract_evidence` for schema-valid structured
objects.

## AER-0870

The second prospective clockwork intent treated two new observations as two
register-revision increments and therefore named revision 603. The clockwork
rejected the reading before commands or publication because the canonical
revision was 601 and one transaction must produce revision 602. The corrected
reading separates the per-transaction revision from the per-observation
incident population: revision 602, incident population 870 and latest incident
AER-0870.

## AER-0871

The first combined provider-free focused/evidence test run called the accepted
deterministic check without its explicit cache-root parameter. The wrapper had
correctly removed `LOCALAPPDATA`, so the test failed with the typed
`localappdata_missing` guard error before any native process was created. The
accepted execution source remains unchanged. The repaired closeout manifest
runs the unchanged test through no-conftest pytest, retaining the accepted host
cache-location binding without loading the repository conftest. Provider-free
wrapper suitability must be checked against bound local-resource requirements
before verifier selection.

## AER-0872

The first AER-0871 correction altered the focused test that the diagnostic
contract binds in `implementation_bytes`. The next deterministic run correctly
rejected with `implementation_digest_mismatch` before any native process was
created. The test was restored byte-for-byte. The environment-sensitive
verification choice now lives in the mutable closeout command manifest as a
no-conftest pytest invocation. After an occupied attempt, every
implementation-bytes path remains immutable.

## AER-0873

The third prospective clockwork intent used two descriptive incident
categories outside the register's closed vocabulary. The clockwork rejected
with `tick_incident_category` before commands or publication. Both observations
now use the admitted `operator_error` coordinate. Future category selection
must read `EXPECTED_ORIGIN_BY_CATEGORY` directly; free-form category labels are
forbidden.
