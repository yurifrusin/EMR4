# Ariadne agent-error register revision 31

Date: 2026-08-06

Status: temporal-weave independent-review evidence reconciled; no incident remains open

## AER-0037 corrected

The fresh schema-constrained Gemini 3.6 Flash/high review returned `pass` at
unchanged clean candidate `f32004a2f39ac769ba746afe2663813f7c422d8a` and its
architectural findings remain admissible. Its prose, however, reported 67 tests
across seven files and cited the contained DeepSeek transport receipt under a
nonexistent DeepSeek inbox path.

Exact collection in the same review worktree yields 120 tests across those
seven files, and Sol ran all 120 successfully without changing the candidate or
making another provider call. The committed receipt is under the Codex inbox as
recorded in the reconciliation receipt. Both the numerical and path claims are
therefore non-authoritative and corrected without discarding the independent
veto.

This is the second exact-packet test undercount in consecutive Context Fabric
reviews. It is now an explicit recurring control signal: every verifier test
count and repository-path claim must be machine-reconciled against exact
collection output and the candidate tree before closeout.

Revision 31 contains 37 bounded incidents: 27 agent-behaviour observations,
three harness failures, two repository defects and five transport timeouts. No
incident remains open. Counts remain workflow-improvement signals only and do
not establish model, provider, transport or role causation.
