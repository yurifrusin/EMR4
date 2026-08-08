# Ariadne agent-error register revision 89

Date: 2026-08-07

Status: exact-catalogue plan correction passed fresh veto

## AER-0095 is corrected

The earlier replacement PostgreSQL plan review remains rejected because its
aggregate-only reconciliation missed the incorrect 4/17/11 split. The corrected
candidate at `c5f0960a240b7f162b1b34e1b09fb166d12fd42e` binds the exact 4 domains,
19 enums, 9 composites and 32 corresponding type-owner rows.

One genuinely fresh Gemini 3.6 Flash/high exact-HEAD veto mechanically grouped
all 388 manifest nodes, compared every one of the 32 type identifiers, exercised
ten hostile mutations, passed 9/9 focused tests and left the review worktree
clean. Sol independently reproduced the same counts and verified that the
32 type/domain identifiers and 32 owner identifiers are unique and identical.

## Register posture

Revision 89 contains 95 bounded incidents: 76 agent-behavior observations,
six harness failures, five repository defects and eight transport timeouts. No
incident is open.

This correction admits only the frozen provider-free implementation boundary.
It supplies no Docker or PostgreSQL execution by itself and no migration,
operational database/source, product/patient data, application/runtime,
command, provider product, deployment, production, release, Pages or
protected-ref authority.
