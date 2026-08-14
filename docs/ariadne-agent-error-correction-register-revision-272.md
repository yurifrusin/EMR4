# Ariadne agent error and correction register — revision 272

Date: 2026-08-15

Timestamp: 2026-08-15T00:14:48+10:00 (Australia/Brisbane)

Revision 272 records AER-0311. The register now contains 311 bounded known
incidents, all corrected or contained by an explicit control.

AER-0311 records a recurrence of the import-dependent repository-script
invocation error already preserved most recently by AER-0302. During local
pre-verifier preparation, Sol invoked `scripts/ariadne_antigravity.py --help`
by filesystem path. Python failed immediately with `ModuleNotFoundError` for
the `scripts` package before Antigravity, a model, a project or any provider
request started.

The corrected module invocation, `python -m scripts.ariadne_antigravity
--help`, completed locally and exposed the expected CLI. Candidate source, the
clean review worktree, external state and all refs remained unchanged.

For the rest of this tranche, every repository Python harness is invoked only
as `python -m scripts.<module>` from the repository root. A launcher label in
handover text does not establish that direct filesystem-path invocation is
safe.
