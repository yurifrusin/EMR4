# S5 B-1: Diary Selection Preservation Repair (Phase B — the single authorized S5 repair)

Sprint: S5
Lane: D-1 (Phase B repair), attempt 1
Resource: `deepseek-flash-workers` instance 1
Parent allocation: `plan-claude-fable-emr4-receptionist-workflow-audit.md`
Gate decision: `plan-claude-fable-s5-phase-b-decision.md`
Completion artifact: `orchestration/agent_inbox/codex/review-deepseek-s5-b1-selection-repair.md`

This packet is the Conductor-selected single S5 repair. It is dispatched by the
orchestrator only after an explicit `complete sprint task` release. It grants
no scope beyond the boundary below and no allocation authority.

## Defect (three-way confirmed)

Every silent auto-refresh (`scheduleRefresh()` → `loadDiary(true)`,
`docs/diary/diary.js:4478-4480`) rebuilds the grid via `renderGrid()`, which
clears `grid.innerHTML` (`diary.js:3520`). The active appointment selection
(`.appt-active`, applied at click, `diary.js:3909-3911`) and any open inline
status editor are destroyed mid-action. Two flow-specific restorations exist
(`diary.js:8634-8644`) but there is no general preservation. Confirmed by A-1
(usability Go Blocker), by the orchestrator's source reproduction, and by the
Conductor's spot-check.

## Mission

Preserve the active appointment selection across silent diary refreshes:

1. Before a silent rebuild, capture the identity (appointment id) of the
   element currently carrying `.appt-active`.
2. After the rebuild, if an element for that appointment id still exists,
   re-apply `.appt-active` to it (follow the existing idiom at
   `diary.js:8634-8644`).
3. Desirable but optional: restore an open inline status dropdown state, only
   if achievable without changing event-handler semantics. If skipped, record
   why in the completion artifact.
4. If the appointment no longer exists after refresh (cancelled/moved off-day),
   the selection is legitimately dropped; do not fabricate a selection.

## Ownership boundary (disjoint from D-2; nothing else may change)

- `docs/diary/diary.js` — the fix.
- `docs/diary/diary.html` — cache-bust `?v=N` bump only.
- `review/test_diary_selection_preservation.py` — one NEW Playwright
  regression test file (bounded boundary extension granted by the gate
  decision). Model it on the route-intercepted patterns in
  `review/test_diary_smoke.py`, but do NOT edit `test_diary_smoke.py`,
  `review/test_raw_status_terminal_rollback_guard.py`, or any other existing
  file in `review/` or `tests/` — those remain D-2's surface.

## Required evidence sequence (failing-first)

1. Write `review/test_diary_selection_preservation.py`: select an appointment
   (assert `.appt-active` on a known appointment id), trigger a silent refresh
   (invoke `loadDiary(true)` or an equivalent smoke-mode hook), assert the same
   appointment still carries `.appt-active`.
2. Run it against the UNFIXED code and record the failure transcript in the
   completion artifact.
3. Apply the fix; run the test again and record the pass.
4. `node --check docs/diary/diary.js` — record pass.
5. `pytest review/test_diary_smoke.py -q` — record the result. Baseline is 8
   known failures / 131 passes (pre-existing harness drift: GraphQL
   practitioner mock + smoke-mode network-bypass assertions). Acceptance
   requires NO NEW failures relative to that baseline. Do not fix or touch the
   8 known failures — that is explicitly out of scope.
6. Bump `?v=N` in `docs/diary/diary.html`.
7. Confirm the diff touches only the three owned files.

## Constraints

- No change to status-change semantics, request payloads, endpoints, or any
  backend file. No new write authority.
- All parent-plan §2 closed gates stay closed: Bernie D5, provider wiring,
  memory/RAG/GraphRAG, historical diary runtime/`local_data`, GraphQL
  expansion, deployment/Pages changes, external clients, schema migrations.
- Do not fix `DIARY_URL`, popup handling, or any other Phase A finding — the
  sprint allows exactly one repair and this is it.
- Diary assets are edited directly in `docs/` (no `sync_taskpane.py` run).
  Do not deploy Pages; integration is orchestrator-owned.
- No commits to `master`/`handoff/current`; use the standard packet `submit`
  path from the packet-scoped disposable worktree.

## Completion artifact requirements

`orchestration/agent_inbox/codex/review-deepseek-s5-b1-selection-repair.md`
must contain: workspace receipt (worktree, branch, cleanliness, relation to
`handoff/current`), the failing-then-passing test transcripts, all command
results from the evidence sequence, the exact diff summary, a
boundary-compliance table, and any recorded skip rationale for the optional
dropdown restoration. Create the artifact skeleton first and append evidence
incrementally. Terminal output is not a result; only this durable artifact is.

Cross-review: D-2 will independently review the diff and the new test
(`orchestration/agent_inbox/codex/review-deepseek-s5-b1-cross-review.md`).
Integration proceeds only on its explicit pass.

End with the canonical line below only after all required sections contain
evidence:

```text
STATUS: complete
```
