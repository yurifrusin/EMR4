# Conductor Gate Decision — S5 Phase A/B: Single Repair Selection

| Field | Value |
|---|---|
| Plan ID | plan-claude-fable-s5-phase-b-decision |
| Sprint ID | S5 (Phase A/B gate; parent plan `plan-claude-fable-emr4-receptionist-workflow-audit`) |
| Role | conductor |
| Conductor resource | `claude-fable-conductor` (Claude Fable, high reasoning, this session) |
| Date | 2026-07-12 |
| Status | final — gate decision issued |
| Settings fingerprint | `sha256:62d949e026a4191287b516f90d117ee4138dbd3ee1b2417e8b543a4caefa025d` (recomputed this session via `orchestration_harness.settings_fingerprint` over `orchestration/harness_settings/`; matches the AGENTS.md baton record) |
| direction_dialogue_disposition | `skipped` (gate decision inside an active verified sprint; direction is already fixed by the verified S5 plan — no dialogue required per `direction_collaboration` rules) |

## 1. Conductor Workspace Receipt

| Field | Value |
|---|---|
| Target worktree | `C:\Users\sarashera\EMR4-worktrees\claude` |
| Expected branch | `claude/current` — confirmed (`## claude/current...origin/claude/current`, no divergence from remote) |
| Cleanliness | clean (no modified/staged/untracked tracked-code files at gate time) |
| HEAD | `4b6ac9f6` — `S5 A1 receptionist usability review` |
| Relation to `handoff/current` | `handoff/current` (`9c5d28a1`) is an ancestor of HEAD; 35 committed S5/harness commits ahead — expected mid-sprint state, recorded, no realignment required |
| Realignment | none performed; none required |
| Settings fingerprint | recomputed and matching (see header) |

## 2. Evidence Reviewed (accepted Phase A artifacts)

| Artifact | Lane | Result |
|---|---|---|
| `review-deepseek-s5-workflow-audit.md` | D-1 (attempt 2, static frontend trace) | No material functional or usability defect from static trace; 3 minors, 5 observations; all `node --check` passes |
| `review-deepcode-s5-backend-audit.md` | D-2 (backend contract audit) | 0 material functional; 1 claimed material usability (terminal→non-terminal rollback permitted on raw PATCH); 4 minors, 3 observations; failing-test proposal at `review/test_raw_status_terminal_rollback_guard.py` |
| `review-sol-s5-d2-validation.md` | Orchestrator validation of D-2 | Ran the proposed test: raw PATCH returns `200` for `Completed → Booked` and `DNA → Confirmed`, confirming the behavior. Sol's explicit caveat: this proves current behavior, **not** that it is incorrect product policy |
| `review-antigravity-s5-usability.md` | A-1 (usability veto) | **Conditional Go.** Go Blocker: 60-second silent auto-refresh (`loadDiary(true)`) rebuilds the grid DOM and destroys the active selection (`.appt-active`) and open inline editing state. Also reported 8/139 smoke-test failures (GraphQL-vs-REST mock drift + `?smoke=true` network-bypass assertions), hardcoded `DIARY_URL`, popup-consent friction, and lower-ranked findings |
| Orchestrator reproduction (Sol, reported at gate) | — | Independently reproduced the 8 smoke failures and confirmed in source that `loadDiary(true)` → `renderGrid()` rebuilds `grid.innerHTML` with no general active-selection preservation |

Conductor source spot-check (this session, read-only): `docs/diary/diary.js:3520` (`grid.innerHTML = ""` in `renderGrid`), `diary.js:4478-4480` (`scheduleRefresh` → `loadDiary(true)` on `REFRESH_INTERVAL_MS`), `diary.js:3909-3911` (`.appt-active` applied only at click), `diary.js:8634-8644` (two flow-specific post-reload restorations exist, proving the idiom works and that no general mechanism does). The claim is corroborated by three independent sources: A-1 static analysis, Sol source confirmation, and this Conductor spot-check.

## 3. Candidate Analysis

The verified S5 plan (§3, repair allocation) pre-authorizes **at most one** bounded repair, selected by the Conductor, on the lane owning the defect's surface (D-1 frontend, D-2 backend/tests), if and only if a material functional or usability defect is demonstrated.

### Candidate 1 — Terminal-status rollback on raw PATCH (D-2 finding) — **not selected**

Whether `Completed → Booked` or `DNA → Confirmed` must be forbidden, warned, or permitted (e.g. legitimate correction of a mis-clicked status) is a **product-policy decision that has not been delegated**. Sol's validation says exactly this. Selecting this repair would require the Conductor to improvise clinical/administrative policy, which `operating_model.yaml` reserves for the user (`user_pause.only_for: undelegated_material_product_choice`). The finding does **not** block the sprint: the failing-test proposal (`review/test_raw_status_terminal_rollback_guard.py`) stands as durable documentation, and the policy question is queued for Yuri at closeout as a decision item, not a pause. Note also: the proposal path already surfaces an `already_terminal` warning, so the receptionist-facing flow is not silently unsafe today.

### Candidate 2 — Eight smoke-test failures (A-1 tested, Sol reproduced) — **not selected**

Both root causes are **test-harness drift**, not product defects: (a) tests mock REST `/practice/practitioners` while the client now queries GraphQL first; (b) `?smoke=true` mode locally simulates proposal/confirm and legitimately bypasses the asserted network calls. Repairing the harness is worthwhile but is not a "material functional or usability defect" in the receptionist workflow, which is the only repair class the verified S5 plan authorizes. Recorded as the top follow-up candidate for the next sprint's scope.

### Candidate 3 — Auto-refresh destroys active selection (A-1 Go Blocker) — **SELECTED**

- **Materiality:** direct receptionist-workflow harm — every 60 seconds, an in-progress selection/edit affordance is silently destroyed mid-action. A-1 ranked it the sole Go Blocker in its Conditional Go verdict.
- **Evidence quality:** independently established three ways (A-1, Sol, Conductor spot-check) at named source lines. No live-stack ambiguity remains for a DOM-lifecycle defect that is fully determined by source.
- **Boundedness:** fix is confined to frontend DOM-state preservation in `docs/diary/diary.js`. No API, schema, status-semantics, write-authority, or policy change. Opens no §2 closed gate of the parent plan.
- **No undelegated decision:** preserving a user's active selection across a background refresh is unambiguously correct UX; no product-policy choice is implicated.

### Other A-1 conditions — dispositioned, no repair

- **Hardcoded `DIARY_URL`:** dev-ergonomics friction, not a receptionist-workflow defect; touching the URL-routing/deploy surface brushes deployment discipline. Deferred; recorded.
- **`displayDialogAsync` consent prompt:** a documented Office platform security gate (AGENTS.md §4: unsuppressible); mitigation is copy/UX guidance, deferred.
- **Reason-code friction, date-picker `showPicker()`, grid search, hover cards, icon-only button:** medium/low; recorded for future diary UX sprints.

## 4. Gate Decision

**One repair authorized: B-1 — preserve active appointment selection (and, where low-risk, open inline status-editor state) across silent diary auto-refresh.**

- **Owning lane:** **D-1** (`deepseek-flash-workers` instance 1, `deepseek-v4-flash` / high, Deep Code transport, packet-scoped disposable worktree) — per the parent plan's repair allocation: frontend surface → D-1. DeepSeek lane count remains 2 (D-1 + D-2), within the 1–3 cap.
- **Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s5-b1-diary-selection-preservation-repair.md` (issued alongside this decision).
- **Ownership boundary (Conductor-adjusted for Phase B, disjoint from D-2):**
  - `docs/diary/diary.js` (the fix)
  - `docs/diary/diary.html` (cache-bust `?v=N` bump only)
  - `review/test_diary_selection_preservation.py` (**one new file** — a narrow Playwright regression test). This is an explicit, bounded extension of D-1's boundary into `review/` for exactly one new file, granted so the single repair stays on one lane. D-1 must **not** edit `review/test_diary_smoke.py`, `review/test_raw_status_terminal_rollback_guard.py`, or anything else in `review/`/`tests/` (those remain D-2's surface).
- **Cross-review:** D-2 reviews the diff and the new test and returns an explicit pass/fail packet, per the parent plan ("verified by the other lane's review plus harness runs"). If the fix fires, D-1 loses audit-independence for this finding; D-2's cross-review restores the independent check (parent §4).

### Exact acceptance evidence (all required)

1. **Failing-before/passing-after:** `review/test_diary_selection_preservation.py` selects an appointment (asserts `.appt-active` present on a known appointment id), triggers a silent refresh (invoke `loadDiary(true)` or equivalent smoke-mode hook), and asserts the same appointment still carries `.appt-active` afterward. A recorded run against pre-fix code must fail; the same test must pass after the fix.
2. `node --check docs/diary/diary.js` passes.
3. `pytest review/test_diary_smoke.py -q` shows **no new failures relative to the recorded baseline of 8 known failures / 131 passes**. The 8 pre-existing failures are documented harness drift (Candidate 2) and are explicitly not this packet's problem to fix or worsen.
4. `pytest tests -q` unchanged (backend untouched); orchestrator runs it once for the record.
5. Cache-bust `?v=N` bumped in `docs/diary/diary.html`.
6. Diff confined to the three owned files; no `sync_taskpane.py` run needed (diary assets are edited directly in `docs/`, per CLAUDE.md).
7. Durable D-1 completion artifact at `orchestration/agent_inbox/codex/review-deepseek-s5-b1-selection-repair.md` with workspace receipt, before/after evidence transcripts, and boundary-compliance table. Terminal output is not a result.
8. D-2 cross-review packet at `orchestration/agent_inbox/codex/review-deepseek-s5-b1-cross-review.md` with explicit `DECISION: pass` or `revision_required`.

### Constraints binding on B-1

- No change to status-change semantics, request payloads, endpoints, or any backend file. No new write authority. All parent-plan §2 closed gates remain closed (Bernie D5, providers, memory/RAG/GraphRAG, historical diary runtime, GraphQL expansion, deployment/Pages, external clients, schema migrations).
- Do not attempt to fix the GraphQL/smoke-mode harness drift, `DIARY_URL`, or any other Phase A finding — one repair total.
- Minimum acceptable fix: preserve `.appt-active` on the same appointment across a silent rebuild. Restoring an open inline status dropdown is desirable but only if achievable without altering event-handler semantics; if skipped, record why.
- No commit to `master`/`handoff/current`; standard packet `submit` path only.

## 5. Verification Posture (independent LLM verification: **not requested**)

Checked against `operating_model.yaml` / `sprint_worker_policy.yaml` risk triggers:

| Trigger | Applies? |
|---|---|
| new_security_write_deployment_or_release_authority | No — pure frontend DOM-state preservation; no API/auth/deploy change |
| conductor_orchestrator_material_disagreement | No — Sol's evidence and this decision align; Sol reproduced the defect |
| mandate_or_scope_boundary_is_ambiguous | No — repair was pre-authorized in the verified S5 plan §3; this gate exercises exactly that clause |
| allocation_exceeds_declared_resource_limits | No — 2 DeepSeek lanes, within 1–3 cap; no new lanes |
| prior_drift_signal_affects_authority_or_ownership | No — the one boundary adjustment (one new test file) is Conductor-authored and recorded here |

Deterministic checks remain mandatory: the orchestrator must run the standard deterministic plan checks on this delta (fingerprint match — header above; conductor authorship; no allocation-authority transfer; lane cap; distinct artifacts; workspace receipts) before dispatching B-1. Independent LLM verification is available on demand if the orchestrator finds a trigger I have missed, but none applies on the current evidence.

## 6. Dispositions of Remaining Findings (audit record)

| Finding | Disposition |
|---|---|
| Terminal→non-terminal raw PATCH rollback (D-2) | **Queued user decision** for Yuri at closeout: block, warn-and-allow, or allow with audit emphasis. Failing-test proposal retained as documentation. Not a sprint pause — the sprint does not depend on the answer. |
| 8 smoke-test failures (harness drift) | **Top follow-up candidate** for the next sprint (bounded harness-repair scope: mock `/graphql` practitioners + align smoke-mode network assertions). Audit-only this sprint. |
| Hardcoded `DIARY_URL`, popup consent, reason-code friction, date-picker, grid search, hover cards, icon-only button (A-1) | Recorded for future diary UX sprints; no action in S5. |
| D-2 minors/observations (pagination, `booked_via` validation, slots `datetime` param, `default_duration` naming, PUT-on-terminal, GET-side-effect commit) | Recorded; no action in S5. |
| D-1 minors (no `--check` mode on sync helper, etc.) | Recorded; no action in S5. |

## 7. Orchestrator Instructions (derived)

1. Run deterministic delta checks on this decision packet; proceed only if they pass.
2. Collect the D-1 disposable-worktree workspace receipt (fresh packet-scoped worktree from current `handoff/current`-lineage baseline), then dispatch `deepcode-s5-b1-diary-selection-preservation-repair.md` with the explicit `complete sprint task` release the parent plan requires for Phase B. No artifact wall-clock deadline (per the recorded S5 correction: progress observation over elapsed time); mailbox polling plus PTY completion event as observation posture.
3. Accept only the durable completion artifact; then dispatch the D-2 cross-review packet (D-2's existing lane may be reused if contextually coherent, else a fresh instance-2 session — still within the 2-lane count).
4. Run acceptance evidence items 3–4 orchestrator-side; verify items 1–2 and 5–6 from the artifact and diff.
5. On cross-review `pass`: integrate, mark packets, `record-integration`, update `orchestration/sprint_closeout.md` (including the queued Yuri policy decision from §6 and the continuation history for D-1 attempt 1), push `master` + `handoff/current`, realign mirrors from their own worktrees, `audit --fetch`, `retire-stale`, and close S5 with sprint-engine state `continuing`. The continuous sprint engine then hands back to the Conductor for the next sprint (the smoke-harness repair from §6 is the leading candidate scope, alongside the already-queued bounded cross-boundary Ariadne contract audit).
6. On cross-review `revision_required` or any stop condition of the parent plan: return to the Conductor; do not improvise.

The Conductor does not launch workers, integrate, commit, or push. This packet is the complete and final Phase A/B gate decision for S5: **exactly one repair (B-1, D-1-owned, selection preservation across silent refresh); all other findings close audit-only with the dispositions above.**
