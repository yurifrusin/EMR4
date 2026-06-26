# claude-bernie-dev-review-fixture-route

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | a390acc |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-dev-review-fixture-route --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-dev-review-fixture-route --commit-message "Dispatch Sprint 55 Bernie dev review fixture route" --message "Sprint 55 dispatched: Bernie dev review fixture route"` |

## Mission

Plan first, then after approval add a narrow backend-only non-PHI dev fixture source for Bernie supervised review payloads so the dev launcher/review panel can exercise realistic deterministic payloads without hand-authored Playwright route payloads.

## Scope

### In Scope

Plan packet first; after approval a dev/test-only route or fixture helper under the appointments proposal surface, response schema reuse where possible, non-PHI deterministic payloads for blocked/candidate/confirmation-ready states, explicit gating so production/default behaviour is unaffected, auth/practice scoping if exposed as an API route, no appointment/audit writes, no LLM/provider calls, and focused pytest coverage.

### Out of Scope

Diary UI changes, taskpane, Command Centre, live autonomous booking, production default exposure, real patient data, Gemini/LLM parsing, migrations unless strictly unavoidable, appointment write semantics, SMS, billing, resource admin, broad appointment router redesign, and unrelated test hygiene.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Before editing project code, write an implementation plan and stop. The plan
   must be shown in the agent GUI and captured for Codex with the plan command
   above. Do not code until the user/Codex says `complete sprint task`.
5. After plan approval, work only inside the stated scope unless the user or Codex
   expands it.
6. Do not merge to `master`.
7. Do not move `handoff/current`.
8. Run the verification listed below.
9. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
10. Finish with the submit command above.

## Implementation Plan Requirements

Before coding, the implementation plan must include:

- My Understanding
- Intended Surface / Boundary
- Out of Scope
- Files I Expect To Edit
- Implementation Steps
- Visual / Behavioural Acceptance Checks
- Risks / Ambiguities

Pay special attention to visually loaded words such as cards, slots, stacking,
panels, waiting room, diary grid, booking slot, and status. State exactly which
surface is affected and which nearby surfaces must not change.

## Hard Stop Rules

- Do not push to `master` or `handoff/current`.
- Do not manually work around a failed protocol command (`handin`, `sync`, `submit`,
  `realign`, or related orchestration commands).
- Report every protocol-followed command back to Codex/orchestrator, whether it
  succeeds or fails. For success, include the command, working directory, branch,
  and short success result.
- If any protocol command refuses to run or fails, stop and report the exact command,
  working directory, branch, `git status --short --branch`, and error output to the
  orchestrator. On push failure, `submit` will also try to publish a
  `submit-alert/...` branch for Codex to poll.
- If these instructions conflict with remembered prior protocol, trust the current
  `handin` alerts and this task packet.

## Verification

Plan packet first; after approval py_compile touched backend modules/tests, focused pytest for the dev fixture route/helper, adjacent Bernie supervised-booking/review payload tests where relevant, no-write/no-audit proof, no-LLM/provider proof, auth/practice/default-gating checks if route is exposed, and git diff hygiene.

## Merge Criteria

Ariadne can verify the fixture source is deterministic and non-PHI, default production paths remain unaffected, it cannot write appointments or audit rows, it does not call any LLM/provider surface, it is suitably gated for dev/test use, tests cover blocked/candidate/confirmation-ready payloads, and the branch submits through protocol with clean diff hygiene.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - NEW `app/routers/bernie_dev.py` — dev-gated router at `/api/v1/appointments/dev`;
    one endpoint `GET /api/v1/appointments/dev/bernie-review-fixtures` returning
    deterministic non-PHI `BernieSupervisedBookingOut` fixtures keyed by state (blocked /
    candidate_selection_required / confirmation_ready); optional `?state=` query filter
    returns a single-key dict for that state; gated via a `_require_dev_environment`
    router-level dependency (404 in non-dev); auth required (`get_current_user`);
    no DB writes, no audit rows, no LLM imports; `staff_review` built via the live
    `_bernie_staff_review_payload` helper imported from `app.routers.appointments` so
    the fixture contract tracks the live wrapper output; `confirm_endpoint` is
    `/api/v1/appointments/proposals/create/confirm-bernie` and `confirm_payload.confirmed`
    is `False` (not yet explicitly staff-approved); fixtures built once at module import
    time using sentinel UUIDs in the `f170000000xx` range.
  - EDIT `app/main.py` — import and include `bernie_dev.router` (already present from draft).
  - NEW `tests/test_bernie_dev_fixtures.py` — 16 tests covering: auth gate (401),
    dev-only gate (404 in production via monkeypatch), 200 in dev, all-three-states
    default response, per-state structure assertions (blocked/candidate/confirmation),
    exact `confirm_endpoint` value assertion, `confirm_payload.confirmed is False` assertion,
    parametrized state filter (all 3 valid states + 422 for invalid), no-write proof
    (Appointment + AppointmentAuditLog row counts unchanged), no-LLM-import proof
    (source inspection), non-PHI proof (pattern scan), and determinism check.

- Verification run:
  - `py_compile app/routers/bernie_dev.py app/main.py tests/test_bernie_dev_fixtures.py` → OK
  - `pytest tests/test_bernie_dev_fixtures.py -v` → 16 passed
  - `pytest tests/ -k bernie -v` → 75 passed (all Bernie wrapper/review/confirm/normalizer/harness tests)
  - `git diff --check` → clean (CRLF line-ending note on packet file only — not a code issue)

- Remaining risks:
  - The `_ALL_FIXTURES` dict is module-level (built at import). If any schema validator
    changes the `SlotSearchProposalIn` date-range or field rules in a way that rejects
    the fixture values, `bernie_dev.py` will fail to import. Unlikely given the fixture
    uses fixed future dates and standard field values.
  - Fixture UUIDs (`f17000000001`–`f17000000004`) are sentinel values that do not exist
    in the DB; the route never queries them, so no DB lookup failures possible. If a
    future route change adds DB lookups to this endpoint, the sentinel IDs will return
    404-equivalent DB misses.
  - `monkeypatch.setattr(bernie_dev_module.settings, "environment", "production")` works
    because `pydantic_settings.BaseSettings` is not frozen by default. If `Settings` is
    ever marked `frozen=True`, the env-gate test will need a different approach.
  - `_bernie_staff_review_payload` is imported directly from the private module namespace
    of `app.routers.appointments`. If it is ever renamed, `bernie_dev.py` will break at
    import time with a clear `ImportError`.
