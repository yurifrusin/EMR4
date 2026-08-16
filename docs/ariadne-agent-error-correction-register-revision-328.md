# Ariadne agent error and correction register — revision 328

Date: 2026-08-17

Timestamp: 2026-08-17T09:01:00.4324287+10:00 (Australia/Brisbane)

Status: corrected and contained

## Revision

Revision 328 records 377 bounded known incidents. No incident is open.

- AER-0377 preserves the occupied DHI-S07 stop after the evidence-minter owner
  was corrected. The manual probe still omitted the exact signed evidence from
  its nested proposal, so the accepted adapter correctly blocked it before the
  physical RLS boundary with `signed_confirmation_evidence_invalid`.
- The occupied lifecycle and two non-sensitive response-class diagnostics each
  verified exact cleanup and zero surviving labelled resources. Only HTTP
  status, typed block code and receipt absence were printed locally.
- The repair copies the same evidence into the nested proposal and strengthens
  the provider-free regression to require exact nested/top-level equality.

## Boundary

No product source, API, schema, command meaning, database authority, provider,
deployment state or protected ref changes. `docs/branding/` and every unrelated
untracked file remain preserved.
