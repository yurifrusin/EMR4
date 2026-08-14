# Independent veto packet: Reception One practitioner reassignment

Date: 2026-08-14

Timestamp: 2026-08-14T13:33:32+10:00 (Australia/Brisbane)

Decision required: exactly one terminal `pass` or `revision_required`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\practitioner-review-f085`
- Branch: `codex/review-reception-one-practitioner-f085`
- Frozen plan/source parent: `5dfd6d34fa908fe9b50862ff84979698e27a661f`
- Candidate: `f085fc98ead21a3e7929ee9adbda81abfc7542c9`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Review only. The committed latch names the candidate's
immediate pre-commit source because a commit cannot contain its own hash; this
packet and the orchestrator receipt bind the exact candidate above.

## Purpose

Independently decide whether the candidate safely composes one selected
current appointment's practitioner reassignment into Reception One through the
ordinary Diary's existing update proposal/confirm path, while date, start,
duration and all unrelated meanings remain fixed and no projection state can
outrun current backend truth.

## Exact allowed review surface

Read only these files and the exact parent-to-candidate diff:

- `AGENTS.md`
- `docs/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-plan.md`
- `docs/security/raisa-reception-one-selected-appointment-practitioner-reassignment-composition-threat-model-delta.md`
- `docs/raisa-projection-neutral-kernel-truth-architecture.md`
- `docs/diary/diary.html`
- `docs/diary/diary.js`
- `docs/diary/meta-grid.js`
- `docs/diary/meta-grid.css`
- `review/test_reception_one_practitioner_reassignment_action.py`
- `review/test_reception_one_duration_action.py`
- `review/test_reception_one_time_reschedule_action.py`
- `review/test_reception_one_status_action.py`
- `review/test_two_projection_truth_parity.py`
- `tests/test_reception_one_practitioner_reassignment_composition.py`
- `tests/test_raisa_reception_one_selected_appointment_practitioner_reassignment_composition_plan.py`
- `tests/test_reception_one_duration_composition.py`
- `tests/test_reception_one_time_reschedule_composition.py`
- `tests/test_appointment_update_proposal.py`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `app/routers/appointments.py`
- `orchestration/continuity/ariadne-active-operation-latch/current.json`
- exact practitioner-reassignment receipts appearing in the
  `5dfd6d34fa908fe9b50862ff84979698e27a661f..f085fc98ead21a3e7929ee9adbda81abfc7542c9`
  diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not run a repository-
wide content search. Review sources one exact allowlisted path at a time.

## Required challenges

1. Verify exact HEAD, branch, clean checkout and parent-to-candidate file list
   before and after review.
2. Confirm Reception One offers only distinct, current directory rows marked
   active, excludes current/inactive/blank/oversized/unlisted/duplicate target
   identities and re-reads the exact appointment plus current directory before
   starting any proposal.
3. Confirm the bridge binds one frozen freshly admitted practitioner identity,
   rejects a caller-column mismatch, fixes both start and duration deltas at
   literal zero and delegates once to existing `handleMoveResize`.
4. Confirm `meta-grid.js` contains no fetch, API route, proposal, confirm,
   signature, idempotency or raw PUT implementation and creates no second
   command path.
5. Confirm only the existing update proposal endpoint and proposal-supplied
   allowlisted confirm endpoint can write. Opaque confirmation evidence and
   distinct idempotency semantics remain owned by the ordinary Diary path.
6. Confirm the changed target's same-practice active status is checked by the
   existing backend proposal and checked again because confirmation re-runs
   that proposal. An unchanged inactive practitioner must remain valid for
   historical time/duration edits.
7. Confirm date, start, duration, patient linkage, type, location, status,
   waiting area, reason, notes and booking channel remain outside the new
   control and are preserved from exact current appointment truth.
8. Challenge all six paired outcomes: safe commit, warning cancel, blocked,
   stale confirm, proposal/transport failure and warning commit. Require exact
   proposal/confirm counts, zero raw writes, zero unexpected mutations and
   equal fresh normalized truth across conventional grid and Reception One.
9. Confirm failed directory reads, disappearing targets, blocked, cancelled,
   stale, failed and interrupted actions leave no optimistic practitioner and
   require exact fresh reconciliation before another selected action.
10. Confirm explicit staff review, blocked no-confirm behavior, Escape/focus
    containment, selector focus return and mutual exclusion across status,
    time, duration and practitioner actions.
11. Confirm the first-200 directory boundary and desktop/tablet/phone
    horizontal containment without claiming pagination or live product proof.
12. Confirm no new route/schema, OpenAPI, GraphQL, database, event, watcher,
    provider, product-data, deployment, Pages or protected-ref authority.
13. Run every exact command below and leave HEAD/worktree unchanged and clean.

## Exact commands

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-practitioner-f085 review\test_reception_one_practitioner_reassignment_action.py tests\test_reception_one_practitioner_reassignment_composition.py tests\test_raisa_reception_one_selected_appointment_practitioner_reassignment_composition_plan.py tests\test_appointment_update_proposal.py tests\test_reception_one_duration_composition.py tests\test_reception_one_time_reschedule_composition.py review\test_two_projection_truth_parity.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app\routers\appointments.py review\test_reception_one_practitioner_reassignment_action.py tests\test_reception_one_practitioner_reassignment_composition.py tests\test_raisa_reception_one_selected_appointment_practitioner_reassignment_composition_plan.py tests\test_appointment_update_proposal.py tests\test_reception_one_duration_composition.py tests\test_reception_one_time_reschedule_composition.py
node --check docs\diary\diary.js
node --check docs\diary\meta-grid.js
git diff --check 5dfd6d34fa908fe9b50862ff84979698e27a661f..f085fc98ead21a3e7929ee9adbda81abfc7542c9
git status --short --branch
git rev-parse HEAD
```

Expected pytest result: exactly 80 passed across the seven listed modules.
Ruff, both JavaScript syntax checks and Git whitespace must pass.

## Forbidden actions

Do not edit, format, commit, push, install dependencies, write inside the
candidate worktree, contact a product/provider surface, access patient,
clinical, product-derived or protected data, inspect `docs/branding/`, move
refs or accept your own output.

## Decision rule

Return `revision_required` for any P0-P2 finding, second command path,
confirmation bypass, inactive-target race, immutable-field widening, stale or
optimistic truth, incomplete paired matrix, failed exact command, widened
containment or dirty postcondition. Otherwise return exactly one `pass`, with
findings, exact test counts, candidate HEAD and post-review cleanliness.
