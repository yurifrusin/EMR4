# Ariadne Agent Error and Correction Register — Revision 644

Date: 2026-08-23

Timestamp: 2026-08-23T14:16:06.8891174+10:00 (Australia/Brisbane)

Status: `accepted_pending_clockwork_publication`

<!-- ariadne-agent-error-register-reading
revision: 644
incident_count: 1115
new_incident_ids: AER-1110,AER-1111,AER-1112,AER-1113,AER-1114,AER-1115
open_incident_count: 0
-->

## AER-1110 — Closeout used an unindexed descriptive Baton label

The first clockwork dry run used a newly coined descriptive acceptance-row
label instead of an established closed rolling label. The clockwork rejected
it before generation or publication. The corrected intent selects the general
rolling slot and preserves the lineage row unchanged.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1111 — Closeout exceeded the live Baton compaction budget

After the label correction, the second dry run reached the byte-budget guard
and rejected an exhaustive artifact list. The complete inventory remains in
the immutable closeout graph; the live row now carries only four essential
lookup paths.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1112 — Incident observation exceeded its typed tranche-name limit

The third dry run rejected the canonical operation name in an incident's
bounded `tranche` field because it exceeded 120 characters. The observations
now use one stable short alias while retaining the canonical operation ID in
the transaction manifest and evidence paths.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1113 — First source validator rejected canonicalizable CRLF

The first manual source-validation command rejected every carriage return,
which was stricter than the frozen mode: normalize CRLF to LF and reject only
bare CR. The corrected command applied that exact rule and passed all thirteen
source hashes and all thirteen Git-object ancestry bindings.

Origin: operator. Severity: low. Status: corrected and contained.

## AER-1114 — First publication replaced a lineage-bearing active row

The first live publication reused the arrival/check-in relation row. Its four
lookup paths passed the clockwork but removed three literal lineage objects
required by the postpublication consistency contract. The affected test caught
the error; the clockwork restored the immediately previous generation byte
exactly. The corrected publication uses the established general rolling slot.

Origin: operator. Severity: moderate. Status: corrected and contained.

## AER-1115 — Replacement check preceded rollback-lease source binding

The first replacement dry run followed the byte-exact rollback immediately,
before the rollback's monotonic lease-203 pointer had been committed as the
new source. The clockwork rejected `tick_pointer_physical_drift`. The recovery
now binds that pointer in Git before preparing the replacement generation.

Origin: operator. Severity: low. Status: corrected and contained.

## Aggregate reading

The durable register will contain 1,115 corrected or contained incidents and
zero open incidents after clockwork publication. All six new incidents are
corrected or contained; the one live projection was restored byte-exactly.
There was no product change, external call or authority expansion.
