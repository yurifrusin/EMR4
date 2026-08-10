# Context Fabric durability behavior failure 041 — rejection precedence diagnosis

Date: 2026-08-08

Attempt 041 passed the repaired BTR-E04 readback and reached BTR-I03. It then
failed closed as `transition_result_missing`. Its immutable evidence has
SHA-256 `c1215b6dae6e1f2608c55d38ee35ecbea5df2f341f1141707239e8371f129491`;
the exact owned container was removed and confirmed absent, and the protected
mutable evidence alias was restored byte-for-byte.

The failure cannot yet diagnose the database replay branch. The parent harness
called its transition-marker parser before classifying the process result and
bounded SQLSTATE. Consequently, any underlying BTR-I03 rejection without a
marker was masked as `transition_result_missing`, and the evidence intentionally
persisted no raw stderr.

The bounded correction classifies an unexpected rejection before demanding a
success marker, and classifies an SQLSTATE mismatch before demanding the marker
for an expected-rejection scenario. Once transport is admitted, the exact typed
marker remains mandatory. Database artifact, body, behavior contract, scenario
population and authority are unchanged. Another characterization remains closed
until deterministic tests and a fresh exact-HEAD independent veto pass.
