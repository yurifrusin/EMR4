# Context Fabric durability behavior failure 043 — missing-source SQLSTATE diagnosis

Date: 2026-08-08

Attempt 043 reached `BTR-E06` after the repaired receipt-lock path and failed
closed as `sqlstate_mismatch`. Its immutable evidence has SHA-256
`00805d8b31ba445523a9a3e82581e07a4232873164ba49961ae5913f15617801`;
the exact owned container was removed and confirmed absent, and the protected
mutable evidence alias was restored byte-for-byte.

The mismatch is between the later behavior plan and the already accepted
database body, not evidence of a database mutation defect. `BTR-E06` supplies
an outbox position which does not exist. The rendered admission function's
exact source selection maps `NO_DATA_FOUND` to the established cardinality
failure `F_CARDINALITY` / `CF004`. The later `F_ADMISSION_SOURCE` / `CF201`
assertion compares the packet's source-membership digest only after an exact
source row has been obtained, so it is unreachable for a missing row.

The parent harness persisted only the expected string `CF201` when reporting
the mismatch; it did not preserve the scenario or observed bounded SQLSTATE.
The bounded correction therefore aligns `BTR-E06` with `F_CARDINALITY` /
`CF004` and adds typed scenario, expected-SQLSTATE and observed-SQLSTATE fields
to future mismatch evidence. The function body, inert SQL, parse evidence,
scenario population, authority and runtime boundaries remain unchanged. A new
characterization remains closed until deterministic tests and a fresh
exact-HEAD independent veto pass.
