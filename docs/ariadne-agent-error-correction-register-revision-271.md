# Ariadne agent error and correction register — revision 271

Date: 2026-08-14

Timestamp: 2026-08-14T23:32:15+10:00 (Australia/Brisbane)

Revision 271 records AER-0310. The register now contains 310 bounded known
incidents, all corrected or contained by an explicit control.

AER-0310 records a recurrence of the exact source-binding error already
preserved by AER-0301. Immediately after cherry-picking the one-file test
candidate, Sol expanded displayed short hash `d1544bb4` into a nonexistent full
hash in the uncommitted active-operation latch instead of resolving the Git
object first.

No receipt, acceptance or Git action used that value. Sol ran `git rev-parse
HEAD`, obtained exact object `d1544bb40602c017c35cb7d3c50250d4c312c9c1`,
and corrected both latch occurrences before deterministic admission. Candidate
source and all refs remained unchanged.

The recurrence strengthens the existing control: every full Git object ID in a
receipt, latch, acceptance or source-binding claim must be copied from an exact
Git command result. A displayed short hash must never be manually completed.
