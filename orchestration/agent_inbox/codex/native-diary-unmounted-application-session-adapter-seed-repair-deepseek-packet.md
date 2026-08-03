# Native-Diary runtime acceptance seed repair — DeepSeek packet

Candidate source: `b2b64eee537eb9e2be23045c9510a1ef5ade219f`

Worktree: `C:\Users\sarashera\EMR4-worktrees\native-diary-unmounted-application-session-adapter`

Branch: `codex/native-diary-unmounted-application-session-adapter`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No fallback is authorised.

## Rehydrate and verify

Read `AGENTS.md` completely and state all five mandatory rehydration sources.
Read the EMR4 API Steward skill and checklist completely. Verify the exact
branch, candidate source and clean worktree. Read only the two owned files plus
the exact `Practitioner` column definitions in `app/models/tenancy.py`.

## Exact failed gate

Root ran the live-local HTTP/PostgreSQL acceptance script. It failed closed at
`synthetic_product_seed` with PostgreSQL `DataError`; cleanup passed completely.
No product read occurred. Root traced the deterministic mismatch:

- `provider_number` is `String(20)`, while `SYNTH-ND-PROVIDER-001` is 21 chars.
- `prescriber_number` is `String(20)`, while `SYNTH-ND-PRESCRIBE-01` is 21 chars.

The failed generated evidence was removed and is not part of this repair.

## Task and ownership

Repair only:

- `scripts/raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance.py`
- `tests/test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py`

Use authored-synthetic seed markers of at most 20 characters without weakening
the sensitive-column non-release proof. Add a deterministic test that verifies
all populated bounded practitioner identifiers in the seed remain within their
actual model limits, so the defect cannot recur. Preserve every runtime,
failure, privacy, role, cleanup and evidence contract.

Do not edit any other path. Do not create evidence. Do not run pytest,
PostgreSQL or the acceptance script; root retains the serial lease. You may run
Ruff, py_compile, the new test directly without `conftest.py`, and diff hygiene.

Commit exactly the two owned files with explicit paths. Before committing,
verify `git diff --cached --name-only` is exact and contains no
`docs/branding/`. Never use `git add -A`, `git add .`, `git clean`, fetch,
merge, rebase, switch or push.

Return the five-source statement, exact commit/files/checks/blockers and end
with exactly one `DECISION: pass` or `DECISION: revision_required`.
