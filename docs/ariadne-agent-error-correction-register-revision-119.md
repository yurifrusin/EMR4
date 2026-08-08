# Ariadne agent error and correction register revision 119

Date: 2026-08-09

Status: bounded register correction candidate

Revision 119 adds AER-0142 and brings the register to 142 bounded incidents.

## AER-0142 - local system `xmin` was not selected into record projections

Attempt 019 passed corrected artifact and catalogue admission and reached
`BTR-E01`, then returned SQLSTATE `42703` with zero admitted scenarios and
verified cleanup. A fresh diagnosis-only container released the exact safe
coordinate `cf_fence_stream_head_v1` line 33: the trigger evaluated
`(final_head).xmin` after loading only the table's user columns into a named
table-composite local.

PostgreSQL system columns are not members of named table composites. Static
whole-contract reconciliation found fourteen `LOCAL SYSTEM_XMIN` consumers
whose alias, stream-head or outbox exact reads omitted `xmin`.

The three shared projection lists now include `xmin`, so those reads render to
record locals. More importantly, the body validator now rejects
`xmin_not_selected` whenever a local system-`xmin` operand cannot be traced to
a definitely assigned exact read that projected it. Focused hostile and
renderer tests bind both the prevention rule and the complete affected symbol
set.

The typed body, inert artifact, parse/catalogue and unchanged twenty-scenario
behavior contract must be regenerated, rebound and freshly reviewed before
another behavior attempt.
