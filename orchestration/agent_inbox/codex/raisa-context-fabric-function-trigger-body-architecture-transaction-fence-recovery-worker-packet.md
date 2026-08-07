# Current-transaction fence recovery worker packet

Source HEAD: `7ad40bd337ac6433bd6cc84653dd5883679ed13b`

Worktree: `C:\Users\sarashera\emr4`

Branch: `codex/ariadne-bernie-davida-parallel-seam`

## Read first

Read `AGENTS.md` sections 3-7, the active function/trigger-body plan, its four
normative recoveries, the exact veto, immutable parent contract and current
trigger-program source before editing.

## Owned files

- `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_trigger_programs.py`
- `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_transaction_fence_recovery.py`
- `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-transaction-fence-recovery-worker.md`

Do not edit any other path. Other workers share this worktree; preserve their
changes and do not stage or commit.

## Task

Implement R3 without changing the temporal-update proof.

- In the non-temporal appointment branch, count only exact effects created by
  the current top-level transaction.
- Event membership must be current-XID and exact appointment/type/schema.
- Alias membership must be current-XID insertion for the exact
  practice/source/stream/appointment; an older immutable alias is valid history.
- Outbox membership must be current-XID and tied through the exact alias,
  event, aggregate revision and transaction/appointment relationship; an
  unrelated or historical practice/stream outbox row must be irrelevant.
- Head movement must be assessed as the exact current transaction's movement,
  not historical head existence. Preserve the same-transaction second-update
  rejection and all legal trigger image/terminal behavior.
- Add focused operand-level tests that distinguish historical rows from current
  effects and fail if current-XID or exact relational joins are removed.

Do not weaken the validator/schema and do not regenerate the contract.

## Forbidden surfaces and checks

The same closed surfaces as the plan apply: no SQL/DDL, database/source,
provider/data, app/API/Diary/runtime, command, deployment, Pages, protected ref,
`docs/branding/**`, staging or commit. Run only `py_compile`, focused Ruff and
`git diff --check` on owned paths. Do not run pytest during parallel work; Sol
will run it serially.

## Durable result

Write the owned worker artifact naming exact changes, static checks and any
remaining issue. End with exactly one line:

`RESULT: candidate_ready`

or

`RESULT: blocked — <specific reason>`
