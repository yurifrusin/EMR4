# Context Fabric disposable PostgreSQL behavior/transaction plan veto

Perform one fresh read-only independent review of exact clean commit
`1f21a3cca4b6a855fe8992f26023fee1750fd0df` in
`C:/Users/sarashera/EMR4-worktrees/r73` on branch
`codex/review-context-fabric-durability-behavior-plan-1f21a3cc`, using Gemini
3.6 Flash/high.

Rehydrate all five named `AGENTS.md` sources. Verify local/origin `master` and
`handoff/current` remain protected
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Inspect only the exact planning
diff `bc0120f574ff4a9fb34a5d463537542f906c5916..HEAD` and the parent files named
by the candidate contract. Do not inspect protected evidence or unrelated
untracked paths.

The candidate must establish all of these without changing the worktree:

1. The plan is an internal async/context-durability experiment only: no API,
   Diary, application, Alembic, provider, product/patient data, command,
   deployment, Pages or protected-ref authority is added, and no runtime is
   authorized by the planning result itself.
2. All six parent paths, source heads and SHA-256 bindings are exact, including
   inert SQL
   `sha256:a33baca6f622835b62fc84c378f05a49c2936cf28925db6fb5fe4a4fb4d50a36`.
   Parent SQL, functions, triggers, roles, RLS and privileges are unchanged.
3. The whole-document contract/schema freezes exactly twenty ordered scenarios
   with exact category counts `6/4/3/4/3` for entry point, trigger, RLS,
   idempotency and rollback. Every custom failure maps to the accepted body
   failure registry; standard `42501` and injected `P0001` are not
   misclassified.
4. The positive serial thread is implementation-complete and coherent:
   registration -> producer position one -> PRIMARY admission -> coordinator
   apply -> exact replay. The isolated position-two conflict and three outer-
   rollback partitions cannot contaminate the happy thread.
5. Bootstrap superuser setup is explicitly outside behavior evidence. Every
   scenario uses one fresh connection and one pre-transaction session
   authorization; fixture grants touch only the four synthetic `public.*`
   relations and grant no Fabric DML, trigger execute, inheritance, role
   membership, `BYPASSRLS`, schema create or owner authority.
6. Runtime containment is exact no-pull/no-network/no-port/no-mount/tmpfs/
   argv-only/one-container/one-database/exact-ID cleanup. Fixtures are opaque,
   authored-synthetic and contain no patient, clinical, product-derived or
   narrative values. Evidence is counts/digests/SQLSTATEs only.
7. Claim boundaries are honest: selected serial behavior only; concurrency,
   key rotation, retention execution, unknown commit, applied migration,
   runtime wiring, watcher/listener/source access, operational persistence and
   production remain closed.
8. Reproduce the separate pre-existing baseline failure at unchanged HEAD
   `bc0120f574ff4a9fb34a5d463537542f906c5916` only by inspection of the
   candidate's preserved clean-baseline evidence or by the named test in r73:
   `test_idempotency_continuity_index_covers_openapi_command_paths` identifies
   exactly three omitted already-tracked paths. Confirm the candidate changes
   no API Spine file and does not claim repair. This known node is not a
   candidate failure and is excluded from the admitted count.
9. Collect and pass this exact eight-file packet, with only the named baseline
   node deselected:
   - new behavior/transaction plan: 27
   - parse/catalogue parent plan: 9
   - migration/transaction parent plan: 12
   - function/trigger body parent plan: 7
   - API Spine artifacts: 36
   - idempotency continuity index: 4 admitted, 1 named baseline deselected
   - audit correlation continuity index: 7
   - update-confirm idempotency route contract: 22
   Total: exactly 124 collected/admitted and 124 passed, plus exactly one named
   baseline deselection.
10. Validate both new JSON documents, run Ruff on the new test, and run
    `git diff --check bc0120f574ff4a9fb34a5d463537542f906c5916..HEAD`.
    Verify the exact HEAD and clean status after every command.

Use the already-installed primary repository venv executables by absolute path
while keeping cwd at r73. Do not run `uv`, install/update dependencies, edit
files, fetch, push, start Docker/PostgreSQL, access protected evidence, read
patient/product data, call any provider/product runtime, deploy or rebuild
Pages. Report every P0-P3 finding. `pass` requires zero P0-P2 findings and no
unresolved P3 that changes meaning. Do not repair. Emit exactly one schema-
constrained decision.
