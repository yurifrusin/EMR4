# antigravity-sprint-r18-bernie-manifest-domain-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 379d0df |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r18-bernie-manifest-domain-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r18-bernie-manifest-domain-review --commit-message "Dispatch R18 Bernie manifest domain review" --message "Sprint R18 Bernie manifest domain review packet"` |

## Mission

Review the proposed Bernie Diary Capability Manifest v1 concept: Bernie should be schema-literate over native diary entities/states/transitions without becoming code-authoritative. Produce a domain/UX/safety critique and recommended manifest sections for Gemini/Bernie context.

## Scope

### In Scope

orchestration/bernie_native_diary_agent_notes.md, orchestration/bernie_interaction_model.md, orchestration/bernie_release_gates.md, app/services/diary/*.py, app/services/bernie/*.py, app/schemas/appointments.py, app/schemas/diary.py, docs/diary/diary.js, and a docs/orchestration review artifact.

### Out of Scope

Runtime Gemini prompt changes, backend route behaviour changes, migrations, live AI calls, GraphRAG deployment, codebase-dump context, or granting any write authority to Bernie.

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

Write a concise artifact under docs/ or orchestration/ naming the manifest sections, safety boundaries, what Gemini should know, what it must not decide, and acceptance criteria for schema-literacy without write authority.

## Merge Criteria

Ariadne can use the artifact to implement a compact read-only manifest and golden tests; recommendations preserve deterministic backend authority and human confirmation.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: `orchestration/bernie_diary_manifest_review.md`.
- Verification run: Gemini/Antigravity inspected diary/bernie services, schemas, frontend constants, and safety boundaries; Ariadne preserved the accepted domain critique in master.
- Remaining risks: manifest content must remain synchronized with backend/Pydantic source and must not be treated as executable policy or write authority.
