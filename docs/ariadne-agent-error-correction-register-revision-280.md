# Ariadne agent error and correction register — revision 280

Date: 2026-08-15

Timestamp: 2026-08-15T05:06:24+10:00 (Australia/Brisbane)

Revision 280 records AER-0319. The register now contains 319 bounded known
incidents, all corrected or contained by an explicit control.

AER-0319 records two closeout-fixture defects found by the first full final
packet. Sol emitted latch status `completed` where the schema admits `complete`,
and global Compass/current-baton tests still asserted the predecessor kernel
node and its old next-work wording. The correction also exposed a compactor
edge case that rejected a refreshed live acceptance row already present in the
historical ledger instead of replacing it by label.

No product source, accepted candidate, provider call, protected evidence,
notification or protected ref changed. The latch now uses the exact schema
enum; the global fixtures bind the accepted editor at Continuity 293 / Compass
275 and the read-only post-editor orientation; same-label index refresh now
replaces the historical row in place. Future closeouts must validate emitted
enums, search all global predecessor fixtures and exercise index refresh before
the aggregate packet.
