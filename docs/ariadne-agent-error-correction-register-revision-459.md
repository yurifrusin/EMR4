# Ariadne agent error and correction register — revision 459

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 459 preserves revision 458 and adds AER-0529. The AER-0528 patch added
the correct terminal source assertion but retained the obsolete predecessor
assertion immediately below it, making the fixture demand two mutually
exclusive source heads. The repeated focused packet is rejected as evidence.

The correction removes the obsolete assertion and retains exactly one reviewed
source. The register contains 529 bounded incidents, all corrected or
explicitly contained and none open.
