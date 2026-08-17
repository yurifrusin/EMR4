# Ariadne agent error and correction register — revision 360

Date: 2026-08-18

Timestamp: 2026-08-18T07:23:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 360 adds AER-0411. The first compact handover/baton/register packet
failed one assertion because the live register row had advanced to the current
AER-0405 through AER-0410 chain while the fixture permanently required the
superseded AER-0399 and AER-0401 names. Compactness and the complete register
suite passed.

The correction requires current revision/count and current correction-chain
endpoints while preserving historical incident detail in the canonical
register and revision documents.

## Population

- incidents: 411;
- corrected or explicitly contained: 411;
- open: 0;
- latest id: `AER-0411`.

No product, data, provider, deployment or protected-ref authority changed.
