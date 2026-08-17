# DeepSeek V4 Flash/high bounded cancellation-action test packet

Date: 2026-08-17

Timestamp: 2026-08-17T13:58:00+10:00 (Australia/Brisbane)

Source HEAD: `a6fefda036dc46b964f1f1951d5e2efb48534219`

Assigned worktree:
`C:\Users\sarashera\EMR4-worktrees\reception-one-cancellation-test-worker-36edc1e5`

Assigned branch:
`codex/reception-one-cancellation-test-worker-36edc1e5`

## Authority

You are the DeepSeek V4 Flash/high test-engineering worker. You own exactly one
new artifact: `review/test_reception_one_cancellation_action.py`. The completed
file must not exceed 900 source lines. You may read only the exact allowlist
below, create/edit only the new test, run only the listed checks, stage that
exact path and make one worker commit. You have no product-source, existing-
test, architecture, orchestration, acceptance, integration, push, protected-
ref, provider, database, runtime, package-install or deployment authority.
Permission availability is not authority.

Read `AGENTS.md` completely before acting. Then read only:

- `docs/raisa-reception-one-selected-appointment-cancellation-composition-plan.md`
- `docs/security/raisa-reception-one-selected-appointment-cancellation-composition-threat-model-delta.md`
- `review/harness.py`
- `review/test_reception_one_status_action.py`
- `review/test_reception_one_selected_action_console.py`
- `docs/diary/diary.js`
- `docs/diary/meta-grid.js`
- `docs/diary/meta-grid.css`
- `docs/diary/diary.html`
- `app/schemas/appointments.py`
- `docs/api-spine/openapi/appointment-commands.yaml`

Use literal exact-path reads only. Do not use Glob, Grep, `rg`, recursive
search, directory listing, protected paths or any file outside this allowlist
and the new test. Do not install dependencies or alter an environment.

## Frozen product selectors and contract

The parallel Sol implementation will supply:

- choice `meta-grid-action-choice-cancel`;
- panel `meta-grid-cancellation-action`;
- reason select `meta-grid-cancellation-reason-code`;
- optional note `meta-grid-cancellation-reason`;
- submit `meta-grid-cancellation-submit`;
- feedback `meta-grid-cancellation-feedback`;
- the existing shared editor and `status-proposal-dialog`;
- bridge operation `EMR4DiaryMetaGridBridge.cancelAppointment`.

The action uses only:

- `POST /api/v1/appointments/proposals/delete/{appointment_id}`; and
- canonical `POST /api/v1/appointments/proposals/delete/confirm`.

Opening/drafting sends no request. Every admissible proposal needs visible
explicit staff confirmation. There is no raw `DELETE`, status-proposal
fallback, ordinary `deleteBooking()` delegation or optimistic mutation.

The strict successful body is
`raisa.delete_confirm_public_envelope.v1` with one exact
`appointment.delete_confirmation_receipt.v1`, matching appointment/reason,
`Cancelled`, null waiting area and only optional `waiting_area_cleared`. It has
no `appointment` read model or unknown field. Every terminal/uncertain outcome
performs a fresh scoped appointment-list read before displaying truth.

## Deliverable

Create one self-contained provider-free route-intercepted Playwright pytest
contract with fixed authored-synthetic data. Reuse only minimum helper patterns
from the two allowlisted sibling tests and do not import them as mutable test
dependencies.

Implement exactly eight focused test functions:

1. `test_cancellation_palette_and_draft_are_route_inert`
   - fifth native danger choice, correct shared-editor ARIA, 44px target;
   - open/collapse/reopen, ten exact reason options and 500-character note;
   - zero proposal/confirm/raw/status routes before submit.
2. `test_safe_cancellation_requires_dialog_and_fresh_removal`
   - required reason, one dedicated proposal, visible contained dialog;
   - no confirm before visible click; one canonical confirm after click;
   - strict public receipt; fresh list read removes the appointment;
   - exact active-action terminal outcome and zero fallback/raw route.
3. `test_staff_escape_cancels_without_confirm_and_retains_truth`
   - Escape or Cancel closes the dialog, sends no confirm, runs fresh list read,
     retains the current appointment/status and returns focus.
4. `test_blocked_proposal_is_close_only_and_never_confirms`
   - typed block, no confirm control/request, no status/raw fallback, fresh
     reconciliation and unchanged current truth.
5. `test_stale_or_revoked_confirm_fails_closed_without_fallback`
   - typed blocked confirm, no optimistic removal, one fresh list read and zero
     status/raw fallback.
6. `test_malformed_or_widened_public_receipt_fails_closed`
   - parametrize at least: unknown top-level `appointment`, unknown receipt
     field, mismatched appointment ID, mismatched reason, non-null waiting area
     and unknown warning code;
   - each performs fresh reconciliation and never renders untrusted fields or
     claims success.
7. `test_busy_confirmation_locks_palette_reselection_and_interruption`
   - all five choices disabled, only cancellation editor mounted, selected card
     cannot change, dialog Tab/Escape contained, interruption creates no second
     command and requires a fresh result before another action.
8. `test_cancellation_accessibility_and_responsive_contract`
   - viewports 1280x720, 768x1024 and 390x844;
   - native keyboard activation, labelled editor, exactly one polite atomic
     live region, target >=44px and no document/host/editor horizontal overflow.

The route fixture must count all non-read requests and explicitly fail any raw
`DELETE`, status proposal or non-canonical delete confirm. Drive authority-
bearing behavior only through visible controls and the visible confirmation
button. Do not call page-internal execution functions.

Keep the evidence labels `route_intercepted_browser` and
`authored_synthetic_client_fixture` in the module and never claim live
backend/database operation. Product implementation is intentionally absent at
this source, so behavioral assertions may remain red until Sol integrates the
parallel source. Do not weaken the contract to fit the baseline.

## Allowed checks

- `python -m py_compile review/test_reception_one_cancellation_action.py`
- a literal line-count command for that exact file
- `git status --short --untracked-files=no`
- `git diff --check -- review/test_reception_one_cancellation_action.py`
- `git diff -- review/test_reception_one_cancellation_action.py`
- `git add -- review/test_reception_one_cancellation_action.py`
- `git diff --cached --check`
- `git commit -m "test(reception-one): specify cancellation action"`
- `git rev-parse HEAD`

Do not run pytest in the worker worktree. Sol owns execution after source
admission.

## Terminal receipt

Return one compact result containing: status, exact changed file, final line
count, syntax-check result, expected-red behavioral status, commit hash,
boundary attestation and any genuine blocker. Do not claim acceptance.
