# Ariadne agent error and correction register — revision 424

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 424 preserves revision 423, AER-0493 and adds AER-0494. During source
inspection for the correction, the orchestrator again used a read-only
PowerShell pipeline despite the exact one-executable rule restored by AER-0484
and AER-0485.

The correction stops occupied setup, preserves the repetition explicitly and
requires one executable with native context arguments for every subsequent
source inspection. The canonical register contains 494 bounded incidents, all
corrected or explicitly contained and none open.

The exact sparse packet and disposable runner files are populated. No Harness
session, broker/worker container or occupied provider call has started.
