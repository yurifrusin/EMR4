# Ariadne agent error and correction register — revision 247

Date: 2026-08-12

Revision 247 records and contains AER-0280. The register now contains 280
bounded known incidents.

## AER-0280 — repeated omitted formatter gate invalidated a planning veto

Sol repeated the exact AER-0274 workflow error: the CF-D2 recovery planning
test passed semantic tests and Ruff lint, but the required Ruff formatter
check was not run locally before commit and verifier dispatch. The fresh Gemini
receipt recorded `ruff format --check` exit 1 with `Would reformat`, yet still
returned `pass`.

That decision is rejected. The worktree remained clean and unchanged, and the
review performed zero Docker, database, provider, product-read or external-
network operations. No recovery implementation or runtime became eligible.

The mechanical correction formats only the new planning test and its paired
baton-consistency test. All 51 exact planning checks, 20 recovery/baton/archive
checks, Ruff lint, Ruff formatting and diff checks then pass. A fresh exact-
HEAD Gemini 3.6 Flash/high veto remains mandatory before implementation.

The stronger prevention control is structural: verifier command lists must be
generated from one locally executed gate whose exit codes are persisted, and
the launcher must reject any nominal external `pass` containing a nonzero
required command outcome.
