# Ariadne agent error and correction register — revision 647

<!-- ariadne-agent-error-register-reading
revision: 647
incident_count: 1130
new_incident_ids: AER-1129,AER-1130
open_incident_count: 0
-->

## AER-1129

The frozen 151-leaf no-incident label subtracted the 25-leaf observation from
the 176-leaf incident intent but retained its one generated register-revision
acceptance path. The matched review corrected the fully normalized baseline to
150 and the live reduction to 89 leaves / 59.3 percent. Acceptance remains
unchanged because 61 still passes the frozen 100-leaf ceiling.

## AER-1130

The postpublication idempotent `--publish` correctly skipped verification and
canonical mutation, then overwrote the operation's non-canonical evidence pair
with the idempotent reading. Canonical generation, transaction, pointer and
latch remain valid, but the earlier command digests are no longer durable in
that convenience artifact. Repeat `--publish` readback is contained pending
the selected evidence-preservation repair; no digest was reconstructed.
