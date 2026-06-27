# claude-bernie-selected-instruction-safety-review

| Item | Value |
|---|---|
| To | claude |
| Branch | `claude/current` |
| Status | integrated |
| Created | 39e0f6c |
| Start Command | `python scripts\agent_worktrees.py handin --agent claude` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent claude --task claude-bernie-selected-instruction-safety-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent claude --task claude-bernie-selected-instruction-safety-review --commit-message "Submit Bernie instruction safety review" --message "claude-bernie-selected-instruction-safety-review ready for Codex review"` |

## Mission

Provide an independent read-only safety/contract review for Sprint 73 before implementation is integrated. Focus on how selected-appointment instruction affordances should preserve explicit staff submit, stale-context protection, no manual ID exposure, no browser/query persistence of free text, and confirmation gating.

## Scope

### In Scope

Read-only review of docs/diary/diary.js, review/test_diary_smoke.py, and relevant orchestration context; update this task packet Completion Notes and submit a Codex review packet with concrete acceptance criteria, edge cases, and any safety concerns. No production code edits.

### Out of Scope

Implementing UI changes, modifying app/backend/routes/schemas/models/migrations, changing tests unless explicitly asked later, dependency work, provider/Gemini changes, taskpane, Command Centre, billing, SMS, resource admin, and broad diary redesign.

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

No runtime tests required for read-only review; run git status --short --branch before submit and report if clean. If any file is edited, git diff --check must pass.

## Merge Criteria

Codex receives a concise submitted review packet with concrete acceptance criteria/edge cases and no production code changes.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: None (read-only safety/contract review). Inspected `docs/diary/diary.js`
  (Bernie pilot context/instruction surface), `review/test_diary_smoke.py` (live + fixture
  Bernie harness), and `orchestration/parallel_workstreams.md` Sprint 73/67-70 context.

- Verification run: `git status --short --branch` only (no production code or tests edited;
  the sole change is this packet's Completion Notes). No runtime tests required for a
  read-only review per the packet. `git diff --check` not applicable to a Markdown-only edit.

### Safety contract the Sprint 73 implementation must preserve

These gates already exist in `diary.js` and the affordance work must not weaken them:

1. **Explicit staff submit** — supervised review/interpret must fire only from an explicit
   action (`btn-bernie-instruction-submit` / `bernie-pilot-use-selected`), never automatically
   on selection import, panel open, or context readiness. Interpretation stays gated behind
   `shouldRequestBernieInterpretation()` (`bernie_interpret=true` + smoke/dev/active pilot).
2. **Stale-selection guard** — `resolveBerniePilotLaunchRequest()` must keep emitting
   `stale_selected_appointment_context` whenever `explicitContext.sourceAppointmentId` is set
   and the currently active appointment's id differs (or no appointment is active). Any new
   suggested-instruction chip/button must route through this same resolver, not bypass it.
3. **No manual ID exposure in ordinary mode** — `isBernieManualContextAllowed()` (true only
   for `smoke`/`bernie_dev_review`) must remain the sole gate for manual practitioner/patient
   inputs and for reading `practitioner_id`/`patient_id` query params. Production context must
   continue to come only from the "Import context from selected" affordance.
4. **No browser/query persistence of free text** — instruction text must stay body-only POST
   (`{instruction, reference_date}`); no localStorage/sessionStorage/URL persistence of
   instructions or imported PHI context. `berniePilotContext` stays in-memory module state.
5. **Confirmation gating** — confirm stays disabled until the approval checkbox is checked;
   no call to `/proposals/create/confirm-bernie` before explicit confirm click.

### Concrete acceptance criteria for the affordance

- AC1: Suggested-instruction affordances (chips/buttons/placeholder copy) populate the
  instruction input only; they do NOT trigger interpret/supervised/confirm by themselves.
- AC2: With imported context and a matching active appointment, the affordance produces a
  ready instruction state (`request.ready === true`) and the context summary renders the
  selected appointment (practitioner+patient match path in `renderBernieInstructionInput`).
- AC3: After import, if the active appointment changes or is deselected, the next submit is
  blocked by `stale_selected_appointment_context` and the instruction surface is not "ready".
- AC4: In ordinary (non-smoke/non-dev) mode, no manual practitioner/patient ID inputs render
  and query-param IDs are ignored.
- AC5: No new localStorage/sessionStorage/URL keys carry instruction text or PHI context.
- AC6: Diary asset `?v=` cache-bust bumped if `docs/diary/*` runtime assets change; full
  `review/test_diary_smoke.py` harness run when diary runtime assets change.

### Edge cases to cover in the harness

- E1: Deselected appointment after import → resolver block fires (apptId null ≠ sourceAppointmentId).
- E2: Selected appointment lacks practitioner context → "Selected appointment lacks practitioner
  context" error path; no import button.
- E3: Provisional/unlinked patient (`isPatientIdentityUnconfirmed`) → blocked import, error path.
- E4: Default/smoke-shaped IDs in production mode → `default_practitioner_context` /
  `default_patient_context` blocks still fire.
- E5: Empty instruction submit → no provider call (existing empty/clarification handling).
- E6: Suggested affordance text must not inject autonomous-booking language that the interpret
  layer would have to block; if it can, confirm the interpret `blocked` hold path still holds
  supervised review (existing `test_bernie_interpret_preview_holds_supervised_review_until_safe`).

### Remaining risks / dissent

- R1 (medium): The stale guard only runs when `!allowManualContext`. In smoke/dev mode the
  guard is intentionally bypassed, so any new affordance tested only in smoke could mask a
  stale-context regression. Require at least one harness assertion exercising the production
  (`allowManualContext === false`) resolver path, or document why smoke coverage is sufficient.
- R2 (low): `showSelectedAppt` in the context summary requires the active appointment's
  practitioner AND patient to match imported context; a suggested affordance that pre-fills
  context without keeping the appointment active will silently drop the summary while still
  reporting ready. Affordance copy should not imply the summary is guaranteed.
- R3 (low): `buildBernieInterpretInstruction()` truncates to 1000 chars and the input
  placeholder says "non-PHI"; suggested chips must not template real patient names/identifiers
  into the free-text instruction (keep them as IDs/structured tokens only).
- R4 (process): Recommend NOT merging the affordance unless the diary `?v=` bump and a green
  full `review/test_diary_smoke.py` run accompany any `docs/diary/*` change, per Sprint 73
  verification.

No production code changes recommended from this review; gates are sound as written and the
affordance work should layer on top of the existing resolver rather than around it.
