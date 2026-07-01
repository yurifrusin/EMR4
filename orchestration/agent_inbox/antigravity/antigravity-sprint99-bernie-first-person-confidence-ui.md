# antigravity-sprint99-bernie-first-person-confidence-ui

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | submitted |
| Created | 76e00f9 |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint99-bernie-first-person-confidence-ui --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint99-bernie-first-person-confidence-ui --commit-message "Sprint 99 Bernie first-person confidence UI" --message "antigravity-sprint99-bernie-first-person-confidence-ui ready for Codex review"` |

## Mission

Plan the receptionist-facing Bernie UI response layer for confidence-aware booking: first-person assistant copy, compact default evidence, Details disclosure, inferred-date messaging, candidate/preview behavior, and calm blocked clarification prompts.

## Scope

### In Scope

Plan packet first only. Review docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py, orchestration/bernie_release_gates.md. Propose exact UI/copy changes so normal mode says 'I've assumed...' and 'Do you mean...' rather than 'Please tell Bernie...', shows most-likely diary preview when confidence permits, compacts evidence above confidence thresholds with Details, expands evidence below thresholds, and prepares for future voice/chat parity.

### Out of Scope

Production code before plan approval; backend schema implementation except requested contract fields; live voice/headset work; phone-system/Caller ID/Medicare integrations; broad diary redesign; removing staff confirmation; raw debug details in ordinary mode.

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

Plan must name exact diary files/tests, route-intercepted smoke cases for inferred today, typo-resolved practitioner, ambiguous patient candidate, details toggle, no raw snake_case in ordinary mode, no write before confirm, asset version checks, and deployed/local review strategy.

## Merge Criteria

Ariadne can approve only if the plan keeps the ordinary receptionist surface calm and concise, provides technical Details on demand, supports a future voice interaction model, and does not reduce API guardrails or confirmation gates.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Implementation completion update - supersedes the earlier plan-gate notes below.

- Files changed:
  - `docs/diary/diary.html`
  - `docs/diary/diary.css`
  - `docs/diary/diary.js`
  - `review/test_diary_smoke.py`
- Implementation summary:
  - Renamed the ordinary panel to *bernie* and removed the masked-robot/scary
    safety phrasing from the receptionist surface.
  - Added first-person assumption/clarification copy, including "I've assumed..."
    and "Do you mean..." flows.
  - Added compact high/medium-confidence evidence with a `Details` disclosure
    rather than always showing verbose technical text.
  - Added confidence-aware auto-preview of the most likely provisional diary slot
    when the backend state permits it, while respecting the user suppression path.
  - Preserved the no-write-before-confirm behaviour and confirm shortcut surface.
  - Added route-intercepted review tests for inferred today, practitioner typo,
    patient ambiguity, details disclosure, no write before confirm, and provisional
    diary preview behaviour.
- Verification run:
  - `node --check docs\diary\diary.js`
  - `C:\Users\YuriFrusin\Documents\EMR4\.venv\Scripts\python.exe -m pytest review\test_diary_smoke.py -q` -> 72 passed.
  - `git diff --check`
- Remaining risks:
  - Live diary confirmation still depends on the backend confirm endpoint and
    real diary data shape; local review covers the frontend contract with route
    interception.
  - Voice input remains future work; this sprint only makes text responses
    voice-ready.

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
  - `orchestration/agent_inbox/antigravity/antigravity-sprint99-bernie-first-person-confidence-ui.md` (task packet Completion Notes)
  - `orchestration/agent_inbox/codex/plan-antigravity-antigravity-sprint99-bernie-first-person-confidence-ui.md` (written implementation plan)
- Verification run:
  - Plan phase validation: Ran `python scripts\agent_worktrees.py plan` to generate the plan and verified formatting of the resulting Markdown file. Ensured repository contains no production code edits.
- Remaining risks:
  - Integration dependencies on Workstream FA (Claude Code) API fields for confidence-aware booking. These fields will be aligned prior to code changes in the implementation phase.
