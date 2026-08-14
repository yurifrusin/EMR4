# DeepSeek V4 Flash/high bounded practitioner-reassignment test packet

Date: 2026-08-14

Timestamp: 2026-08-14T12:52:06+10:00 (Australia/Brisbane)

Source HEAD: `5dfd6d34fa908fe9b50862ff84979698e27a661f`

Assigned worktree:
`C:\Users\sarashera\EMR4-worktrees\practitioner-test-worker-5dfd`

Assigned branch: `codex/reception-one-practitioner-test-worker-5dfd`

## Authority

You are the DeepSeek V4 Flash/high test-engineering worker. You own exactly one
new artifact:
`review/test_reception_one_practitioner_reassignment_action.py`. The completed
file must not exceed 650 source lines. You may read the exact allowlist below,
create and edit only that new file, run only the listed checks, stage that exact
file and make one worker commit. You have no product implementation,
existing-test edit, orchestration, acceptance, integration, push,
protected-ref, provider, database, runtime or deployment authority. Permission
availability is not authority.

Read `AGENTS.md` completely before acting. Then read only:

- `docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-plan.md`
- `docs/security/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-threat-model-delta.md`
- `review/test_reception_one_time_reschedule_action.py`
- `review/test_reception_one_duration_action.py`
- `review/test_reception_one_status_action.py`
- `review/test_two_projection_truth_parity.py`
- `docs/diary/diary.js`
- `docs/diary/meta-grid.js`
- `docs/diary/meta-grid.css`
- `docs/diary/diary.html`

Use literal exact-path reads only. Do not use Glob, Grep, `rg`, recursive
search, directory listing, protected paths or any file outside that allowlist
and your new test artifact.

## Deliverable

Create one compact self-contained authored-synthetic provider-free pytest
browser contract for same-date, same-start, same-duration practitioner-only
reassignment. Reuse only the minimum local helpers; do not import mutable test
helpers or copy unrelated matrices. Stop once the closed matrix is complete.

The contract must require:

1. A selected-card `New practitioner` selector and
   `Review practitioner change` action.
2. Options drawn only from current authenticated practice-scoped directory
   rows with `active === true`, excluding the current practitioner. Same,
   blank, malformed, inactive, unlisted and duplicate targets make zero update
   proposal or confirm request.
3. Exact fresh appointment and active-directory rechecks before delegation;
   directory failure or target disappearance fails closed.
4. A bridge that supplies literal zero start and duration deltas, resolves the
   exact target practitioner and delegates once to `handleMoveResize`; no
   bridge-local update route, proposal, confirm, signing, idempotency or raw
   `PUT` implementation.
5. Existing update proposal and proposal-supplied confirm routes only.
6. Six paired `conventional_grid` / `reception_one` outcomes: safe commit,
   warning cancel, blocked, stale confirmation, transport/directory failure
   and explicit warning commit.
7. Identical fresh normalized appointment id, date, start, end, practitioner,
   duration, patient linkage and status for every pair; exact route counts;
   zero raw `PUT` and zero unexpected mutation routes.
8. Separate interruption/fresh-read, four-way mutual exclusion, dialog
   focus/Escape, time/duration/status regressions, 200-row boundary and
   desktop/tablet/phone no-overflow cases.
9. Evidence labels `route_intercepted_browser` and
   `authored_synthetic_client_fixture`; never claim live product operation.

The product code is intentionally absent at this source. Behavioural
assertions may remain red until Sol's parallel implementation lands. Do not
weaken the contract to pass the pre-implementation source. Prefer parameterized
cases and small helpers so the file remains at or below 650 lines.

## Allowed checks

- `python -m py_compile review/test_reception_one_practitioner_reassignment_action.py`
- a literal line-count command for that exact file
- `git status --short --untracked-files=no`
- `git diff --check -- review/test_reception_one_practitioner_reassignment_action.py`
- `git diff -- review/test_reception_one_practitioner_reassignment_action.py`
- `git add -- review/test_reception_one_practitioner_reassignment_action.py`
- `git diff --cached --check`
- `git commit -m "test(reception-one): specify practitioner reassignment"`
- `git rev-parse HEAD`

Do not run pytest in the worker worktree; Sol owns execution after admission.

## Terminal receipt

Return one compact result containing: status, exact changed file, final line
count, syntax-check result, expected-red behavioural status, commit hash,
boundary attestation and any genuine blocker. Do not claim acceptance.
