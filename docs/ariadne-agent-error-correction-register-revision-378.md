# Ariadne agent error and correction register — revision 378

Date: 2026-08-18

Timestamp: 2026-08-18T13:22:34+10:00 (Australia/Brisbane)

Status: accepted correction

## Revision

Revision 378 adds AER-0430. Before Gemini preparation, Sol invoked the
repository package CLI `scripts/ariadne_antigravity.py` by file path for its
help output. The process exited 1 because package imports were unavailable.
No provider or verifier launched and the exact candidate stayed unchanged.

Sol immediately reran the command through its admitted module entry point,
`python -m scripts.ariadne_antigravity --help`, which returned exit 0 and the
supported invocation contract. All subsequent repository package CLIs must use
`python -m`, including help and read-only diagnostics.

## Population

- incidents: 430;
- corrected or explicitly contained: 430;
- open: 0;
- latest id: `AER-0430`.

No provider, product data, deployment, release, Pages or protected-ref action
occurred.
