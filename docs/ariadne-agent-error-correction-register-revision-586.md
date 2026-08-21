# Ariadne agent error and correction register — revision 586

Date: 2026-08-21
Timestamp: 2026-08-21T13:26:54.8506659+10:00 (Australia/Brisbane)

<!-- ariadne-agent-error-register-reading
revision: 586
incident_count: 772
new_incident_ids: AER-0770,AER-0771,AER-0772
open_incident_count: 0
-->

## AER-0770 — historical latch test was selected after successor advance

The first widened diagnosis run selected a historical attempt-004 test whose
purpose is to require the attempt-004 live latch. The live latch had correctly
advanced to the source-diagnosis successor, so the test failed closed. Rolling
the latch backwards or weakening the test would both be false. The exact test
is now deselected from successor regressions while every other test in its
module remains selected. A durable selection note records the reason.

## AER-0771 — grouped verification reused mnemonic test filenames

A later grouped verification command named two remembered test filenames that
do not exist under those exact paths. Pytest rejected the command before
collection. `rg --files` then supplied the current repository inventory and the
corrected exact-path command passed 58 tests. Future grouped selections are
resolved mechanically from the repository rather than reconstructed from
mnemonic names.

## AER-0772 — closeout contract evidence used the wrong shape

The first read-only clockwork closeout check supplied a plain artifact path in
`contract_evidence`, where the Continuity schema requires structured
cross-contract evidence objects. The prospective projection rejected the input
before commands or publication. This diagnosis makes no cross-contract claim,
so the corrected field is the exact empty list; its ordinary contract artifact
remains in the node evidence and baton acceptance paths.

All three incidents are corrected or contained and none remains open.
