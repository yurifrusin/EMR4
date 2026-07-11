# Conductor Sprint Plan — S5: EMR4 Receptionist Appointment Workflow Audit

| Field | Value |
|---|---|
| Plan ID | plan-claude-fable-emr4-receptionist-workflow-audit |
| Sprint ID | S5 |
| Role | conductor |
| Conductor resource | `claude-fable-conductor` (Claude Fable, high reasoning, this session) |
| Date | 2026-07-11 |
| Status | awaiting_verifier |
| Settings fingerprint | `sha256:6d5a113aa1c0f418f402032b7503c6a0478e71a05fe6c18f093c91ef95831b78` (recomputed this session via `orchestration_harness.settings_fingerprint` over `orchestration/harness_settings/`; matches AGENTS.md) |
| direction_dialogue_disposition | `agreed_initial` |

## 1. Direction Dialogue Record

The protected orchestrator (GPT Sol, `openai-primary-orchestrator`) supplied an
advisory direction proposal: return to genuine EMR4 product work with a bounded
end-to-end receptionist appointment workflow audit from the Word taskpane
through the real local backend, permitting at most one concrete repair only if
the audit demonstrates a material functional or usability defect, while keeping
Bernie D5, provider/live-provider wiring, memory/RAG/GraphRAG, historical diary
runtime, broader GraphQL, deployment/production readiness, external clients,
and any new write authority closed.

The Conductor **accepts the initial proposal without counter**. It matches the
recorded next-recommended-work in AGENTS.md, targets the highest-value product
surface (the diary/receptionist workflow that Phase 2 and Bernie both depend
on), and opens no closed gate. Per `direction_collaboration.yaml`, agreement
ends the dialogue immediately; no rejoinder occurred. No allocation authority
was transferred: the proposal contained direction only, and every assignment
below is authored solely by the Conductor.

## 2. Boundary

**Sprint kind:** product evidence/audit sprint (feature-adjacent, read-heavy)
with one optional bounded repair.

**In scope:**

- End-to-end audit of the receptionist appointment workflow as it exists
  today: taskpane diary entry point (`EMR4 Sidebar/src/taskpane/`), native
  diary grid (`docs/diary/`), appointments/diary/proposal API
  (`app/routers/appointments*.py`, `app/routers/diary.py`,
  `app/schemas/appointments.py`), against the real **local dev backend**
  (`run_dev.ps1` stack or `uvicorn` + local Postgres, seeded dummy data,
  `dr.shera@emr4dev.local` only — no PHI, no production services).
- Deterministic evidence via existing harnesses: `pytest tests -q`,
  `pytest review/test_diary_smoke.py`, `node --check` on diary/taskpane JS,
  targeted route-intercepted Playwright checks.
- Findings packets with severity classification (material functional defect /
  material usability defect / minor / observation).
- **At most one** concrete repair, only if the audit demonstrates a material
  functional or usability defect, on the lane that owns that surface, behind
  the normal plan gate (§5, Phase B).

**Out of scope (closed gates — any packet touching these is a protocol
violation and a stop condition):**

- Bernie D5; provider or live-provider wiring; memory/RAG/GraphRAG; historical
  diary trove runtime access, H15/H-series runtime imports, or `local_data`
  reads; broader GraphQL; deployment/production readiness or Pages/Cloud Run
  changes; external clients (booking portal, kiosk, SMS); any **new write
  authority** (no new mutating endpoints, no bypass of proposal/confirm
  patterns, no schema migrations).
- H56 remains binding: no worker may propose interpretation-harness runtime,
  provider, or trove wiring; the readiness command posture stays blocked.
- No writes to `master` or `handoff/current` by any non-orchestrator role.

## 3. Assignments (Conductor-authored allocation)

| Lane | Resource | Model / reasoning | Role class | Ownership boundary (disjoint) | Expected artifact |
|---|---|---|---|---|---|
| D-1 workflow audit | `deepseek-flash-workers` (instance 1) | `deepseek-v4-flash` / high | implementation owner (audit) | Frontend workflow trace: `EMR4 Sidebar/src/taskpane/`, `docs/diary/`, `docs/taskpane/` (read/audit); owns `orchestration/agent_inbox/codex/review-deepseek-s5-workflow-audit.md` | Durable Deep Code audit packet: step-by-step workflow trace taskpane → diary → API with classified findings and reproduction steps |
| D-2 backend contract audit | `deepseek-flash-workers` (instance 2) | `deepseek-v4-flash` / high | independent review / test engineering | Backend: `app/routers/appointments*.py`, `app/routers/diary.py`, `app/schemas/appointments.py`, `tests/`, `review/` (read/audit + failing-test proposals only); owns `orchestration/agent_inbox/codex/review-deepseek-s5-backend-audit.md` | Durable Deep Code packet: contract/conflict/slot/proposal audit, harness run evidence, failing-test proposals for any defect |
| A-1 usability veto | `antigravity-gemini-flash-3-5-worker` | `gemini-flash-3.5` / medium | consumer/product review (veto surface) | Receptionist-usability critique of the live local diary/taskpane workflow; owns `orchestration/agent_inbox/codex/review-antigravity-s5-usability.md`; no code edits | Durable repo artifact (CLI stdout is not proof): usability findings ranked by receptionist impact, explicit go/no-go on workflow usability |
| V-1 verifier | `deepseek-flash-verifier` | `deepseek-v4-flash` / high | plan verification | This plan packet only | Durable Deep Code verifier artifact `orchestration/agent_inbox/codex/review-deepcode-s5-plan.md` returning `DECISION: pass` or `revision_required` |
| Orchestrator | `openai-primary-orchestrator` | `gpt-sol` / high | dispatch, acceptance gate, integration | Packet dispatch, verification runs, integration to `master`/`handoff/current` | Integration log entry + sprint closeout |

- `deepseek_lane_count`: **2** (within the declared 1–3 cap; a third instance
  is reserved for the declared fallback only, never a fourth).
- `antigravity_decision`: **use** — the audit's usability half gives Gemini a
  distinct veto surface no DeepSeek lane duplicates. Transport quirk applies:
  require the committed artifact, verify via `poll --fetch`/git, not stdout.
- Antigravity platform use: Gemini Flash 3.5 via
  `agy.exe --add-dir C:\Users\sarashera\EMR4-worktrees\antigravity --print`.
- Deep Code transport: `deepcode -p <packet>` in a real interactive TTY,
  packet-scoped disposable worktrees, durable packet artifact is the only
  accepted result; permission prompts are not authority; PTY adapter answers
  no prompts.
- **Repair allocation (conditional, Phase B):** if and only if the
  orchestrator-accepted audit demonstrates a material functional or usability
  defect, the Conductor pre-authorizes **one** bounded repair packet on the
  lane that owns the defect's surface (D-1 for frontend, D-2 for
  backend/tests). One repair total, plan-gated, verified by the other lane's
  review plus harness runs, no boundary from §2 may be opened by the repair.
  Two or more defects: the Conductor selects the single highest-impact one;
  the orchestrator may not choose or substitute.

## 4. Independence Labels & Reduced Independence

- D-1 vs D-2: independent (disjoint file/review ownership, separate packets,
  separate Deep Code sessions).
- A-1: independent consumer lane; no code ownership, so no overlap risk.
- Verifier V-1 shares the DeepSeek API account with D-1/D-2
  (`quota_scope: api_budget`) — **reduced independence: shared provider
  account**, mitigated by separate packets and the orchestrator acceptance
  gate. All worker worktrees are `lower_assurance_local_mode` (shared-user
  local worktrees, not sandboxed patch delivery); acceptable for a read-heavy
  audit with at most one gated repair.
- If the repair fires, the repairing lane loses audit-independence for that
  finding; the cross-review by the other DeepSeek lane restores an
  independent check.

## 5. Execution Phases & Plan Gate

- **Phase A (audit, parallel):** orchestrator dispatches D-1, D-2, A-1
  packets after verifier pass and workspace receipts. Workers audit and
  submit durable packets via the standard `submit --task` path. No project
  code edits in Phase A beyond packet/coordination files.
- **Gate:** Conductor reviews accepted findings and either declares
  `no material defect — sprint closes audit-only` or names the single repair
  target. Explicit `complete sprint task` release required before Phase B.
- **Phase B (optional single repair):** one bounded repair on the owning
  lane, cross-reviewed, harness-verified, then normal orchestrator
  integration.

## 6. Verification Plan

- Verifier V-1 checks this packet against `orchestration/harness_settings/`
  per `sprint_worker_policy.yaml` `verifier_checks` (fingerprint match,
  conductor authorship, no allocation-authority transfer, lane caps 1–3,
  distinct artifacts, capability eligibility, explicit fallbacks, no
  orchestrator substitution, receipts).
- Audit evidence must include: `pytest tests -q` result,
  `pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q`
  result, `node --check docs/diary/diary.js` (and taskpane JS), and for any
  claimed defect a concrete reproduction (request/response transcript or
  Playwright assertion), all against the local dev stack only.
- Phase B repair (if any) additionally requires: failing test or scripted
  reproduction before the fix, passing after; cross-lane review packet; no
  diff outside the owning boundary; cache-bust/`sync_taskpane.py` discipline
  if taskpane files change.

## 7. Acceptance Evidence (sprint closes when)

1. Verifier artifact `DECISION: pass` on this plan.
2. Three durable worker packets (D-1, D-2, A-1) submitted and visible via
   `poll --fetch`, each with classified findings or an explicit clean result.
3. Harness runs recorded with results in the closeout.
4. Either a recorded `no material defect` disposition, or exactly one
   integrated repair with before/after evidence and cross-review.
5. Orchestrator closeout in `orchestration/sprint_closeout.md` +
   `record-integration`, mirrors realigned, audit run.

## 8. Stop Conditions

- Verifier returns `revision_required` → plan returns to the Conductor; the
  orchestrator must not improvise.
- Any packet proposes touching a §2 closed gate → halt that lane, revise.
- More than one repair, or a repair without a demonstrated material defect →
  halt; Conductor decision required.
- A worker cannot produce a valid workspace receipt, or a Deep Code lane has
  no real TTY (adapter evidence, not DeepSeek unavailability) → revise
  transport, do not substitute silently.
- Local dev stack cannot be brought up with seeded dummy data → pause; audit
  against a dead backend is not acceptance evidence.
- Any PHI-bearing or `local_data` content appears in a packet → immediate
  halt and user notification.

## 9. Fallback Reasons

- Conductor: Fable → Opus (`claude-opus-conductor`) only on Fable
  usage/availability failure → distinct spawned GPT Sol subagent
  (`gpt-sol-conductor-fallback`, no integration authority). The protected
  orchestrator session may never fill this role.
- Antigravity quota-capped/silent without a durable artifact → stand down
  A-1 and substitute **one** additional `deepseek-flash-workers` lane (D-3,
  usability-consumer review, distinct packet), staying within the 3-lane cap.
  This is the only pre-authorized third lane; no fourth lane exists.
- A DeepSeek worker lane fails/expires → orchestrator reports; Conductor
  replans (recovery-lease rules per
  `docs/ariadne-orchestrator-recovery-lease.md` apply to any adopted partial
  output).

## 10. Unfilled Obligations

- No security-specific lane: acceptable because the sprint adds no new write
  authority or endpoints; D-2's contract audit covers auth-gating regressions
  via existing tests. Recorded as a conscious gap.
- High-assurance brokered-patch isolation is not yet implemented; all lanes
  run `lower_assurance_local_mode` as declared in §4.

## 11. Workspace Receipts

**Conductor receipt (this session, generated pre-plan):**

| Field | Value |
|---|---|
| Target worktree | `C:\Users\sarashera\EMR4-worktrees\claude` |
| Expected branch | `claude/current` — confirmed (`## claude/current...origin/claude/current [ahead 1]`) |
| Cleanliness | clean (no modified/untracked tracked-code files at plan time) |
| Relation to `handoff/current` | `handoff/current` (`9c5d28a1`) is an ancestor of HEAD (`100fd944`); divergence is 14 committed Ariadne harness commits — expected, recorded, no realignment required |
| Realignment | none performed; none required |
| Settings fingerprint | recomputed and matching (see header) |

**Worker receipts (required before dispatch, orchestrator-collected):** each of
D-1, D-2, A-1 must supply target worktree, expected branch
(packet-scoped disposable worktree for Deep Code lanes;
`antigravity/current` for A-1), cleanliness, relation to `handoff/current`,
and any realignment executed **from that worker worktree**. A missing, stale,
dirty, or mis-targeted receipt is `revision_required` before that packet is
read. Context Health rules apply at new-session/post-compaction continuation
points per `orchestration_harness/orchestrator_preflight.py`.

## 12. Integration Instructions (orchestrator-only)

1. Run the verifier (V-1) on this packet; proceed only on `DECISION: pass`.
2. Collect worker receipts, clean stale artifacts from the Claude/Antigravity
   worktrees per protocol, report DeepSeek lane count/reuse, then dispatch
   the three Phase A packets with `HANDIN READY` naming lanes, channels, and
   cleanliness.
3. Accept only durable packet artifacts via `poll --fetch`; stdout and TUI
   output are not results.
4. Return findings to the Conductor for the Phase A/B gate decision; do not
   select or scope the repair yourself.
5. After Phase B (if any): integrate, mark packets, `record-integration`,
   update `orchestration/sprint_closeout.md`, push `master` +
   `handoff/current`, realign mirrors from their own worktrees, `audit
   --fetch`, `retire-stale`, and send the closeout with sprint-engine state
   and strategic placement (Phase 2 diary/receptionist track; audit/evidence
   sprint preceding diary interactivity and Bernie 2B).

The Conductor does not launch workers, integrate, commit, or push. This packet
is the complete and final sprint definition and allocation for S5.

## 13. Conductor Authorship & Provenance Record

A pre-existing **untracked** draft of this packet was found at this path during
the Conductor session of 2026-07-11 (no commit in history adds this file; it
did not appear in the session-start status snapshot). Per provenance-preserving
recovery principles, the Fable Conductor (`claude-fable-conductor`, this
session) adopted that draft as an **untrusted candidate** and independently
re-verified every factual claim before ratification:

- Settings fingerprint recomputed via `orchestration_harness.settings_fingerprint`:
  `sha256:6d5a113aa1c0f418f402032b7503c6a0478e71a05fe6c18f093c91ef95831b78` — matches.
- Workspace receipt re-measured: branch `claude/current`, clean, ahead 1 of
  origin, HEAD `100fd944`, `handoff/current` (`9c5d28a1`) is an ancestor,
  divergence exactly 14 commits — all match the packet's claims.
- The allocation (2 DeepSeek Flash audit lanes within the 1–3 cap, Antigravity
  usability veto lane, DeepSeek Flash verifier, single pre-authorized
  conditional repair, single pre-authorized third-lane substitution) matches
  the allocation this Conductor independently formed from
  `orchestration/harness_settings/` before discovering the draft.
- Direction dialogue disposition independently determined this session:
  `agreed_initial` — the Conductor accepted GPT Sol's advisory proposal
  without counter; no rejoinder occurred; no allocation authority transferred.

The Conductor owns every statement in this packet as its own final sprint
definition and allocation. The verifier should treat the untracked-draft
provenance as a flagged anomaly for the orchestrator to note at dispatch, but
authorship responsibility rests with `claude-fable-conductor` as of this
ratification. This amendment is the only change made to the adopted draft.
