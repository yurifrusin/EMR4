# DeepSeek V4 Flash/high bounded duration test-engineering packet

Date: 2026-08-14

Timestamp: 2026-08-14T10:54:44+10:00 (Australia/Brisbane)

Source HEAD: `65f0e6ff117bb5a764beb5ac8fc7a8b5cea13cab`

Assigned worktree: `C:\Users\sarashera\EMR4-worktrees\duration-test-worker-65f0`

Assigned branch: `codex/reception-one-duration-test-worker-65f0`

## Authority

You are the DeepSeek V4 Flash/high test-engineering worker. You own exactly one
new artifact: `review/test_reception_one_duration_action.py`. You may read the
exact allowlist below, create and edit only that new file, run only the listed
checks, stage that exact file, and make one worker commit. You have no product
implementation, existing-test edit, orchestration, acceptance, integration,
push, protected-ref, provider, database, runtime or deployment authority.
Permission availability is not authority.

Read `AGENTS.md` completely before acting. Then read:

- `docs/raisa-reception-one-selected-appointment-duration-composition-plan.md`
- `docs/security/raisa-reception-one-selected-appointment-duration-composition-threat-model-delta.md`
- `review/test_reception_one_time_reschedule_action.py`
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
contract for a same-date, same-start, same-practitioner selected-appointment
duration action. Reuse only the minimum helpers needed in the new file; do not
edit or import mutable helpers from an existing test module if that would make
the artifact order-dependent.

The contract must require:

1. A selected-card duration selector and `Review duration change` action.
2. Targets derived by whole 15-minute deltas from the exact current duration,
   including a valid non-multiple current duration such as 20 -> 35; integer
   15..480 and same-day-end admission; invalid, unchanged and out-of-day input
   makes zero request.
3. A bridge that computes only duration delta, supplies literal zero start
   delta, keeps the same practitioner and delegates once to existing
   `handleMoveResize`; it owns no fetch, route, proposal, confirm, signing,
   idempotency or raw PUT implementation.
4. Existing update proposal and proposal-supplied confirm routes only.
5. Six paired `conventional_grid` / `reception_one` outcomes: safe commit,
   warning cancel, blocked, stale confirmation, transport failure and explicit
   warning commit.
6. Identical fresh normalized appointment id, date, start, end, practitioner,
   duration, patient linkage and status for every pair; exact route counts;
   zero raw PUT and zero unexpected mutation routes.
7. Separate invalid/no-op/out-of-day zero-route, interruption/fresh-read,
   mutual exclusion, dialog focus/Escape, time-action regression and
   desktop/tablet/phone no-overflow cases.
8. Evidence labels `route_intercepted_browser` and
   `authored_synthetic_client_fixture`; never claim live product operation.

Aim for a bounded readable contract. It is acceptable and expected for
behavioural assertions to remain red until Sol's parallel product implementation
lands. Do not weaken the contract to make it pass against pre-implementation
source.

## Allowed checks

- `python -m py_compile review/test_reception_one_duration_action.py`
- `git status --short --untracked-files=no`
- `git diff --check -- review/test_reception_one_duration_action.py`
- `git diff -- review/test_reception_one_duration_action.py`
- `git add -- review/test_reception_one_duration_action.py`
- `git diff --cached --check`
- `git commit -m "test(reception-one): specify duration composition"`
- `git rev-parse HEAD`

Do not run pytest in the worker worktree; Sol owns execution after integration.

## Terminal receipt

Return one compact result containing: status, exact changed file, syntax-check
result, expected-red behavioural status, commit hash, boundary attestation and
any genuine blocker. Do not claim acceptance.
