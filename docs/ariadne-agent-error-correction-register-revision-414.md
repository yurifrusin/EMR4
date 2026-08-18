# Ariadne agent error and correction register — revision 414

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 414 preserves accepted revision 413 and adds AER-0484. During the
exact-tool-view proof checks and pre-dispatch rehydration, the orchestrator
used a bounded series of read-only PowerShell pipelines for file slicing and
metadata projection. Those commands changed no repository or protected state,
but violated the exact one-executable, no-pipeline command rule.

The correction stopped pipeline use before occupied dispatch, changed
subsequent reads to direct indexed expressions, and adds a focused invariant
to the complete register suite. The canonical register contains 484 bounded
incidents, all corrected or explicitly contained and none open.

This correction does not broaden the exact tool view, worker package, provider,
data, application, deployment, release, Pages or protected-ref authority.
