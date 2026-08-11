# Ariadne agent error and correction register — revision 208

Date: 2026-08-11

Revision 208 adds AER-0242 and brings the register to 242 bounded incidents.

## AER-0242 — PowerShell statement sequences embedded inside expressions

During AES-C2 preplanning, Sol issued several read-only PowerShell probes with
invalid statement composition. Two commands attempted to pipe directly from a
`foreach` statement without first capturing the collection. Three commands
placed a command and `$LASTEXITCODE` statement sequence inside a parenthesized
object-property expression. PowerShell rejected each affected command at parse
time with `EmptyPipeElement` or `MissingEndParenthesisInExpression`; none of the
intended probes ran and no source, Git ref, worker, receipt or evidence changed.

The corrected probes use explicit intermediate variables: collect `foreach`
output into an array, run each Git command as a separate statement, capture its
exit code into a named Boolean, and only then construct the output object. Each
corrected read-only probe completed successfully.

The prevention control is mechanical: PowerShell orchestration probes use one
statement per step and never embed semicolon-delimited statement sequences
inside a property expression.
