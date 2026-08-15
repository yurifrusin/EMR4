# Ariadne agent error and correction register — revision 295

Date: 2026-08-15

Timestamp: 2026-08-15T21:18:03+10:00 (Australia/Brisbane)

Revision 295 records AER-0334. The register now contains 334 bounded known
incidents, all corrected or contained by an explicit control.

AER-0334 records a low-severity recurrence of unsafe validation composition
during the delete-confirm scaffold plan gate. Sol invoked two package-aware
CLIs by file path and chained them before `git diff --check`. Both CLIs failed
to import `orchestration_harness`, but the final successful diff command made
the shell call return zero. A separately captured pytest still rejected the
new in-progress latch because its terminal reason was not the one closed
literal required by the validator.

No worker was dispatched, no product source was admitted, and no external or
database action occurred. The latch literal was corrected, the CLIs were
re-run through `python -m`, and latch, journal, focused pytest and diff gates
then passed as four separately captured outcomes.

The strengthened control generalizes AER-0333: admission gates may run in
parallel, but each must be a separately captured process result. Sequential
shell chaining is forbidden wherever a later success could mask an earlier
failure. Repository package CLIs must use their admitted module invocation.
