# Independent veto packet: Reception One selected-appointment time reschedule

Date: 2026-08-14

Timestamp: 2026-08-14T09:12:10+10:00 (Australia/Brisbane)

Decision required: exactly one terminal `pass` or `revision_required`

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r133`
- Branch: `codex/review-reception-one-time-reschedule-d803d1d8`
- Frozen-plan/dispatch parent: `1b5d790338ca8fbfd1b42806aaa9a3d9be01bb00`
- Candidate: `d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First perform the complete five-source rehydration required by `AGENTS.md` and
name `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. The live active-operation latch is in progress and
the packet grants review only.

## Purpose

Independently decide whether the candidate safely composes one same-date,
same-practitioner, duration-fixed selected appointment start-time action into
Reception One through the ordinary Diary's existing update proposal/confirm
interaction, without creating a second command path or allowing presentation
state to outrun fresh authoritative truth.

## Exact allowed review surface

Read only these files and the exact baseline-to-candidate diff:

- `AGENTS.md`
- `docs/raisa-reception-one-selected-appointment-time-reschedule-composition-plan.md`
- `docs/security/raisa-reception-one-selected-appointment-time-reschedule-composition-threat-model-delta.md`
- `docs/raisa-reception-one-time-reschedule-deepseek-test-integration-recovery.md`
- `docs/raisa-projection-neutral-kernel-truth-architecture.md`
- `docs/diary/diary.js`
- `docs/diary/meta-grid.js`
- `docs/diary/meta-grid.css`
- `review/test_reception_one_time_reschedule_action.py`
- `review/test_reception_one_status_action.py`
- `review/test_two_projection_truth_parity.py`
- `tests/test_reception_one_time_reschedule_composition.py`
- `tests/test_api_spine_update_confirm_idempotency_preflight.py`
- `tests/test_api_spine_update_confirm_idempotency_route_contract.py`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `app/routers/appointments.py`
- `orchestration/continuity/ariadne-active-operation-latch/current.json`
- exact Ariadne receipts and AER revisions that appear in the
  `1b5d790338ca8fbfd1b42806aaa9a3d9be01bb00..d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a`
  diff.

Do not open, enumerate or search any protected holdout, historical Diary,
branding, patient, product-derived or unrelated path. Do not run a repository-
wide content search. Review sources one exact allowlisted path at a time.

## Required challenges

1. Verify exact HEAD, branch, clean checkout and baseline-to-candidate file
   list before and after review.
2. Confirm the Reception One bridge validates the exact selected appointment
   and aligned `HH:MM`, computes only `deltaStart`, passes literal zero for
   `deltaDuration`, resolves the same practitioner column and delegates once to
   existing `handleMoveResize`.
3. Confirm `meta-grid.js` contains no fetch, API route, proposal, confirm,
   signature, idempotency or raw PUT implementation and therefore creates no
   second command path.
4. Confirm only the existing update proposal endpoint and proposal-supplied
   allowlisted confirmation endpoint can commit; the client preserves the
   opaque server payload and alters only existing confirmation acknowledgement
   fields.
5. Confirm date, practitioner, duration, patient linkage, type, location,
   status, waiting area, reason, notes and booking channel remain outside the
   Reception One control surface and are preserved by the ordinary path.
6. Challenge all six paired outcomes: safe commit, warning cancel, blocked,
   stale confirm, proposal/transport failure and warning commit. Verify exact
   proposal/confirm counts, zero raw compatibility writes, zero unexpected
   mutations and equal fresh normalized coordinates across conventional grid
   and Reception One.
7. Confirm no optimistic requested coordinate survives a failed, blocked,
   cancelled, stale or interrupted action; after commit, the visible selected
   card cannot announce completion before the bridge's exact fresh appointment
   coordinate is applied.
8. Confirm explicit staff review, blocked no-confirm behavior, Escape ownership,
   dialog focus containment, deterministic return focus and single-action
   interruption/reconciliation behavior.
9. Confirm time input is a standard 900-second/15-minute control, no-op is
   disabled, unaligned values make zero requests and desktop/tablet/phone
   layouts do not overflow.
10. Confirm existing status composition and truth-parity behavior remains
    intact and the historical update-preflight test repair describes current
    delete-confirm idempotency wiring without changing backend or API meaning.
11. Confirm no backend, OpenAPI, GraphQL, database, event, watcher, provider,
    product-data, deployment, Pages or protected-ref authority widened.
12. Run every exact command below and leave HEAD/worktree unchanged and clean.

## Exact commands

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-r133 review\test_reception_one_time_reschedule_action.py tests\test_reception_one_time_reschedule_composition.py review\test_reception_one_status_action.py review\test_two_projection_truth_parity.py tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_api_spine_update_confirm_idempotency_route_contract.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check review\test_reception_one_time_reschedule_action.py tests\test_reception_one_time_reschedule_composition.py tests\test_api_spine_update_confirm_idempotency_preflight.py tests\test_api_spine_update_confirm_idempotency_route_contract.py
node --check docs\diary\diary.js
node --check docs\diary\meta-grid.js
git diff --check 1b5d790338ca8fbfd1b42806aaa9a3d9be01bb00..d803d1d85267af31ee5b6a08b0ecfefb6ad3e04a
git status --short --branch
git rev-parse HEAD
```

Expected focused result: 35 passed (9 + 5 + 4 + 5 + 6 + 6). Ruff,
JavaScript syntax and Git whitespace must pass.

## Forbidden actions

Do not edit, format, commit, push, install dependencies, write inside the
candidate worktree, start a backend/database/browser beyond the exact tests,
contact a product/provider surface, access patient/clinical/product or
protected data, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `revision_required` for any P0-P2 finding, second command path,
confirmation bypass, immutable-field widening, stale/optimistic truth,
incomplete outcome matrix, failed exact command, widened containment or dirty
postcondition. Otherwise return exactly one `pass`, stating findings, exact
test counts, candidate HEAD and post-review cleanliness.
