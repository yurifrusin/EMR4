# Final evidence veto: corrected-artifact parse/catalogue proof

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r97`
- Branch: `codex/review-context-fabric-parse-evidence-2f0047cd`
- Runtime-candidate baseline: `32bc625debf82726123c95cfe0cd37531f3f22ac`
- Evidence candidate: `2f0047cd90a8448ec4e738483a7237fbf2860bcb`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

Perform and name the five required rehydration sources from `AGENTS.md`:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`.

## Purpose

Independently veto or accept the committed runtime evidence that PostgreSQL 16
atomically admitted the corrected row-composite projection artifact and
reproduced the exact catalogue/privilege contract, with exact cleanup.

This is an evidence review only. Do not start Docker/PostgreSQL or repeat the
runtime. Do not infer behavior proof from parse/catalogue evidence.

## Allowed review surface

- exact diff `32bc625d..2f0047cd`;
- `docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-row-composite-projection-order-rebind.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-row-composite-projection-order-rebind-closeout.md`;
- parse/catalogue `rehearsal-contract.json`, `rehearsal-evidence.schema.json`,
  `provider-free-disposable-postgresql-evidence.json`, and the explicit
  `provider-free-disposable-postgresql-evidence-pre-row-composite-projection-order-recovery.json` predecessor;
- `scripts/raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py`;
- the two parse/catalogue test modules; and
- exact execution/review receipts added by the candidate.

You may read directly imported modules required by those tests. Do not open,
enumerate or search protected holdouts, historical diary, branding,
patient/clinical/product-derived data or unrelated untracked paths.

## Required challenges

Verify and report:

1. evidence schema validity and exact terminal result
   `raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_pass`;
2. exact lifecycle through `catalogue_matched`, `cleanup_verified`, `passed`;
3. parent artifact SHA-256
   `83359fbc0cf2fb8f7d147b5dc820aa28910129428c9727daa1e1dc0259ce73f5`,
   contract SHA-256
   `4dc142f8dd357474739fbc79b4964352b8ccd723459ae91f52633ddd1ab4093b`,
   1,404,420 bytes and 412 statements;
4. every contract-bound exact catalogue digest equals the runtime evidence;
5. exact image ID, `pull_attempted: false`, stable PostgreSQL 16 readiness,
   networkless/no-port/no-mount containment and minimized evidence;
6. cleanup records exact captured ID
   `e44443027e9ad46d4217c48ca042b13326f422b5bc7a88258eeaadb853769e0c`,
   removal and absence verification;
7. committed evidence raw SHA-256
   `ff127b4061bd9fe904c4929e8fff5ab0d06ef72b37710edc3dbd271bec5155d4`;
8. predecessor evidence remains byte-identical at raw SHA-256
   `3ef47b7a14b2581b6c7bf1732594b1e1c322a90e07ec7d43e2e5b5006b1a3281`
   and is not used as corrected-artifact proof;
9. the closeout claims only parse, atomic installation, catalogue and cleanup,
   not function, trigger, RLS or transaction behavior;
10. 113 focused tests, Ruff and diff check pass; and
11. exact HEAD/worktree remain unchanged and clean.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r97 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
git diff --check 32bc625debf82726123c95cfe0cd37531f3f22ac..2f0047cd90a8448ec4e738483a7237fbf2860bcb
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run the harness,
contact a provider/product surface, access protected/product/patient data,
inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `fail` for any P0-P2 finding, evidence/schema/hash/count/catalogue
mismatch, widened claim or authority, missing cleanup proof, historical/current
evidence conflation, incomplete deterministic packet or dirty postcondition.
Otherwise return one exact `pass`, with findings, exact command counts, HEAD and
post-review cleanliness.
