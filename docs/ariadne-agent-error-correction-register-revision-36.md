# Ariadne agent-error register revision 36

Date: 2026-08-06

Status: invalidation/reassembly orchestration ordering and search scope contained

## AER-0043 corrected

Sol opened the bounded native implementation lane after a passed five-source
`pre_sprint_planning` receipt but before the separately required
`pre_worker_dispatch` receipt. The worker was interrupted before any candidate,
decision or acceptance was admitted. The frozen plan and committed source were
unchanged. The correction requires the distinct passed pre-dispatch receipt
before the same exact two-file lease may resume.

## AER-0044 contained

While inspecting the agent-error register schema, an intended exact-file `rg`
command returned broad repository search output. Sol did not use that output for
candidate analysis or inspect it further. Subsequent register/schema work uses
only explicit `Get-Content -LiteralPath` reads with bounded line ranges. This is
recorded conservatively as a command-scope breach; it does not assert that
protected content was opened or exposed.

Revision 36 contains 44 bounded incidents: 32 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
No incident remains open. Counts remain workflow-improvement signals only and
do not establish model, provider, transport or role causation.
