# Ariadne agent error and correction register — revision 216

Date: 2026-08-11

Revision 216 adds AER-0252 and brings the register to 252 bounded incidents.

## AER-0252 — worker-only evidence paths in primary register

The first AER-0251 draft cited the rejected candidate's closeout, script and test
paths relative to the primary repository even though those files existed only
in the isolated, unintegrated worker worktree. The register validator correctly
returned `revision_required` on the first missing path before report generation
or corrected worker dispatch.

The correction writes a primary Sol rejection record with the exact candidate
SHA and reproduced findings, retains the primary transport receipt and cites
only evidence that resolves under the primary repository root. Future register
entries for unintegrated candidates must use a primary receipt or rejection
record rather than treating worker-worktree paths as primary files.

No candidate was adopted, no external verifier ran and no protected surface or
ref changed.
