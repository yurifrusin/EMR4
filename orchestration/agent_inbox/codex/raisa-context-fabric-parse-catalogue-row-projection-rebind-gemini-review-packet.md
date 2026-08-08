# Independent veto packet: corrected-artifact parse/catalogue rebind

Date: 2026-08-08

Decision required: exactly one terminal `pass` or `fail`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r96`
- Branch: `codex/review-context-fabric-parse-rebind-32bc625d`
- Baseline: `0931f3e658f06e02e7de4c5ea02238184da9e767`
- Candidate: `32bc625debf82726123c95cfe0cd37531f3f22ac`
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

Independently decide whether the existing disposable PostgreSQL parse/catalogue
harness is safely and exactly rebound to the corrected row-composite
projection artifact before any PostgreSQL execution occurs.

The predecessor parse/catalogue pass proves only inert SQL
`sha256:9407b8b641488b8c48ad51ef58c7ca2c3c15e83dca89da58de8f5726aef69f65`.
The candidate must preserve it byte-for-byte under the explicit historical
filename and bind the next proof to exact source
`0931f3e658f06e02e7de4c5ea02238184da9e767`, corrected inert SQL
`sha256:83359fbc0cf2fb8f7d147b5dc820aa28910129428c9727daa1e1dc0259ce73f5`,
1,404,420 LF bytes, 412 statements and canonical parse contract
`sha256:4dc142f8dd357474739fbc79b4964352b8ccd723459ae91f52633ddd1ab4093b`.

## Allowed review surface

Review the exact baseline-to-candidate diff and these candidate files:

- `docs/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-row-composite-projection-order-rebind.md`
- `docs/raisa-provider-free-disposable-postgresql-durability-behavior-row-composite-projection-order-recovery.md`
- `docs/security/raisa-context-fabric-row-composite-projection-order-recovery-threat-model-delta.md`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/rehearsal-contract.json`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/rehearsal-contract.schema.json`
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-parse-catalogue-rehearsal/provider-free-disposable-postgresql-evidence-pre-row-composite-projection-order-recovery.json`
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`
- `scripts/raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py`
- `tests/test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py`
- `tests/test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py`

You may read directly imported repository modules needed to understand these
tests. Do not open, enumerate or search any protected holdout, historical diary,
branding, patient, product-derived or unrelated untracked path. Do not use
repository-wide search outside the exact packet.

## Required challenges

Verify and report:

1. the candidate diff changes only the exact rebind, preserved predecessor
   evidence, tests, documentation and Ariadne provenance;
2. the parent source head, artifact hash, byte count, statement count and
   manifest SQL binding all reconcile exactly;
3. the canonical parse contract digest is correct and enforced before Docker;
4. the predecessor evidence file is byte-identical to the pre-candidate
   canonical pass and still validates against the evidence schema;
5. no catalogue expectation, Docker profile, SQL admission, credential,
   network, port, mount, cleanup, data or claim boundary has widened;
6. the unchanged exact catalogue digests are a coherent expectation because
   the row-projection correction changes function body expressions but no
   catalogue-visible schema, signature, role, privilege, policy or trigger;
7. historical evidence is not used to claim the corrected artifact passed;
8. the 112-test focused packet, Ruff and diff checks pass; and
9. the candidate HEAD and worktree remain exact and clean after review.

Run at least:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r96 tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal_plan.py
git diff --check 0931f3e658f06e02e7de4c5ea02238184da9e767..32bc625debf82726123c95cfe0cd37531f3f22ac
git status --short --branch
git rev-parse HEAD
```

## Forbidden actions

Do not edit, format, commit, push, start Docker/PostgreSQL, run the harness,
contact a provider/product surface, access patient/clinical/product/protected
data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `fail` for any P0-P2 finding, wrong hash/head/count, predecessor-evidence
drift, widened containment/authority, incomplete deterministic packet, dirty
postcondition or evidence claim that treats the historical pass as proof of the
corrected artifact. Otherwise return one exact `pass`. State findings, exact
commands/counts, HEAD and post-review cleanliness.
