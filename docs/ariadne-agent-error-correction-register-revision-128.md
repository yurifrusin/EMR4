# Ariadne agent error and correction register revision 128

Date: 2026-08-09

Status: bounded register correction candidate

Revision 128 adds AER-0153 and brings the register to 153 bounded incidents
with zero open incidents.

## AER-0153 — predeclared verifier without assignment receipt

The first top-level-XID behavior-veto predispatch state declared the Gemini
verifier active and assigned while its `workspace_receipts` array contained
only the separate verifier-worktree preflight path. The deterministic Ariadne
preflight returned `revision_required` with `workspace_receipt_missing`; it set
`worker_dispatch_permitted` false and no Antigravity or model call occurred.

The failed state and receipt remain immutable. A distinct corrected state
leaves agent assignment and active-instance arrays empty, while retaining the
exact clean r107 worktree evidence separately. This recurrence is grouped with
the existing worker-dispatch runtime-contract family, including AER-0024,
without asserting attempt-peer linkage or model fault. Future predispatch
states must distinguish a schema-governed assignment receipt from a general
evidence path before declaring a worker active.
