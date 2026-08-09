# Ariadne agent error and correction register revision 122

Date: 2026-08-09

Status: bounded register correction candidate

Revision 122 adds AER-0146 and brings the register to 146 bounded incidents
with zero open incidents.

## AER-0146 — anonymous record `xmin` used SQL composite syntax

Attempt 021 admitted the renderer 2.0.8 artifact and its synthetic fixtures,
then stopped at `BTR-E01` with SQLSTATE `42703`, zero admitted scenarios and
verified cleanup. A fresh diagnosis-only container released the same safe
coordinate, `cf_fence_stream_head_v1` line 33, record `final_head`, column
`xmin`, without persisting raw diagnostics.

This established a separate representational defect after the explicit
projection and alias repairs. `final_head` is an anonymous PL/pgSQL `record`,
but `SYSTEM_XMIN` lowered its field access as `(final_head).xmin`—SQL composite
syntax that requires a fixed descriptor. Renderer 2.0.9 emits direct
`final_head.xmin` access instead.

The typed validator now rejects every non-local `SYSTEM_XMIN`; the renderer
acceptance binds the complete direct-access population; and the artifact
recognizer rejects every residual `(record).xmin` form. The existing exact
projection and explicit `AS xmin` controls remain mandatory.
