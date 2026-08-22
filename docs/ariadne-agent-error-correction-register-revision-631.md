# Ariadne agent error and correction register — revision 631

Date: 2026-08-23

<!-- ariadne-agent-error-register-reading
revision: 631
incident_count: 1015
new_incident_ids: AER-1009,AER-1010,AER-1011,AER-1012,AER-1013,AER-1014,AER-1015
open_incident_count: 0
-->

## AER-1009 — Preplanning receipt prose repeated machine-owned Git IDs

Status: `closed_corrected`

The first attempt-007 preplanning runtime state manually repeated task and
protected Git objects in free-form `git_refs_and_worktree` evidence. The
preflight rejected both before planning. The rejected receipt is preserved;
the corrected receipt contains zero manually supplied object IDs and uses only
the builder's machine snapshot.

## AER-1010 — Attempt-007 envelope field names crossed the redaction vocabulary

Status: `closed_corrected`

The first uncommitted wrapper used `start_argv_repair_*` envelope fields. The
base redaction rule forbids any evidence key containing `argv`, so pure
pass/failure tests rejected the projection. The fields were changed to the
closed `start_option_repair_*` vocabulary before commit and all pure tests
passed.

## AER-1011 — Plan-test oracles repeated wrapping sensitivity and contradiction

Status: `closed_corrected`

The first pure plan tests used one raw multiline substring assertion and both
a negative and positive assertion for the same threat phrase. The run failed
before commit. The corrected tests use the normalized plan representation and
one positive claim-boundary predicate.

## AER-1012 — Provider-free manifest selected a direct conftest importer

Status: `closed_corrected`

The first broad provider-free command manually included the database-backed
A5.1 runtime test, which directly imports `tests.conftest`. The admission
runner rejected before pytest collection. The corrected provider-free
selection retained the static API and no-database boundaries and passed
serially.

## AER-1013 — Occupied success projection reached an unadmitted redaction key

Status: `closed_contained`

The sole attempt-007 invocation consumed its authority and ended at
`redaction/forbidden_field`. Deterministic source evaluation reproduces that
failure on
`closed_boundaries.live_secret_existing_hosted_or_product_database_used`.
No retry occurred, no success or attestation was released, the terminal is
immutable and independent inspection found zero owned Docker residue. The
read-only successor must exercise the complete prospective success projection
through redaction before any future occupied plan.

## AER-1014 — Wrapper terminal lost the base cleanup projection

Status: `closed_contained`

Because the redaction exception escaped after base finalization, the wrapper's
fallback terminal recorded `cleanup_status=not_started` rather than the base
cleanup state. Independent Docker inspection proves only zero owned external
resources; transaction semantics and role absence before teardown remain
unproved. The successor must specify a typed post-finalization terminal bridge
without altering the immutable attempt-007 record or authorising a rerun.

## AER-1015 — Closeout lineage was authored as a general graph

Status: `closed_corrected`

The first closeout intent supplied two `builds_on` parents, and the next
revision retained the older attempt node rather than the immediately projected
predecessor. The clockwork rejected both before publication. The corrected
intent contains exactly one parent: the accepted start-option repair that
projected attempt 007. Attempt 006 remains evidence rather than a second edge.

The durable control is to inject the one canonical predecessor from the live
projection instead of asking the caller to author relationship structure.
