# Threat-model delta: durability system-`xmin` record-projection recovery

Date: 2026-08-09

Status: bounded provider-free recovery control

## Scope change

The accepted typed body used system `xmin` to prove current-top-level-
transaction provenance but allowed some `LOCAL` table-composite symbols to be
consumed without an exact `xmin` projection. PostgreSQL rejected the first
such use before any behavior scenario passed. This recovery changes only the
typed read projections and validator invariant needed to represent those
already accepted provenance checks.

## Threats and controls

| Threat | Control | Required evidence |
|---|---|---|
| A named table composite is mistaken for a row carrying system columns | Every `LOCAL SYSTEM_XMIN` consumer must trace to a definitely assigned exact read whose closed projection includes `xmin` | Validator rejects `xmin_not_selected`; regenerated SQL uses record locals |
| Repair adds a caller-supplied or retained transaction identifier | Only PostgreSQL system `xmin` selected from the exact keyed row is admitted; current-XID32 remains database-derived and neither value is stored or exposed | Typed operands and rendered SQL remain exact; no new input or relation column |
| A broad projection leaks product or payload data | Only three already accepted closed column lists gain the system column; no new relation, free text, payload release or evidence field is added | Contract diff and evidence schema remain closed |
| Record locals weaken positional row guarantees | Only `xmin`-carrying exact reads become records; table-composite assignments without system columns retain exact user-column order checks | Positional verifier and record-local renderer tests pass |
| Repair silently widens principal, RLS or privilege authority | Predicates, role bindings, RLS policies, grants, security-definer owners and trigger declarations remain unchanged | Parent catalogue/privilege digests must be freshly reproduced |
| One observed site hides the same defect elsewhere | Whole-contract traversal reconciles every `SYSTEM_XMIN` local consumer, not only the first runtime line | Zero unprojected local consumers and fourteen corrected sites are asserted |
| Diagnosis evidence retains raw server text | Only the allowlisted function, line, relation type, column, SQLSTATE and evidence digest are persisted | Diagnosis receipt says `raw_error_persisted: false` |

## Residual boundary

The repair does not prove runtime behavior. It must flow through regenerated
body, inert artifact, parse/catalogue, behavior rebind, deterministic packet,
fresh independent veto and a fresh disposable run. Concurrency, unknown-
commit recovery, key rotation, retention execution, applied migration,
operational persistence and all product/provider/production surfaces remain
outside the claim.
