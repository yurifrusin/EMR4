# Ariadne agent-error register revision 163

Date: 2026-08-10

Revision 163 adds AER-0189 as a repository-origin durability defect. Behavior
attempt 034 reached `BTR-E03` and failed closed with SQLSTATE `23514`; its exact
owned container was removed and absence verified, and the accepted mutable
behavior evidence was restored byte-exactly.

Deterministic diagnosis binds the historical body, structural contract,
entry-program generator and inert DDL at source HEAD `df5352fb`. The generated
PRIMARY admission populated `attempted_admission_digest` despite
`ck_cf_04_02` requiring it null. The same shared binding generator populated
PRIMARY-only outcome fields on CONFLICT rows, and five insert-or-reload winner
predicates used ordinary equality against typed null values.

The correction is architecture-strengthening: emit exact PRIMARY/CONFLICT row
shapes, use `IS NULL` for typed-null winner comparisons, regenerate the body
and inert artifacts, reprove parse/catalogue identity and rebind the unchanged
twenty behavior scenarios before any further runtime attempt. No scenario,
principal, SQLSTATE, RLS, authority, product, provider, data or deployment
boundary is weakened or widened.
