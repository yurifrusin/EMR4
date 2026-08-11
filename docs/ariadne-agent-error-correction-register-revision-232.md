# Ariadne agent error and correction register — revision 232

Date: 2026-08-11

Revision 232 adds AER-0267. The register now contains 267 bounded known
incidents.

## AER-0267 — short recovery commit fabricated into a full source ID

Sol expanded displayed short commit `e3ebc119` into a nonexistent forty-
character source ID while drafting the first local-fake preexecution state.
The mistake was detected before preflight and before any database, product,
credential, cloud or provider action. The invalid state supplies no authority.

The corrected attempt captures the full ID directly with `git rev-parse HEAD`,
verifies it with `git cat-file -e`, and repeats all five sources in a new state.
