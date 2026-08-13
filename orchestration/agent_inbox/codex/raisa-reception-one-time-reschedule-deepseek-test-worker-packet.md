# DeepSeek V4 Flash/high bounded test-engineering packet

Date: 2026-08-14

Timestamp: 2026-08-14T07:58:00+10:00 (Australia/Brisbane)

Source HEAD: `19e2f5021dd188643a7a723657beac2536daa044`

Assigned worktree: `C:\Users\sarashera\EMR4-worktrees\rt1`

Assigned branch: `codex/reception-one-time-reschedule-test-worker`

## Authority

You are the DeepSeek V4 Flash/high test-engineering worker. You own exactly one
new artifact: `review/test_reception_one_time_reschedule_action.py`. You may
read the exact allowlist below, create and edit only that new file, run only the
listed checks, stage that exact file, and make one worker commit. You have no
product implementation, existing-test edit, orchestration, acceptance,
integration, push, protected-ref, provider, database, runtime or deployment
authority. Permission availability is not authority.

Read `AGENTS.md` completely before acting. Then read:

- `docs/raisa-reception-one-selected-appointment-time-reschedule-composition-plan.md`
- `docs/security/raisa-reception-one-selected-appointment-time-reschedule-composition-threat-model-delta.md`
- `review/test_reception_one_status_action.py`
- `review/test_two_projection_truth_parity.py`
- `review/test_diary_smoke.py`
- `docs/diary/diary.js`
- `docs/diary/meta-grid.js`
- `docs/diary/meta-grid.css`
- `docs/diary/diary.html`

Use literal exact-path reads only. Do not use Glob, Grep, `rg`, recursive
search, directory listing, protected paths or any file outside that allowlist
and your new test artifact.

## Deliverable

Create one self-contained, authored-synthetic, provider-free pytest browser
contract for the same-date, same-practitioner, duration-fixed selected-
appointment start-time action. Reuse patterns by copying only the minimum
helpers needed into the new file; do not edit or import mutable helpers from an
existing test module if that would make the artifact order-dependent.

The contract must require:

1. A selected-card 15-minute-step time input and `Review time change` action.
2. A bridge that computes start delta, fixes duration delta at zero and
   delegates to existing `handleMoveResize`; it owns no fetch, route, proposal,
   confirm, signing, idempotency or raw PUT implementation.
3. Existing update proposal and proposal-supplied confirm routes only.
4. Six paired `conventional_grid` / `reception_one` outcomes: safe commit,
   warning cancel, blocked, stale confirmation, transport failure and explicit
   warning commit.
5. Identical fresh normalized appointment id, date, start, end, practitioner,
   duration, patient linkage and status for each pair; exact route counts;
   zero raw PUT and zero unexpected mutation routes.
6. Separate invalid/no-op zero-route, interruption/fresh-reconciliation,
   keyboard/focus/Escape and desktop/tablet/phone no-overflow cases.
7. Evidence labels `route_intercepted_browser` and
   `authored_synthetic_client_fixture`; never claim live product operation.

Aim for a readable bounded contract rather than exhaustive duplication. It is
acceptable and expected for behavioural assertions to remain red until Sol's
parallel product implementation lands. Do not weaken the contract to make it
pass against the pre-implementation source.

## Allowed checks

- `python -m py_compile review/test_reception_one_time_reschedule_action.py`
- `git status --short --untracked-files=no`
- `git diff --check -- review/test_reception_one_time_reschedule_action.py`
- `git diff -- review/test_reception_one_time_reschedule_action.py`
- `git add -- review/test_reception_one_time_reschedule_action.py`
- `git diff --cached --check`
- `git commit -m "test(reception-one): specify time reschedule composition"`
- `git rev-parse HEAD`

Do not run pytest in the worker worktree; Sol owns execution after integration.

## Terminal receipt

Return one compact result containing: status, exact changed file, syntax-check
result, expected-red behavioural status, commit hash, boundary attestation and
any genuine blocker. Do not claim acceptance.
