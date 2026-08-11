# Fresh recovery veto packet — CF-D1 marker telemetry and attempt-003 admission

Review id: `raisa-context-fabric-durability-concurrency-marker-telemetry-recovery-gemini-36-high-veto-003`

Model: Gemini 3.6 Flash/high in one genuinely fresh Antigravity project

Exact source: `359989a77fb3c26d4fa732bac0e52f392b3dd70b`

Bound worktree:
`C:\Users\sarashera\EMR4-worktrees\cf-d1-marker-telemetry-gemini-review`

Bound branch: `codex/cf-d1-marker-telemetry-gemini-review`

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
- `docs/raisa-context-fabric-durability-concurrency-attempt-002-marker-telemetry-analysis.md`;
- `docs/ariadne-agent-error-correction-register-revision-237.md`;
- `orchestration/continuity/raisa-provider-free-disposable-postgresql-durability-concurrency-rehearsal/provider-free-durability-concurrency-evidence-attempt-002.json`;
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
- `scripts/raisa_provider_free_disposable_postgresql_durability_parse_catalogue_rehearsal.py`;
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/durability-schema.sql.inert`; and
- `orchestration/continuity/raisa-provider-free-unmounted-durability-inert-ddl-rehearsal/render-manifest.json`.

Do not list or search repository roots, tests, orchestration, fixtures,
holdouts, reports, receipts or untracked paths. Do not inspect
`docs/branding/`. Do not open another path. If an unlisted direct dependency is
necessary, return `revision_required` and name it without opening it.

## Required review

Decide whether this exact recovery adds actionable minimized failure evidence
and truthful attempt accounting without changing the frozen races, and whether
attempt 003 may proceed. Veto on any material uncertainty. In particular:

1. verify immutable attempt-002 evidence failed closed at `result_marker`,
   completed zero scenarios, cleaned its exact container and proves no pass;
2. verify the diagnosis correctly rejects the static twelve-transaction field
   as actual-attempt accounting without inventing an exact historical count;
3. trace `_counting_runner`: it must recognize exactly one fixed
   `application_name` marker, count `_a`/`_b` as participant and `_r` as
   precondition under a lock, ignore every nonparticipant stdin payload, and
   fail on ambiguous markers;
4. verify pass evidence now requires exactly twelve participant and eleven
   precondition transactions, while historical attempt-002 failure remains
   whole-document schema-valid without the optional new count;
5. trace every `_expect_success`/`_expect_failure` call and verify its fixed
   coordinate is correct, syntactically closed and cannot receive database
   content;
6. verify `_bounded_failure` releases only closed coordinate, principal,
   isolation, allowlisted result markers/count and safe SQLSTATE and cannot
   retain raw stdout, stderr, query, server text, PID, lock key or payload;
7. verify attempt 003 is a distinct evidence path and no attempt-002 evidence
   is overwritten;
8. confirm diff from `73cd360c68e835d8abe86846810198ee5cc9f6b7`
   changes only telemetry/accounting/evidence schema/tests/AER provenance and
   makes no SQL, scenario, fixture, role, isolation, transaction, overlap,
   container, cleanup or claim-contract change;
9. validate AER-0271, register revision 237, pattern report and exact test
   accounting: 213 AER + 26 implementation + 14 plan = 253 tests; and
10. verify the review performs zero Docker starts, database operations,
    provider calls, product reads and external-network operations, and identify
    any remaining ambiguity that should block attempt 003.

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
