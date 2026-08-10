# Independent veto: admission-replay parse characterization rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `revision_required`.

Review clean worktree
`C:\Users\sarashera\EMR4-worktrees\raisa-context-fabric-durability-parse-r177`
on branch `codex/review-context-fabric-admission-replay-parse-char-f5c8fb0f`
at exact candidate `f5c8fb0f01dc5836647b90acdf96c8ed6c21fc05`, predecessor
`cbac3a940890baa48b3ee245026a5935f61058db`. Protected local/origin `master`
and `handoff/current` must remain exactly
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform the complete AGENTS.md five-source rehydration naming
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

Review only AGENTS.md; exact diff
`cbac3a940890baa48b3ee245026a5935f61058db..f5c8fb0f01dc5836647b90acdf96c8ed6c21fc05`;
the parse contract/schema, fixed harness, focused tests and bounded rebind note.
Do not inspect either mutable evidence alias, holdouts, historical Diary data,
`docs/branding/`, patient/clinical/product data or unrelated paths.

Verify:

1. exact clean candidate before/after and protected refs;
2. parent source is exact independently accepted
   `5a9a7ae907308aa0a8a4256e9043b833f8c416ae`;
3. artifact is exact 424 statements, 1,436,664 LF bytes and SHA-256
   `dc475f71005a2b5a37de829e7f5e21be425dc970091e5b5567099cf2449142d7`;
4. canonical contract SHA-256 is
   `942ed41554fee46b3c4d11e663afd5e62c3c5e00250fc21fabb3e06009c98726`;
5. catalogue mode is exactly `characterization_only` with an empty expected
   digest map, so the run cannot self-accept a new catalogue;
6. Docker remains pull-never, networkless, portless, mountless, tmpfs-only,
   fixed-path and exact-ID-cleanup bounded;
7. all generated SQL and security/authority boundaries are unchanged from the
   reviewed parent;
8. the commands below pass with a clean postcondition; and
9. no Docker/PostgreSQL run, operational database, watcher/feed,
   application/API/Diary wiring, provider/product data, deployment, Pages or
   protected-ref boundary opens.

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r177 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py
git diff --check cbac3a940890baa48b3ee245026a5935f61058db..f5c8fb0f01dc5836647b90acdf96c8ed6c21fc05
git status --short --branch
git rev-parse HEAD
git rev-parse master
git rev-parse handoff/current
git rev-parse origin/master
git rev-parse origin/handoff/current
```

Do not edit, commit, push, start Docker/PostgreSQL, run either disposable
database harness, contact another provider/product, inspect forbidden data,
move refs or self-accept. Return `revision_required` for any P0-P2 finding,
drift, failed check or dirty postcondition; otherwise return exact `pass`.
