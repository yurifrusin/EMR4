# Fresh Gemini veto: parse/catalogue digest-recovery rebind

Role: independent contract-binding and containment veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r83`

Branch: `codex/review-context-fabric-parse-digest-rebind-cbc6c2d0`

Baseline HEAD: `580c1d05ed150cdfd63549f1a35e61c72a41cb20`

Candidate HEAD: `cbc6c2d094cca6093bcd7e1289a730b0a1fff2b3`

Read-only exact-worktree review through one fresh Antigravity project. Do not
mutate files/refs, start Docker/PostgreSQL, inspect another worktree or write
worktree-local temporary state. Providers, credentials, protected evidence,
patient/clinical/document/product-derived/real-identity data and
`docs/branding/` are forbidden.

Read `AGENTS.md` completely and name all five rehydration sources. Read the EMR4
API Steward skill/checklist, the digest-domain recovery and threat-model delta,
the parse rebind recovery, the parse plan/design/threat model and the accepted
artifact-review receipt.

Review the exact diff. Verify that:

- the parse contract binds source commit
  `580c1d05ed150cdfd63549f1a35e61c72a41cb20`, 1,404,420 canonical LF bytes
  and artifact SHA-256
  `9407b8b641488b8c48ad51ef58c7ca2c3c15e83dca89da58de8f5726aef69f65`;
- its canonical contract digest and closed JSON Schema are exact;
- the manifest independently binds the same artifact, 412 statements,
  PostgreSQL 16 and the accepted population;
- the parent-validation path checks all these facts before Docker resolution;
- formatting-only movement in the harness changes no command, SQL, timeout,
  pipe cap, cleanup, evidence, catalogue or containment behavior;
- old parse evidence is not claimed as evidence for the revised artifact; and
- a pass authorises exactly one fresh contained parse/catalogue run, not the
  behavior run or any broader surface.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r83 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py tests\test_raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_durability_inert_ddl_rehearsal.py check
git diff --check 580c1d05ed150cdfd63549f1a35e61c72a41cb20..cbc6c2d094cca6093bcd7e1289a730b0a1fff2b3
git status --short --branch
git rev-parse HEAD
```

Additional checks remain read-only. Findings first; confirm clean unchanged
HEAD and separate observation from inference. End exactly `DECISION: pass` or
`DECISION: revision_required`.
