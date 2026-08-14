# Ariadne agent error and correction register — revision 269

Date: 2026-08-14

Timestamp: 2026-08-14T21:38:47+10:00 (Australia/Brisbane)

Revision 269 records AER-0308. The register now contains 308 bounded known
incidents, all corrected or contained by an explicit control.

AER-0308 records two wording/count defects in the otherwise passing fresh
Gemini review receipt. The receipt says that five mandatory shell commands ran,
while its frozen packet contains nine exact command lines. It also summarizes
the non-mutating Ruff `format --check` result as two files formatted rather
than two files already formatted.

The verifier's detailed evidence is internally sufficient to reconcile both
defects without another model call: it reports the exact 144, 79 and 234
pytest packet results, totalling 457; separate Ruff lint and format-check passes;
the exact name-only and whitespace checks; unchanged candidate HEAD
`fbb7ffb46e041bbfc193ff3a76b2f970c06dee58`; and a clean worktree. The
Antigravity harness independently records the same unchanged clean postcondition.
The candidate and the verifier's single `pass` decision therefore remain
unchanged, while no broader claim is admitted from the defective prose.

The added control requires Sol to compare a verifier receipt's narrative
command count and mutation wording against the frozen packet and harness
postcondition before acceptance, preserving any mismatch in a distinct
reconciliation receipt.
