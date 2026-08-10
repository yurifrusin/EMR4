# Ariadne agent error and correction register — revision 199

Date: 2026-08-08

Revision 199 adds AER-0233 and brings the register to 233 bounded incidents.

## AER-0233 — expected native nonzero exit was promoted to a PowerShell error

The first post-attempt exact-ID Docker absence command used
`$ErrorActionPreference='Stop'`. PowerShell promoted Docker's expected
`no such object` stderr and exit 1 into a terminating native-command error after
the immutable copy and protected-alias restoration had already completed. The
fresh exact-ID-only check used explicit exit-code capture and confirmed absence.
Future expected-nonzero probes must locally capture the native result before
interpreting it.
