# Davida pure-read SQL-capture repair — DeepSeek packet

Candidate source: `90781e212ac04a7b58135c9c9d9a202c6682d3f9`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-pure-read-context-desk`

Branch: `codex/davida-pure-read-context-desk`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No fallback is authorised.

## Rehydrate and verify

Read `AGENTS.md` completely and state all five mandatory rehydration sources.
Read the EMR4 API Steward skill and checklist completely. Verify the exact
branch, candidate source and clean worktree. Read only the two owned files.

## Exact failed gate

Root ran the provider-free in-process PostgreSQL acceptance script. Every data,
tenant, active-only, bounds, context-frame, privilege-denial, sensitive-residue,
table/session-integrity and cleanup gate passed. The result correctly remained
`revision_required` only because `select_reads_present` was false while seven
non-DML statements were captured.

The deterministic classifier defect is exact: it applies `.upper()` to each
captured SQL statement and then searches for lowercase fragments
`"FROM practice_locations"` and `"FROM practitioners"`, which can never match.
The failed generated evidence was removed and is not part of this repair.

## Task and ownership

Repair only:

- `scripts/davida_provider_free_practice_administration_pure_read_acceptance.py`
- `tests/test_davida_provider_free_practice_administration_pure_read.py`

Make the SELECT-presence classifier case-consistent and narrowly prove that it
requires both the `practice_locations` and `practitioners` reads while still
rejecting any DML/DDL statement. Add deterministic regression coverage that
would fail on the current mixed-case bug. Preserve every service, context,
contract, role, privacy, cleanup and evidence requirement.

Do not edit any other path. Do not create evidence. Do not run pytest,
PostgreSQL or the acceptance script; root retains the serial lease. You may run
Ruff, py_compile, the new pure test directly without `conftest.py`, and diff
hygiene.

Commit exactly the two owned files using explicit staging paths. Before
committing, verify `git diff --cached --name-only` is exact and contains no
`docs/branding/`. Never use `git add -A`, `git add .`, `git clean`, fetch,
merge, rebase, switch or push.

Return the five-source statement, exact commit/files/checks/blockers and end
with exactly one `DECISION: pass` or `DECISION: revision_required`.
