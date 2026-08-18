# Ariadne agent error and correction register — revision 401

Date: 2026-08-18

Timestamp: 2026-08-18T17:53:14.1830350+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 401 carries forward AER-0454 through AER-0461 and adds AER-0462.

AER-0462 preserves the rejected reentrant Continuity updater correction. The
first recovery linked inherited contract plans, findings and closeouts but
still omitted the two inherited contract test paths from the node's typed
`tests` evidence. Compass returned two exact
`contract_evidence_type_unlinked` reasons and did not render the report.

The correction binds both exact existing product-lineage tests through the
inherited contracts and the node's `tests` inventory. Graph and Compass remain
on the same reentrant Continuity 320 / Compass 302 node. No provider,
candidate, external runtime or protected ref changed.

## Population

- incidents: 462;
- corrected or explicitly contained: 462;
- open: 0;
- latest id: `AER-0462`.
