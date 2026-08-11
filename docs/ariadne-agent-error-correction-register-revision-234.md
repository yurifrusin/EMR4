# Ariadne agent error and correction register — revision 234

Date: 2026-08-11

Revision 234 adds AER-0269. The register records 269 bounded known incidents at
this revision.

## AER-0269 — CF-D1 direct entrypoint lacked repository-root bootstrap

The CF-D1 attempt-001 harness imported its parent through the `scripts` package
before installing the repository root on Python's module path. The invocation
failed closed before the harness, Docker or PostgreSQL ran. No evidence file or
container was created.

This recurs the package-path family already recorded at AER-0058, AER-0066,
AER-0190 and AER-0204. The bounded correction copies the accepted parent
bootstrap, adds a direct child-process entrypoint test, consumes attempt 001 and
requires a distinct attempt 002 after fresh review.
