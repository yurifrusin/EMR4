# claude-r29-native-action-grammar-foundation

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/native-action-grammar-foundation` |
| Status | submitted |
| Created | c610e1de |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-r29-native-action-grammar-foundation --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-r29-native-action-grammar-foundation --commit-message "Dispatch R29 native action grammar foundation" --message "claude-r29-native-action-grammar-foundation ready for Codex review"` |

## Mission

Plan the native Bernie/Diary action grammar foundation. Define a minimal backend/domain contract for typed diary action vocabulary and envelopes that can later support create, move, resize/extend, cancel, status, waiting-area, check-in, slot search, and explain-schedule flows while preserving deterministic backend write authority. Plan first only; do not implement until approved.

## Scope

### In Scope

Read AGENTS.md, orchestration/protocol_alerts.md, orchestration/agent_inbox/codex/plan-claude-claude-r28-fable-full-trove-readiness-review.md, orchestration/phase_programmes.md, app/services/bernie/capabilities.py, app/services/bernie/session.py, app/services/bernie/policy.py, app/services/bernie/frames.py, app/services/bernie/temporal.py, app/routers/appointments.py proposal/confirm sections, app/schemas/appointments.py, and focused Bernie/appointment tests. Produce an implementation plan naming exact backend/domain files, test files, invariants, and compatibility boundaries.

### Out of Scope

Production code edits before plan approval, frontend/diary.js, taskpane, raw trove/local_data, H15 semantic fixtures, provider calls, migrations unless explicitly justified in the plan, broad router rewrites, autonomous agent writes, and master/handoff movement.

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

Plan packet only. Must include exact file boundary, no-UI-change statement, confirmation/write-authority invariants, focused pytest plan, and risks around compatibility with existing proposal/confirm routes.

## Merge Criteria

Ariadne receives an implementation-ready plan for the smallest native action grammar foundation sprint, with safe boundaries and verification.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

- Files changed:
  - NEW app/services/diary/action_grammar.py — DiaryActionVerb enum (11 verbs),
    DiaryActionVerbDescriptor frozen dataclass, DIARY_ACTION_GRAMMAR table,
    GRAMMAR_SCHEMA_VERSION="diary.action_grammar.v1", get_verb_descriptor,
    action_verb_for_envelope bridge, assert_grammar_consistency
  - NEW app/services/bernie/action_grammar.py — compatibility facade re-exporting
    all diary-domain grammar symbols; objects are identical (is-checks pass)
  - MODIFIED app/services/diary/__init__.py — added 7 grammar symbols to imports
    and __all__
  - MODIFIED app/services/bernie/__init__.py — added 7 grammar symbols to imports
    and __all__
  - NEW tests/test_diary_action_grammar.py — 31 tests covering all mandatory
    Codex/Delta gates

- Verification run:
  - pytest tests/test_diary_action_grammar.py -q → 31 passed
  - pytest tests/test_diary_action_envelopes.py tests/test_diary_action_boundary_contracts.py
    tests/test_bernie_diary_rehome_compatibility.py tests/test_bernie_domain_package.py
    tests/test_bernie_diary_capability_manifest.py tests/test_bernie_confirm_create_proposal.py
    tests/test_bernie_session_store.py tests/test_bernie_transition_table.py
    tests/test_bernie_confidence_policy.py -q → 138 passed, 0 failures
  - python -m py_compile all 3 new files → OK
  - git diff --name-only → exactly 5 files (2 modified inits + 3 new)
  - sprint98 failures (4 tests) confirmed pre-existing DB-dependent failures on branch;
    not caused by this change

- Remaining risks:
  - move/resize share the update confirm action in v1; a future sprint adding a
    dedicated move endpoint must update action_grammar.py (non-breaking: just
    change confirm_actions tuple for DiaryActionVerb.move)
  - action_verb_for_envelope bridge covers common action_name strings; unknown
    names return None (non-breaking by design)
  - Grammar is not yet wired into dispatch or the manifest prompt (deliberate
    scaffold posture); Sprint+2 replay harness will be the first consumer
