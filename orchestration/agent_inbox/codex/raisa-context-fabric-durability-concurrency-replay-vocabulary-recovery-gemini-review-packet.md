# Fresh recovery veto packet — CF-D1 native replay vocabulary and attempt-004 admission

Review id: `raisa-context-fabric-durability-concurrency-replay-vocabulary-recovery-gemini-36-high-veto-004`

Model: Gemini 3.6 Flash/high in one genuinely fresh Antigravity project

Exact source: `43f168f3d5d1f71ec0f9071c40fadf14b6107621`

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\cf-d1-replay-vocabulary-gemini-review`

Bound branch: `codex/cf-d1-replay-vocabulary-gemini-review`

## Start and scope

Read `AGENTS.md` completely first. Verify the exact root, clean branch and HEAD.
This is a fresh read-only recovery veto. Do not edit, create, delete, stage,
commit, switch, merge, push, start Docker/PostgreSQL, execute either rehearsal
harness, generate runtime evidence, contact a provider/database/application
route/credential/cloud service/network destination, or inspect an unlisted
path.

Inspect only these exact files:

- `AGENTS.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-plan.md`;
- `docs/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-design.md`;
- `docs/security/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal-threat-model-delta.md`;
- `docs/raisa-context-fabric-durability-concurrency-attempt-003-replay-vocabulary-analysis.md`;
- `docs/ariadne-agent-error-correction-register-revision-238.md`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence-attempt-003.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/concurrency-rehearsal-contract.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/concurrency-rehearsal-contract.schema.json`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence.schema.json`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py`;
- `tests/test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py`;
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`;
- `orchestration/continuity/ariadne-agent-error-register/pattern-report.json`;
- `tests/test_ariadne_agent_error_register.py`;
- `scripts/raisa_provider_free_disposable_postgresql_durability_behavior_transaction_rehearsal.py`;
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert`; and
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`.

Do not list or search repository roots, tests, orchestration, fixtures,
holdouts, reports, receipts or untracked paths. Do not inspect
`docs/branding/`. Do not open another path. If an unlisted direct dependency is
necessary, return `revision_required` and name it without opening it.

## Required review

Decide whether this exact recovery truthfully reconciles CF-D1 with the
accepted native replay vocabulary, preserves attempt 003 and all frozen race
semantics, and whether attempt 004 may proceed. Veto on any material
uncertainty. In particular:

1. verify immutable attempt-003 evidence failed closed at
   `c05_exact_coordinator_replay`, expected only `RECEIPT_REPLAY`, admitted no
   observed marker, truthfully counted ten participant and ten precondition
   transactions, cleaned its exact container and proves no pass;
2. independently trace the accepted PostgreSQL enum and exact replay return
   branch and prove the native scalar is `RECEIPT_REPLAYED`;
3. independently trace the accepted serial behavior harness and prove
   `BTR-I03` expects `RECEIPT_REPLAYED`;
4. verify CF-D1 before the correction alone used `RECEIPT_REPLAY`, so the
   diagnosis is source-supported and does not attribute a database failure;
5. verify the correction replaces only that misspelling in the parser
   allowlist, both C05/C06 fresh-replay expectations and all evidence-schema
   marker enums, with no alias or fallback;
6. verify the regression binds the parser, schema and exactly two replay
   coordinates to `RECEIPT_REPLAYED`, rejects the misspelling and preserves an
   existing evidence file byte-for-byte during the direct-entrypoint probe;
7. verify attempt 004 is a distinct fixed evidence path and attempts 002 and
   003 cannot be overwritten;
8. confirm the diff from `359989a77fb3c26d4fa732bac0e52f392b3dd70b`
   changes no accepted SQL, contract, scenario topology, fixture, role,
   isolation, transaction, overlap, wait proof, container, cleanup or claim
   boundary;
9. validate AER-0271 closure, AER-0272 containment, register revision 238,
   pattern report and exact test accounting: 213 AER + 27 implementation + 14
   plan = 254 tests; and
10. verify the review performs zero Docker starts, database operations,
    provider calls, product reads and external-network operations, and identify
    any remaining ambiguity that should block attempt 004.

## Allowed commands

Run only these commands from the bound worktree:

```powershell
git status --short --branch
git rev-parse HEAD
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format --check scripts\raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py tests\test_ariadne_agent_error_register.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py tests\test_raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal_plan.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m py_compile scripts\raisa_provider_free_disposable_postgresql_durability_concurrency_rehearsal.py
git diff --check
git status --short --branch
```

Do not execute either rehearsal script and do not run Docker.

Return `pass` only if there is no P0-P2 finding. In `review`, report exact HEAD,
all reviewed paths, exact per-file/total test counts, command results, findings
with precise file/line support, and explicit Docker starts, database operations,
provider calls, product reads and external operations performed by the review
(all must be zero). Return `revision_required` for any material defect, command
deviation or uncertainty. Emit exactly one schema-constrained terminal decision.
