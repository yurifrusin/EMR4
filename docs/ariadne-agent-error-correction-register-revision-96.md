# Ariadne agent error and correction register revision 96

Date: 2026-08-08

Status: accepted register correction

Revision 96 adds AER-0116 and brings the register to 116 bounded incidents.

## AER-0116 — synthetic fixture foreign-key topology gap

The second admitted disposable PostgreSQL behavior run passed the corrected
catalogue boundary and then failed closed during fixture bootstrap. Failure
evidence 002 records successful catalogue reconciliation, zero behavior
scenarios and verified exact container cleanup.

The practice-beta fixture exists only to prove cross-practice invisibility in
the application-read projections. Its observer generation nevertheless still
requires a generation-registry barrier through `fk_cf_06_01`, and its
invalidation watermark requires a durability checkpoint through `fk_cf_11_01`.
The original fixture omitted those two parents.

The repaired beta seed is a single explicit dependency chain:

1. generation-registry barrier;
2. observer generation;
3. durability checkpoint;
4. frame generation;
5. invalidation watermark; and
6. reassembly obligation.

Each child CTE reads its required parent CTE, and a static regression test
freezes the ordering and references. No production SQL, grant, role, RLS,
scenario, claim or runtime boundary changed. The corrected candidate remains
closed until deterministic checks and a fresh exact-HEAD independent veto pass.
