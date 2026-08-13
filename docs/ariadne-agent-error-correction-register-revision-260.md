# Ariadne agent error and correction register — revision 260

Date: 2026-08-13

Timestamp: 2026-08-13T19:35:39+10:00 (Australia/Brisbane)

Revision 260 records and corrects AER-0293. The register now contains 293
bounded known incidents with none open.

The first CF-D2 event/cue parse-and-catalogue attempt passed its contract,
source, cached-image and exact owned-container profile gates, then stopped in
the readiness loop. `pg_isready` had accepted the socket while the immediately
following authenticated PostgreSQL-major query still returned nonzero. The
harness incorrectly raised that transient outside the bounded readiness loop.
No artifact byte was executed, no catalogue was created, no row or product
data entered the server, and exact owned-container cleanup passed.

This recurs the readiness family first recorded by AER-0100. The correction is
narrow: a nonzero or malformed authenticated version probe now resets the
consecutive-observation counter inside the already frozen startup deadline.
Only three consecutive paired socket and authenticated PostgreSQL-16
observations open artifact execution. Focused tests passed before a fresh
owned-container attempt.

Attempt 002 then passed the readiness gate, streamed the exact accepted 12,022
artifact bytes, admitted the exact catalogue, proved zero rows and completed
verified cleanup. The initial failure evidence remains immutable; it is not
overwritten or reclassified as a database or artifact defect.
