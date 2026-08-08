# Independent veto packet: behavior-contract row-projection rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r98`
- Branch: `codex/review-context-fabric-behavior-rebind-17fe1ea6`
- Baseline: `bec71540424a2a4bcdb21434129f051945aedd40`
- Candidate: `17fe1ea650d5353712bd1dbcef6d9d25b9f137e6`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name:

1. `live_handover_current_baton`;
2. `current_authority_allocation`;
3. `active_plan_and_acceptance`;
4. `protected_evidence_boundaries`; and
5. `git_refs_and_worktree`.

## Purpose

Independently decide whether the existing disposable PostgreSQL behavior and
transaction rehearsal is safely and exactly rebound to the independently
accepted corrected row-composite projection artifact before behavior attempt
016 may run.

Behavior attempt 015 failed before admitting any scenario, at `BTR-E01`, with
SQLSTATE `22P02` inside
`emr4_context_fabric.register_observer_generation_v1`. The corrected artifact
has separately passed the PostgreSQL parse/catalogue proof. The candidate must
update only the behavior proof-chain parents and harness digest while leaving
all twenty scenarios byte-for-byte unchanged.

## Allowed review surface

Review the exact baseline-to-candidate diff and these files:

- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-row-composite-projection-order-rebind.md`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal/behavior-transaction-rehearsal-contract.json`
- `scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`
- `tests/test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`
- `tests/test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/synthetic-prerequisite-contract.json`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence.json`
- `docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-row-composite-projection-order-rebind-closeout.md`
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`
- `orchestration/continuity/raisa-provider-free-unmounted-durability-function-trigger-body-architecture/function-trigger-body-architecture-contract.json`
- the candidate Ariadne runtime-state/receipt files named by the exact diff.

You may read directly imported repository modules needed to understand these
tests. Do not open, enumerate or search any protected holdout, historical
Diary, branding, patient, product-derived or unrelated untracked path. Do not
use repository-wide search outside the exact packet.

## Required challenges

Verify and report:

1. candidate HEAD and exact baseline-to-candidate diff;
2. exactly six parent bindings reconcile to the current canonical files,
   their recorded source heads and UTF-8/LF SHA-256 values;
3. the accepted runtime source is the corrected parse/catalogue closeout at
   source `2f0047cd90a8448ec4e738483a7237fbf2860bcb`, and the ledger's current
   canonical text legitimately names that accepted source;
4. corrected inert SQL is exactly
   `sha256:83359fbc0cf2fb8f7d147b5dc820aa28910129428c9727daa1e1dc0259ce73f5`,
   render-manifest file hash is exactly
   `sha256:66c103adac8c9ba52440077e25d2f3fc58ed6d30005576034bb42115c746dd71`,
   body-contract file hash is exactly
   `sha256:4338082445261a8a4aeaaa09d9aa615812d1585fa47b44a05abc716a1df84242`,
   and the parse prerequisite remains exactly
   `sha256:313d283b4a53c08a34b65f7c932457010cc9317c87a3bfe6a1b9dc218ba220b7`;
5. the canonical behavior contract digest is exactly
   `sha256:0ac09578c56aeb6528f5a05dc1e32f5b71d953dfd43ab6d8b5030cab202e7d03`
   and is enforced before any Docker resolution or process start;
6. after removing only `parent_bindings`, the candidate behavior contract is
   structurally and byte-semantically identical to the baseline contract:
   all twenty scenario objects, exact order, fixture/principal inputs,
   SQLSTATEs, transaction shapes, readbacks, forbidden effects and cleanup
   requirements are unchanged, with category counts `6/4/3/4/3`;
7. the current attempt-015 evidence remains outside the candidate commit and
   is neither rewritten nor used as proof of the corrected contract;
8. no Docker profile, credential, network, port, mount, data, evidence, claim,
   product-write, provider or authority boundary widened;
9. the 180-test behavior-plus-parse deterministic packet, Ruff and diff checks
   pass; and
10. HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r98 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan.py
git diff --check bec71540424a2a4bcdb21434129f051945aedd40..17fe1ea650d5353712bd1dbcef6d9d25b9f137e6
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run the behavior
harness, contact a provider/product surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `fail` for any P0-P2 finding, wrong hash/head/count, scenario drift,
widened containment/authority, incomplete deterministic packet, dirty
postcondition, or evidence claim that treats attempt 015 as proof of the
corrected artifact. Otherwise return one exact `pass`. State findings, exact
commands/counts, HEAD and post-review cleanliness.
