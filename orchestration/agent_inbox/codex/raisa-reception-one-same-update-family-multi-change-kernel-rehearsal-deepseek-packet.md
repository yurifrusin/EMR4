# DeepSeek packet — same-update-family multi-change kernel rehearsal

Date: 2026-08-14

Timestamp: 2026-08-14T22:49:35+10:00 (Australia/Brisbane)

## Identity and immutable source

- Worker: DeepSeek V4 Flash/high through Claude Code `--bare`.
- Worktree: `C:\Users\sarashera\EMR4-worktrees\same-update-multi-change-worker-5411d09a`
- Branch: `codex/worker-reception-one-same-update-multi-change-5411d09a`
- Required start HEAD: `5411d09a132b0cc28a1bec5045c3819986c642b4`
- Base task branch: `codex/ariadne-bernie-davida-parallel-seam`

Confirm the exact worktree, branch, clean state and start HEAD before reading or
changing anything. If any differs, return `blocked` without mutation.

## Objective

Implement the frozen M1-M7 provider-free authored-synthetic rehearsal in one
new test module. Prove that changed practitioner, local time and duration travel
through the existing appointment update proposal/confirm path as one command,
including stale truth, new conflict, inactive target, exact replay, different-
body key conflict, correlated audit/idempotency and injected pre-commit rollback
followed by clean same-key retry.

## Mandatory exact reads

Read `AGENTS.md` completely, then only these task sources unless a Python import
error names one exact additional ordinary file:

- `docs/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-plan.md`
- `docs/security/raisa-reception-one-same-update-family-multi-change-kernel-rehearsal-threat-model-delta.md`
- `app/schemas/appointments.py`
- `app/routers/appointments.py`
- `app/models/appointments.py`
- `app/models/tenancy.py`
- `tests/conftest.py`
- `tests/test_appointment_update_proposal.py`
- `tests/test_api_spine_update_confirm_idempotency_route_contract.py`
- `tests/test_bernie_stage2_confirmation_recovery.py`

Do not run repository-wide search, file enumeration, recursive listing, `rg`,
`grep`, `find`, `Get-ChildItem`, `git grep`, `git ls-files` or glob discovery.
Do not open any protected fixture, historical Diary material, local data,
provider artifact or unrelated untracked path.

## Owned path

You may create and modify exactly:

- `tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py`

No other file may change. In particular do not edit `app/**`, `docs/**`,
OpenAPI, GraphQL, UI, migrations, configuration, receipts, plans or handover
state. If an existing product defect appears necessary to fix, preserve the
failing test and return `blocked_product_recovery_required`; do not repair it.

## Required test design

- Use newly authored synthetic appointments and practitioners only.
- Freeze the clinic clock at a known future-open authored-synthetic time.
- Exercise the ordinary proposal HTTP route for candidate construction.
- Exercise the real confirm route or direct route function with an independently
  owned SQLAlchemy session where transaction rollback must be observed.
- Commit fixture setup before direct-session rollback/replay operations.
- For M1, assert one full command carries all three new values and proposal
  causes no appointment/audit/idempotency mutation.
- For M2, assert all three values commit together and exactly one update audit
  plus one completed idempotency row correlate by command and appointment.
- For M3-M5, snapshot counts after the independently committed intervening
  truth change and assert the candidate confirmation adds no mutation or claim.
- For M6, replay the exact body and key from a fresh session, return the exact
  stored body, keep counts unchanged, then prove different validated body with
  the same key returns `idempotency_key_conflict` without mutation.
- For M7, monkeypatch `complete_appointment_command` to raise after update and
  audit flush but before route commit. Invoke using a separately owned session,
  let context-manager closure roll back, verify original practitioner/time/
  duration and zero new audit/ledger, then restore the helper and prove one clean
  same-key success plus mutation-free replay.
- Do not assert committed-event behavior; its feature posture is unchanged and
  outside this claim.
- Prefer a small number of cohesive tests, but every M1-M7 property must be
  directly asserted.

## Required commands

Run serially from the worker worktree using the primary workspace interpreter:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff format tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests/test_appointment_update_proposal.py tests/test_api_spine_update_confirm_idempotency_route_contract.py tests/test_api_spine_artifacts.py tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py
git diff --check -- tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py
git status --short
```

Repository pytest processes share one PostgreSQL schema. Do not run any pytest
commands concurrently.

## Commit and postcondition

If and only if all required commands pass and the owned path is the sole change:

```powershell
git add -- tests/test_raisa_reception_one_same_update_family_multi_change_kernel_rehearsal.py
git commit -m "test(reception-one): rehearse combined update kernel"
```

Do not push. End with a clean worktree on the worker branch. If any check fails,
do not weaken the matrix, do not amend product source and do not claim success.

## Decision format

Return exactly one JSON object and no prose:

```json
{
  "decision": "candidate_ready|blocked|blocked_product_recovery_required",
  "start_head": "full sha",
  "end_head": "full sha",
  "branch": "exact branch",
  "owned_paths_changed": ["exact paths"],
  "commit": "full sha or null",
  "tests": [{"command": "exact command", "exit_code": 0, "summary": "short"}],
  "worktree_clean": true,
  "issues": []
}
```
