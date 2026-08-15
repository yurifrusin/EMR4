# DeepSeek worker packet — delete-confirm physical scaffold

Date: 2026-08-15

Timestamp: 2026-08-15T21:31:00+10:00 (Australia/Brisbane)

Decision authority: Sol only

Worker: DeepSeek V4 Flash / high through Claude Code `--bare`

Exact source HEAD: `d500f1f86a83695cee0c2aac93aa2e2735e8f799`

Exact worktree: `C:\Users\sarashera\EMR4-worktrees\r192`

Exact branch: `codex/worker-delete-confirm-scaffold-d500f1f8`

## Required reading

Read `AGENTS.md` completely, then read these exact controlling files:

- `docs/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold-plan.md`;
- `docs/security/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture/physical-design-contract.json`;
- `app/models/tenancy.py`;
- `app/models/appointments.py`;
- `app/services/appointment_status_physical.py`; and
- `alembic/versions/w2x3y4z5a6b7_add_status_confirm_physical_scaffold.py`.

The plan is closed. Do not make a new semantic choice. If exact implementation
is impossible, stop with `DECISION: revision_required` and identify the
contradiction.

## Exact implementation task

Implement the complete narrow scaffold described by the plan. You may edit
only:

- `app/models/tenancy.py`;
- `app/models/appointments.py`.

You may create only:

- `alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py`;
- `app/services/appointment_delete_physical.py`;
- `tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py`;
- `scripts/raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/scaffold-contract.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/scaffold-contract.schema.json`;
- `orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold/provider-free-scaffold-evidence.json`.

Do not edit `app/models/__init__.py`; importing `app.models.tenancy` already
registers the new mapping. Do not edit or mount any router, schema, OpenAPI,
generic idempotency service, status service or earlier migration.

## Two non-negotiable audited traps

1. Generation-trigger composition: a direct submitted user generation must be
   ignored, while each capability INSERT/DELETE must advance the exact parent
   generation once. A naïve nested `UPDATE users` that the user trigger
   neutralizes is a failure. Freeze and statically test the tightly bounded
   nested database-owned path, direct injection suppression, grant UPDATE
   rejection and overflow rollback.
2. Transaction ordering: do not copy status-confirm's insert-first behavior or
   one fixed timeout. Use one monotonic cumulative 2000 ms deadline and exact
   order `User FOR SHARE -> Appointment FOR UPDATE -> full authority check ->
   select existing idempotency FOR UPDATE -> only-if-absent target-bound
   conflict-do-nothing insert -> winning row FOR UPDATE -> repeat full authority
   check -> classification`. Apply only positive remaining budget before every
   potentially blocking statement.

Both authority checks must be internal, not a caller callback, and require
active exact user, exact authenticated server role in the admitted set, signed
generation equal to locked truth and exact `appointment.cancel.confirm` row.

## Incompleteness boundary

The new service is unmounted. It may expose pure canonical-response,
session-binding, integrity, authority/classification and transaction-context
helpers. It must not itself verify a real proposal, mutate an appointment,
create an audit, complete a receipt or return display truth. A yielded
`new_command` context that is not completed by a future separately admitted
kernel must fail closed and roll back on context exit.

No migration function, DDL/SQL, engine, database, route or real lock may be
executed during this task or its tests.

## Deterministic artifacts and tests

Create a closed schema-valid contract and minimized authored-synthetic evidence
bound to source HEAD `d500f1f86a83695cee0c2aac93aa2e2735e8f799` and exact input/
implementation hashes. The validator must be provider-free and must not import
application, Alembic, database, network or provider modules. The focused test
must prove the full plan and reject at least ninety hostile mutations.

Run, separately:

1. `.venv\Scripts\python.exe scripts\raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py`
2. `.venv\Scripts\python.exe -m pytest -q tests\test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py`
3. `.venv\Scripts\python.exe -m pytest -q tests\test_raisa_provider_free_unmounted_status_confirm_physical_schema_transaction_scaffold.py`
4. `.venv\Scripts\ruff.exe check app\models\tenancy.py app\models\appointments.py app\services\appointment_delete_physical.py scripts\raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py tests\test_raisa_provider_free_unmounted_delete_confirm_physical_schema_transaction_scaffold.py alembic\versions\x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py`
5. `git diff --check`

The worker `.venv` is a junction to the repository environment. These tests are
static/provider-free; do not start or contact PostgreSQL.

## Completion

Inspect the exact changed-path set. Stage only the nine authorised source/
evidence paths with explicit path names, commit them on the worker branch with
message `Implement delete-confirm physical scaffold`, and do not push.

Return exactly:

- `DECISION: pass` or `DECISION: revision_required`;
- the full candidate commit and parent;
- exact changed files;
- each command and exit result;
- hostile mutation count;
- confirmation of zero database, migration, route, provider, product-data,
  network, push and protected-ref action; and
- any remaining risk or contradiction.

Worker self-pass is provenance only. Sol admission and a fresh Gemini 3.7
Flash/high exact-candidate veto remain mandatory.
