# plan-antigravity-antigravity-r29-action-grammar-receptionist-review

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-r29-action-grammar-receptionist-review` |
| Status | integrated |
| Created | 2026-07-06 15:30 +1000 |
| Source HEAD | `9d759599` |

## Plan Summary

Receptionist acceptance review plan for R29 action grammar: Define the domain vocabulary, write authority constraints, and strict UI boundaries for the backend action grammar foundation to ensure safety and clarity for the receptionist workflow, preserving the H15 gate and no-write/no-autonomous-booking invariants.

## My Understanding

The mission is to define receptionist-domain acceptance criteria for the R29 native Bernie/Diary action grammar foundation (dispatched in Programme 2B/2D). The R28 Fable recommendations suggest establishing a stable native action grammar (Create, Move, Resize, Cancel, Roster change, Check-in, Link-patient) that respects backend write authority and runs in a deterministic replay harness before opening the H15 semantic gate or mining the trove. The review will be captured in `docs/receptionist_review_r29.md` post-approval. No UI changes are allowed.

## Intended Surface / Boundary

- Surface: Creation of `docs/receptionist_review_r29.md` after plan approval.
- Boundaries to preserve (MUST NOT EDIT): `app/` backend, `tests/`, `migrations/`, frontend visual styles/components (diary grid, booking slots, sidebar panels, waiting room UI, card stacking, statuses), raw trove files, and local ignored JSON files.

## Out Of Scope

Production code, test implementations, frontend visual assets, live provider API calls, database migrations, stashing or processing raw trove files, and changing the state of the H15 semantic gate.

## Files I Expect To Edit

- `docs/receptionist_review_r29.md` (after plan approval)
- `orchestration/agent_inbox/antigravity/antigravity-r29-action-grammar-receptionist-review.md` (status and completion notes)

## Implementation Steps

1. Execute the plan command to capture this plan.
2. Commit and submit the plan packet via `scripts/agent_worktrees.py submit` to notify Codex/Ariadne for plan review.
3. Stop and wait for the user/Codex to say `complete sprint task`.
4. After plan approval, create `docs/receptionist_review_r29.md` detailing the receptionist acceptance criteria for the action grammar, mapping the domain actions (booking cards, time slots, status changes) to safety invariants.
5. Verify the artifact for correctness, UTF-8 compliance, and git hygiene.
6. Record completion notes in the task packet and run final submit.

## Visual / Behavioural Acceptance Checks

- The review document `docs/receptionist_review_r29.md` is successfully created.
- The document defines domain vocabulary for Create, Move, Resize, Cancel, Roster changes, Link-patient, and Check-in.
- It specifies that the backend action grammar must preserve receptionist-only write authority and forbid autonomous bookings.
- It enforces a strict zero-UI-change boundary for the foundation.
- It keeps the H15 semantic gate closed.

## Risks / Ambiguities

- **Risk: Backend grammar terminology might diverge from receptionist domain concepts.** The review document will mitigate this by defining clean terminology mappings.
- **Risk: Over-specifying implementation details.** We mitigate this by keeping the review focused strictly on domain validation and safety boundaries.
- **Risk: Inadvertent UI modifications.** The review will establish a hard block on visual changes.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
