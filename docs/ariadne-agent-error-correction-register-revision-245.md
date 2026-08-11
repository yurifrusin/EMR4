# Ariadne agent error and correction register — revision 245

Date: 2026-08-11

Revision 245 records and contains AER-0278. The register now contains 278
bounded known incidents.

## AER-0278 — CF-D2 successor admission was ordered too early

Immutable CF-D2 attempt 001 stopped during fixture setup before any scenario or
`SIGKILL`. It recorded `unexpected_terminal_success`, zero external operations
and exact cleanup. A bounded setup-only characterization then proved fixture
calls 1–7 passed and call 8 attempted position-two admission for the first
generation before position one had advanced. The process exited zero but no
allowlisted admission row existed.

The correction changes no inert SQL, contract, classifier, atomic member,
recovery-anchor authority, durability setting or claim. Setup now admits only
position one. R01 and R03 admit position two after durable predecessor progress
and record the least-privilege observer result in their scenario actions. The
closed evidence schema binds ten setup preconditions and at most six actions,
and any new evidence is written only as immutable attempt 002.

This is the one bounded launcher/schema correction permitted by the frozen
CF-D2 plan. It remains pending the complete deterministic recovery gate before
any fresh runtime attempt.
