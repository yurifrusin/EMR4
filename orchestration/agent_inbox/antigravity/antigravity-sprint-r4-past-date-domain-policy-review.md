# antigravity-sprint-r4-past-date-domain-policy-review

| Item | Value |
|---|---|
| To | antigravity |
| Branch | `antigravity/current` |
| Status | integrated |
| Created | 20a420f |
| Start Command | `python scripts\agent_worktrees.py handin --agent antigravity` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent antigravity --task antigravity-sprint-r4-past-date-domain-policy-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent antigravity --task antigravity-sprint-r4-past-date-domain-policy-review --commit-message "Sprint R4 Gemini past-date domain policy review" --message "antigravity-sprint-r4-past-date-domain-policy-review ready for Codex review"` |

## Mission

Use Antigravity/Gemini for a domain-policy and receptionist-safety review of Bernie backdated-date handling: define expected staff-facing behavior, issue codes, and edge cases for absolute past dates versus same-day past windows.

## Scope

### In Scope

orchestration review packet; optional docs/receptionist_review_r4.md notes; tests/fixtures recommendations. Treat Gemini as a real backend/domain-policy reviewer, not just UX.

### Out of Scope

Production code edits; diary UI redesign; broad patient collision work; live provider calls; GraphRAG/indexer automation.

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

Submit a review packet with acceptance criteria and risk notes; no runtime tests required unless Antigravity adds a docs-only fixture check.

## Merge Criteria

Codex receives a concrete policy recommendation distinguishing absolute past dates, same-day fully-past windows, and stale reference-date cases, with actionable acceptance tests.

## Completion Notes

- Integrated by Ariadne after normalising outcome names to the scenario-corpus validator.
- Files integrated: `docs/receptionist_review_r4.md` and three natural-language scenario fixtures under `tests/fixtures/bernie_scenarios/`.
- `stale_reference_date_confirmation_blocked.yaml` remains corpus memory/xfail until a future executable replay can set up session freshness and confirmation evidence.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed:
- Verification run:
- Remaining risks:
