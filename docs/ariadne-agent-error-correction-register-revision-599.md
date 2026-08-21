# Ariadne agent error and correction register — revision 599

<!-- ariadne-agent-error-register-reading
revision: 599
incident_count: 819
new_incident_ids: AER-0810,AER-0811,AER-0812,AER-0813,AER-0814,AER-0815,AER-0816,AER-0817,AER-0818,AER-0819
open_incident_count: 0
-->

This revision note supersedes the unpublished revision-595 through
revision-598 drafts for the attempt-005 readiness closeout. It binds the five
earlier contained readiness observations plus the successor-boundary, three
postrollback regression and incident-vocabulary observations. The canonical
JSON register and pattern report remain clockwork-owned.

## AER-0810 through AER-0814

The PowerShell inventory syntax, self-auditing source guard, historical test
selection, authority-opening shape and authority-opening vocabulary
observations remain as described in revision 594. All were contained or
corrected without a Harness process or provider request.

## AER-0815

The first published successor latch retained the exact narrow
authored-synthetic data boundary but omitted the canonical general
no-product-data boundary required by the standing current-baton consistency
control. The final postpublication assertion failed closed. The generation was
rolled back byte-exactly before attempt-005 preparation, Harness startup or a
provider request. The corrected intent retains both boundaries and adds a
prepared-generation check of the canonical boundary set before republication.

## AER-0816

The first focused run after rollback found that the readiness regression used
operation identity alone to decide whether to recompute its deliberately
non-reusable clockwork reading. Rollback restored the readiness operation but
advanced the live pointer from lease 116 to lease 118, so the recomputation
failed closed with `clockwork_reading_mismatch`. The guard now requires exact
generation and lease equality; a later lease or successor latch verifies the
stored immutable evidence without attempting reuse. No Harness process or
provider request ran.

## AER-0817

The first implementation of that generation-and-lease guard named a
`CLOCKWORK_CURRENT_PATH` subject attribute that does not exist. The focused
test failed closed with `AttributeError` before recomputation. The corrected
test uses the subject's exported `CLOCKWORK_ROOT` joined with `current.json`.
Future cross-module regression coordinates must be resolved from the subject
source before use. No Harness process or provider request ran.

## AER-0818

After the new regression advanced the recorded packet sizes from 9/75 to
10/76, the binding test still asserted the old two counts. The widened packet
failed only on that stale value. The paired assertions now advance with the
evidence, and future test-count changes are treated as one mechanical edit set
covering both the evidence fields and their exact binding assertions. No
Harness process or provider request ran.

## AER-0819

The first correction source described its follow-up incident stages as
`postpublication_verification` and `postrollback_verification`, and described
the rolled-back canonical state as `canonical_rolled_back`. Those values were
clear prose but were outside the register's closed vocabularies. The read-only
clockwork check rejected at `tick_incident_stage` with zero publication. The
observations now use the admitted `closeout` stage and canonical states, and a
complete intent-schema admission is required before the next source commit.
No Harness process or provider request ran.
