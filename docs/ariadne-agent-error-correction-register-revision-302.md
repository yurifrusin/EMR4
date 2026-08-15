# Ariadne agent error and correction register — revision 302

Date: 2026-08-16

Timestamp: 2026-08-16T00:04:34+10:00 (Australia/Brisbane)

Revision 302 records AER-0341. The register now contains 341 bounded known
incidents, all corrected or contained by an explicit control.

AER-0341 preserves the first Gemini 3.7 delete-confirm scaffold veto. Five of
six manifest commands passed and the substantive audit reported no product
defect, but the focused-test command used the serial wrapper from the primary
checkout with relative candidate test paths. The wrapper correctly serialized
pytest yet resolved those paths against its own checkout, where the
not-yet-integrated focused test did not exist. The command exited 1 and the
verifier correctly returned `revision_required` at unchanged clean candidate
`bdfea42a47c0ebcbfc9d4ac6ae5685a380079ca7`.

No failed result is admitted. The correction preserves the receipt, leaves the
candidate unchanged and binds each candidate-owned test path absolutely under
the exact review worktree before one fresh no-fallback veto. Future command
admission must reject relative candidate paths that cross checkout roots.
