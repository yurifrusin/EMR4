# Fresh Gemini veto: allowlisted bootstrap failure coordinate

Role: independent evidence-egress, PostgreSQL-protocol and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r79`

Branch: `codex/review-context-fabric-behavior-coordinate-dc4c4160`

Baseline HEAD: `7fa7fa598dacb014d0510aa42740eaaa2b944c12`

Candidate HEAD: `dc4c4160e9b6b5c1bdafdb4acb3312ce9c6b7cb5`

Review only in this exact clean worktree through one fresh Antigravity project.
Do not mutate files/refs, deploy, open Docker/PostgreSQL, inspect another
worktree or write worktree-local temp. Protected evidence, credentials,
patient/clinical/document/product-derived/real-identity data, provider calls,
runtime gates and `docs/branding/` are forbidden.

Read `AGENTS.md` completely; perform and report all five rehydration sources:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`; then read the EMR4 API Steward skill/checklist.
Inspect only this exact diff, failure evidence 004, AER-0119, schema, harness
and tests.

Adversarially verify:

- evidence 004 safely establishes only SQLSTATE `23502`, zero scenarios and
  cleanup; it contains no raw message;
- the parser admits exactly one schema/table/column triple from anchored
  verbose psql protocol lines, with each identifier lowercase and bounded;
- a triple is released only if the schema-qualified relation and column match
  the fixed bootstrap allowlist; unknown, malformed, incomplete or ambiguous
  triples release no coordinate;
- every allowlisted relation is actually written by the fixed bootstrap and
  every allowlisted column belongs to that relation in the accepted DDL or
  synthetic prerequisite contract;
- the evidence schema is closed, enumerates only those relations, admits a
  lowercase identifier column, and offers no raw-output/message field;
- the code never releases a relation without its allowlisted column, preserves
  SQLSTATE-only fallback, and hashes the canonical safe metadata dictionary;
- no SQL, fixture, scenario, DDL, role, grant, RLS, containment, claim,
  provider/data/deployment/Pages/protected-ref boundary changed;
- AER-0119 accurately records why this minimal coordinate is needed.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r79 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 7fa7fa598dacb014d0510aa42740eaaa2b944c12..dc4c4160e9b6b5c1bdafdb4acb3312ce9c6b7cb5
git status --short --branch
git rev-parse HEAD
```

Additional checks must be read-only with no worktree-local temp. Findings come
first; confirm unchanged exact HEAD and clean worktree, distinguish observation
from inference and name unestablished claims. A pass authorises only one
provider-free diagnostic rerun under the unchanged sealed container boundary.
End with exactly one terminal line: `DECISION: pass` or
`DECISION: revision_required`.
