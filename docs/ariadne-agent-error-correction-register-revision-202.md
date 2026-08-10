# Ariadne agent error and correction register — revision 202

Date: 2026-08-08

Revision 202 adds AER-0236 and brings the register to 236 bounded incidents.

## AER-0236 — abbreviated HEAD supplied to exact-head preflight

The first local preflight for the admission-replay parse characterization
review supplied display abbreviation `f5c8fb0f` where the helper requires the
full 40-character commit identity. The helper returned `revision_required`
before writing a pass receipt and before any provider or database action. Git
confirmed the clean worktree at exact
`f5c8fb0f01dc5836647b90acdf96c8ed6c21fc05`; the corrected invocation used
that full identity and passed. Future invocations must take `expected_head`
from full `git rev-parse HEAD` output.
