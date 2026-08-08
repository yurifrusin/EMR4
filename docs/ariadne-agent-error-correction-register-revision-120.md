# Ariadne agent error and correction register revision 120

Date: 2026-08-09

Status: bounded register correction candidate

Revision 120 adds AER-0143 and brings the register to 143 bounded incidents.

## AER-0143 — selected system `xmin` lacked a stable record-field alias

Attempt 020 admitted the record-local and explicit-projection repair and
reached `BTR-E01`, then returned SQLSTATE `42703` with zero admitted scenarios
and verified cleanup. A fresh diagnosis-only container released the exact safe
coordinate `cf_fence_stream_head_v1` line 33: PostgreSQL could not identify
field `xmin` in record local `final_head`.

The previous correction was necessary but incomplete. It ensured that every
local `SYSTEM_XMIN` consumer selected the system value into a `record`, but the
renderer emitted `relation.xmin` without an explicit result-field name.

Renderer 2.0.8 now emits `relation.xmin AS xmin` for every system-column exact
projection. The accepted renderer test requires all 62 occurrences to carry
that alias, rejects every remaining unaliased `.xmin INTO STRICT`, and retains
the independent typed `xmin_not_selected` control introduced by AER-0142.

The inert artifact, exact parse/catalogue proof and unchanged twenty-scenario
behavior contract must be regenerated, rebound and freshly reviewed before
another behavior attempt.
