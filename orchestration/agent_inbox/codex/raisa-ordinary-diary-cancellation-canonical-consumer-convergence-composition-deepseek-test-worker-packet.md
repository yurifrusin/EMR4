# DeepSeek V4 Flash/high bounded ordinary Diary cancellation test packet

Date: 2026-08-17

Timestamp: 2026-08-17T20:52:17.1498076+10:00 (Australia/Brisbane)

Source HEAD: `967ac705bad2013734beaed127cd5e811823d2c7`

Assigned worktree:
`C:\Users\sarashera\EMR4-worktrees\ordinary-diary-cancel-tests-967ac705`

Assigned branch:
`codex/worker-ordinary-diary-cancel-tests-967ac705`

## Authority

You are the DeepSeek V4 Flash/high test-engineering worker. You own exactly one
new artifact:
`review/test_ordinary_diary_cancellation_convergence.py`. The completed file
must not exceed 1,100 source lines. You may read only the exact allowlist below,
create/edit only the new test, run only the listed checks, stage that exact path
and make one worker commit.

You have no product-source, existing-test, plan, architecture, orchestration,
acceptance, integration, push, protected-ref, provider, database, runtime,
package-install or deployment authority. Permission availability is not
authority. The source does not yet contain Sol's parallel product change, so
behavioral assertions may be red until integration; never weaken the frozen
contract to fit the baseline.

Read `AGENTS.md` completely before acting. Then read only:

- `docs/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-plan.md`
- `docs/security/raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition-threat-model-delta.md`
- `review/harness.py`
- `review/test_reception_one_cancellation_action.py`
- `review/test_diary_smoke.py`
- `docs/diary/diary.js`
- `docs/diary/diary.html`
- `docs/api-spine/openapi/appointment-commands.yaml`
- `app/schemas/appointments.py`

Use literal exact-path reads only. Do not use Glob, Grep, `rg`, recursive search,
directory listing, protected paths or any file outside this allowlist and the
new test. Do not install dependencies or alter an environment.

## Frozen product contract

The parallel Sol implementation will preserve the ordinary booking editor
selectors and supply:

- deliberate first click `#btn-booking-delete` -> `Confirm Cancel`;
- administrative reason `[data-testid='booking-status-reason-code']`;
- optional note `[data-testid='booking-cancel-reason']`;
- proposal dialog `[data-testid='status-proposal-dialog']` and its visible
  confirmation control;
- only `POST /api/v1/appointments/proposals/delete/{appointment_id}`;
- only canonical `POST /api/v1/appointments/proposals/delete/confirm`;
- strict `raisa.delete_confirm_public_envelope.v1` validation without an
  appointment object; and
- one fresh authorised appointment-list read after every terminal or uncertain
  result before a terminal claim or another attempt.

Proposal 404, malformed proposal, staff cancellation, typed proposal block,
typed confirm denial, transport/non-OK failure, malformed response, committed
receipt and replay all reconcile. A failed reconciliation leaves the modal
visible, changes the button to an explicit refresh-required state and keeps it
disabled. No local appointment removal is acceptance evidence.

## Deliverable

Create one self-contained provider-free route-intercepted Playwright pytest
module with fixed authored-synthetic data. Reuse only minimum patterns from the
allowlisted siblings; do not import a sibling test module as a mutable fixture
dependency. Keep evidence labels `route_intercepted_browser` and
`authored_synthetic_client_fixture` explicit.

Cover the frozen ten scenario families with a compact fixture and parametrized
tests:

1. committed minimal receipt, exact delete idempotency and fresh read showing
   absent or `Cancelled` before success and modal close;
2. replay-equivalent committed receipt;
3. typed proposal block, no confirm request, fresh unchanged truth;
4. visible staff cancellation, no confirm request, fresh unchanged truth;
5. typed canonical confirm block/denial and fresh unchanged truth;
6. proposal 404 with zero status proposal/confirm and zero raw `DELETE`;
7. confirm transport or non-OK uncertainty resolved only by fresh current truth;
8. malformed/widened public response (at least unknown top-level appointment,
   unknown receipt field, mismatched appointment/reason, non-null waiting area
   and unknown warning code) followed by fresh truth;
9. valid committed receipt contradicted by a fresh still-active appointment,
   with no success claim; and
10. failed reconciliation with explicit disabled refresh-required state and no
    success/non-commit claim.

Also assert:

- the first destructive-intent click is route-inert;
- every accepted proposal requires a visible user confirmation click;
- cancellation reason and optional note remain exact in proposal/receipt;
- no request reaches status proposal, status confirm, hyphenated delete-confirm
  or raw appointment `DELETE`;
- no trusted output contains an appointment read model;
- the fresh appointment read occurs after each terminal/uncertain result; and
- authority-bearing behavior is driven through visible controls only, never by
  calling `deleteBooking()`, `applySignedDeleteProposal()` or another page
  internal directly.

The route fixture must count exact proposal, confirm, appointment-list, status
and raw-delete requests. Use a non-smoke client URL with route-intercepted auth,
template, locations, types, roster, waiting-area and appointment responses so
the cancellation path consumes the ordinary authenticated loader. Never call
this live backend or database evidence.

## Allowed checks

- `python -m py_compile review/test_ordinary_diary_cancellation_convergence.py`
- a literal line-count command for that exact file
- `git status --short --untracked-files=no`
- `git diff --check -- review/test_ordinary_diary_cancellation_convergence.py`
- `git diff -- review/test_ordinary_diary_cancellation_convergence.py`
- `git add -- review/test_ordinary_diary_cancellation_convergence.py`
- `git diff --cached --check`
- `git commit -m "test(diary): specify canonical cancellation convergence"`
- `git rev-parse HEAD`

Do not run pytest in the worker worktree. Sol owns execution after product-source
integration.

## Terminal receipt

Return one compact result containing: status, exact changed file, final line
count, syntax-check result, expected-red behavioral status, commit hash,
boundary attestation and any genuine blocker. Do not claim acceptance.
