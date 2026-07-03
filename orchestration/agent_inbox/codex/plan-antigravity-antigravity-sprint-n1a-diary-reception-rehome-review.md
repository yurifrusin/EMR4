# plan-antigravity-antigravity-sprint-n1a-diary-reception-rehome-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint-n1a-diary-reception-rehome-review` |
| Status | pending_plan_review |
| Created | 2026-07-03 19:26 +1000 |
| Source HEAD | `0debced` |

## Plan Summary

This plan focuses on verifying and protecting the contract compatibility of the Diary UI and the review smoke test harness during the rehome of the four core reception-domain modules from `app/services/bernie/` to `app/services/diary/`.

## My Understanding

- **Sprint N1a Objective:** The rehome package migrations (capabilities, temporal, frames, and policy) must be purely structural. They must not introduce any functional, copy, or structural changes to the wire APIs.
- **Contract Compatibility Requirements:**
  - The Diary UI (`docs/diary/diary.js`) and review smoke harness (`review/test_diary_smoke.py`) rely on exact, byte-identical JSON keys for the `reception_policy` API payload.
  - The frame-set serialization must strictly maintain `"schema_version": "bernie.reception_context.v1"` to prevent parsing failures.
  - Compatibility facades must remain in `app/services/bernie/` to forward all legacy imports to the new `app/services/diary/` package.
- **Our Role:** As the Antigravity review/verification agent, we will design and add a strict contract compatibility test suite to ensure that facades and serialization do not regress, and verify that the review harness passes cleanly.

## Intended Surface / Boundary

- **Import Verification:** Facades in [__init__.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/services/bernie/__init__.py) and the submodules must re-export identical types/functions from the new `app/services/diary/` modules.
- **Serialization Verification:** The output of `/proposals/bernie/interpret-booking-instruction` and `/proposals/bernie/supervised-booking` endpoints in [appointments.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/routers/appointments.py) must remain byte-identical.
- **Harness Verification:** The Playwright smoke tests in [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py) targeting `reception_policy` must continue to pass without changes to the tests themselves.

## Out Of Scope

- Actually moving the production modules (this is Claude's N1a implementation lane).
- Any alterations to the Diary UI rendering layout, styling (`docs/diary/diary.css`), or user-facing messaging.
- Persistent session storage migrations or changes to event schema structures.
- Envelope schemas (`DiaryActionIntent`, etc.) which are part of Sprint N1b.

## Files I Expect To Edit

- **New Test File:** `tests/test_bernie_diary_rehome_compatibility.py` to assert import identity and serialization correctness.
- **Inspect/Verify (Zero edits expected):**
  - [appointments.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/routers/appointments.py)
  - [__init__.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/services/bernie/__init__.py)
  - [test_diary_smoke.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/review/test_diary_smoke.py)

## Implementation Steps

1. **Create the Compatibility Suite:** Write `tests/test_bernie_diary_rehome_compatibility.py` to:
   - Import all relocated symbols from both `app.services.bernie` and `app.services.diary` and assert `is` identity (e.g. `assert bernie.BernieReceptionContextFrameSet is diary.BernieReceptionContextFrameSet`).
   - Validate that serializing `BernieReceptionContextFrameSet` outputs `"schema_version": "bernie.reception_context.v1"` exactly.
   - Assert that evaluating a frame set using `evaluate_reception_context` produces a `BernieReceptionPolicyDecision` with identical fields.
2. **Execute Green Verification:**
   - Run the new compatibility test file.
   - Run existing unit test suites `pytest tests/test_bernie_context_frames.py` and `pytest tests/test_bernie_domain_package.py`.
   - Run the frontend review smoke tests: `pytest review/test_diary_smoke.py -q -k reception_policy`.
3. **Verify Claude's Rehome Branch:** Once Claude's rehome implementation is ready, run the new suite on their changes to verify absolute identity of imports and wire schemas.

## Visual / Behavioural Acceptance Checks

- Complete execution of `pytest tests/test_bernie_diary_rehome_compatibility.py` with 100% pass rate.
- All 5 `reception_policy` smoke tests in `review/test_diary_smoke.py` pass without any changes to the test files.
- No Python import errors or collection errors in `pytest tests/`.

## Risks / Ambiguities

- **Facade Import Churn:** If Claude uses wrapper functions rather than direct aliases, `is` identity checks will fail. We mitigate this by defining strict `is` checks in our new test.
- **Pydantic Serialization Differences:** Changes in package names could affect default schema settings in Pydantic. We mitigate this by asserting that model dumps produce byte-identical JSON strings.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
