# Ariadne agent-error register revision 59

Date: 2026-08-06

Status: recovery-8 reviewer preflight corrected; veto pending

## Exact-HEAD preflight failure preserved

After committing the eighth candidate at
`194d5f329e8f84ae411e5cd6492076ae6a21a894`, Sol created the clean `r31`
review worktree but supplied the abbreviated `194d5f32` value to a verifier
preflight that requires exact 40-character equality. The preflight returned
`revision_required` before any reviewer was dispatched. No candidate, worktree
or protected ref changed.

This is AER-0056. The failure receipt is preserved. A distinct correction used
the complete SHA and passed cleanly; future verifier setup must copy the full
`git rev-parse HEAD` value into `--expected-head` and may use an abbreviation
only in human-facing labels.

AER-0051 remains open until the corrected architecture passes an independent
veto. No provider, database, source, patient/product data, runtime, SQL,
migration, deployment, Pages or protected-ref authority changed.

Revision 59 contains 56 bounded incidents: 44 agent-behaviour observations,
three harness failures, two repository defects and seven transport timeouts.
Counts are workflow-improvement signals, not model, provider, transport or role
causation.
