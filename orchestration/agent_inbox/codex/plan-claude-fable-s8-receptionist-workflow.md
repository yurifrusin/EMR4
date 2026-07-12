# Conductor Plan — S8 Receptionist Workflow Implementation

| Field | Value |
|---|---|
| Sprint | S8 |
| Date | 2026-07-13 |
| Conductor | `claude-fable-conductor` (`claude-fable-5`, high reasoning) |
| Source packet | `orchestration/agent_inbox/claude/claude-fable-s8-receptionist-workflow-plan.md` |
| Settings fingerprint (verified this session) | `sha256:58313bbfd011f4eb70234fc320b1c0393f2a6a56dd537f329baacd830010cb24` |
| Direction dialogue disposition | `agreed_initial` |
| DeepSeek Flash lane count | 3 |
| Antigravity decision | using — consumer UX verification lane (A-2) |
| Independent LLM plan verifier | not risk-triggered (rationale in §9); deterministic plan checks still mandatory |

## 1. Conductor Workspace Receipt

- Target worktree: `C:\Users\sarashera\EMR4-worktrees\claude`
- Branch: `claude/current` (matches assigned agent)
- Preflight found the mirror stale at `763c4991` (S5 close). Realignment was
  executed from this worker worktree, not the integration checkout:
  `git fetch origin` + `git merge --ff-only origin/handoff/current`,
  fast-forward `763c4991 → e46a8594`.
- Post-realign state: clean tree, HEAD `e46a8594` == `origin/handoff/current`
  ("dispatch Fable S8 planning"). Local `claude/current` is ahead of
  `origin/claude/current` by the integrated commits; pushing the durable
  mirror is Sol's realign duty, not the Conductor's.
- Settings fingerprint recomputed from
  `orchestration/harness_settings/*.yaml` via
  `orchestration_harness/settings_fingerprint.py` logic and matches the
  packet value exactly.

Sol must collect an equivalent preflight receipt (worktree, branch,
cleanliness, relation to `handoff/current`, Context Health) from every worker
lane before packet dispatch, using the
`scripts/ariadne_orchestrator_preflight.py` receipt core. A missing, stale,
dirty, or mis-targeted receipt is `revision_required` before dispatch.

## 2. Direction Dialogue Disposition

Sol's advisory direction (return to substantial product work; S8 = diary
launch reliability + visible launch-failure handling first, with the
remaining S5 usability findings sequenced behind that tranche) is **accepted
as proposed** — disposition `agreed_initial`. The dialogue ends here; no
rejoinder is needed. The refinements below (lane structure, acceptance
criteria, internal ordering of the second tranche) are Conductor sequencing
inside the agreed direction, not a counterproposal. No allocation authority
was transferred: this final sprint definition and every worker assignment
below are authored by the Conductor.

Sol's two exclusions are ratified:

- The auto-refresh selection blocker (fixed in S5 B-1) and the eight diary
  smoke failures (fixed in S6, suite now 139/139) are **not** re-opened.
- Terminal-to-active status transition policy (block/warn/allow) remains an
  undelegated product decision for Yuri. S8 must not silently choose it, and
  its deferral must not block this sprint (see §10).

## 3. Sprint Definition and Boundary

**S8: Receptionist Workflow Implementation — diary launch reliability and
diary usability affordances.** First coherent product implementation sprint
after the S5 audit; frontend-only.

**Boundary (in scope):**

- `EMR4 Sidebar/src/taskpane/taskpane.js`, `taskpane.html`, `taskpane.css`
  (diary launch path only)
- `sync_taskpane.py` (patch-parity only, to preserve the documented
  cross-file invariant on the `BACKEND_URL` replace block at
  `sync_taskpane.py:22–35`)
- `docs/diary/diary.js`, `docs/diary/diary.html`, `docs/diary/diary.css`
- `review/` Playwright/pytest additions and cache-bust version bumps
  (`docs/taskpane/*` regeneration itself is Sol's integration step via
  `python sync_taskpane.py`)
- Worker packets, review artifacts, receipts, acceptance evidence, closeout
  docs under `orchestration/` and `docs/`

**Boundary (explicitly closed — no lane may open these):** provider /
live-provider wiring, database migrations or schema, deployment/production
authority beyond Sol's existing routine Pages-from-`master` integration duty,
external patient-facing clients, H15/H-series runtime imports, historical
diary trove material, memory/RAG/GraphRAG, Bernie D5 expansion, new
model-write authority, terminal-status policy semantics, backend route or
model changes of any kind.

Because this plan names those closed runtime/provider/trove surfaces, the
H68 proposal-surface guard requirement is satisfied here: before any future
sprint proposes such surfaces, Ariadne must run
`.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py`
and confirm `runtime_or_provider_wiring_ready=false`,
`raw_trove_access_ready=false`, `runtime_gate_decision=blocked`. S8 does not
propose those surfaces and does not require the gate to change.

## 4. Verified Code Facts (inspected this session at `e46a8594`)

1. `EMR4 Sidebar/src/taskpane/taskpane.js:1020` — `DIARY_URL` is a hardcoded
   constant pointing at the deployed GitHub Pages diary; no environment
   resolution exists (unlike `BACKEND_URL`, which is environment-aware and
   patched by `sync_taskpane.py`).
2. `taskpane.js:1025–1057` — `openDiary()` closes any prior dialog handle and
   synchronously reopens; failure handling is a single small status line
   (`setStatus("Could not open Diary: " + result.error.message)`) with no
   Office error-code mapping (12007 dialog-already-open, 12009 user declined,
   12011 popup blocked), no retry affordance, and no visible guidance.
3. `sync_taskpane.py:22–35` — the `.replace()` patch block breaks silently if
   the `BACKEND_URL` source text drifts. Any Lane 1 edit near that block must
   keep patch parity and prove it.
4. `docs/diary/diary.html:9–10` — `diary.css?v=135`, `diary.js?v=183`.
   `scripts/check_frontend_versions.py` enforces version discipline.
5. `docs/diary/diary.js:6969–7003, 7040–7044, 7098–7101` — the
   `booking-status-reason-code-container` is hidden by default and revealed
   only after status change events; `saveBooking()` (`:7693`) rejects a
   missing reason code only at save time. `TERMINAL_STATUSES` lives at
   `:7490` and `:8605`. This matches the S5 A-1 [High] validation-friction
   finding.
6. `docs/diary/diary.js:6749–6760` — the calendar affordance depends on
   `input.showPicker()` with a `.click()` fallback that cannot work because
   `#diary-date-picker` is `opacity:0; pointer-events:none`
   (`diary.css:175`). Matches A-1 [Medium] webview-compatibility finding.
7. `docs/diary/diary.html` has no grid-level search/filter input; the only
   search box is the booking-modal patient search (`:178–181`). Matches A-1
   [Medium].
8. Appointment reasons/notes require opening the edit modal or depend on
   card height. Matches A-1 [Medium].
9. `review/harness.py` provides `serve_dir(DOCS_DIR)` and `stub_office(page)`
   (routes `**/office.js`), so bounded Playwright coverage of the taskpane
   launch path is feasible without Word.
10. Baseline signal: `review/test_diary_smoke.py` = 139 passed (S6);
    `review/test_diary_selection_preservation.py` = 3 passed (S5 B-1).

## 5. Worker Allocation

All allocations are from the committed worker pool
(`orchestration/harness_settings/worker_pool.yaml`) and are Conductor-final.

| Lane | Resource | Model/Reasoning | Role class | Transport |
|---|---|---|---|---|
| W1 | `deepseek-flash-workers` (instance 1 of 3) | `deepseek-v4-flash` / high | implementation owner | Deep Code `deepcode -p <packet>`, real TTY via PTY adapter, disposable packet-scoped worktree |
| W2 | `deepseek-flash-workers` (instance 2 of 3) | `deepseek-v4-flash` / high | implementation owner | same |
| W3 | `deepseek-flash-workers` (instance 3 of 3) | `deepseek-v4-flash` / high | independent review / veto | same, review mode, clean candidate-containing worktree |
| A-2 | `antigravity-gemini-flash-3-5-worker` | `gemini-flash-3.5` / medium | consumer/product review / veto | `agy.exe --add-dir <antigravity worktree> --print`, durable artifact required |
| Orchestrator | `openai-primary-orchestrator` | `gpt-sol` / high | execution, acceptance, integration | protected session |
| Conductor | `claude-fable-conductor` | `claude-fable-5` / high | this plan; re-entry per §11 | Claude CLI |

DeepSeek lane count is 3 — within the declared one-to-three cap. No fourth
DeepSeek lane exists in any fallback path (S4d lesson). Escalation of any
Deep Code lane to `deepseek-v4-pro` or `max` reasoning requires a recorded
leverage reason per `deepcode_model_profile.yaml`; none is pre-authorized.
Deep Code permission prompts are not authority; durable packet artifacts plus
PTY receipts are the only accepted worker results.

### W1 — Taskpane diary-launch reliability and visible failure handling

**Mission.** Make the diary launch work correctly across local dev, ngrok,
and deployed Pages environments, and make launch failure visible and
actionable.

**Owned files (exclusive):**
`EMR4 Sidebar/src/taskpane/taskpane.js`,
`EMR4 Sidebar/src/taskpane/taskpane.html`,
`EMR4 Sidebar/src/taskpane/taskpane.css`,
`sync_taskpane.py`,
new test file `review/test_taskpane_diary_launch.py`.

**Required behavior:**

1. Replace the hardcoded `DIARY_URL` constant with a pure, unit-testable
   resolver (e.g. `resolveDiaryUrl(location)`) mirroring the `BACKEND_URL`
   environment pattern: dev-server origin (port 3000) resolves to a
   documented local diary URL; ngrok/Pages hosts resolve to the deployed
   Pages diary. The resolver must default safely to the current deployed URL
   so production behavior is unchanged when the environment is unrecognized.
   Local diary *hosting* mechanics (e.g. `run_dev.ps1` serving `docs/`) are
   out of scope for S8 — record as follow-up if resolution alone is
   insufficient for local iteration (§12).
2. Map `displayDialogAsync` failure codes to distinct, receptionist-readable
   messages with recovery guidance: 12007 (dialog already open — auto-retry
   once after the close event instead of failing), 12009 (user declined the
   Office new-window prompt — explain the Allow prompt), 12011 (popup
   blocked — explain enabling popups for this site), and a generic fallback
   including the raw message. The failure surface must be clearly visible in
   the taskpane (not only the small status line) and must offer a retry
   affordance.
3. Harden the close-then-reopen path in `openDiary()` so reopening after a
   stale handle cannot race into an unhandled 12007.
4. Preserve `sync_taskpane.py` patch parity: if the `BACKEND_URL` block or
   its surrounding text changes, update the `.replace()` source/target pair
   in the same commit and prove the patched `docs/taskpane/taskpane.js`
   output still resolves correctly. If the diary resolver needs a
   Pages-specific patch, add it to `sync_taskpane.py` explicitly.
5. Bump the taskpane cache-bust `?v=N` in `taskpane.html`.
6. Do not touch `openCommandCentre()` behavior beyond shared helpers that W1
   proves are behavior-preserving for it.

**Acceptance evidence:** new `review/test_taskpane_diary_launch.py`
(harness `serve_dir` + `stub_office` pattern; failing-first where practical)
covering URL resolution per environment, error-code→message mapping, retry
affordance, and 12007 auto-retry; `node --check` on source and patched
taskpane.js; `sync_taskpane.py` run output showing the patch applied; all
existing review suites unchanged-passing.

**Packet:** `orchestration/agent_inbox/deepcode/deepcode-s8-w1-diary-launch-reliability.md`
**Result artifact:** `orchestration/agent_inbox/codex/review-deepseek-s8-w1-launch-reliability.md`
**PTY receipt:** `orchestration/deepcode_pty/s8-w1-receipt.json`

### W2 — Diary usability affordances (sequenced S5 A-1 findings)

**Mission.** Implement the four remaining S5 usability findings inside
`docs/diary/`, in this priority order, as one lane with internal checkpoints:

1. **Terminal-status reason-code affordance** [A-1 High]. When a
   reason-requiring status (`Cancelled`, `NoShow`, `DNA`) is selected in the
   booking modal, reveal and highlight the
   `booking-status-reason-code-container` immediately, with inline
   validation and focused recovery before `saveBooking()` — the save-time
   error remains as backstop, never the first signal. The signed
   proposal/confirm network flow and payload shape must not change.
2. **Date-picker fallback** [A-1 Medium]. Feature-detect `showPicker()`; when
   unavailable, fall back to a usable, accessible date input (e.g. making the
   input visible and interactive) with no external dependencies. Keyboard
   accessible.
3. **Same-day search/filter** [A-1 Medium]. A header text input that filters
   or highlights already-rendered appointments client-side (patient name /
   provisional name / reason). No new network calls. Must survive the silent
   60-second refresh without stealing focus or resetting the query, and must
   not interfere with `.appt-active` selection preservation.
4. **Read-only reason/notes access** [A-1 Medium]. A hover/long-press preview
   card exposing full reason/notes (data already present in the appointment
   payload) without opening the edit modal. Read-only; no mutation
   affordances on the card.

**Owned files (exclusive):** `docs/diary/diary.js`, `docs/diary/diary.html`,
`docs/diary/diary.css`; new focused test files
`review/test_diary_reason_code_affordance.py`,
`review/test_diary_date_picker_fallback.py`,
`review/test_diary_day_search.py`,
`review/test_diary_note_preview.py` (or a justified consolidation).

**Hard constraints:** diary.js cache key v183 → v184 (css v135 → v136 if
touched); the 139-test `review/test_diary_smoke.py` baseline and the 3-test
selection-preservation suite must remain fully passing; no change to
terminal→active transition semantics, raw PATCH behavior, GraphQL/REST
switching, or signed-confirm evidence contracts; the [Low] icon-only diary
button finding is *not* in scope (deferred, §12).

**Acceptance evidence:** the four focused test files passing (failing-first
where practical), full existing review suite passing under Sol's own
authoritative collection, `node --check docs/diary/diary.js`,
`scripts/check_frontend_versions.py` passing with the bumps.

**Packet:** `orchestration/agent_inbox/deepcode/deepcode-s8-w2-diary-usability-affordances.md`
**Result artifact:** `orchestration/agent_inbox/codex/review-deepseek-s8-w2-diary-affordances.md`
**PTY receipt:** `orchestration/deepcode_pty/s8-w2-receipt.json`

W1 and W2 file ownership is fully disjoint (taskpane+sync vs `docs/diary/`;
distinct new test files), so they may run in parallel at Sol's discretion.

### W3 — Independent review lane (veto surface)

**Mission.** Independent static + test-evidence review of each candidate
(W1, then W2; two artifacts), in a clean candidate-containing worktree, in
review mode. Checks: scope adherence to this plan, closed-gate compliance,
cross-file invariants (`sync_taskpane.py` patch parity, cache-bust bumps,
`PROTECTED_SECTIONS` untouched), test honesty (counts match Sol's
authoritative collection), and Word Online strictness risks. Each artifact
must end with canonical `DECISION: pass` or `DECISION: revision_required`.

**Owned artifacts (no code ownership, no edits):**
`orchestration/agent_inbox/codex/review-deepseek-s8-w1-independent-review.md`,
`orchestration/agent_inbox/codex/review-deepseek-s8-w2-independent-review.md`;
receipts `orchestration/deepcode_pty/s8-w3-*-receipt.json`.

**S7 executable gate is mandatory:** Sol may accept a W3 review only through
`scripts/ariadne_review_acceptance.py` (worktree, branch, candidate
ancestry, decision marker, receipt shape, artifact identity, process
cleanup, review mode, authoritative pytest collection). Persist each
decision under `orchestration/harness_evidence/s8-w{1,2}-review-acceptance.json`.
Scratch output cannot substitute for the declared artifact or receipt
(S6 lesson; enforced by the gate).

### A-2 — Antigravity consumer UX verification (veto surface)

**Mission.** Read-only re-verification of the S5 A-1 findings against the
integrated S8 candidates, by the platform that authored them. For each of
the six S5 findings addressed or deferred by S8 (launch URL, launch-failure
UX, reason-code affordance, date-picker, search, note access), record
`resolved | partially_resolved | unresolved` with evidence, plus an explicit
overall verdict (`go | conditional_go | no_go`) on receptionist readiness of
the S8 scope. No code edits; no PHI/`local_data`; artifact on disk is
authoritative over CLI stdout.

**Timing:** after both W1 and W2 candidates pass W3 review and are
checkpointed, from a realigned clean `antigravity/current` worktree.

**Packet:** `orchestration/agent_inbox/antigravity/antigravity-s8-a2-ux-verification.md`
**Result artifact:** `orchestration/agent_inbox/codex/review-antigravity-s8-ux-verification.md`

**Distinct value:** cross-provider product veto from the original findings'
author — the only non-DeepSeek review surface in this sprint.

## 6. Independence Labels

- W1, W2: implementation owners, disjoint file ownership.
- W3: independent review — same provider as W1/W2 (DeepSeek). This is
  **reduced independence** and is recorded as such; it is mitigated by (a)
  the deterministic S7 acceptance gate on every review, (b) Sol's own
  authoritative test collection, and (c) the cross-provider A-2 lane.
- A-2: independent consumer review, distinct provider (Gemini via
  Antigravity), read-only, veto surface.
- No lane was allocated to fill a slot: each has a distinct artifact or veto
  surface named above. No native Codex subagent lanes are needed.

## 7. Verification Plan (Sol-run, authoritative)

Per accepted candidate and at closeout:

1. `pytest review/test_diary_smoke.py -q` → 139 passed, exit 0 (baseline).
2. `pytest review/test_diary_selection_preservation.py -q` → 3 passed.
3. `pytest review/test_diary_graphql_practitioner_switch.py review/test_diary_deprecation_consumer.py review/test_raw_status_terminal_rollback_guard.py -q` → passing.
4. New S8 focused suites (W1: launch; W2: four affordance files) → passing;
   failing-first evidence preferred where recorded by the lanes.
5. `node --check docs/diary/diary.js`; `node --check` on both taskpane.js
   copies (source and `sync_taskpane.py` output).
6. `scripts/check_frontend_versions.py` → passing with v184 (and v136 if css
   touched) plus the taskpane `?v=N` bump.
7. `git diff --check` clean; `python sync_taskpane.py` run at integration and
   its patched output committed.
8. S7 gate acceptance JSONs persisted for both W3 reviews.
9. The known non-clean full-project `pytest tests -q` environment signal is
   pre-existing and out of scope; it must not be claimed as passing and must
   not be "fixed" by any S8 lane.

Word Online remains the primary target: any W1/W2 rendering-affecting change
must respect the standing strictness constraints (no reliance on
Desktop-tolerated behavior); W3 review explicitly checks for this.

## 8. Fallbacks and Reduced-Independence Handling

- **Conductor:** Fable first; Opus (medium) only on a real provider-reported
  Claude usage/window limit or genuine unavailability; then
  `deepseek-pro-conductor-fallback` (Deep Code); then a distinct spawned GPT
  Sol subagent. Estimated dollar cost is not an availability signal; no
  `--max-budget-usd`. No monetary or wall-clock caps are active.
- **DeepSeek lane failure:** same-lane retry/revision owned by Sol
  (Orchestrator execution duty; no Conductor re-entry). Failed candidates may
  be adopted only under the recovery lease
  (`docs/ariadne-orchestrator-recovery-lease.md`); this sprint's surfaces are
  the low-risk docs/tests/frontend class → deterministic tests plus diff
  review suffice for recovery verification.
- **Deep Code non-TTY refusal** is adapter evidence, not DeepSeek
  unavailability; repair transport and retry the same lane.
- **Antigravity unavailable/quota-capped/silent without durable artifact:**
  A-2 stands down with the reason recorded in the closeout. Do **not** spawn
  a substitute DeepSeek lane (the three-lane cap is already reached); Sol
  covers the UX verdict with deterministic Playwright evidence plus the W3
  artifacts, and the closeout records the reduced cross-provider
  independence. This is the recorded no-substitution rationale required by
  protocol.
- **W3 review rejected by the S7 gate:** revision returns to W3 (or the
  implementing lane, if the defect is in the candidate); an invalid review is
  quarantined, never acceptance evidence (S6 precedent).

## 9. Verifier Posture

Deterministic plan checks (`sprint_worker_policy.yaml`) run as always.
Independent LLM plan verification is **not risk-triggered**: no new
security/write/deployment/release authority is opened; there is no
Conductor–Orchestrator disagreement (`agreed_initial`); the mandate boundary
is unambiguous; allocation is within declared limits (3 Flash lanes, 1
Antigravity); prior S6 drift signals were remediated by the S7 executable
gate, which this plan mandates for all worker-review acceptance. If Sol
disputes executability, the operating model's single bounded challenge
applies before execution.

## 10. Closed Gates and User Decision Boundary

All gates listed in §3 remain closed; no lane may open one without a
separately justified boundary decision escalated to the Conductor and, where
material, to Yuri.

The single genuine user decision boundary carried by S8 is unchanged from
S5: **terminal→active appointment-status transition policy (block / warn /
allow)**. It is deferred to Yuri, is not blocking, and no S8 lane may
implement any variant of it. The [Low] icon-only diary-button labeling
finding is deferred as a recorded unfilled obligation, not silently dropped.

## 11. Execution, Checkpoints, and Conductor Re-entry

Sol owns execution end-to-end within this verified plan: dispatch order
(W1 ∥ W2 → W3 per candidate → integrate → A-2 → closeout), waiting,
same-lane retries, transport recovery, test command selection, disposable
worktree lifecycle, integration, Pages deploy from `master`, and mirror
realignment.

Commit/push checkpoints (advance `handoff/current` after each accepted
checkpoint): (1) accepted W1 candidate + gate-accepted W3 review; (2)
accepted W2 candidate + gate-accepted W3 review; (3) A-2 artifact
integration; (4) sprint closeout doc + protocol/status updates. Workers
never push `master`.

Conductor re-entry only for: material scope change (e.g. a fix demands
backend or schema work), worker assignment/ownership change, acceptance
criteria change, or S8 closure and S9 planning. Ordinary failure handling
per `autonomous_continuation.yaml` continues without user permission.

## 12. Unfilled Obligations (recorded, not silently dropped)

1. Terminal→active status policy — Yuri decision, deferred (§10).
2. [Low] diary-button labeling/onboarding tooltip — deferred to a later UX
   polish sprint or S9 A-lane.
3. Local diary *hosting* in `run_dev.ps1` (serving `docs/diary/` locally) —
   follow-up if W1's URL resolution alone proves insufficient for local
   iteration; out of S8 scope.
4. Full-project `pytest tests -q` environment/readiness failures —
   pre-existing, out of scope, not claimed as passing.
5. Dependabot alert 5 (dev-only Microsoft toolkit transitives) — remains
   open per standing instruction; no forced overrides.

STATUS: complete
