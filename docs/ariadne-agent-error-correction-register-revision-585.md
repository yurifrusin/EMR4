# Ariadne agent error and correction register — revision 585

Date: 2026-08-21
Timestamp: 2026-08-21T12:24:55.9790653+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 585
incident_count: 763
new_incident_ids: AER-0760,AER-0761,AER-0762,AER-0763
open_incident_count: 0
-->

## AER-0760 — grouped verification named a non-existent test

The first provider-free grouped verification command named a generic
structured-diagnostic controller test file that does not exist in the current
repository. The strict provider-free runner rejected that path before pytest
collection, so it launched no Harness, broker, worker, model or provider. The
test inventory was then resolved with `rg --files`, and the corrected command
used only exact existing paths. Future grouped commands derive path selection
from that inventory reading.

## AER-0761 — no-retry guard contradicted required evidence vocabulary

The first attempt-004 focused test prohibited the substring `retry` throughout
the runner while also requiring its mandatory `automatic_retry_count` field.
The first collected run therefore rejected the test's own contradictory
assertions. The guard now checks the behavior structurally: one Harness launch,
no unbounded loop, zero automatic retry count, false resume permission and zero
fallback count. The corrected 44-test provider-free group passes.

## AER-0762 — register draft used an unadmitted stage

The first revision-585 register draft labelled both new incidents with the
descriptive stage `verification`; the register schema admits the more precise
`deterministic_verification`. Schema validation rejected the draft before the
pattern report was written. Both rows now use the admitted value, and the
schema remains the executable vocabulary reading rather than a memory burden.

## AER-0763 — topical links did not satisfy attempt-peer identity

The second register draft linked AER-0762 to the two test incidents because
they were topically related. The deterministic validator correctly requires
related IDs to satisfy its attempt-peer rule and rejected that draft before
publication. The invalid links are removed; independently identified attempts
retain empty related-ID lists.

All four incidents are corrected and none remains open.
