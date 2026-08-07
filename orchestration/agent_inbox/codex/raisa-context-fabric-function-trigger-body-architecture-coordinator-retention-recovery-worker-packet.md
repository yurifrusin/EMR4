# Coordinator and retention recovery worker packet

Source HEAD: `7ad40bd337ac6433bd6cc84653dd5883679ed13b`

Worktree: `C:\Users\sarashera\emr4`

Branch: `codex/ariadne-bernie-davida-parallel-seam`

## Read first

1. `AGENTS.md` sections 3-7;
2. `docs/raisa-provider-free-unmounted-durability-function-trigger-body-architecture-plan.md`;
3. all four normative recovery documents named by that plan, ending with the
   exact-veto recovery;
4. the exact veto artifact; and
5. the immutable parent contract plus the current entry-program source.

## Owned files

- `scripts/raisa_provider_free_unmounted_durability_function_trigger_body_architecture_entry_programs.py`
- `tests/test_raisa_provider_free_unmounted_durability_function_trigger_body_architecture_exact_veto_entry_recovery.py`
- `orchestration/agent_inbox/codex/raisa-context-fabric-function-trigger-body-architecture-coordinator-retention-recovery-worker.md`

Do not edit any other path. Other workers share this worktree; preserve their
changes and do not stage or commit.

## Task

Implement R1 and R2 of the exact-veto recovery in the typed operand grammar.

- Make the coordinator explicitly represent receipt replay, stored terminal
  replay, conflict/missing/ambiguous admission, predecessor/gap/epoch/key and
  dependent-state branches. Required successful effects must include receipt,
  checkpoint, watermarks, one-way frame retirement, coalesced obligation and
  dependent rows, minimized lifecycle/audit and the exact closed composite.
- Make retention select exactly every lifecycle state except `CONSUMED` and
  bind checkpoint, anchor, active-pin and key populations to that same complete
  generation census. Derive slowest checkpoint, policy grace and actual key
  interval overlap from operands. Use only the exact REC19 reason constants.
- Add focused tests that inspect operands and branches independently of the
  generated whole-contract baseline. They must demonstrate that an ACTIVE-only
  census, out-of-enum reason, unscoped related set, omitted grace/key proof or
  omitted coordinator state/effect fails the focused assertions.

Do not weaken the validator or schema and do not regenerate the contract.

## Forbidden surfaces

No SQL/DDL rendering or execution; migration/database/source/feed/watcher/
listener/provider/network/product/patient/protected data; `app/**`,
`alembic/**`, `docs/api-spine/**`, `docs/diary/**`, `docs/branding/**`;
runtime/command/deployment/release/Pages/protected refs; broad Git staging or
commit.

## Checks

Run only `py_compile`, focused Ruff and `git diff --check` on owned paths. Do
not run pytest while parallel lanes are active; Sol will run the complete
serial suite after reconciliation.

## Durable result

Write the owned worker artifact naming exact changes, static checks and any
remaining issue. End with exactly one line:

`RESULT: candidate_ready`

or

`RESULT: blocked — <specific reason>`
