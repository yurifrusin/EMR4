# Ariadne agent error and correction register — revision 429

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 429 preserves accepted revision 428 and adds AER-0499. During closeout
notification discovery, the orchestrator piped `rg` output into
`Select-Object`, repeating the prohibited one-executable read-only projection
pattern after runtime teardown.

The correction stops publication, records the repetition, advances the exact
generated recurrence list and uses the already identified notification script
directly. The canonical register contains 499 bounded incidents, all corrected
or explicitly contained and none open.

No candidate or protected state changed. The consumed occupied attempt remains
ineligible for retry or resume.
