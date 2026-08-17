# Ariadne agent error and correction register — revision 362

Date: 2026-08-18

Timestamp: 2026-08-18T07:34:51+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 362 adds AER-0413. The first arrival/check-in closeout packet found
that Compass and Current Baton fixtures still pinned the predecessor position
and prose after the accepted Continuity advance. The same packet found that
the updated live handover had crossed its 80 KB compactness guard.

The correction rebinds only the current-state fixtures, compacts the four live
baton rows without removing authority or protected boundaries, records the
current register revision/count and requires a fresh complete closeout packet.
A direct compactness recheck then exposed eight current product-lineage rows
missing from the active-label classification. The same correction aligns the
script and manifest allowlists with those already-live current rows before the
fresh packet. That packet then exposed one remaining exact-prose fixture for
the compacted cancellation phrase; the correction retains the material token
rather than requiring superseded wording. No product source or accepted
command-family decision changed.

## Population

- incidents: 413;
- corrected or explicitly contained: 413;
- open: 0;
- latest id: `AER-0413`.

No product, data, provider, deployment or protected-ref authority changed.
