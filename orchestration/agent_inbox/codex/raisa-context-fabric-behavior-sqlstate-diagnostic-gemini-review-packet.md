# Fresh Gemini veto: safe bootstrap SQLSTATE diagnostic

Role: independent evidence-egress, deterministic-proofreader and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\r78`

Branch: `codex/review-context-fabric-behavior-sqlstate-7fa7fa59`

Baseline HEAD: `7ac63adfe9ccd3d72437235a14730ce06fe6b7a4`

Candidate HEAD: `7fa7fa598dacb014d0510aa42740eaaa2b944c12`

Review only in this exact clean worktree through one fresh Antigravity project.
Do not edit/create/delete/stage/commit/push/deploy, open Docker/PostgreSQL,
inspect another worktree or write worktree-local temporary artifacts. Protected
evidence, credentials, patient/clinical/document/product-derived/real-identity
data, provider calls, runtime gates and `docs/branding/` are forbidden.

Read `AGENTS.md` completely; perform and name the required rehydration sources
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`; then read the EMR4 API Steward skill/checklist.
Inspect only the exact diff, failure evidence 003, AER-0117/0118, evidence
schema, harness and tests.

Adversarially verify:

- failure 003 proves only the recurring generic bootstrap boundary, zero
  scenarios and verified cleanup; it does not prove the remaining cause;
- AER-0117 correctly retracts the prior sole-cause claim without discarding the
  valid foreign-key topology repair;
- the byte regex can admit only one five-character uppercase/digit SQLSTATE
  from an anchored verbose psql ERROR line of bounded prefix length;
- zero matches, multiple distinct matches, malformed tokens, arbitrary prose,
  SQL, row values and messages cannot enter the released `sqlstate` field;
- the evidence schema admits only `^[0-9A-Z]{5}$`, with no widened raw-output
  field, and all historical failures remain schema-valid without it;
- runtime failure construction releases only stage, code, a digest and the
  optional safe SQLSTATE; no stdout/stderr or message survives;
- no SQL, fixture, scenario, DDL, role, grant, RLS, containment, claim,
  provider/data/deployment/Pages/protected-ref boundary changed;
- AER-0118 accurately records the telemetry gap and requires this exact fresh
  veto before one diagnostic rerun.

Run only:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r78 tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal_plan_continuity.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe format --check scripts\raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py tests\test_ariadne_agent_error_register.py
git diff --check 7ac63adfe9ccd3d72437235a14730ce06fe6b7a4..7fa7fa598dacb014d0510aa42740eaaa2b944c12
git status --short --branch
git rev-parse HEAD
```

Additional checks must be read-only and need no worktree-local temp. Findings
come first; confirm unchanged exact HEAD and clean worktree, distinguish
observation from inference and name claims not established. A pass authorises
only one provider-free diagnostic rerun under the unchanged sealed container
boundary. End with exactly one terminal line: `DECISION: pass` or
`DECISION: revision_required`.
