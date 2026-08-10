# Sol acceptance: Context Fabric durability parse exact pass

Date: 2026-08-10

Accepted candidate: `ebcd813b22db6f8da49af5aa44652d047a323b8c`

Fresh r153 Gemini 3.6 Flash/high review passed at exact HEAD with a clean
postcondition: 463/463 tests, twelve-file Ruff check and format, builder, inert
artifact, immutable pass SHA, attempt ID, all 15 digests, exact cleanup ID and
candidate diff all passed. No database or product surface was opened during
review.

The receipt's prose incorrectly labels the protected historical
`3bf66870...` file as a DML-name characterization. That label is rejected and
is not copied into acceptance. The authoritative protected path remains
`provider-free-disposable-postgresql-evidence-json-key-set-order-exact-rerun-failure.json`;
Sol reverified its exact SHA-256
`3bf66870cf80edc507b191d6022a5e3d22f3b7f3073c9ae4e696fed2fc54155c`,
and the preceding independently accepted r152 receipt correctly reconciled the
literal filename. This prose defect does not change the reviewed candidate,
the 463-test path binding, immutable exact-pass evidence or clean postcondition.

The parse/catalogue dependency is accepted for a provider-free behavior
contract rebind. This grants no behavior database execution until the rebound
candidate itself passes deterministic and fresh independent review.
