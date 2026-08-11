# Ariadne agent error and correction register — revision 218

Date: 2026-08-11

Revision 218 records AER-0253 and brings the register to 253 bounded known
incidents.

## AER-0253 — AES-C3 worker-dispatch envelope correction

The first AES-C3 worker predispatch state repeated the historical
worker-dispatch-envelope defect: it used `pre_dispatch` instead of the exact
approved `pre_worker_dispatch` event and predeclared an external worker in
`assigned_agent_ids` with a handwritten workspace entry. The deterministic
preflight returned `revision_required` with
`continuation_event_missing_or_unapproved` and
`workspace_receipt_missing:deepseek-aes-c3-blue-001`.

No worker, provider or model call followed the refused receipt, and the clean
candidate worktree remained at exact plan source
`d44be5cbe0774b6340c7e4f6ca76075242b2f156`. Sol preserved the failed state
and receipt, generated the dedicated clean-worktree preflight, and created a
distinct v2 state with the approved event plus empty `workspace_receipts` and
`assigned_agent_ids`. The v2 receipt passed with all five sources and
`worker_dispatch_permitted: true`.

The correction retains the exact recurrence signature from AER-0080. Future
AES-C3 external-worker/verifier receipts must copy the admitted event and
assignment structure from a prior passing envelope; separate exact-worktree
preflight evidence belongs in the five-source text, not an invented assignment
receipt.
