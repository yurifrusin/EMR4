# Ariadne agent-error register revision 46

Date: 2026-08-06

Status: durability state-machine semantic recovery pending fresh veto

## AER-0050 remains open

The first recovery at `0f3f687be40d57489a4a221161ba900bb63f4040`
closed the original receipt/audit structural and retention-authority defects.
Its fresh veto nevertheless found that a mutually resealed receipt and audit
could tell a no-intersection story while retaining the original relevant
transition's watermark, retired frame and obligation. It also accepted a
coupled wrong disposition, detached audit schedule/key/predecessor/lifecycle
fields, deletion of the audit prefix and arbitrary state lifecycle inflation.

Sol kept the recovery lease active. The pending correction now freezes the
baseline receipt and frame collections, requires the complete audit prefix,
binds decision-specific dispositions and predecessor/key/lifecycle semantics,
uses a stable position-bounded key-schedule digest across valid future
rotation, and deterministically rederives watermarks, frame retirement,
coalesced obligations, rolling cause digests and count buckets from the audit
sequence. Direct reproductions and canonical collection mutations pass locally.
AER-0050 remains open until another genuinely fresh exact-head veto accepts the
corrected candidate.

Revision 46 contains 50 bounded incidents: 38 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
AER-0050 is the sole open incident. Counts remain workflow-improvement signals
and do not establish model, provider, transport or role causation.
