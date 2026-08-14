# Independent veto packet: Reception One selected-appointment duration

Date: 2026-08-14

Timestamp: 2026-08-14T11:49:23+10:00 (Australia/Brisbane)

Decision required: exactly one terminal `pass` or `revision_required`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r191`
- Branch: `codex/review-reception-one-duration-f397a370`
- Frozen plan/source parent: `65f0e6ff117bb5a764beb5ac8fc7a8b5cea13cab`
- Candidate: `f397a3706f3b870b8436eb3993bd90c6c0c742a8`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. The active operation remains in progress and this
packet grants review only. The candidate's committed latch names its immediate
pre-commit source because a commit cannot contain its own hash; the packet and
orchestrator receipt bind the exact candidate above.

## Purpose

Independently decide whether the candidate safely composes one same-date,
same-start, same-practitioner selected-appointment duration change into
Reception One through the ordinary Diary's existing update proposal/confirm
interaction, without creating a second command path or allowing presentation
state to outrun fresh authoritative truth.

## Exact allowed review surface

Read only these files and the exact parent-to-candidate diff:

- `AGENTS.md`
- `docs/raisa-reception-one-selected-appointment-duration-composition-plan.md`
- `docs/security/raisa-reception-one-selected-appointment-duration-composition-threat-model-delta.md`
- `docs/raisa-reception-one-duration-deepseek-test-integration-recovery.md`
- `docs/raisa-projection-neutral-kernel-truth-architecture.md`
- `docs/diary/diary.html`
- `docs/diary/diary.js`
- `docs/diary/meta-grid.js`
- `docs/diary/meta-grid.css`
- `review/test_reception_one_duration_action.py`
- `review/test_reception_one_time_reschedule_action.py`
- `review/test_reception_one_status_action.py`
- `review/test_two_projection_truth_parity.py`
- `tests/test_reception_one_duration_composition.py`
- `tests/test_reception_one_time_reschedule_composition.py`
- `tests/test_api_spine_update_confirm_idempotency_preflight.py`
- `tests/test_api_spine_update_confirm_idempotency_route_contract.py`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `app/routers/appointments.py`
- `orchestration/continuity/ariadne-active-operation-latch/current.json`
- exact duration receipts appearing in the
  `65f0e6ff117bb5a764beb5ac8fc7a8b5cea13cab..f397a3706f3b870b8436eb3993bd90c6c0c742a8`
  diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not run a repository-
wide content search. Review sources one exact allowlisted path at a time.

## Required challenges

1. Verify exact HEAD, branch, clean checkout and parent-to-candidate file list
   before and after review.
2. Confirm the bridge obtains an exact fresh current appointment, validates an
   integer target from 15 through 480 minutes, admits only whole 15-minute
   deltas, keeps the derived end on the same date, fixes start delta at literal
   zero, resolves the same practitioner and delegates once to
   `handleMoveResize`.
3. Confirm a valid current duration that is not itself a multiple of 15 (for
   example 20 minutes) retains reachable options such as 35 minutes.
4. Confirm `meta-grid.js` contains no fetch, API route, proposal, confirm,
   signature, idempotency or raw PUT implementation and therefore creates no
   second command path.
5. Confirm only the existing update proposal endpoint and the proposal-
   supplied allowlisted confirmation endpoint can commit. The client must
   preserve the opaque confirmation payload and existing acknowledgement/
   idempotency semantics.
6. Confirm date, start, practitioner, patient linkage, type, location, status,
   waiting area, reason, notes and booking channel remain outside the new
   control surface and are preserved by the ordinary path.
7. Challenge all six paired outcomes: safe commit, warning cancel, blocked,
   stale confirm, proposal/transport failure and warning commit. Verify exact
   proposal/confirm counts, zero raw writes, zero unexpected mutations and
   equal fresh normalized truth across conventional grid and Reception One.
8. Confirm no optimistic target duration/end survives failed, blocked,
   cancelled, stale or interrupted action. A terminal callback must not announce
   completion before the bridge completes its exact fresh read and projection
   update; reconciliation failure must remain visibly fail closed.
9. Confirm explicit staff review, blocked no-confirm behavior, Escape ownership,
   dialog focus containment, return focus to the duration selector and mutual
   exclusion with status/time actions.
10. Confirm the bounded selector rejects invalid/no-op/out-of-day targets with
    zero request and desktop/tablet/phone layouts remain horizontally contained.
11. Confirm time/status/truth-parity behavior remains intact and no backend,
    OpenAPI, GraphQL, database, event, watcher, provider, product-data,
    deployment, Pages or protected-ref authority widened.
12. Run every exact command below and leave HEAD/worktree unchanged and clean.

## Exact commands

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r191 review\test_reception_one_duration_action.py tests\test_reception_one_duration_composition.py review\test_reception_one_time_reschedule_action.py tests\test_reception_one_time_reschedule_composition.py review\test_reception_one_status_action.py review\test_two_projection_truth_parity.py tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_api_spine_update_confirm_idempotency_route_contract.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check review\test_reception_one_duration_action.py tests\test_reception_one_duration_composition.py tests\test_reception_one_time_reschedule_composition.py tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_api_spine_update_confirm_idempotency_route_contract.py
node --check docs\diary\diary.js
node --check docs\diary\meta-grid.js
git diff --check 65f0e6ff117bb5a764beb5ac8fc7a8b5cea13cab..f397a3706f3b870b8436eb3993bd90c6c0c742a8
git status --short --branch
git rev-parse HEAD
```

Expected pytest result: exactly 68 passed across the eight listed modules.
Ruff, JavaScript syntax and Git whitespace must pass.

## Forbidden actions

Do not edit, format, commit, push, install dependencies, write inside the
candidate worktree, contact a product/provider surface, access patient,
clinical, product-derived or protected data, inspect `docs/branding/`, move
refs or accept your own output.

## Decision rule

Return `revision_required` for any P0-P2 finding, second command path,
confirmation bypass, immutable-field widening, stale/optimistic truth,
incomplete outcome matrix, failed exact command, widened containment or dirty
postcondition. Otherwise return exactly one `pass`, stating findings, exact
test counts, candidate HEAD and post-review cleanliness.
