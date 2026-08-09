# Ariadne agent error and correction register revision 126

Date: 2026-08-09

Status: bounded register correction candidate

Revision 126 adds AER-0151 and brings the register to 151 bounded incidents
with zero open incidents.

## AER-0151 — insert/reload renderer authored subtransaction tuple

Behavior attempt 022 stopped at BTR-E01 `CF105` with zero admitted scenarios
and verified cleanup. The corrected conjunct diagnosis proved the new stream
head's position and epoch were exact while its `xmin` did not equal the current
top-level XID32.

The accepted transaction architecture deliberately rejects relevant tuples
authored by savepoints or subtransactions. Renderer 2.0.9 nevertheless placed
all twenty-one `INSERT_OR_RELOAD_COMPARE` writes inside PL/pgSQL blocks with
`EXCEPTION` clauses. PostgreSQL assigns writes in those blocks subtransaction
IDs, while `pg_current_xact_id()` returns the top-level transaction ID. The
stream-head fence therefore rejected the renderer-authored row exactly as its
security contract required.

Renderer 2.0.10 retains exact top-level-XID equality and replaces all twenty-
one write-bearing exception blocks with exact `INSERT ... ON CONFLICT ON
CONSTRAINT ... DO NOTHING RETURNING` plus a read-only strict winner reload when
`NOT FOUND`. Untargeted conflict suppression, wrong constraints, ambiguous
winners and any residual write-bearing unique-violation handler are rejected
deterministically before parse or behavior eligibility.
