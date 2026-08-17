# Ariadne agent error and correction register — revision 330

Date: 2026-08-17

Timestamp: 2026-08-17T10:11:13.1622921+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 330 records 379 bounded known incidents. No incident is open.

- AER-0379 preserves the first durable canonical validation stop. After 233
  passing checks, the live-handover compactness guard found that unchanged
  source HEAD `38660a4a7136094df67b28d5a6ec07ca40c14416` already carried an
  80,040-byte canonical `AGENTS.md` blob and an 80,507-byte Windows CRLF
  checkout against the 80,000-byte live-surface limit.
- The harness implementation had not changed `AGENTS.md`; the result is a
  pre-existing repository-maintenance defect, not a candidate regression.
- One superseded revision-42 incident narrative was replaced by a compact
  pointer to the current register and topic ledger. The checkout is now 78,188
  bytes and 496 lines, and the four acceptance-index tests pass.
- The runner behaved correctly: it durably recorded the first failed command
  and left Ruff, compilation and whitespace commands pending rather than
  masking the failure.

## Boundary

No Raisa product, API, database, migration, provider, credential, deployment,
release, Pages or protected ref changed. Full incident provenance remains in
the canonical register and revision history. `docs/branding/` and every
unrelated untracked file remain preserved.
