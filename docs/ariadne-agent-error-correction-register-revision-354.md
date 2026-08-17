# Ariadne agent error and correction register — revision 354

Date: 2026-08-18

Timestamp: 2026-08-18T06:28:00+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 354 adds AER-0405. The first focused arrival/check-in convergence
review run passed seven checks and failed five newly authored documentation
fixtures. Four expected phrases crossed Markdown line wraps without whitespace
normalization; one omitted the opening backtick around the untyped route
parameter. No product source or semantic review claim failed.

The correction normalizes multi-line semantic prose, retains literal matching
only for machine-significant tokens, preserves the failed process evidence and
passes all eleven checks in a fresh serial run.

## Population

- incidents: 405;
- corrected or explicitly contained: 405;
- open: 0;
- latest id: `AER-0405`.

No product, data, provider, deployment or protected-ref authority changed.
