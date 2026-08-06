# Sol recovery lease — source-specific durability architecture

Date: 2026-08-06

Status: active

Rejected candidate:
`92cf76b17bbab276df701ee1e0af0da77e1768a9`

## Basis

The fresh independent veto found one material contract-integrity defect: five
safety-critical arrays were structurally closed only by cardinality and string
shape, so a different internally valid contract could widen payload/audit
fields or replace tenancy/atomicity coordinates. The candidate is rejected and
cannot be accepted on its passing 83-test packet.

## Sol-owned correction

Under the orchestrator recovery lease, Sol may amend only:

- the JSON Schema definitions for the exact payload-free allowed/prohibited
  fields, producer transaction members, checkpoint key fields, atomic commit
  members and audit allowed/prohibited fields;
- focused adversarial tests that append, remove, replace or reorder those exact
  tuples; and
- AER-0048, review and recovery evidence.

No architecture meaning, principal, stream, data posture, live/runtime gate or
claim may widen. A fresh exact-head reviewer must verify the correction and all
postconditions before acceptance. No database/source/provider/runtime/command,
deployment, Pages or protected-ref action is authorised.
