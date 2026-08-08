# Threat-model delta: row-composite projection-order recovery

Date: 2026-08-08

This delta covers only the provider-free recovery in
`docs/raisa-provider-free-disposable-postgresql-durability-behavior-row-composite-projection-order-recovery.md`.

## Security properties retained

- Complete typed rows retain the accepted physical relation schema; no field,
  predicate, authority check or write effect is added or removed.
- Binding capability, practice, source and stream predicates remain exact and
  continue to pass through the existing support-helper and RLS boundaries.
- The new check runs before rendering and cannot contact PostgreSQL, a model,
  a provider, a product database or external state.
- Historical evidence and predecessor hashes remain immutable and cannot prove
  the corrected artifact.

## Threats and controls

| Threat | Control |
|---|---|
| A projection silently shifts values between different typed fields | Every table-composite row assignment must equal the complete physical user-column order. |
| A later recovery appends a relation column without updating a body projection | The renderer derives the relation order independently and fails closed before output. |
| A partial system-column read is incorrectly forced into a table composite | The existing explicit `xmin` record-local path remains separate and excluded from the table-composite invariant. |
| A source correction is treated as runtime proof | Fresh exact-HEAD review, parse/catalogue rehearsal and behavior rehearsal are all required. |

## Unchanged closure

There is no patient, clinical, product-derived or real-identity data; no
provider or internet call; no application database; no migration application;
no runtime wiring; no deployment, release, Pages or protected-ref movement.
