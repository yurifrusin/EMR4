# review-claude-claude-bernie-selected-instruction-safety-review

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-bernie-selected-instruction-safety-review` |
| Status | queued |

## Review Request

claude-bernie-selected-instruction-safety-review ready for Codex review

## Worker Completion Notes

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

## Required Review Steps

1. Fetch the worker branch.
2. Inspect `orchestration/agent_inbox/claude/claude-bernie-selected-instruction-safety-review.md`.
3. Review the branch diff against `master`.
4. Run the verification listed in the source task or explain why not.
5. Integrate only if the work is correct, scoped, and compatible with current baton.

## Completion Notes

- Review result:
- Follow-up required:
