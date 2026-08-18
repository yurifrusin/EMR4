# Ariadne agent error and correction register — revision 373

Date: 2026-08-18

Timestamp: 2026-08-18T10:14:34+10:00 (Australia/Brisbane)

Status: accepted bounded correction

## Revision

Revision 373 adds AER-0425. Gemini's first admitted decision found no
substantive defect in the exact check-in adapter. It returned
`revision_required` solely because the manifest placed the fixture-dependent
A5.1 runtime suite inside a provider-free no-conftest command. This repeated
the test-selection class already preserved by AER-0420.

The corrected manifest retains only four self-contained adapter, plan and
convergence suites; their exact unchanged-candidate run passes 101/101. The
verifier preflight also now uses the canonical parsed-manifest digest produced
by `load_command_manifest` and `command_manifest_sha256`, not a raw JSON-file
hash.

## Population

- incidents: 425;
- corrected or explicitly contained: 425;
- open: 0;
- latest id: `AER-0425`.

The product candidate remains unchanged at
`8de886c5148b3259428c8c517674f10ea92d937e`. No route, database, patient or
product data, deployment or protected ref opened.
