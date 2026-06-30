# plan-codex-codex-bernie-reception-acceptance-review

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/bernie-reception-acceptance-review` |
| Source Task | `codex-bernie-reception-acceptance-review` |
| Status | pending_plan_review |
| Created | 2026-06-30 23:12 +1000 |
| Source HEAD | `68d3728` |

## Plan Summary

Sprint 96 Bernie acceptance review plan

## My Understanding

Sprint 96 should convert the existing Bernie supervised-booking prototype into a calmer receptionist-facing proposal workflow while preserving the strict backend rule that search/interpret/selection are non-mutating and only confirm-bernie can create a booking after explicit staff confirmation and revalidation. Current screenshots show a working end-to-end review surface, but it still exposes internal prototype language, raw identifiers/provider labels, red/blocked theatrics, and provisional-booking wording that could alarm staff. Backend contracts already have proposal, selection, confirm, appointment audit, Access AI audit, and context-frame seams; this review will help Ariadne judge whether Claude and Antigravity plans tighten those seams without overreaching into live Caller ID, phone-system, OPV/PVM/IHI, or Medicare integrations.

## Intended Surface / Boundary

Review-only orchestration artifact for Sprint 96, covering acceptance criteria for app/schemas/appointments.py, app/routers/appointments.py, app/models/appointments.py, app/models/ai_audit.py, docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js, review/test_diary_smoke.py, and orchestration planning notes. Visually adjacent surfaces that must not change in this sprint: the main diary grid geometry, Waiting Room patient-flow model, resource admin, taskpane, Command Centre, billing, SMS, and live identity integrations.

## Out Of Scope

No production code edits by this worker. Sprint 96 should not choose or implement a real Caller ID provider, phone/PBX integration, OPV/PVM/IHI/Medicare verification, live Medicare lookup, SMS workflow, patient-facing booking portal, broad diary redesign, general audit-log migration, or appointment enum migration. Those remain placeholders/context-frame seams only.

## Files I Expect To Edit

Only orchestration coordination files generated/updated by protocol: orchestration/agent_inbox/codex/plan-codex-codex-bernie-reception-acceptance-review.md and orchestration/agent_inbox/codex/codex-bernie-reception-acceptance-review.md completion notes. No app/, docs/diary/, tests/, review/, migrations, or production runtime files.

## Implementation Steps

1. Inspect protocol alerts, workstream board, resource-admin Bernie design, phase programmes, appointment schemas/router/models, audit model, diary UI, review harness, and attached screenshots. 2. Classify what is working versus not working. 3. Define Sprint 96 acceptance gates for backend evidence contracts, UI tone/hierarchy, confirmation/no-mutation behavior, audit evidence, and deterministic tests. 4. Define risks and resubmission criteria for Claude and Antigravity plans. 5. Submit the review through the task packet protocol without implementing any production change.

## Visual / Behavioural Acceptance Checks

Acceptance gates: backend plans must keep interpret/slot-search/supervised-booking non-mutating, reserve writes for confirm-bernie, revalidate selected slot/create command before write, return structured staff_review identity/slot/confirmation/audit evidence, and assert Caller ID/OPV/PVM/IHI/Medicare are context-frame placeholders only. UX plans must replace prototype/alarmist language with calm reception language, hide raw UUID/provider/internal state from ordinary staff, keep candidate slots selectable and visibly focused on the diary, keep confirmation disabled until explicit staff approval, and retain deterministic smoke checks for blocked, candidate-selection, confirmation-ready, no-write-before-confirm, and confirm-adapter behavior. Both plans must name focused tests and asset cache-bust/version checks.

## Risks / Ambiguities

Hidden risks: raw context values or provider labels can leak internal implementation detail into staff workflow; red blocked styling can train staff to ignore warnings or fear the tool; provisional preview could be mistaken for an actual booking; candidate selection may visually focus the diary without being obviously non-mutating; identity evidence may appear stronger than it is if placeholder Caller ID/identity frames are worded as live verification; confirm payloads can become stale between slot search and approval; live/smoke/dev adapter flags can accidentally call the write path in tests; audit evidence may remain too narrow if it only records warning codes and not enough proposal provenance for later review.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
