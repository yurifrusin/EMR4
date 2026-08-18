# Ariadne agent error and correction register — revision 450

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 450 preserves revision 449 and adds AER-0520. The first complete
revision-449 register run retained two stale population fixtures: its global ID
range stopped before AER-0519 and its standalone agent-origin count remained at
the pre-incident value. The run is rejected as acceptance evidence.

The correction advances the full ID range, standalone origin length, revision,
total, aggregate dictionaries and affected recurrence baselines atomically,
then regenerates the canonical pattern report. The register contains 520
bounded incidents, all corrected or explicitly contained and none open.
