# Context Fabric frame-mask recovery behavior-parent rebind

Date: 2026-08-08

Status: deterministic provider-free candidate; runtime remains closed

The behavior rehearsal is rebound to the first-run frame-mask recovery
parse/catalogue pass without changing any scenario, fixture, role, capability,
RLS, SQLSTATE, transaction or command boundary.

The six canonical parent bindings now resolve as follows:

- accepted runtime source: immutable parse/catalogue pass at
  `9bf59ed860e2c4e119b13e5dd38911dbb9591ad0`, SHA-256
  `4583c8b0bca881964ba9a337cfd1b5c9ae535ad7cc78c06766f844ffe95d998a`;
- inert SQL: frame-mask recovery source
  `a8cef7045fcada54a33a1060e83fd4d9929ac56b`, SHA-256
  `fc1c00ab7209a6689f4de29a14a134719a0110dfd3b556172781384332af41fa`;
- render manifest: the same recovery source, canonical SHA-256
  `fec0bb1399ebf5af0d06ca933069614ca4a8c84a9593d5eee0e983b0afffb9fd`;
- structural contract, body contract and parse prerequisite: unchanged.

The rebound behavior contract has canonical SHA-256
`9dd97600289733fb48a03a54d0b4a2418c6c502c98f75ba0181213a6088518dc`.
All 20 authored-synthetic scenarios and their exact order remain unchanged.

This is an inert parent-binding operation only. It does not run PostgreSQL or
Docker and grants no application migration, operational database,
watcher/feed, application/API/Diary wiring, provider, patient/clinical/product
data, deployment, release, Pages or protected-ref authority. A fresh exact-HEAD
independent veto must pass before a separately receipted behavior rehearsal may
start.
