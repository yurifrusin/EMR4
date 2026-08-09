# Ariadne agent error and correction register revision 145

Date: 2026-08-09

Status: corrected; descendant proof pending

Revision 145 adds AER-0170 and brings the register to 170 bounded incidents
with zero open incidents.

## AER-0170 — UPDATE exception-subtransaction provenance mismatch

Behavior attempt 029 failed safely at `BTR-E02` with `CF603`, completed zero
scenarios and verified exact cleanup. Deterministic source reconciliation proved
that the stream-head `UPDATE ... RETURNING` was rendered inside a PL/pgSQL
`EXCEPTION` block. That block authors the row version under a subxid, while the
accepted deferred fence compares `xmin` with the top-level xid returned by
`pg_current_xact_id()`.

This is related to AER-0151: the earlier control correctly removed write-bearing
exception blocks from `INSERT_OR_RELOAD_COMPARE`, but it was too opcode-specific
to cover the renderer's separate `UPDATE` lowering. The repaired control now
covers both write families. All thirty-nine typed updates must prove an exact
primary or unique key before rendering, execute outside exception
subtransactions, and map zero rows to stable `CF004` through `FOUND`.

Another behavior runtime remains closed until artifact recognition, fresh
parse/catalogue characterization and exact reproduction, behavior-parent
rebind, the complete deterministic packet and a fresh independent veto pass.
