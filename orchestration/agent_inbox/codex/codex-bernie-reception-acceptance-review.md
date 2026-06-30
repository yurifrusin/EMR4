# codex-bernie-reception-acceptance-review

| Item | Value |
|---|---|
| To | codex |
| Branch | `codex/bernie-reception-acceptance-review` |
| Status | submitted |
| Created | 67f1c02 |
| Start Command | `python scripts\agent_worktrees.py handin --agent codex` |
| Plan Command | `python scripts\agent_worktrees.py plan --agent codex --task codex-bernie-reception-acceptance-review --summary "Short plan summary"` |
| Submit Command | `python scripts\agent_worktrees.py submit --agent codex --task codex-bernie-reception-acceptance-review --commit-message "Bernie Product API Acceptance Review" --message "codex-bernie-reception-acceptance-review ready for Codex review"` |

## Mission

Independently analyse the current Bernie screenshots, backend contracts, diary UI, audit seams, and implementation-plan fit; submit acceptance criteria and risks for Ariadne to use when judging Claude and Antigravity plans.

## Scope

### In Scope

Plan/review packet first only. Read-only inspection of Bernie backend contracts, diary UI, review harness, Access AI/audit seams, orchestration/resource_admin_bernie_tool_design.md, orchestration/phase_programmes.md, and screenshots. Identify what is working, what is not, what belongs in Sprint 96, what must be deferred, and what should cause plan resubmission.

### Out of Scope

Production code edits before plan approval; implementing or integrating other worker work; live service setup; live Caller ID/OPV/phone integration; broad implementation-plan rewrite; broad security/dependency work.

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

Review must include concrete acceptance gates, hidden risks, API/UX resubmission criteria, recommended focused tests, and an explicit check that Caller ID and OPV/PVM remain placeholders only for this sprint.

## Merge Criteria

Ariadne accepts the review if it gives actionable criteria for accepting/rejecting the other plans and keeps Sprint 96 focused on product usability plus API rigor.

## Dissent / Risks

Record concerns, alternative designs, or reasons this task should not be merged as-is.

Codex worker review:

- Working now: the backend already separates non-mutating interpretation,
  normalization, slot search, supervised selection, staff review payloads, and
  the single `confirm-bernie` write endpoint. `confirm-bernie` requires
  `confirmed=true`, revalidates the supplied selection/create proposal against
  current state, and writes bounded appointment audit evidence. The diary panel
  already renders blocked, candidate-selection, and confirmation-ready states;
  candidate slots are buttons; the confirm button is disabled until a staff
  checkbox is ticked; existing smoke coverage checks blocked/candidate/ready
  states and protects one live-smoke path from accidental confirm writes.
- Not working well enough for reception: the UX still reads as an internal
  safety prototype rather than a calm assistant. Screenshots show "Supervised
  Booking Review", robot/masked iconography, red/blocked theatre, raw
  practitioner UUID/provider text, backend issue codes in primary copy, and
  "BERNIE PROVISIONAL BOOKING" staged directly in the diary. Candidate slots are
  functionally selectable but not yet a polished receptionist decision flow, and
  identity evidence can look both alarming and more definitive than the current
  placeholder context supports.
- Sprint 96 belongs here: calmer receptionist-facing language and hierarchy;
  structured API evidence for interpreted intent, slot candidates, selected
  slot, identity evidence, warning/block summaries, confirm endpoint/payload,
  and audit evidence; tests proving proposal routes remain non-mutating and the
  confirm route is the only Bernie booking write; UI smoke checks for calm copy,
  candidate focus/preview, explicit confirmation, and no write before confirm.
- Must defer: real Caller ID source selection, phone/PBX integration, OPV/PVM,
  IHI and live Medicare verification, SMS/reminder semantics, patient-facing
  booking, broad diary redesign, appointment enum migration, and a general audit
  platform migration. For Sprint 96 these should remain optional
  `context_frames`/metadata placeholders only and must not be represented as live
  verification in staff copy.
- Backend acceptance gates for Claude: proposal/interpreter/supervised routes
  remain no-write and no-appointment-audit except bounded Access AI audit for
  live interpretation; `staff_review` has stable structured fields for
  receptionist display without raw provider noise; confirmation-ready payloads
  include selected-slot and create-proposal evidence plus confirm endpoint and
  evidence codes; `confirm-bernie` revalidates stale/conflicting/mismatched
  evidence and writes exactly one appointment plus one appointment audit trail;
  tests assert no mutation for interpret, normalize, slot-search, supervised
  search, and candidate-selection states; tests assert stale/mismatched confirm
  payloads block; migration rationale is explicit, preferably no migration.
- UX acceptance gates for Antigravity: replace prototype labels with calm
  reception language such as "Booking assistant" / "Review booking suggestion";
  warnings are plain-language and proportionate; raw UUIDs, provider names like
  "live live", backend codes, and internal state names are hidden from ordinary
  staff or moved to an unobtrusive technical detail; candidate slots show useful
  time, duration, practitioner/patient context, and warnings; clicking a
  candidate visibly previews/focuses the diary while clearly saying nothing is
  booked yet; staged preview wording cannot be mistaken for a real booking;
  confirm remains behind explicit staff approval and is keyboard reachable.
- Recommended focused tests: backend pytest for no-write proposal routes,
  confirm-only mutation, stale conflict revalidation, identity evidence for
  unlinked/linked/placeholder caller-id frames, and Access AI audit bounded to
  interpreter provider use; frontend review harness checks for calm labels,
  absence of alarmist prototype strings in ordinary mode, candidate preview and
  focus, disabled/enabled confirm state, confirm adapter payload shape, no
  confirm call before checkbox+button, and diary asset version/cache-bust.
- Resubmission criteria for Claude plans: resubmit if the plan mutates bookings
  from interpret/search/selection, treats Caller ID/OPV/PVM/IHI/Medicare as live
  services, omits no-write assertions, relies on raw LLM output rather than typed
  schemas, weakens confirm revalidation, omits audit evidence, or proposes broad
  schema/security rewrites not required for Sprint 96.
- Resubmission criteria for Antigravity plans: resubmit if the plan preserves
  scary/prototype tone, shows raw UUIDs/provider/debug state in primary staff
  UI, weakens explicit confirmation, makes staged previews look like real
  bookings, changes unrelated diary/waiting-room/resource-admin surfaces, omits
  keyboard/accessibility checks, or lacks deterministic smoke coverage.

## Completion Notes

Required before submit. These notes are copied into Codex's review packet automatically:

- Files changed: orchestration-only protocol artifacts:
  `orchestration/agent_inbox/codex/plan-codex-codex-bernie-reception-acceptance-review.md`
  created by the plan helper; this task packet updated with review/completion
  notes. No `app/`, `docs/diary/`, `tests/`, `review/`, `migrations`, or
  production runtime files were edited.
- Verification run: `python scripts\agent_worktrees.py handin`; read
  `AGENTS.md`, `orchestration/protocol_alerts.md` via handin output,
  `orchestration/parallel_workstreams.md`,
  `orchestration/resource_admin_bernie_tool_design.md`,
  `orchestration/phase_programmes.md`,
  `app/schemas/appointments.py`, key sections of
  `app/routers/appointments.py`, `app/models/appointments.py`,
  `app/models/ai_audit.py`, `docs/diary/diary.html`,
  `docs/diary/diary.css`, `docs/diary/diary.js`, and
  `review/test_diary_smoke.py`; inspected attached screenshots for UX/product
  issues; ran `git status --short --branch`.
- Remaining risks: review is static and screenshot-based; I did not run pytest,
  Playwright, or live API calls because this worker is plan/review-only. Ariadne
  should require worker plans to turn these criteria into focused backend and UI
  tests before implementation is accepted. Caller ID, phone-system integration,
  OPV/PVM, IHI, and live Medicare must remain placeholders/context-frame
  concepts only in Sprint 96.
