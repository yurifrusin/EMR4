# plan-antigravity-antigravity-sprint152-create-proposal-client-compatibility

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-sprint152-create-proposal-client-compatibility` |
| Status | pending_plan_review |
| Created | 2026-07-07 13:41 +1000 |
| Source HEAD | `8d711a8d` |

## Plan Summary

Assess client compatibility risk for enforcing Idempotency-Key minLength: 8 at runtime on create-proposal, and submit the review plan.

## My Understanding

Currently, the backend enforces only a non-blank check at runtime for the create-proposal endpoint, while the OpenAPI spec documents a minLength: 8 requirement. We must analyze client code and backend tests to determine if immediate runtime enforcement of minLength: 8 is safe or if it risks breaking any active client workflows.

## Intended Surface / Boundary

Plan packet only; no production code, tests, or UI files are to be edited during this plan gate.

## Out Of Scope

Modifying FastAPI route logic in app/, OpenAPI spec files, test files, diary UI, taskpane, or accessing raw/ignored trove data.

## Files I Expect To Edit

orchestration/agent_inbox/codex/plan-antigravity-antigravity-sprint152-create-proposal-client-compatibility.md

## Implementation Steps

1. Run plan command to generate the plan packet. 2. Submit the plan using the submit command. 3. Wait for complete sprint task approval.

## Visual / Behavioural Acceptance Checks

Codex plan packet is written and committed/pushed successfully. Review indicates low client compatibility risk (since diary.js does not send keys yet, and its generator generates 30+ char event IDs; taskpane does not use proposals; tests are isolated). No production code or tests are changed.

## Risks / Ambiguities

No active risk. Static analysis shows that no production client currently sends short non-blank idempotency keys. The only test using a short key is the explicit compatibility guard, which will be updated.

## Client Compatibility Review & Findings

### 1. Client Analysis (Code & Behaviors)
* **Diary Frontend ([diary.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/docs/diary/diary.js))**:
  - In `saveBooking()`, the client sends POST requests to `/appointments/proposals/create` without an `Idempotency-Key` header.
  - In non-smoke mode, this already results in a `400 Bad Request` (`idempotency_key_required`) because the backend requires a non-blank key.
  - When the frontend is updated to send the header, its standard key generator `generateEventId()` produces a UUID or an `evt-` prefixed string that is $\ge 30$ characters long.
  - Therefore, any future compliant client will naturally satisfy the `minLength: 8` requirement. There is **zero compatibility risk** from the main web client.
* **Taskpane Frontend ([taskpane.js](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/EMR4%20Sidebar/src/taskpane/taskpane.js))**:
  - Static analysis shows the taskpane does not call proposal creation endpoints. There is **zero compatibility risk**.

### 2. Test Coverage & Alignments
* **FastAPI Backend Route Alignment**:
  - FastAPI currently accepts short keys (e.g. `"a"`), which is guarded by `test_short_nonblank_key_is_accepted_until_minlength_client_readiness_decision` in [test_api_spine_create_proposal_idempotency_route_contract.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_create_proposal_idempotency_route_contract.py#L289-L299).
  - Enforcing `minLength: 8` at runtime will cause this test to fail. It must be updated to expect a `400 Bad Request` with `idempotency_key_invalid_length`.
  - All other tests default to keys with length $\ge 8$ (e.g. `"proposal-key"`) and will continue to pass.

### 3. Recommendation & Bounded Acceptance Action Plan
We recommend **enforcing the minLength: 8 runtime validation immediately** to align the FastAPI backend with the OpenAPI specification and resolve header schema drift.

* **Task 1: Backend Normalizer Hardening**:
  Update `_normalize_create_proposal_idempotency_key` in [appointments.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/app/routers/appointments.py) to raise a 400 error if `len(normalized) < 8`.
* **Task 2: Test Suite Realignment**:
  Update the contract tests in [test_api_spine_create_proposal_idempotency_route_contract.py](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/tests/test_api_spine_create_proposal_idempotency_route_contract.py) to expect 400 for keys under 8 characters.
* **Task 3: Document/Alignment Update**:
  Update [api_spine_appointment_idempotency_create_proposal_header_alignment.md](file:///C:/Users/sarashera/EMR4-worktrees/antigravity/orchestration/api_spine_appointment_idempotency_create_proposal_header_alignment.md) to record active runtime enforcement.

---

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no

