# Bernie Stage 1 R2 execution evidence

## Outcome

The restarted provider-free synthetic execution completed S0-S7 evidence on
source commit `2d3fa717d612add9d1f871daf9e899751c5d210c` plus the frozen bounded
Tranche C reference-date correction. The packet is ready for a fresh Sol High
Tranche D acceptance/closeout chat. A separate Extra High pass is not required
merely because High performed the execution. This execution context records
`partial_evidence`, not a final `stage1_pass`.

The non-intercepted happy path is labelled
`live_local_browser_backend_postgres`; supporting direct HTTP replay is
`live_local_backend_postgres`; the six deterministic UI regression nodes are
`route_intercepted_browser`.

## Bounded correction

The unchanged candidate found seven slots but failed closed because the future
pinned `D=2026-07-20` differed from clinic-local today. The failure was
reproduced with zero product writes before editing. The bounded correction in
`app/routers/appointments.py` changes both ordinary backend paths so only a
reference date earlier than clinic-local today is stale. Today and future pinned
dates are current. Six focused past/today/future cases pass and no new policy,
authority, migration, mutation family, provider, or session design was added.

## Scenario result

| Scenario | Result | Key evidence |
|---|---|---|
| S0 | Pass | Fresh isolated synthetic R2 database, authenticated receptionist, eligible practice, fake provider, no external/protected access |
| S1 | Pass | Seven real backend candidates; 14:00 proposal; visible explicit confirmation; counts remain 0/0/0 |
| S2 | Pass | Visible confirmation creates exactly 1 appointment, 1 audit, and 1 completed idempotency result; typed receipt and Diary readback |
| S3 | Pass | Identical HTTP replay returns identical receipt with counts 1/1/1; fresh Diary attempt reports the existing booking and exposes no confirm action |
| S4 | Pass | Two same-name synthetic patients cause bounded DOB clarification; no confirm action; counts 0/0/0 |
| S5 | Pass | Explicit blocking fixture produces typed no-slot result and safe next actions; no Bernie mutation |
| S6 | Pass | Competing fixture added after proposal causes confirmation to fail closed; no Bernie appointment, audit, ledger result, or success receipt |
| S7 | Pass for exact-node scope | Six serial route-intercepted nodes cover selection/recovery/receipt/no-confirm/calm-copy behavior; live S3 covers duplicate behavior |

The whole `review/test_diary_smoke.py` file was not invoked because the
protected-safe rule permits exact pytest node IDs only and forbids test
discovery, while the frozen plan does not provide a complete exact-node list.
The separate Extra High pass must explicitly judge this scope note.

## Verification

- Reference-date focused cases: 6 passed.
- Route-intercepted Diary nodes: 6 passed.
- Combined bounded backend/API Spine command: 11 passed.
- Total recorded pytest cases across commands: 23 passed, 0 failed, 0
  deselected.
- Exact Python compilation and exact-path `git diff --check`: passed.

## Durable artifacts

- Machine-readable packet:
  `docs/bernie-stage1-r2-execution-evidence.json`
- Passed pre-acceptance Ariadne receipt naming all five mandatory sources:
  `orchestration/agent_inbox/codex/bernie-stage1-r2-preacceptance-receipt.json`
- Bounded correction evidence:
  `docs/bernie-stage1-tranche-c-reference-date-correction-evidence.json`
- Backend replay:
  `docs/stage1-evidence/stage1-r2-s3-backend-replay.json`
- Screenshots:
  `docs/stage1-evidence/stage1-r2-final-s1-proposal-before-confirmation.png`,
  `stage1-r2-final-s2-confirmed-receipt.png`,
  `stage1-r2-final-s3-exact-duplicate.png`,
  `stage1-r2-final-s4-ambiguity.png`, `stage1-r2-final-s5-no-slot.png`, and
  `stage1-r2-final-s6-conflict.png`.

## Protocol clarification

Yuri authorized driver-neutral browser evidence and worker-lane economy rules.
They are now in mandatory `AGENTS.md` and
`orchestration/bernie_release_gates.md`. A non-intercepted Playwright script is
equivalent to interactive browser control when it drives the visible UI and
real backend/database path; interception determines the label. Serial,
stateful, tightly coupled acceptance stays Sol-owned unless a separable worker
artifact or required independent veto produces net leverage.

Yuri subsequently clarified that reasoning level follows risk rather than Git
ceremony. Sol High may perform the fresh Tranche D review and check-gated
closeout; Extra High is reserved for material architecture/authority/policy
forks, failed-gate overrides, contradictory evidence, or broader claims. Each
named tranche starts in a fresh chat and repeats five-source rehydration. Native
subagents use the same net-leverage rule as external worker lanes.

No commit, push, baton movement, deployment, release, provider call, external
prompt, cloud mutation, migration, durable session, non-synthetic data access,
or closeout notification was performed. The loopback browser/backend runtime was
stopped after capture; the disposable synthetic database remains available for
the fresh Tranche D acceptance readback.
