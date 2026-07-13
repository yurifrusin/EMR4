# DeepSeek Pro Conductor — S10 Receptionist Workflow Chain Harness (V2 — Test-Only Replan)

Role: routine Conductor
Resource: `deepseek-pro-conductor-fallback`
Model: `deepseek-v4-pro` / high
Artifact: `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow-v2.md`
Schema: `ariadne.sprint_worker_policy.v1` conductor plan
Replan reason: **Sol-mandated.** The prior S10 plan (V1) allocated W1's production
harness module in `app/services/bernie/workflow_chain.py`. Terra's acceptance
review found that the candidate commit `ae0fb775` edited the excluded
`tests/test_bernie_interpretation_runtime_isolation.py` to exempt the new
module, and the Conductor plan explicitly forbade editing that file. The
deeper conflict is structural: a new `app/services` module that imports
interpretation-harness tooling cannot satisfy the runtime-isolation boundary
without either moving to a test-only surface or revising the guard. Sol
resolved the escalation: **preserve the runtime-isolation boundary and its
acceptance criteria; do not exempt a new `app/services` module from the
guard; do not integrate `ae0fb775`.** This V2 replan reallocates W1 onto a
test-only surface. The Conductor authored this replan, not Terra.

The V1 plan and rejection evidence are preserved at:
- `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow.md`
- `orchestration/agent_inbox/codex/review-terra-s10-w1-acceptance.md`
- `orchestration/agent_inbox/codex/review-deepseek-s10-w1-workflow-chain.md`

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

## Critical Structural Change from V1

**V1 (rejected):** W1 owned `app/services/bernie/workflow_chain.py` — a
production-path `app/services` module importing interpretation-harness
tooling. This violated the runtime isolation guard
(`tests/test_bernie_interpretation_runtime_isolation.py`), which scans all
`app/*.py` sources for forbidden fragments including
`"bernie_interpretation_harness"`.

**V2 (this plan):** W1 owns `tests/workflow_chain/harness.py` — a test-only
helper module. Tests are not scanned by the runtime isolation guard. The
harness imports `app.services.bernie.interpretation_harness` normally
(tests importing app code is allowed). The runtime isolation test is not
edited. The test-only surface preserves all provider-free, route-free,
DB-free, authored-synthetic evidence while keeping the `app/` runtime
isolation boundary intact.

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
- Test-only harness module in `tests/` (new; provider-free)
- Orchestration plan/review/test artifacts only

# Direction Dialogue Disposition

No direction collaboration was triggered for this sprint. The S9 closeout
recorded the next recommended work as "DeepSeek 4 Pro/high must define and
allocate S10 end-to-end receptionist workflow work through the detached real-PTY
path." The S5 and S8 receptionist workflow closeouts confirmed the frontend and
backend workflow surface and recorded the remaining boundaries. No dispute or
ambiguity required a GPT Sol direction proposal or rejoinder cycle. The
Conductor defined and allocated S10 directly.

The V1 plan passed review and was accepted, but W1 acceptance failed on the
runtime-isolation guard. Sol's escalation resolution directed this replan. The
Conductor authored this V2 plan under Sol's explicit boundary instruction. No
direction dialogue transferred allocation authority.

# Inspected Evidence

## Sol Escalation Resolution
- `orchestration/agent_inbox/codex/review-terra-s10-w1-acceptance.md`: Terra
  found that W1 candidate `ae0fb775` edited
  `tests/test_bernie_interpretation_runtime_isolation.py` (an excluded file)
  and that `app/services/bernie/workflow_chain.py` imports interpretation-harness
  tooling from inside `app/services/`. Decision: `revision_required`. Escalation
  triggered as `scope_authority_or_acceptance_change` and
  `conflicting_acceptance_evidence`.

## V1 W1 Implementation Evidence
- `orchestration/agent_inbox/codex/review-deepseek-s10-w1-workflow-chain.md`:
  86/86 W1 focused tests passed; all ~225 existing interpretation-harness
  regression tests passed; report CLI emitted correct aggregate JSON with 19
  chains across 44 steps; `py_compile` passed; boundary posture confirmed
  (no routes, providers, DB, trove, memory, RAG/GraphRAG, H15/H-series).
  The only blocking issue was the runtime-isolation violation.

## V1 Conductor Plan
- `orchestration/agent_inbox/codex/plan-deepseek-pro-s10-receptionist-workflow.md`:
  Accepted V1 plan with settings fingerprint
  `sha256:02a14d07e5391d324045c8be8a204d8a60f40f47e1a8319cd01f5c47fcf26f14`,
  2 DeepSeek lanes, W1 implementation + W2 adversarial review.

## S8 Receptionist Workflow Closeout
- `docs/emr4-s8-receptionist-workflow-closeout.md`: S8 completed the Conditional
  Go receptionist workflow tranche. Terminal-to-active policy remains user-owned.
  Provider, database/schema, deployment/production, external patient client,
  H15/H-series, historical diary, memory/RAG/GraphRAG, and new model-write gates
  remain closed.

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

## Runtime Isolation Guard
- `tests/test_bernie_interpretation_runtime_isolation.py`: scans all `app/*.py`
  sources for forbidden fragments including `"bernie_interpretation_harness"`,
  `"bernie_interpretation_harness_report"`, `"bernie_interpretation_runtime_gate_check"`,
  `"bernie_interpretation_readiness_check"`, and
  `"bernie-interpretation-harness-runtime-gate"`. Any `app/` module that imports
  or references interpretation-harness tooling fails.
- The interpretation harness itself (`app/services/bernie/interpretation_harness.py`)
  is the guarded entity; it is allowed in `app/services/` because its runtime
  use is blocked by the runtime gate (`blocked`), not because it is exempt from
  scanning. No other `app/` module may import it.

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
sprint produces only provider-free test-only harness code, authored synthetic
fixtures, deterministic chain-level tests, and a safe aggregate report. No UI
surface, consumer copy, visible Diary behavior, or product-policy judgment
changes. Recording as intentionally stood down.

## Claude Decision

**Not used.** Claude has no distinct artifact or veto surface in S10. The sprint
is a deterministic test-only harness layer over already-reviewed interpretation
surfaces. No new receptionist-domain judgment, architecture dispute, or product
decision requires Claude's reasoning. If Claude were available, its reviewer role
would overlap with the DeepSeek adversarial lane without adding independent
surface. Recording as intentionally stood down.

## DeepSeek Lane Count: 2

Both lanes are within the declared 1-3 limit in `sprint_worker_policy.yaml`.
Each has a distinct artifact or veto surface:

1. **Lane W1 (Implementation):** Builds the workflow chain harness core as a
   **test-only** helper module, authored workflow fixtures, focused tests, and
   safe aggregate report. The harness lives in `tests/`, not `app/services/`.
2. **Lane W2 (Adversarial Review):** Independently challenges chain invariants,
   context-propagation leakage, frame coherence across steps, refusal propagation,
   memory-context boundary, and the chain-level report safety assertions.

Both lanes use `deepseek-v4-flash` / `high` through the Deep Code PTY adapter.
The Conductor uses `deepseek-v4-pro` / `high` as authorized by the model profile
for the routine Conductor fallback role with recorded leverage reason: this is a
Sol-mandated replan at the S10 sprint boundary requiring reasoning over the V1
plan, Terra's acceptance evidence, the runtime-isolation boundary, and the
test-only structural constraint.

# Worker Packets

## Packet W1 — DeepSeek Flash Implementation (Test-Only Surface)

| Field | Value |
|---|---|
| Agent | `deepseek-flash-workers` (instance 1) |
| Model | `deepseek-v4-flash` / `high` |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-flash-s10-w1-workflow-chain-harness-v2.md` |
| Ownership | `tests/workflow_chain/__init__.py` (new), `tests/workflow_chain/harness.py` (new), `tests/fixtures/bernie_workflow_chains/` (new), `tests/test_bernie_workflow_chain.py` (new), `scripts/bernie_workflow_chain_report.py` (new), `tests/test_bernie_workflow_chain_report.py` (new) |
| In Scope | Test-only deterministic in-memory multi-step workflow chain runner in `tests/workflow_chain/harness.py` (NOT in `app/services/`); authored synthetic workflow fixtures (8-12 sequences, 3-6 steps each); chain-level invariant tests; safe aggregate workflow-chain report; report safety assertions; runtime isolation guard proof that the test-only harness does not cause any `app/` import change |
| Out of Scope | Route dispatch, provider calls, database access, appointment/audit writes, H15/H-series runtime imports, historical diary trove, memory/RAG/GraphRAG, UI/Diary frontend changes, taskpane changes, existing interpretation harness behavior changes, existing frame-projection behavior changes, new DiaryActionVerb additions, route-contract changes, adversarial chain fixtures (owned by W2), **any edit to `app/services/`** (the harness is tests-only), **any edit to `tests/test_bernie_interpretation_runtime_isolation.py`** (excluded file, must not be modified), **any edit to `app/config.py`** |
| Verification | `py_compile` for the test-only harness module and report script; focused workflow-chain pytest; adjacent interpretation harness regression run; safe aggregate report CLI; report safety assertions; critical runtime isolation guard check: `pytest tests/test_bernie_interpretation_runtime_isolation.py -q` must show unchanged failure count (zero new failures beyond documented baseline at `b05ee20a`, no new `app/` module imports harness tooling); `git diff --check` |
| Merge Criteria | All tests pass; report emits expected aggregate-only shape; no utterance text or payload IDs in report; runtime isolation guard shows unchanged failure count (zero new failures beyond documented baseline at `b05ee20a`) without modification; existing interpretation harness tests unchanged; no new or modified files in `app/services/` |

### Implementation Design (Test-Only)

**`tests/workflow_chain/__init__.py`** — empty init to make the test-only package
importable.

**`tests/workflow_chain/harness.py`** — pure test-only domain module:

- `WorkflowStep` dataclass: `utterance: str`, `expected_verb: DiaryActionVerb | None`, `expected_frame_kind: str | None`, `step_label: str`
- `WorkflowChain` dataclass: `chain_id: str`, `label: str`, `steps: tuple[WorkflowStep, ...]`
- `WorkflowContext` dataclass (in-memory only): `resolved_patient_descriptor: str | None`, `resolved_practitioner_descriptor: str | None`, `time_window_descriptor: str | None`, `accumulated_action_verbs: tuple[str, ...]`, `preceding_frame_kind: str | None`, `chain_refusal_state: str | None`
- `Resolution` enum: `resolved`, `clarification_needed`, `refused_planned`, `refused_unsafe`, `refused_unknown`
- `ChainReport`: aggregate-only shape with chain count, step count, resolution distribution, frame-kind distribution, omitted fields, boundary posture
- `run_workflow_chain(chain, context=None) -> tuple[WorkflowContext, ChainReport]`
- Imports from `app.services.bernie.interpretation_harness` (tests importing app code is allowed and expected)
- No route import, no provider import, no DB import, no H15/H-series import, no trove import, no RAG/GraphRAG import
- No import of `bernie_interpretation_harness_report`, `bernie_interpretation_runtime_gate_check`, or `bernie_interpretation_readiness_check` (these are scripts/test tooling that `app/` code must not import; a test-only harness importing them would be unusual but not a violation since tests are outside the `app/` scan; however, the harness should import only the interpretation harness itself to stay clean)

**Critical: The runtime isolation guard scans `app/*.py` only.** The test-only
harness at `tests/workflow_chain/harness.py` is outside the scan boundary.
W1 must verify this by running `pytest tests/test_bernie_interpretation_runtime_isolation.py -q`
and confirming zero new failures beyond the documented baseline failure at `b05ee20a`. The test must not be edited.

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
- Imports from `tests.workflow_chain.harness` (or directly from `app.services.bernie.interpretation_harness` for single-step utilities)
- Omits utterance text, payload IDs, patient/practitioner/appointment/slot identifiers
- Self-validates with `assert_workflow_chain_report_safety()` before emitting
- Declares boundary posture: provider-free, route-free, DB-free, trove-free, memory-free

## Packet W2 — DeepSeek Flash Adversarial Review

| Field | Value |
|---|---|
| Agent | `deepseek-flash-workers` (instance 2) |
| Model | `deepseek-v4-flash` / `high` |
| Packet | `orchestration/agent_inbox/deepcode/deepcode-flash-s10-w2-workflow-chain-adversarial-review-v2.md` |
| Ownership | `docs/adversarial/s10_workflow_chain_review_v2.md` (new); `tests/fixtures/bernie_workflow_chain_review/` (new, non-overlapping with W1's `tests/fixtures/bernie_workflow_chains/`); `tests/test_bernie_workflow_chain_adversarial.py` (new) |
| In Scope | Source-safe adversarial review artifact; adversarial chain fixture(s) in `tests/fixtures/bernie_workflow_chain_review/` (a separate, non-overlapping fixture directory from W1's `tests/fixtures/bernie_workflow_chains/`); challenge context-propagation leakage between steps; challenge frame coherence across multi-step chains; challenge refusal propagation (does a mid-chain refusal poison subsequent steps correctly?); challenge memory-context boundary (does the in-memory context ever look like it could become a persistence seam?); challenge report safety (can utterance text or payload IDs leak through the aggregate report boundary?); challenge test-only boundary (does the harness import or leak into `app/` in any way?); verify the runtime isolation guard shows unchanged failure count (zero new failures beyond documented baseline) |
| Out of Scope | W1's implementation files (review only, no edits); W1's `tests/workflow_chain/` directory (review only, no edits); W1's `tests/fixtures/bernie_workflow_chains/` directory (no edits or additions to W1's fixture files); existing interpretation harness edits; route dispatch; provider calls; database access; appointment/audit writes; H15/H-series; historical diary trove; memory/RAG/GraphRAG; UI/Diary frontend; taskpane; any edit to `tests/test_bernie_interpretation_runtime_isolation.py` |
| Verification | Review artifact inspection; adversarial chain fixture parse and chain-run; focused adversarial tests pass; W1 + W2 combined suite passes; `git diff --check`; `pytest tests/test_bernie_interpretation_runtime_isolation.py` shows unchanged failure count (zero new failures beyond documented baseline) |
| Merge Criteria | Adversarial review artifact is committed; adversarial chain fixture(s) expose at least one class of context/coherence/refusal/report-safety risk; adversarial tests pass; no overlap with W1 ownership files (W2 owns only `tests/fixtures/bernie_workflow_chain_review/`, not W1's `tests/fixtures/bernie_workflow_chains/`); runtime isolation guard shows zero new failures beyond documented baseline |

# Ownership Boundaries

W1 owns:
- `tests/workflow_chain/__init__.py` (new)
- `tests/workflow_chain/harness.py` (new)
- `tests/fixtures/bernie_workflow_chains/` (new, entire directory)
- `tests/test_bernie_workflow_chain.py` (new)
- `scripts/bernie_workflow_chain_report.py` (new)
- `tests/test_bernie_workflow_chain_report.py` (new)

W2 owns:
- `docs/adversarial/s10_workflow_chain_review_v2.md` (new)
- `tests/fixtures/bernie_workflow_chain_review/` (new, entirely separate from W1's `tests/fixtures/bernie_workflow_chains/`; for adversarial fixtures only)
- `tests/test_bernie_workflow_chain_adversarial.py` (new)

Neither worker may edit:
- `app/services/bernie/interpretation_harness.py` (existing harness)
- `app/services/diary/action_grammar.py` (existing grammar)
- `app/services/diary/action_route_contract.py` (existing route contract)
- `tests/fixtures/bernie_interpretation_harness/` (existing fixtures)
- `tests/test_bernie_interpretation_harness.py` (existing tests)
- `tests/test_bernie_interpretation_runtime_isolation.py` (**explicitly protected** — V1's edit to this file was the acceptance blocker)
- `app/config.py` (**explicitly protected** — Terra noted a pre-existing fragment reference but this is not changed)
- Any route, provider, DB, or UI file
- Any file under `app/services/`

W2 must not create or modify files under W1's `tests/fixtures/bernie_workflow_chains/`
directory. W2's adversarial chain fixtures live exclusively in
`tests/fixtures/bernie_workflow_chain_review/`, which is a genuinely distinct
directory path with no overlap against W1's ownership surface.

If W2 discovers a genuine bug in W1's implementation, it must record the finding
in its review artifact; Terra may then request a same-lane W1 correction.

# Verification Plan

## Conductor Verification (this turn; no product code or tests edited)

```powershell
git status --short --branch
```

The Conductor does not run tests or edit code in this turn.

## Integration Verification (after both workers submit)

### 1. Runtime isolation guard (baseline comparison)
```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_runtime_isolation.py -q
```
Expected: unchanged failure count — one failure from `app/config.py` (documented baseline at `b05ee20a`). Zero new failures. The test-only harness in `tests/`
is outside the `app/*.py` scan. No `app/` file imports `bernie_interpretation_harness`
or other harness tooling.

### 2. Compile check
```powershell
.venv\Scripts\python.exe -m py_compile tests\workflow_chain\harness.py scripts\bernie_workflow_chain_report.py
```

### 3. New W1 tests
```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_workflow_chain.py tests\test_bernie_workflow_chain_report.py -q
```

### 4. W2 adversarial tests
```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_workflow_chain_adversarial.py -q
```

### 5. Existing regression (interpretation harness)
```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_harness.py tests\test_bernie_interpretation_harness_report.py -q
```

### 6. Report CLI execution
```powershell
.venv\Scripts\python.exe scripts\bernie_workflow_chain_report.py
```

### 7. Readiness check (unchanged baseline)
```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_readiness_check.py -q
```

### 8. Whitespace check
```powershell
git diff --check
```

## Deterministic Plan Checks (Terra)

1. Settings fingerprint matches `sha256:02a14d07e5391d324045c8be8a204d8a60f40f47e1a8319cd01f5c47fcf26f14`
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
12. W1 and W2 fixture directories are genuinely non-overlapping (W1: `tests/fixtures/bernie_workflow_chains/`; W2: `tests/fixtures/bernie_workflow_chain_review/`)
13. **W1 owns zero files under `app/services/`** (test-only surface structural check)
14. **W1 does not edit `tests/test_bernie_interpretation_runtime_isolation.py`** (V1 blocker, explicitly protected)
15. **W1 does not edit `app/config.py`** (explicitly protected)
16. **Runtime isolation guard shows zero new failures beyond the documented baseline failure at `b05ee20a` after W1 submit** (acceptance gate)

# Acceptance Gate: Runtime Isolation

This is the single most important acceptance criterion for W1. The V1 candidate
failed here. The V2 plan makes it the first integration check.

The unchanged `b05ee20a` base has one documented runtime-isolation failure:
`app/config.py` contains the string `bernie-interpretation-harness-runtime-gate`
(via `"docs" / "bernie-interpretation-harness-runtime-gate.json"` in
`LIVE_BERNIE_INTERPRETER_PROVIDERS`). This is a known baseline; neither
`app/config.py` nor the guard test may be edited to convert it into a pass.

Terra must run **before accepting W1**:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_bernie_interpretation_runtime_isolation.py -q
```

Expected: **unchanged failure count — exactly one failure, from `app/config.py`
only. Zero new failures beyond this documented baseline.** If the test shows any
new failure, additional failures, a different failure location, or zero failures
(indicating the guard was edited), or if
`tests/test_bernie_interpretation_runtime_isolation.py` was edited, Terra must
reject the candidate with `revision_required` and must not dispatch W2.

The test-only harness at `tests/workflow_chain/harness.py` lives outside the
`app/*.py` scan. It may freely import `app.services.bernie.interpretation_harness`
because tests importing app code is the normal Python testing pattern. The guard's
purpose is to prevent `app/` runtime code from importing harness tooling, not to
prevent tests from importing app code.

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

- W1: **Implementation owner** — owns all new test-only modules, fixtures, tests,
  scripts
- W2: **Independent review/veto** — owns adversarial review artifact and
  non-overlapping adversarial fixtures and tests; may produce a
  `revision_required` finding
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
- The V1 W1 implementation evidence (`ae0fb775`) is preserved for reference but
  not integrated. The functional design (dataclasses, resolution logic, chain
  report shape) informed this V2 plan but the test-only structural constraint
  is new.

# Workspace Receipts

## Conductor Workspace (this turn)

| Field | Value |
|---|---|
| Target worktree | `C:\Users\sarashera\EMR4-worktrees\deepcode-s10-conductor-v2` |
| Target branch | `deepcode/s10-conductor-v2` |
| Cleanliness | Clean tracked-code state (plan artifact only) |
| Handoff/current | `b05ee20a` (resolved S10 preflight: assigned-agent-only receipts) |
| Head at handoff | Merge-base is `b05ee20a` |
| Realignment | Not required (worktree is intentionally ahead for Conductor planning) |

## Worker W1 Required Receipt (before dispatch)

Terra must verify before dispatching W1:
- Target worktree exists (disposable, packet-scoped)
- Target branch is unique and worker-owned (e.g., `deepcode/s10-w1-workflow-chain-v2`)
- Target worktree is clean
- Target head matches `handoff/current` at `b05ee20a` or has recorded divergence
- Realignment is executed from the target worktree, not the integration worktree
- Injected Python path: `C:\Users\sarashera\emr4\.venv\Scripts\python.exe`
- Injected Node path: `C:\Program Files\nodejs\node.exe`

## Worker W2 Required Receipt (before dispatch)

Same requirements as W1, with non-overlapping branch (e.g.,
`deepcode/s10-w2-workflow-chain-adversarial-v2`).

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
- Edit product code or tests in this turn

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

# Summary of Changes from V1

| Aspect | V1 (rejected) | V2 (this plan) |
|---|---|---|
| Harness module location | `app/services/bernie/workflow_chain.py` | `tests/workflow_chain/harness.py` |
| Runtime isolation impact | Failed — new `app/services` module imported harness tooling | Unchanged baseline failure count — test-only module outside `app/` scan; zero new failures beyond documented baseline at `b05ee20a` |
| `test_bernie_interpretation_runtime_isolation.py` | Edited (blocked) | Not edited (explicitly protected) |
| Acceptance gate | Standard verification | Runtime isolation guard: zero new failures beyond documented baseline at `b05ee20a` is acceptance prerequisite |
| Plan mandate | Conductor allocation | Sol-mandated replan preserving runtime boundary |

STATUS: complete
