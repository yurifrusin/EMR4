# Ariadne agent error and correction register revision 144

Date: 2026-08-09

Status: corrected; descendant proof pending

Revision 144 adds AER-0169 and brings the register to 169 bounded incidents
with zero open incidents.

## AER-0169 — PL/pgSQL DML local/column namespace ambiguity

Behavior attempt 028 failed safely at `BTR-E02` with `42702` and exact cleanup.
Deterministic source mapping proved that the outbox insert used two scalar
locals with the same names as target and returning columns. The renderer left
both namespaces implicit.

Renderer 2.0.14 now labels every generated outer block `cf_body`, qualifies
scalar local references through that label and qualifies DML return projections
through their exact target. It does not use `#variable_conflict`, rename body
symbols, change typed programs, alter scenarios or widen authority.

Another runtime remains closed until regenerated artifact recognition, fresh
parse/catalogue characterization and exact reproduction, six-parent behavior
rebind, the complete deterministic packet and a fresh independent veto pass.
