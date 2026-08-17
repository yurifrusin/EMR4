# Ariadne agent error and correction register — revision 346

Date: 2026-08-18

Timestamp: 2026-08-18T02:27:10.5565393+10:00 (Australia/Brisbane)

Status: corrected

## Revision

Revision 346 retains 397 bounded known incidents. No incident is open.

- AER-0396 preserves the first Continuity 313 updater's missing test-evidence
  link for a satisfied contract. The exact source-composition test is now
  linked and canonical Compass validation passes.
- AER-0397 preserves the recurrent semicolon-composed updater/readback command
  that masked the updater's nonzero exit with a later successful inspection.
  The corrected updater ran as one standalone captured process; readback ran
  only afterward in a distinct process.
- Neither incident changed the accepted cancellation product candidate,
  protected refs or any live/product authority.

## Boundary

These are closeout Continuity and orchestration-capture corrections only. They
change no cancellation product semantics, backend, API, database, provider or
protected ref and grant no product data, deployment, release or Pages authority.
