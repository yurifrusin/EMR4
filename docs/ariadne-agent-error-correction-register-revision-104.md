# Ariadne agent error and correction register revision 104

Date: 2026-08-08

Status: accepted register correction

Revision 104 adds AER-0126 and brings the register to 126 bounded incidents.

## AER-0126 - replacement digest used an incomplete projection

The reviewed retry again admitted the complete revised SQL artifact, then
failed closed at the sole `types` catalogue digest. The predicted replacement
had been calculated from a reduced fixture rather than the full PostgreSQL
projection.

The correction reconstructs all 32 type rows, including domain definitions,
enum labels and composite attributes. It first reproduces the predecessor
characterization digest exactly, then proves the complete row-level delta is
only `digest_sha256.domain_not_null: true -> false`. The resulting replacement
digest is bound in the contract. Another runtime attempt remains closed until
deterministic checks and a fresh exact-HEAD independent veto pass.
