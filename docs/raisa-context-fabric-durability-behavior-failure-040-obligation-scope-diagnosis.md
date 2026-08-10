# Context Fabric durability behavior failure 040 — obligation scope diagnosis

Date: 2026-08-08

Attempt 040 safely localized BTR-E04 to probe 5: the assertion that exactly one
pending reassembly obligation exists. Its immutable failure evidence has
SHA-256 `93af223dfb25aab6a217f98eea45aa43c27efdb2d85d102caaf0f3b05b41ff98`.
The exact owned container was removed and independently confirmed absent. The
protected mutable evidence alias was restored byte-for-byte.

This is a harness-scope defect, not evidence of a database-body defect. The
closed bootstrap deliberately seeds a beta-practice pending obligation using
the same authored-synthetic `observer_happy` identifier. BTR-E04 then passed
its exact transition marker and relation-delta gate, proving one new alpha
obligation. The old probe filtered only by observer and pending state, so it
necessarily counted both rows. The same omission would affect BTR-I03 next.

The bounded correction adds the already-bound alpha practice and stream to the
BTR-E04 and BTR-I03 obligation probes. It changes no database artifact, body,
behavior contract, scenario population, expected relation delta, authority,
provider or product boundary. Another database characterization remains closed
until deterministic tests and a fresh exact-HEAD independent veto pass.
