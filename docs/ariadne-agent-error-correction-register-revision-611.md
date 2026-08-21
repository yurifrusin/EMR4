# Ariadne agent error and correction register — revision 611

Date: 2026-08-22

Status: **three corrected incidents added; none open**

<!-- ariadne-agent-error-register-reading
revision: 611
incident_count: 922
new_incident_ids: AER-0920,AER-0921,AER-0922
open_incident_count: 0
-->

## AER-0920

After the preceding clockwork closeout, the notification-receipt push guard
copied Git's abbreviated display and manually supplied an invented 40-character
expected-origin value. The guard rejected it before any push, so remote and
canonical state were unchanged. The corrected command derived its expected
remote parent directly from `git rev-parse HEAD^`; every later tranche push
used the same machine-derived parent and passed.

## AER-0921

The first isolated-fixture focused suite asserted that the accepted sanitizer
must not contain its internal `code, detail: null` terminal constructor. That
constructor is the source-owned mechanism that guarantees the content-free
terminal and is required. The static suite rejected the assertion before the
single Node attempt. The corrected test requires the constructor and
`PRESET_MOUNT_UNCLASSIFIED` mapping while retaining exact source-hash
verification. All 24 focused tests then passed.

## AER-0922

The first unvalidated clockwork intent contained a manually composed plausible
`recorded_at` timestamp rather than a value copied from the creation clock or
typed evidence. Pre-validation inspection caught it before any canonical
publication. The intent now carries the exact tool-returned Brisbane clock
reading, and the next-operation boundary requires generated timestamps to come
directly from a machine reading.

## Control reading

None of the three incidents consumed a Node, native-Harness, worker, model or provider
attempt. AER-0920 is a direct recurrence of the clerical Git-object class and
shows why push ancestry as well as evidence identity must be a machine reading.
AER-0921 corrected a test that confused an internal typed constructor with raw
detail release. AER-0922 extends the same principle to orchestration time: the
model selects the field but takes its value from the clock. The accepted fixture
then used zero caller-authored Git object IDs and exactly one successful Node
process.
