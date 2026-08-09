# Ariadne agent error and correction register revision 148

Date: 2026-08-10

Status: corrected

Revision 148 adds AER-0173 and brings the register to 173 bounded incidents
with zero open incidents.

## AER-0173 — required renderer subcommand omitted

The first renderer 2.0.17 invocation omitted the required `check` or
`regenerate` subcommand. Argparse failed closed with exit code 2 before any
artifact was opened or written and before any database, provider or runtime
contact. The preserved receipt records the exact failure boundary.

The fresh corrected package-module invocation supplied `regenerate`, exited
zero and wrote exactly the four fixed inert outputs. The prevention control is
to inspect the module's fixed CLI choices or invoke `--help` before a first
state-changing CLI call whose complete command shape is not already bound in
the active plan.
