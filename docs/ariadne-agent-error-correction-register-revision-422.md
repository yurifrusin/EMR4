# Ariadne agent error and correction register — revision 422

Date: 2026-08-18

Status: accepted correction update

Reasoning level: high

Revision 422 preserves accepted revision 421 and adds AER-0492. The first
Docker network-absence query passed an unquoted Go-template format operand
through PowerShell. Docker rejected it as an invalid shorthand flag before
listing or creating a resource.

The correction requires every Docker format template to be one explicitly
quoted argument. The canonical register contains 492 bounded incidents, all
corrected or explicitly contained and none open.

The exact sparse packet is populated. No worker/broker container, Docker
network or volume, occupied provider call or protected change has started.
