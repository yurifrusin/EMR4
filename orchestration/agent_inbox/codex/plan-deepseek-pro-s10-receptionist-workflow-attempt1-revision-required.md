# DeepSeek Pro Conductor — S10 Receptionist Workflow Chain Harness

Role: routine Conductor
Resource: `deepseek-pro-conductor-fallback`
Model: `deepseek-v4-pro` / high
Artifact: `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow.md`
Schema: `ariadne.sprint_worker_policy.v1` conductor plan

# Boundary

S10 is a single bounded sprint inside the approved S9-S12 operational-hardening
tranche. The sprint scope is **one provider-free, route-free, DB-free, in-memory
receptionist workflow chain harness** layered on the existing H40-H68
interpretation harness.

The harness accepts authored synthetic multi-step receptionist utterance
sequences, resolves each step through the existing interpretation harness,
projects each step to a fake-provider frame through the existing frame-projection
path, and carries an in-memory workflow context between steps (resolved patient
descriptor, practitioner descriptor, time window, accumulated action intent,
preceding frame kind, refusal/planned propagation state). It classifies the
completed chain's end-to-end readiness and emits a safe aggregate workflow-chain
report.

This is the missing bridge between single-utterance interpretation (H40-H68) and
multi-step receptionist workflow evidence. It is not runtime route dispatch,
provider wiring, database access, H15/H-series, historical diary trove,
memory/RAG/GraphRAG, or write authority.

## Closed Gates (unchanged)

- Provider/live-provider wiring, live calls, provider prompt/dry-run
- Database/schema access, appointment/audit writes, migration
- External patient client
- H15/H-series runtime imports
- Historical diary trove access or raw file processing
- Memory/RAG/GraphRAG
- New model-write gates
- Deployment, production, release
- Protected-master authority, `handoff/current` advancement
- Terminal-to-active appointment status policy (user-owned; not chosen, inferred,
  or implemented)

## Open Gates (current sprint only)

- Provider-free interpretation harness (already open through H40-H68)
- Authored synthetic workflow fixtures (new; provider-free)
- Deterministic chain-level invariant tests (new; provider-free)
- Safe aggregate workflow-chain report (new; provider-free)
- Orchestration plan/review/test artifacts only

# Direction Dialogue Disposition

No direction collaboration was triggered for this sprint. The S9 closeout
recorded the next recommended work as "DeepSeek 4 Pro/high must define and
allocate S10 end-to-end receptionist workflow work through the detached real-PTY
path." The S5 and S8 receptionist workflow closeouts confirmed the frontend and
backend workflow surface and recorded the remaining boundaries. No dispute or
ambiguity required a GPT Sol direction proposal or rejoinder cycle. The
Conductor defined and allocated S10 directly.

# Inspected Evidence

## S8 Receptionist Workflow Closeout
- `docs/emr4-s8-receptionist-workflow-closeout.md`: S8 completed the Conditional
  Go receptionist workflow tranche. Terminal-to-active policy remains user-owned.
  Provider, database/schema, deployment/production, external patient client,
  H15/H-series, historical diary, memory/RAG/GraphRAG, and new model-write gates
  remain closed.

## S5 Receptionist Workflow Audit Closeout
- `docs/emr4-s5-receptionist-workflow-audit-closeout.md`: S5 exercised the Word
  taskpane-to-diary workflow. Deferred terminal-status and diary-smoke findings
  are preserved and not reopened.

## Interpretation Harness (H40-H68)
- `app/services/bernie/interpretation_harness.py`: 44 authored synthetic utterance
  fixtures, 7 dispatch types, projected to 4 frame kinds (proposal, read_request,
  clarify, refusal).
- `tests/fixtures/bernie_interpretation_harness/`: 5 fixture files covering
  authored utterances, adversarial utterances, clarification cases, receptionist
  phrases, and projected-frame contracts.
- Safe aggregate report: `scripts/bernie_interpretation_harness_report.py`
  confirms 44 cases, 7 contracts, 7 dispatches, 4 frame kinds.

## Readiness Gate Check
- Runtime gate: `blocked` (all scope values false, sprint engine continuing)
- Provider-boundary: `default_provider=disabled`, all runtime/provider/trove
  flags false
- Readiness snapshot: matches committed blocked status (44 cases, 7 contracts,
  7 dispatches, 4 frame kinds, `runtime_or_provider_wiring_ready=false`,
  `raw_trove_access_ready=false`, `runtime_gate_decision=blocked`)

## Action Grammar and Route Contracts
- `app/services/diary/action_grammar.py`: 11 verbs (5 implemented mutating, 3
  planned-not-implemented, 2 read-only, 1 meta)
- `app/services/diary/action_route_contract.py`: every verb mapped to current
  backend route authority; implemented confirm verbs map to existing
  `DiaryConfirmAction` endpoints

## Current Harness Gap
The interpretation harness is single-step: utterance → interpret → project
frame. A real receptionist workflow is multi-step with accumulating context.
Example: "I need to book Margaret Thompson" → clarify which Margaret →
"Margaret Thompson, 45, of 12 Smith St" → slot_search/read_request → "today
after 2pm with Dr Shera" → slot_search/read_request with enriched context →
"yes, book the 2:15" → create/proposal. The single-step harness cannot chain
these or carry patient/time/practitioner/action context between steps. This is
the gap S10 fills.

# Assignments

## Antigravity Decision

**Not used.** Antigravity has no distinct artifact or veto surface in S10. The
sprint produces only provider-free backend harness code, authored synthetic
fixtures, deterministic chain-level tests, and a safe aggregate report. No UI
surface, consumer copy, visible Diary behavior, or product-policy judgment
changes. Recording as intentionally stood down.

## Claude Decision

**Not used.** Claude has no distinct artifact or veto surface in S10. The sprint
is a deterministic backend harness layer over already-reviewed interpretation
surfaces. No new receptionist-domain judgment, architecture dispute, or product
decision requires Claude's reasoning. If Claude were available, its reviewer role
would overlap with the DeepSeek adversarial lane without adding independent
surface. Recording as intentionally stood down.

## DeepSeek Lane Count: 2

Both lanes are within the declared 1-3 limit in `sprint_worker_policy.yaml`.
Each has a distinct artifact or veto surface:

1. **Lane W1 (Implementation):** Builds the workflow chain harness core,
   authored workflow fixtures, focused tests, and safe aggregate report.
2. **Lane W2 (Adversarial Review):** Independently challenges chain invariants,
   context-propagation leakage, frame coherence across steps, refusal propagation,
   memory-context boundary, and the chain-level report safety assertions.

Both lanes use `deepseek-v4-flash` / `high` through the Deep Code PTY adapter.
The Conductor uses `deepseek-v4-pro` / `high` as authorized by the model profile
for the routine Conductor fallback role with recorded leverage reason: this is a
sprint-definition turn at the S8→S10 programme boundary requiring reasoning over
47 committed interpretation-harness tests, route-contract evidence, readiness
gates, and S5/S8 closeout context.

# Worker Packets

## Packet W1 — DeepSeek Flash Implementation

| Field | Value |
|---|---|
| Agent | `deepseek-flash-workers` (instance 1) |
| Model | `deepseek-v4-flash` / `high` |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-flash-s10-w1-workflow-chain-harness.md` |
| Ownership | `app/services/bernie/workflow_chain.py` (new), `tests/fixtures/bernie_workflow_chains/` (new), `tests/test_bernie_workflow_chain.py` (new), `scripts/bernie_workflow_chain_report.py` (new), `tests/test_bernie_workflow_chain_report.py` (new) |
| In Scope | Deterministic in-memory multi-step workflow chain runner; authored synthetic workflow fixtures (8-12 sequences, 3-6 steps each); chain-level invariant tests; safe aggregate workflow-chain report; report safety assertions; docs/handover/AGENTS updates; integration-test proof that chains do not import routes, providers, DB, H15/H-series, trove, RAG/GraphRAG, or memory |
| Out of Scope | Route dispatch, provider calls, database access, appointment/audit writes, H15/H-series runtime imports, historical diary trove, memory/RAG/GraphRAG, UI/Dairy frontend changes, taskpane changes, existing interpretation harness behavior changes, existing frame-projection behavior changes, new DiaryActionVerb additions, route-contract changes |
| Verification | `py_compile` for new modules; focused workflow-chain pytest; adjacent interpretation harness regression run; safe aggregate report CLI; report safety assertions; runtime isolation guard (no import of routes/providers/DB/H15/trove/RAG/memory in workflow chain); `git diff --check` |
| Merge Criteria | All tests pass; report emits expected aggregate-only shape; no utterance text or payload IDs in report; runtime isolation guard passes; existing interpretation harness tests unchanged |

### Implementation Design

**`app/services/bernie/workflow_chain.py`** — pure backend domain module:

- `WorkflowStep` dataclass: `utterance: str`, `expected_verb: DiaryActionVerb | None`, `expected_frame_kind: str | None`, `step_label: str`
- `WorkflowChain` dataclass: `chain_id: str`, `label: str`, `steps: tuple[WorkflowStep, ...]`
- `WorkflowContext` dataclass (in-memory only): `resolved_patient_descriptor: str | None`, `resolved_practitioner_descriptor: str | None`, `time_window_descriptor: str | None`, `accumulated_action_verbs: tuple[str, ...]`, `preceding_frame_kind: str | None`, `chain_refusal_state: str | None`
- `Resolution` enum: `resolved`, `clarification_needed`, `refused_planned`, `refused_unsafe`, `refused_unknown`
- `ChainReport`: aggregate-only shape with chain count, step count, resolution distribution, frame-kind distribution, omitted fields, boundary posture
- `run_workflow_chain(chain, context=None) -> tuple[WorkflowContext, ChainReport]`
- No route import, no provider import, no DB import, no H15/H-series import, no trove import, no RAG/GraphRAG import

**`tests/fixtures/bernie_workflow_chains/`** — authored synthetic JSON fixtures:

- `booking_happy_path.json`: Margaret Thompson + Dr Shera + today after 2pm → clarify → slot_search → create proposal (4-5 steps)
- `booking_ambiguous_patient.json`: "book Margaret" → clarification → resolved → slot_search (4 steps)
- `booking_planned_verb_chain.json`: check-in phrasing mixed with slot search → planned refusal propagated (3-4 steps)
- `booking_handoff_chain.json`: "I need to leave a message" → meta handoff → chain ends (2-3 steps)
- `booking_cancellation_chain.json`: "cancel Margaret's 3pm" → clarify → cancel proposal (3-4 steps)
- `adversarial_chain.json`: unsafe instruction in step 2 → refusal propagated to subsequent steps (3-4 steps)
- `explain_schedule_chain.json`: "what does the afternoon look like" → explain_schedule read_request → chain ends (2-3 steps)
- `mixed_read_and_proposal.json`: explain then book → read_request then proposal (3-4 steps)

**`scripts/bernie_workflow_chain_report.py`** — safe aggregate CLI:

- Loads all committed chain fixtures, runs each through the chain harness, emits aggregate-only JSON
- Omits utterance text, payload IDs, patient/practitioner/appointment/slot identifiers
- Self-validates with `assert_workflow_chain_report_safety()` before emitting
- Declares boundary posture: provider-free, route-free, DB-free, trove-free, memory-free

## Packet W2 — DeepSeek Flash Adversarial Review

| Field | Value |
|---|---|
| Agent | `deepseek-flash-workers` (instance 2) |
| Model | `deepseek-v4-flash` / `high` |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-flash-s10-w2-workflow-chain-adversarial-review.md` |
| Ownership | `docs/adversarial/s10_workflow_chain_review.md` (new); `tests/test_bernie_workflow_chain_adversarial.py` (new, non-overlapping with W1) |
| In Scope | Source-safe adversarial review artifact; non-overlapping adversarial chain fixture(s); challenge context-propagation leakage between steps; challenge frame coherence across multi-step chains; challenge refusal propagation (does a mid-chain refusal poison subsequent steps correctly?); challenge memory-context boundary (does the in-memory context ever look like it could become a persistence seam?); challenge report safety (can utterance text or payload IDs leak through the aggregate report boundary?); verify the chain harness does not import routes/providers/DB/H15/trove/RAG/memory |
| Out of Scope | W1's implementation files (review only, no edits); existing interpretation harness edits; route dispatch; provider calls; database access; appointment/audit writes; H15/H-series; historical diary trove; memory/RAG/GraphRAG; UI/Dairy frontend; taskpane |
| Verification | Review artifact inspection; adversarial chain fixture parse and chain-run; focused adversarial tests pass; W1 + W2 combined suite passes; `git diff --check` |
| Merge Criteria | Adversarial review artifact is committed; adversarial chain fixture(s) expose at least one class of context/coherence/refusal/report-safety risk; adversarial tests pass; no overlap with W1 ownership files |

# Ownership Boundaries

W1 owns:
- `app/services/bernie/workflow_chain.py` (new)
- `tests/fixtures/bernie_workflow_chains/` (new, entire directory)
- `tests/test_bernie_workflow_chain.py` (new)
- `scripts/bernie_workflow_chain_report.py` (new)
- `tests/test_bernie_workflow_chain_report.py` (new)

W2 owns:
- `docs/adversarial/s10_workflow_chain_review.md` (new)
- `tests/test_bernie_workflow_chain_adversarial.py` (new)

Neither worker may edit:
- `app/services/bernie/interpretation_harness.py` (existing harness)
- `app/services/diary/action_grammar.py` (existing grammar)
- `app/services/diary/action_route_contract.py` (existing route contract)
- `tests/fixtures/bernie_interpretation_harness/` (existing fixtures)
- `tests/test_bernie_interpretation_harness.py` (existing tests)
- Any route, provider, DB, or UI file

If W2 discovers a genuine bug in W1's implementation, it must record the finding
in its review artifact; Terra may then request a same-lane W1 correction.

# Verification Plan

## Conductor Verification (this turn; no product code or tests edited)

```powershell
.venv\Scripts\python.exe scripts\bernie_interpretation_readiness_check.py
.venv\Scripts\python.exe scripts\bernie_provider_boundary_readiness_report.py
.venv\Scripts\python.exe scripts\bernie_interpretation_harness_report.py
git status --short --branch
```

## Integration Verification (after both workers submit)

```powershell
.venv\Scripts\python.exe -m py_compile app\services\bernie\workflow_chain.py scripts\bernie_workflow_chain_report.py
.venv\Scripts\python.exe -m pytest tests\test_bernie_workflow_chain.py tests\test_bernie_workflow_chain_report.py tests\test_bernie_workflow_chain_adversarial.py -q
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py -q
.venv\Scripts\python.exe scripts\bernie_workflow_chain_report.py
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_runtime_isolation.py tests\test_bernie_interpretation_readiness_check.py -q
git diff --check
```

## Deterministic Plan Checks (Terra)

1. Settings fingerprint matches `sha256:d495ab7933dcb1999cbb6bdddd2fdd696bab632393b78eb1aef94d644d3a9677`
2. Final sprint and allocation authored by Conductor (this file)
3. No direction dialogue transferred allocation authority
4. Conductor and orchestrator authority are separated (this plan allocates; Terra dispatches, accepts, integrates)
5. Worker count 2 (within declared 1-3 limit)
6. DeepSeek lanes are exactly 2 (within 1-3 cap)
7. Each worker has a distinct artifact or veto surface (W1: implementation; W2: adversarial review)
8. Assignment capabilities match probe eligibility (DeepSeek Flash through Deep Code PTY adapter, both lanes)
9. Fallback and reduced independence are explicit (see below)
10. No orchestrator substitution (this is the Conductor plan; Terra is the executor)
11. Workspace receipts match assigned agent and handoff state (see below)

# Fallback Reasons

- Claude is intentionally stood down: no distinct artifact or veto surface for
  deterministic backend harness work. No receptionist-domain judgment, product
  policy, or architecture dispute requires Claude's reasoning depth.
- Antigravity is intentionally stood down: no UI surface, consumer copy, visible
  Diary behavior, or product-policy judgment changes. No UX or consumer artifact
  surface exists.
- If one DeepSeek lane fails or times out, the remaining lane's artifacts may
  still be integrated if they are independently verifiable. If the implementation
  lane (W1) fails, Terra must reject the sprint and request Conductor
  reallocation rather than substituting. If the adversarial lane (W2) fails, W1
  integration may proceed with the adversarial review obligation recorded as
  unfilled for a follow-up sprint.

# Independence Labels

- W1: **Implementation owner** — owns all new production modules, fixtures, tests,
  scripts
- W2: **Independent review/veto** — owns adversarial review artifact and
  non-overlapping adversarial tests; may produce a `revision_required` finding
- Claude: **Intentionally stood down** — no distinct artifact or veto surface
- Antigravity: **Intentionally stood down** — no UI or consumer artifact surface

# Unfilled Obligations

- No independent LLM verifier is triggered (no new security, write, deployment,
  or release authority; no material Conductor-Orchestrator disagreement; no
  ambiguous mandate; no resource limit exception; no authority/ownership drift
  signal).
- Terminal-to-active appointment status policy remains user-owned and is not
  chosen, inferred, or implemented in S10.
- The workflow chain harness stops at frame projection; it deliberately does not
  resolve frames to route endpoints, confirm payloads, or scheduled actions.
  That is a separate future sprint (S11 or later) after the chain harness proves
  multi-step coherence.
- Planned verbs (check_in, waiting_area_move, link_patient) remain
  `implemented=False` with no confirm actions. The chain harness may exercise
  them as planned-refusal steps only.
- The H15 semantic labelling gate remains approved for its bounded prototype
  scope only; S10 does not use H15 fixtures, H-series profiles, or historical
  diary trove material.
- Dependabot alert 5 remains open; S10 does not force overrides.

# Workspace Receipts

## Conductor Workspace (this turn)

| Field | Value |
|---|---|
| Target worktree | `C:\Users\sarashera\EMR4-worktrees\deepcode-s10-conductor` |
| Target branch | `deepcode/s10-conductor` |
| Cleanliness | Clean tracked-code state (plan artifact only) |
| Handoff/current | `b05ee20a` (resolved S10 preflight: assigned-agent-only receipts) |
| Head at handoff | Yes (merge-base is `b05ee20a`) |
| Realignment | Not required (worktree is intentionally ahead for Conductor planning) |

## Worker W1 Required Receipt (before dispatch)

Terra must verify before dispatching W1:
- Target worktree exists (disposable, packet-scoped)
- Target branch is unique and worker-owned (e.g., `deepcode/s10-w1-workflow-chain`)
- Target worktree is clean
- Target head matches `handoff/current` at `b05ee20a` or has recorded divergence
- Realignment is executed from the target worktree, not the integration worktree
- Injected Python path: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe`
- Injected Node path: `C:\Program Files\nodejs\node.exe`

## Worker W2 Required Receipt (before dispatch)

Same requirements as W1, with non-overlapping branch (e.g.,
`deepcode/s10-w2-workflow-chain-adversarial`).

# Conductor Authority Separation

This Conductor defines and allocates S10 only. The Conductor does **not**:

- Dispatch workers (Terra's role)
- Accept or reject worker artifacts (Terra's deterministic gates plus review)
- Integrate accepted commits (Terra's staging branch only)
- Commit, push, or alter protected `master`
- Advance `handoff/current`
- Redefine or reallocate work after publication
- Alter acceptance criteria
- Open closed runtime, provider, database, deployment, or product-policy gates
- Choose, infer, or implement terminal-to-active appointment status policy

# Current Readiness Checkpoint

```json
{
  "runtime_gate_decision": "blocked",
  "runtime_or_provider_wiring_ready": false,
  "raw_trove_access_ready": false,
  "sprint_engine_state": "continuing",
  "case_count": 44,
  "contract_count": 7,
  "dispatch_count": 7,
  "frame_kind_count": 4,
  "default_provider": "disabled",
  "live_provider_enabled": false,
  "provider_calls_performed": false,
  "route_behavior_changed": false,
  "database_access_performed": false,
  "memory_or_rag_access_performed": false,
  "historical_diary_material_access_performed": false
}
```

STATUS: complete
