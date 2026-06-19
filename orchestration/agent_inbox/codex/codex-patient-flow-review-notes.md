# codex-patient-flow-review-notes

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/patient-flow-review-notes` |
| Status | integrated |
| Created | 62cfeaa |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-patient-flow-review-notes --commit-message "Add patient flow review notes" --message "Patient flow review notes ready for Codex review"` |

## Mission

Define the product/review checklist for read-only patient-flow visibility in the diary before mutation work starts.

## Scope

### In Scope

Inspect current appointment status model, waiting-room endpoint, diary status rendering, sprint_closeout.md, and parallel_workstreams.md. Add or update a small orchestration checklist document that clarifies what Booked, Confirmed, Arrived, InConsult, Completed, Cancelled/NoShow/DNA should mean visually and operationally in read-only diary review. Include exact post-integration user review checks. Keep changes documentation/checklist only unless a tiny task packet note is needed. Fill Completion Notes before submit.

### Out of Scope

Do not edit production backend/frontend implementation, migrations, seed data, tests, taskpane, Command Centre, Gemini/AI code, booking mutations, or status update controls.

## Required Steps

1. Run the start command above.
2. Read the protocol alerts printed by `handin`.
3. Read `AGENTS.md` and `orchestration/parallel_workstreams.md`.
4. Work only inside the stated scope unless the user or Codex expands it.
5. Do not merge to `master`.
6. Do not move `handoff/current`.
7. Run the verification listed below.
8. Fill in the Completion Notes section below with files changed, verification run,
   and remaining risks. The submit command copies those notes into Codex's review
   packet automatically.
9. Finish with the submit command above.

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

Run git diff --check. No JS/Python test is required unless implementation files are touched. Completion Notes must include the exact manual review checklist Codex should use after integrating Claude and Antigravity.

## Merge Criteria

Codex has a concise patient-flow review checklist for Sprint 6; status semantics are explicit enough to guide user review; no production behavior changes are introduced.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Recovered by Codex orchestrator after the Codex worker did not start this
documentation-only task.

- Files changed: `orchestration/patient_flow_review.md`;
  `orchestration/agent_inbox/codex/codex-patient-flow-review-notes.md`.
- Verification run: `git diff --check` passed after merging the sprint review
  branch.
- Remaining risks: This is a review checklist only. It does not validate the
  live waiting-room endpoint or diary UI until Claude and Antigravity submissions
  are integrated and tested.
