# Ariadne agent-error register revision 164

Date: 2026-08-10

Revision 164 adds AER-0190 as an orchestrator command-verification incident.
Sol initially invoked the package-importing body builder by file path, which
failed with `ModuleNotFoundError`, and a following pytest command in the same
PowerShell invocation made the shell's final exit code reflect only the later
passing tests.

The combined result was rejected immediately. The builder was rerun alone
through its correct module entry point and returned contract SHA-256
`d60eb4bd018a5f9180985db10f9b18c92d797b45844fbba345871085da4834c3`
with exit code zero. Required gates will henceforth run independently or stop
explicitly on first failure, and package builders will use `python -m` unless
their standalone entry point is proven.
