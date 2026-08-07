# Bounded same-lane correction: inert durability DDL rehearsal

Date: 2026-08-07

## Allocation and authority

Work only in `C:\Users\sarashera\EMR4-worktrees\r38` at tracked HEAD
`4a1cf9ce811a60aab6eac28cb17a72fa8a7aec09`, on the existing uncommitted
candidate. Use DeepSeek V4 Flash/high through Claude Code bare. This is the one
mechanical same-lane correction allowed by the accepted plan.

You may edit or regenerate exactly these six paths and no others:

1. `scripts/raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py`
2. `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/lowering-contract.json`
3. `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/lowering-contract.schema.json`
4. `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert`
5. `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`
6. `tests/test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py`

Do not commit, stage, push, contact or start PostgreSQL, execute/apply SQL, use a
database/source/feed/outbox/watcher/listener, install a dependency, access
patient/product/protected data, change application/API/Diary/runtime code,
deploy, release, rebuild Pages, or move any ref. Preserve every other file.

## Why correction is required

The first candidate's 41 self-tests passed, but Sol's source/byte audit found
mechanical PostgreSQL-16 lowering defects. The candidate and its first receipt
are untrusted evidence. Repair the defects below and add hostile regression
tests that would have rejected the first bytes. Do not weaken the recognizer or
assertions merely to make tests pass.

## Required corrections

1. Exact cardinality:
   - `SELECT_EXACT` and `LOCK_EXACT` must detect both zero and more than one row.
     Use valid PL/pgSQL strict selection or an equivalently exact construction.
   - Map both outcomes only to value-free `F_CARDINALITY` / SQLSTATE `CF004` /
     `required_row_missing_or_ambiguous`; do not leak `P0002`, `P0003`, `P0001`
     or class-42 errors.
   - `INSERT`, `UPDATE`, and both the insert-success and winner-reload arms of
     `INSERT_OR_RELOAD_COMPARE` must also prove the accepted exact cardinality.
     The expected-constraint fence and nonmatching `RAISE;` must remain exact.

2. Isolation assertions:
   - Lower every `ASSERT_ISOLATION` to an actual read-only check of
     `current_setting('transaction_isolation')` against the exact required
     `READ COMMITTED` or `SERIALIZABLE` value. A comment is not an assertion.
   - Use the existing value-free registered durability-state outcome
     `F_STATE` / `CF303` / `durability_state_ambiguous`; add no new SQLSTATE,
     setting mutation, transaction control, or caller value.

3. Bounded source deletion:
   - Replace PostgreSQL-invalid `DELETE ... ORDER BY ... LIMIT ... RETURNING
     count(*)` with a valid key-bounded PostgreSQL-16 construction. Select at
     most `max_rows` exact ordered key tuples in a CTE, delete only those tuples
     through exact key equality, count the deleted rows in a second CTE/query,
     and assign the accepted bigint output. No unbounded or key-widened delete.

4. PostgreSQL syntax and exact types:
   - `ARRAY[...]` and `ROW(...)` are grammar constructs, not `pg_catalog`
     objects. Remove every invalid `pg_catalog.ARRAY` and `pg_catalog.ROW` while
     retaining explicit qualified casts, including typed empty arrays.
   - A `SELECT_SET` must produce a deterministically ordered value of its exact
     declared array type even when empty. Do not aggregate an anonymous `record`
     and then coalesce it with a relation-row array. For partial relation
     projections, construct the declared relation row deterministically from
     only accepted projected values plus explicitly typed nulls for unprojected
     user columns; never broaden the source read. System `xmin` is not a member
     of a PostgreSQL table composite. If the immutable set contract cannot be
     represented without dropping a demanded, subsequently observable field,
     stop and report the exact contradictory node instead of inventing a type
     or helper surface. (The two current `xmin` set projections are used only
     for count/absence, but the lowering still must remain honest.)
   - Exact row reads that include system `xmin` must preserve it without
     pretending that `(table_row).xmin` exists. Use a deterministic, typed
     PL/pgSQL representation (for example a `record` local for accepted
     product/system-column projections) so every subsequent `SYSTEM_XMIN`
     expression is valid. Do not add schema objects or read extra columns.
   - Role identifiers are cluster principals, not schema objects. Every
     function owner/grant must use the exact role name, never a schema-qualified
     role token. Ensure the support function also receives its accepted owner.
   - Remove the stray `# test marker`.

5. Canonical values:
   - PostgreSQL and the Python reference must canonicalize `timestamptz` as UTC
     with exactly six fractional digits and a literal terminal `Z`.
   - Preserve the profile as component zero using the same
     `type-byte-length:type-name:value-byte-length:value` rule stated by the
     accepted design. Check rather than assume the current profile frame.
   - Render every array constant with an explicit exact array cast; handle a
     typed empty value if one is introduced. Render JSON exact-key comparison
     with a typed array and a typed empty actual-key result.
   - Fail closed on null/array constants outside the accepted closed typed
     forms; never quote Python `None` or a Python list representation as SQL.

6. Static recognizer and regression evidence:
   - Add recognizer/hostile tests for the invalid first-candidate patterns:
     non-strict exact reads, comment-only isolation, `pg_catalog.ARRAY` /
     `pg_catalog.ROW`, invalid bounded delete syntax, anonymous-record set
     aggregation, schema-qualified owners, missing support owner, and UTC digest
     text without `Z`.
   - Add direct renderer tests that cover zero/multiple exact mapping bytes,
     valid key-bounded delete, typed complete sets (including partial rows),
     system `xmin`, isolation levels, and exact unique-race reload behavior.
   - Audit all renderer statement/expression templates for the same classes of
     PostgreSQL-16 syntax/type error, not only the first occurrences. Do not
     claim server parse or catalogue equivalence; that remains a later closed
     gate.

## Required checks and response

Run, without cache creation:

- the accepted plan test plus the focused implementation test;
- Ruff on the renderer and focused test;
- renderer fixed-path `check`;
- `git diff --check` and exact `git status --short`.

Recompute all artifacts from the corrected renderer. Report actual byte count,
statement/render-node/program/instruction/expression counts from the generated
manifest, not memory. Report either `candidate_ready` with exact evidence or
`blocked_contract_contradiction` naming the smallest immutable contradiction.
Self-acceptance is not permitted.
