# Ariadne agent error and correction register revision 140

Date: 2026-08-09

Status: bounded register correction candidate

Revision 140 adds AER-0165 and brings the register to 165 bounded incidents
with zero open incidents.

## AER-0165 — historical evidence compared with a newer mutable attempt

The complete JSON-key-order deterministic packet exposed one test-only
continuity defect. The immutable attempt-025 preservation test treated the
existence of the optional mutable current-evidence file as proof that it must
also contain attempt 025. The file correctly contained the newer attempt 026,
so two valid evidence records were compared byte-for-byte and the packet
failed.

The correction parses the optional mutable evidence and compares bytes only
when its exact attempt identity equals the immutable historical attempt. A
missing or newer mutable alias cannot invalidate historical preservation.
Future immutable-to-mutable evidence comparisons must bind attempt or
generation identity before equality; path existence alone is insufficient.
