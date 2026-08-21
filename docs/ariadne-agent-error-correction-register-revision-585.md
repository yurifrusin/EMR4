# Ariadne agent error and correction register — revision 585

Date: 2026-08-21
Timestamp: 2026-08-21T12:24:55.9790653+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 585
incident_count: 769
new_incident_ids: AER-0760,AER-0761,AER-0762,AER-0763,AER-0764,AER-0765,AER-0766,AER-0767,AER-0768,AER-0769
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

## AER-0764 — checkpoint prose exceeded its closed bound

The first read-only occupied-checkpoint check rejected its completed-stage
text because it exceeded the schema's 500-character bound. No transaction or
command began. The same facts were reduced to a bounded string and the next
read-only check passed.

## AER-0765 — incident intake bypassed clockwork ownership

The first implementation commit directly updated the canonical register,
pattern projection and AGENTS register row. The occupied-checkpoint dry run
correctly returned `canonical_drift`. Those three surfaces were restored
byte-for-byte from the active generation in a descendant commit. The incident
observations are now supplied only through the version-2 closeout intent, so
clockwork remains their exclusive publisher.

## AER-0766 — a yielded test process lost its captured exit reading

One long grouped provider-free test call yielded after showing 96 percent
progress, but its caller had not exposed the returned session identifier. A
process-absence read proved it had ended, but the exit value was unavailable.
The remaining test file was rerun separately with explicit exit capture and
passed. Later long calls always expose and retain the session identifier.

## AER-0767 — prelaunch receipt used a non-admitted probe method

The first occupied-prelaunch receipt described the native Harness observation
with method `native_harness_prelaunch`, outside the preflight's fixed adapter
method vocabulary. Preflight rejected dispatch before any process. The
corrected receipt uses the admitted `synthetic_fixture` method.

## AER-0768 — disposable synthetic Git was mislabelled as a handoff worktree

The same rejected prelaunch receipt supplied the standalone synthetic baseline
as an Ariadne workspace handoff receipt. Preflight correctly reported it was
not at the task handoff and not clean under that false model. The corrected
receipt makes no handoff-workspace claim; the exact synthetic root remains
bound by its preparation and checkpoint artifacts.

## AER-0769 — closeout node supplied two direct parents

The first attempt-004 closeout intent supplied both the readiness and
controller-convergence nodes as direct `builds_on` parents. The transactional
manifest permits exactly one direct relationship and the read-only clockwork
check rejected the draft before commands or publication. The corrected intent
keeps only the readiness parent, which already preserves the controller
lineage.

All ten incidents are corrected or contained and none remains open.
