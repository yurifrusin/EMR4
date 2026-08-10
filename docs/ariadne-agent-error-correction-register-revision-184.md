# Ariadne agent error and correction register — revision 184

Date: 2026-08-08

Revision 184 adds two closed, evidence-backed incidents from Context Fabric
durability behavior attempt 038:

- `AER-0212` records the repository RLS defect that omitted `COORDINATOR` from
  the forced-RLS outbox SELECT policy required by the coordinator entry point.
- `AER-0213` records the harness admission gap that emitted but did not require
  the closed coordinator transition result kind.

The bounded controls add only coordinator logical visibility to the existing
outbox SELECT policy, preserve zero direct coordinator table grants, require
exact transition result kinds, and retain the forbidden relation-delta gate.
No provider, product, patient, runtime, deployment, release, Pages or protected
ref authority is added.

The register now contains 213 closed incidents and no open incident.
