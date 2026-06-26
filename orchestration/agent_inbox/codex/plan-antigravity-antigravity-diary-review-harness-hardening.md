# plan-antigravity-antigravity-diary-review-harness-hardening

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-review-harness-hardening` |
| Status | integrated |
| Created | 2026-06-26 15:20 +1000 |
| Source HEAD | `f5ea0e7` |

## Plan Summary

Extend the deterministic diary review harness to cover the Cancelled flow list section, ensuring the cancelled count badge and cancellation reasons are correctly rendered without relying on visual or manual inspection.

## My Understanding

Currently, `review/checks_diary.json` checks the structure and contents of the main diary grid columns (rooms, breaks like LUNCH/MORNING TEA/BRUNCH, booking slots, and active statuses). However, it does not check the flow panel lists (Expected, Finished, Waiting, Consult, Cancelled).
Cancelled appointments are deliberately excluded from the main grid rendering and are sent to the flow panel's "Cancelled" list.
We want to:
1. Harden the diary DOM by adding stable `data-testid` hooks to make selectors robust against future styling drift.
2. Extend `checks_diary.json` with tests that assert the correct presence, count, and data (patient name, cancellation reason) of cancelled appointments in the flow list.
3. Validate everything using the deterministic `?smoke=true` mock data (specifically `smoke-appt-7` for Alice Wonderland with the cancellation reason "Patient had transport issues").

## Intended Surface / Boundary

- **Affected Surface:** Right-hand flow panel, specifically the "Cancelled" list container (`#flow-list-cancelled`), its child cards, and the section count badge (`#flow-sec-cancelled .flow-sec-count`).
- **Adjacent Surfaces (Must NOT change):** The main diary grid, columns, breaks, booking slots, and other flow list sections (Waiting Room, In Consult, Expected Today, Finished).

## Out Of Scope

- No backend route/model changes or database migrations.
- No live network requests or OAuth authentication.
- No appointment creation/edit/mutation logic changes.
- No Command Centre SPA or AI Scribe behavior changes.
- No styling/CSS changes to the production diary UI.

## Files I Expect To Edit

- `docs/diary/diary.html`: Add `data-testid` to flow section counts.
- `docs/diary/diary.js`: Add `data-testid` to flow cards, names, reasons, cancellation reasons, and status badges.
- `review/checks_diary.json`: Register new data-driven assertions.
- `review/README.md`: Update documentation to describe the new checks.

## Implementation Steps

1. Verify environment setup and package installation (Playwright and pytest).
2. Execute existing smoke tests to ensure a clean baseline:
   `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`
3. Edit `docs/diary/diary.html` to add `data-testid` to count spans (e.g. `data-testid="flow-count-cancelled"`).
4. Edit `docs/diary/diary.js` inside `renderFlowList` to add:
   - `data-testid="flow-card"`
   - `data-status="cancelled"`
   - `data-testid="flow-card-name"`
   - `data-testid="flow-card-cancellation-reason"`
   - `data-testid="flow-card-status"`
5. Update `review/checks_diary.json` with the new checks:
   - Cancelled count badge shows `1`.
   - Cancelled flow card count is `1`.
   - Cancelled patient name matches `Alice Wonderland`.
   - Cancellation reason text matches `Reason: Patient had transport issues`.
   - Status badge shows `Cancelled`.
6. Run `pytest review/test_diary_smoke.py` to confirm all tests pass.
7. Update `review/README.md` to document the new checks.
8. Stage, commit, and push the plan packet to `origin/antigravity/current` as required by the EMR4 protocol, then wait.

## Visual / Behavioural Acceptance Checks

- UI remains visually identical: verify that adding `data-testid` attributes does not affect styles or layouts.
- Harness validation: `pytest` runs green and the JUnit XML contains the new test cases.

## Risks / Ambiguities

- **Mock Data Dependency:** The new tests depend on `smoke-appt-7` in `diary.js`. If the mock appointment is modified or deleted in future sprints, these checks will fail (which is the correct behavior for a deterministic harness).
- **Selector Drift:** By using `data-testid` instead of classes/tag hierarchies, we minimize the risk of selector drift when styles or HTML structures change.

## Codex Plan Review

- Review result: Accepted; scope is deterministic diary smoke-review hardening with stable selectors.
- Required changes before implementation: None.
- Approved to proceed: yes
