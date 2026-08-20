# Ariadne agent error and correction register — revision 578

Date: 2026-08-21

Timestamp: 2026-08-21T07:35:11.0925861+10:00 (Australia/Brisbane)

Status: `prospective_clockwork_reading`

<!-- ariadne-agent-error-register-reading
revision: 578
incident_count: 732
new_incident_ids: AER-0726,AER-0727,AER-0728,AER-0729,AER-0730,AER-0731,AER-0732
open_incident_count: 0
-->

This revision adds seven contained observations from the native-Harness
attempt-003 tranche to revision 577's 725 incidents. The exclusive clockwork
derives the canonical register; this reading must match 732 total incidents,
latest `AER-0732`, and zero open incidents.

## AER-0726 — the first preplanning state recalled an invalid lane disposition

The preplanning receipt rejected `deferred`, which is not in the orchestrator's
admitted lane-disposition vocabulary.

Correction: the Gemini lane uses the schema-owned `reserved` coordinate and
the corrected receipt passed before planning.

## AER-0727 — the first candidate receipt omitted adapter observations

The first candidate precommit state omitted the required declared-adapter
inventory, so preflight rejected it before commit or dispatch.

Correction: the corrected state records every declared adapter and passed.

## AER-0728 — a test selection crossed an immutable historical equality boundary

An over-broad descendant test selection ran two immutable historical-report
equality checks that correctly rejected controller-source drift.

Correction: the frozen plan excludes historical regeneration/equality nodes
and uses focused descendant ordering tests.

## AER-0729 — prelaunch misprojected the synthetic process as a handoff worker

The first occupied prelaunch state represented the synthetic native process as
an assigned Ariadne repository worker, which required an incompatible
workspace receipt.

Correction: the corrected state keeps the native lane planned until controller
dispatch and leaves Ariadne assignment/workspace inventories empty.

## AER-0730 — the native process exited before HMR with no classified cause

Exactly one native Harness attempt exited before the first HMR event with zero
provider requests. The recovered sidecar safely recorded
`unclassified_nonzero_exit`.

Correction: the attempt is consumed, cleaned up and routed to provider-disabled
source-static diagnosis without retry.

## AER-0731 — the first closeout intent used an untyped authority opening

The first read-only clockwork closeout check rejected one prose
`authorized_openings` entry before any canonical write.

Correction: the intent uses separate typed `model-runtime` and `provider-call`
boundary/source objects bound to the committed plan.

## AER-0732 — the first human register reading omitted machine syntax

After the authority-opening repair, the next read-only clockwork check rejected
the prospective revision note because it lacked the exact machine reading
comment and `## AER-nnnn` heading sequence.

Correction: this revision now carries the clockwork-derived count/ID comment
and one ordered heading for each prospective incident before the check reruns.

All seven observations are corrected or contained. None confer comparative
model scoring, occupied retry, product, data, database, production,
deployment, Pages or protected-ref authority.
