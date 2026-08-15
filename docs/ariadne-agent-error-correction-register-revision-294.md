# Ariadne agent error and correction register — revision 294

Date: 2026-08-15

Timestamp: 2026-08-15T20:13:04+10:00 (Australia/Brisbane)

Revision 294 records AER-0333. The register now contains 333 bounded known
incidents, all corrected or contained by an explicit control.

AER-0333 preserves an immediate low-severity process-verification recurrence
after AER-0332. Sol incorrectly reused the same fixed 120-second outer timeout
for a broader six-file local closeout sequence that chained pytest, Ruff and
diff. The wrapper returned exit 124 after about 123.7 seconds; pytest emitted a
stdout-flush `OSError`, and exact process inspection found no surviving Python
child.

The interrupted pytest result is not admitted, and no Ruff or diff result from
the chained command is claimed. No product or evidence corruption occurred.
The corrected run separates every gate. Pytest runs through
`ariadne_serial_pytest` with an explicit 180-second internal timeout and a
240-second outer timeout; Ruff, format, pattern byte comparison, JSON validation
and diff checks run independently and their exact results are recorded.

This is the third occurrence of
`harness.shell_wrapper_timeout_before_live_external_worker_completion`, after
AER-0256 and AER-0332. The strengthened control forbids reuse of arbitrary
fixed outer timeouts: outer budget must exceed the declared inner budget plus
margin, and later gates must never be chained behind a long-running test.
