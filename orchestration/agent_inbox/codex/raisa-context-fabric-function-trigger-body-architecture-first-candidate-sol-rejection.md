# Sol rejection — first function/trigger-body candidate

Date: 2026-08-07

Decision: `revision_required`

Rejected uncommitted contract:
`sha256:c16930c2d6c400c93ea2c2b413ccf084ceb38c4f980fa4edae032b74e3112622`

The candidate is rejected before commit and before final independent-veto
admission. Read-only implementation-lane audit found:

- P0: one opaque step reference plus enum-labelled substeps and untyped
  predicate leaves is not a mechanically lowerable typed body;
- P1: digest-resealed ownership, symbol, branch, expression, step placement,
  return, signature and trigger mutations remained schema-valid;
- P1: effects were declared at step/relation level rather than derived from
  column-minimal typed instructions; and
- P2: call edges and acyclicity/isolation were asserted rather than derived.

No API Spine regression or forbidden side effect occurred. The normative Sol
recovery is
`docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-implementation-recovery.md`.
