# plan-codex-codex-location-diary-view-design-harness

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/location-diary-view-design-harness` |
| Source Task | `codex-location-diary-view-design-harness` |
| Status | integrated |
| Created | 2026-06-22 18:06 +1000 |
| Source HEAD | `1e9444c` |

## Plan Summary

Location diary view design harness plan

## My Understanding

Sprint 16 is about making the diary/resource layer location-aware while preserving the domain split: Practice is the tenant/admin/reception unit, PracticeLocation is a physical site, Room/resource/waiting area/roster/diary template live within a site, and diary page/view groups are screen-real-estate layouts inside a site. This Codex lane is a design/review harness only, coordinating Claude backend and Antigravity diary UI work without implementing production code.

## Intended Surface / Boundary

Docs and review harness only: orchestration notes, implementation-plan wording, sprint closeout/review checklist, and optional API/user-test snippets. No production backend, frontend, migration, taskpane, Command Centre, diary grid geometry, appointment-card stacking, Waiting Room card layout, booking slot rendering, or status mutation behaviour changes.

## Out Of Scope

Production backend/frontend implementation; migrations; FastAPI routers/models/schemas/tests except as referenced in review snippets; docs/diary runtime code; taskpane and Command Centre; autonomous Bernie runtime; drag/drop/resize; changing master, handoff/current, or durable mirror branches.

## Files I Expect To Edit

Likely later edits: orchestration/sprint_closeout.md; a new or updated orchestration/location_diary_view_review.md or similarly named review harness; implementation_plan.md Phase 2/2B notes if wording needs tightening; possibly orchestration/parallel_workstreams.md only if status/guardrail wording needs a tiny plan-approved update; the task packet completion notes after approval. No app/, docs/diary/, EMR4 Sidebar/, alembic/, or tests/ production changes.

## Implementation Steps

1. Add a concise canonical vocabulary table for Practice, PracticeLocation, Room, bookable resource, WaitingArea, DiaryTemplate, DiaryRoster, diary column, diary page/view group, booking slot, appointment status, patient identity, and booking/reminder confirmation. 2. Add a Sprint 16 review harness that tells Codex what to check after Claude and Antigravity submit: backend location scoping, one-location fallback, multi-location selector behaviour, and proof that view groups are not physical locations. 3. Add API/user-test snippets only as review aids, using placeholder IDs or discovery steps, not new runtime dependencies. 4. Tighten implementation-plan notes only if needed so future Bernie tools inherit the same vocabulary. 5. Add risks/dissent and completion notes, then run git diff --check after approval.

## Visual / Behavioural Acceptance Checks

The harness lets a reviewer answer: Does every room, waiting area, roster, diary template, and appointment belong to a physical PracticeLocation inside a Practice? Does the diary UI expose the active physical location without treating page/view groups as extra locations? Does a one-location practice remain boring and uncluttered? Do Waiting Room panels/cards, main diary appointment blocks, booking slots, and status controls remain separate surfaces? Does Bernie tool language require explicit location and resource context before proposing writes? No runtime behaviour changes are included.

## Risks / Ambiguities

Risk: docs-only work can drift from Claude/Antigravity implementation if their plans choose different route names or payload shapes, so snippets should be review aids rather than contracts unless integration confirms them. Risk: legacy terminology like Confirmed, waiting room, room, slot, page, and column can still be misread; the harness should force qualifiers. Dissent: avoid adding a full admin taxonomy beyond what Sprint 16 needs, because over-documenting future resource abstractions could box in the backend before real usage tests.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
