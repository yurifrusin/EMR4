# Ariadne agent error and correction register revision 159

Date: 2026-08-10

Status: corrected; complete static packet must restart

Revision 159 adds AER-0185 and brings the register to 185 bounded incidents
with zero open incidents.

## AER-0185 — live parse-plan parent assertion remained stale

The first complete input-namespace static packet ran to completion with one
failure. The live parse-plan acceptance test still bound the preceding inert
artifact SHA-256 even though the renderer, manifest, catalogue contract,
characterization and exact reproduction all correctly bound the new artifact.
No Docker, database, provider or external runtime was contacted by this test.

The test now includes the input-namespace rebind and binds source `f64f3cd7`,
artifact SHA-256 `8756f315…`, 1,448,546 bytes and exact parse contract
`e783fedb…`. Historical tests retain their immutable old bytes. The entire
static packet must restart on the corrected final candidate.
