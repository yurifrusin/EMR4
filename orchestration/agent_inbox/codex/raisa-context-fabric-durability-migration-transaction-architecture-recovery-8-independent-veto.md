# Recovery-8 independent durability migration/transaction architecture veto

Date: 2026-08-06

Candidate: `194d5f329e8f84ae411e5cd6492076ae6a21a894`

## Result

The independent exact-path review confirmed the structural/body sequencing,
exact admission-owner surface, temporal all-UPDATE cases, savepoint calibration,
event-retention independence and API Spine tests. The authorized four-module
packet passed all 155 tests. It nevertheless returned `revision_required` for
one P1 machine-boundary defect:

- prose required a structural renderer to omit trigger declarations and execute
  grants, but the machine boundary explicitly named only omitted entry-point
  functions, omitted trigger functions and non-effective grants. Because all
  thirteen trigger declarations remain catalogued, a renderer needed an exact
  positive prohibition rather than inference from prose.

No P0 or P2 finding was reported. Two allowlisted descriptive API overview
paths were absent; the reviewer did not substitute or discover other paths and
used only the remaining authoritative API artifacts and their tests. That
packet error is recorded separately and grants no authority.

## Terminal decision

`DECISION: revision_required`

No SQL, migration, database, source, runtime, provider, patient/product-data,
command, deployment, release, Pages or protected-ref authority was opened.
