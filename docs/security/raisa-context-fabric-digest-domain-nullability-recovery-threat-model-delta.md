# Threat-model delta: digest-domain nullability recovery

Date: 2026-08-08

This delta covers only the provider-free inert DDL recovery described in
`docs/raisa-context-fabric-digest-domain-nullability-recovery.md`.

## Security properties retained

- Digest values, when present, still must match the exact `sha256:` plus 64
  lowercase hexadecimal format.
- Every mandatory digest field remains column-level `NOT NULL`.
- The only intentional absence is expressed by an explicitly nullable column
  and further constrained by relation-level invariants, including the
  zero-position checkpoint rule.
- The immutable parent contracts, role/grant/RLS catalogue, trigger and
  function bodies, transaction boundaries, networkless container profile and
  evidence-egress rules remain unchanged.

## Threats and controls

| Threat | Control |
|---|---|
| A nullable domain silently weakens mandatory state | Deterministic tests enumerate representative required digest columns and require their column-level `NOT NULL`. |
| An absent digest is admitted at a positive checkpoint position | `ck_cf_07_03` continues to require a non-null digest above position zero. |
| The recovery drifts beyond one domain flag | The recovery manifest seals the exact old and new domain fragments and the independent veto reviews the exact diff. |
| Old runtime evidence is mistaken for evidence about the revised artifact | Both disposable contracts must be re-bound and both PostgreSQL rehearsals rerun before acceptance. |

## Unchanged closure

There is no patient, clinical, product-derived or real-identity data; no
provider or internet call; no application database; no migration application;
no runtime wiring; no deployment, release, Pages or protected-ref movement.
