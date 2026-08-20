# Ariadne agent error and correction register — revision 570

Date: 2026-08-20

<!-- ariadne-agent-error-register-reading
revision: 570
incident_count: 675
new_incident_ids: AER-0668,AER-0669,AER-0670,AER-0671,AER-0672,AER-0673,AER-0674,AER-0675
open_incident_count: 0
-->

This revision records eight corrected procedure and governance incidents from the DeepSeek
native Harness provider-free complete-composition native-boot recovery. The
canonical machine register now contains 675 incidents and none is open.

## AER-0668 — unadmitted mock-Node tests in an execution-sensitive tranche

Sol ran a widened neighbouring suite before and after the sole native boot.
Three historical tests in each run started synthetic Node drivers even though
the frozen plan prohibited Node from deterministic checks and unit tests. The
drivers did not execute `lib/bin.js`, `--profile headless`, the Harness or
provider code and did not change the immutable terminal, but their six process
starts were outside the admitted test boundary.

Correction: the verifier and closeout manifests excluded the three exact
modules. Future execution-sensitive manifests must statically classify
`subprocess`, `Popen` and resolved Node launch sites and exclude them unless the
frozen plan explicitly admits their executable boundary and count.

## AER-0669 — verifier substituted the wrong incident module names

Gemini correctly adjudicated AER-0668 as a contained P3 procedure incident but
named three nearby non-spawning test modules. Direct source evidence shows the
actual modules were the effective-tool native-boot proof, HMR-boot proof and
preterminal-observable recovery-boot tests.

Correction: Sol preserved the first immutable veto, corrected the exact names
in acceptance and closeout, and did not spend a second provider call on a
narrative-only restatement. Future incident-review packets must bind exact
filenames or identifiers and returned receipts must echo them without
substitution before acceptance.

## AER-0670 — next-operation legacy boundary token omitted

The first clockwork publication expressed the next default-off authority with
narrower controls but omitted the exact compatibility token
`no_ordinary_practice_enablement_feature_flag_allowlist_or_command_mounting`.
The retained 630-test postpublication session found one exact current-baton
consistency failure.

Correction: lease 58 is preserved and rolled back byte-exactly at lease 59.
The corrected intent adds the exact token. Future closeouts must validate the
prospective next latch against the complete compatibility-boundary subset, not
only semantically equivalent tranche-specific wording.

## AER-0671 — accepted operation selected again as successor

Lease 60 selected the already accepted default-off route-adapter operation as
the next tranche. Fresh five-source rehydration found the conflict before any
worker or product action; lease 61 restored the immediately previous generation
byte-for-byte.

Correction: clockwork construction now rejects a next operation ID already
present anywhere in the validated Continuity graph, and the live successor test
compares the graph, latch and Baton rather than Markdown filenames.

## AER-0672 — invalid parallelism leverage vocabulary

The first stale-successor recovery receipt used an invented
`conditional_independence` value instead of the configured parallelism
vocabulary and failed closed before planning or dispatch.

Correction: the rejected receipt is retained, the corrected receipt uses exact
`required_independence`, and the preflight remains the admission boundary.

## AER-0673 — historical successor guard was hard-coded

The prior repository guard looked only for plan filenames in Markdown and one
historical successor name. It could not prevent a later recorded operation from
being selected again.

Correction: the guard now uses exact live graph identities and the clockwork
enforces the same predicate before it can build a generation.

## AER-0674 — incident vocabulary validated too late

The first corrected check at full source
`64d319d7771c3fe60952e70ec17b70248079673c` reached prospective register
projection before rejecting an invalid stage value. Whole-packet inspection
found adjacent severity, causal-claim and correction-status mismatches that
would otherwise have caused serial reruns.

Correction: `validate_tick_intent` now validates every register-bound date,
identifier, enum and constant up front, and its vocabulary is test-bound to the
canonical register schema.

## AER-0675 — human register revision lagged the machine register

Lease 62 correctly published register revision 570 with 674 incidents through
AER-0674, but this human revision still described the earlier 670-incident
draft through AER-0670. Dedicated postpublication readback found the mismatch
before task-branch push; lease 63 restored the prior generation byte-for-byte.

Correction: every incident closeout revision now carries one exact
machine-readable register reading. Clockwork compares its revision, incident
count, ordered new incident IDs, open count and headings with the complete
prospective machine register before publication.

All eight incidents have accepted correction states and `corrected` status. They do
not reopen the sole successful Harness attempt, authorise a retry, or change
any product, data, production, deployment, Pages or protected-ref boundary.
