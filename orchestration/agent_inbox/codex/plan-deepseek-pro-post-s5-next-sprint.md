# Conductor Sprint Plan — S6: Post-S5 Diary Smoke Repair

| Field | Value |
|---|---|
| Plan ID | `plan-deepseek-pro-post-s5-next-sprint` |
| Sprint ID | S6 |
| Role | conductor |
| Conductor resource | `deepseek-pro-conductor-fallback` (DeepSeek 4 Pro, high reasoning, this session) |
| Date | 2026-07-12 |
| Status | awaiting_orchestrator_acceptance |
| Settings fingerprint | `sha256:5ea2b3522cd6c7238640ad8d251206a64561e3c22d89234a73610063e0d2b77b` (from AGENTS.md handover doc; Fable's S5 fingerprint `sha256:6d5a113…` preceded the most recent settings YAML changes; the handover record is newer and authoritative) |
| direction_dialogue_disposition | `accepted_priorities_sequenced` |

## 1. Direction Dialogue Record

The protected orchestrator (Sol) supplied an advisory direction with two post-S5
priorities:

1. Eight reproducible diary smoke failures caused by GraphQL-vs-REST mock drift
   and smoke-mode network assertions.
2. Yuri's requested bounded Ariadne cross-boundary contract audit, focused on
   duplicated operational facts (artifact path, packet/lane identity,
   worktree/branch, settings fingerprint, model/reasoning, authority state).

The Conductor **accepts both priorities but sequences them**. The diary smoke
repair is the higher-value EMR4 product sprint: it restores the CI signal,
improves regression safety for every subsequent diary/Bernie sprint, and has a
known diagnosis path (the GraphQL default-on switch at Sprint 281 changed the
diary's HTTP surface while the smoke test's Playwright route interception still
targets REST URLs). The cross-boundary contract audit is important orchestration
quality work but is deferred to Sprint S7-ContractAudit.

Per `direction_collaboration.yaml`, the Conductor has final say and the
orchestrator may issue at most one rejoinder. Agreement on priorities is
already established; only sequencing is decided here. No allocation authority
was transferred: the orchestrator's direction named priorities, and every
assignment below is authored solely by the Conductor.

## 2. Boundary

**Sprint kind:** harness repair / regression safety sprint — direct EMR4 product
benefit (healthy CI signal for the diary/receptionist surface).

**In scope:**

- Diagnosis of the eight remaining `review/test_diary_smoke.py` failures. The
  known mechanism: Sprint 281 flipped `ENABLE_GRAPHQL_PRACTITIONERS = true` in
  `docs/diary/diary.js`, so the diary now sends `POST /api/v1/graphql` queries
  instead of `GET /api/v1/practice/practitioners?activeOnly=true&limit=200`. The
  smoke test's `route.fulfill()` handlers intercept only REST URLs; uncaught
  GraphQL requests either hit the real backend (failing when it is not running)
  or time out. Not every smoke test depends on practitioner data, so the eight
  failures are the subset where GraphQL mock drift actually matters.
- Fix applied to `review/test_diary_smoke.py` only. No change to
  `docs/diary/diary.js`, `app/`, production code, or non-smoke tests.
- Worker diagnostic artifact: a findings packet listing each failing test, the
  specific GraphQL request it triggers, and the required route interception
  change (add a `route.fulfill()` for `/api/v1/graphql` with the expected
  practitioner-directory response shape, or a narrower per-case intercept).
- Full smoke suite re-verification: `pytest review/test_diary_smoke.py
  --junitxml=review/diary-review.xml -q` with zero failures expected.
- Independent cross-review lane verifying no regression in the smoke suite, no
  GraphQL traffic leakage in smoke mode, no adjacent-gate openings.
- Regular Git commit/push checkpoints.

**Out of scope:**

- No change to `docs/diary/diary.js`, the GraphQL consumer switch, or production
  routing.
- No Bernoulli D5 expansion, no provider/live-provider wiring, no
  memory/RAG/GraphRAG access.
- No H15/H-series, historical diary runtime, or `local_data` access.
- No backend route/schema/service change, no database migrations, no write
  authority.
- No GraphQL deployment, readiness, telemetry, or production claims.
- No external patient-client exposure, no Pages deployment change.
- No terminal-status product-policy decision (deferred, undelegated).
- No cross-boundary contract audit (deferred to Sprint S7-ContractAudit).
- No monetary or wall-clock caps.

**All runtime gates remain closed.** No Bernie D5, provider, memory/RAG,
historical diary runtime, deployment, external-client, schema, or new
write-authority gate is opened.

## 3. Worker Allocation

### Claude — NOT USED

Claude subscription reported a real session limit. Fable and Opus share that
unavailable account window. Per `cost_controls.yaml` and protocol alerts,
Claude is unavailable and must not be waited for.

### Antigravity — CONSULT IF AVAILABLE AFTER PROBE

Antigravity availability was not probed from this conductor session. Before
dispatch, the orchestrator must check `agy.exe` and the Antigravity UI quota
view. If available, use Antigravity as a consumer/UX boundary reviewer:
open the fixed smoke-test diary page, verify the grid renders in smoke mode,
and confirm the eight previously-failing tests now pass from a UX/rendering
perspective. The Antigravity review artifact should be a short PASS/FAIL verdict
with any rendering observations.

If Antigravity is unavailable or quota-limited, the orchestrator should stand
it down and use only the two DeepSeek lanes.

### DeepSeek Flash — 2 WORKER LANES

Per `worker_pool.yaml`, `deepseek-flash-workers` allows up to 3 instances.
Two lanes are allocated here; a third is reserved for the deferred
S7-ContractAudit sprint.

Before dispatch, the orchestrator must close any completed or idle DeepSeek
lanes from S5, check the current `deepseek-flash-workers` instance count, and
spawn fresh lanes if needed.

#### Lane 1: Implementation Owner — `deepseek-s6-diag-smoke`

| Field | Value |
|---|---|
| Resource | `deepseek-flash-workers` (instance 1) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY, durable artifact required) |
| Branch | `codex/s6-diag-smoke` |
| Role | Implementation owner |
| Capabilities | implementer, test_engineer |
| Cost tier | 1 |

**Mission:** Diagnose the eight diary smoke failures. Read `review/test_diary_smoke.py`,
trace each failing test to the GraphQL request it triggers (via
`docs/diary/diary.js`'s `ENABLE_GRAPHQL_PRACTITIONERS = true` path), and add
the necessary route interception so the smoke test intercepts GraphQL requests
instead of letting them time out or hit the real backend.

**Expected fix surface:** `review/test_diary_smoke.py` only. The fix should add
`page.route("**/api/v1/graphql", ...)` handlers that return the expected
practitioner-directory response shape (matching the Sprint 278/279 mock
contract). Tests that do not depend on practitioner data and previously passed
should remain passing.

**Evidence:**
- Worker completion artifact naming each of the eight failures and the fix applied
- Before: `pytest review/test_diary_smoke.py -q --tb=short` → 8 failures
- After: `pytest review/test_diary_smoke.py -q --tb=short` → 0 failures
- `node --check docs/diary/diary.js` → pass
- `git diff --check` → clean
- Boundary assertion: `git diff --stat` shows only `review/test_diary_smoke.py`

**Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s6-diag-smoke.md`

#### Lane 2: Independent Review/Veto — `deepseek-s6-review-smoke`

| Field | Value |
|---|---|
| Resource | `deepseek-flash-workers` (instance 2) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY, durable artifact required) |
| Branch | `codex/s6-review-smoke` |
| Role | Independent review/veto |
| Capabilities | code_reviewer, security_reviewer, test_engineer |
| Cost tier | 1 |

**Mission:** Cross-review the Lane 1 fix. Read the Lane 1 completion artifact
and the diff. Run the full smoke suite independently. Verify no regression in
previously-passing tests, no silent test weakening, no GraphQL traffic leakage
in smoke mode, no adjacent-gate openings, and no unintended production code
changes.

**Evidence:**
- Independent `pytest review/test_diary_smoke.py -q --tb=short` → 0 failures
- Verification that the `?smoke=true` path sends zero real GraphQL requests
- Boundary check: no `app/`, `docs/diary/diary.js`, or non-smoke-test file changes
- PASS or FAIL verdict with specific findings

**Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s6-review-smoke.md`

## 4. Ownership Boundaries

| Surface | Owner | Review |
|---|---|---|
| `review/test_diary_smoke.py` (fix) | Lane 1: `deepseek-s6-diag-smoke` | Lane 2: `deepseek-s6-review-smoke` |
| `docs/diary/diary.js` (read-only) | Lane 1: diagnosis only | Lane 2: boundary check |
| Smoke suite regression | Lane 2: independent run | Orchestrator: final acceptance |
| Consumer/UX rendering | Antigravity (if available) | Orchestrator |

No file overlap between lanes. Lane 1 writes only `review/test_diary_smoke.py`.
Lane 2 reads the diff and runs the suite.

## 5. Acceptance Evidence

| Gate | Check | Owner |
|---|---|---|
| Smoke suite clean | `pytest review/test_diary_smoke.py -q --tb=short` → 0 failures | Lane 2 + Orchestrator |
| No production code changes | `git diff --stat` shows only `review/test_diary_smoke.py` | Lane 2 + Orchestrator |
| JS syntax | `node --check docs/diary/diary.js` → pass | Orchestrator |
| Whitespace | `git diff --check` → clean | Orchestrator |
| No gate openings | No D5/provider/memory/RAG/H15/trove/write/deployment/GraphQL readiness gate opened | Lane 2 + Orchestrator |
| GraphQL smoke isolation | In `?smoke=true` mode, zero real GraphQL requests sent (all intercepted) | Lane 2 |
| Previously-passing tests unaffected | No regression in non-practitioner smoke tests | Lane 2 + Orchestrator |

## 6. Verification Plan (Orchestrator)

After both lanes submit and Antigravity responds (or is stood down):

```powershell
git fetch origin codex/s6-diag-smoke codex/s6-review-smoke
git diff origin/master...origin/codex/s6-diag-smoke --stat
# Expected: only review/test_diary_smoke.py

pytest review/test_diary_smoke.py --junitxml=review/diary-review.xml -q
# Expected: 0 failures (currently 8)

node --check docs/diary/diary.js
# Expected: pass

git diff --check origin/master...origin/codex/s6-diag-smoke
# Expected: clean

.venv\Scripts\python.exe -m pytest tests/test_sprint_closeout_protocol.py -q
# Expected: pass
```

## 7. Fallback Reason and Reduced Independence

**Fallback reason:** Claude subscription reported a real session limit. Fable
and Opus share that unavailable account window. The conductor allocation order
(`role_preferences.yaml`) is [Fable, Opus, DeepSeek Pro, GPT Sol]. Fable and
Opus are unavailable, so DeepSeek 4 Pro via Deep Code is the active conductor.

**Reduced independence:** This conductor session cannot probe Antigravity or
DeepSeek worker availability from the current TTY-only Deep Code context. The
orchestrator retains responsibility for the workspace preflight receipt,
Antigravity probe, DeepSeek lane management, worker packet dispatch, sprint
execution, integration, and closeout. The orchestrator must:

1. Run the orchestrator preflight receipt before dispatch.
2. Close completed/expired S5 DeepSeek lanes.
3. Probe Antigravity availability via `agy.exe` and the UI quota view.
4. Dispatch worker packets to `orchestration/agent_inbox/deepcode/`.
5. Claim and execute the sprint, commit/push checkpoints regularly.
6. Integrate reviewed worker artifacts and close the sprint.

## 8. Unfilled Obligations

| Obligation | Status | Reason |
|---|---|---|
| Claude lane | Not filled | Unavailable (subscription limit) |
| Antigravity lane | Deferred to orchestrator probe | Cannot probe from this conductor session |
| Independent LLM verifier | Not required | `operating_model.yaml`: no risk trigger applies — this is an ordinary low-risk sprint plan with no new security/write/deployment/release authority, no material conductor-orchestrator disagreement, no ambiguous mandate boundary, no resource limit exception, and no authority/ownership drift signal |
| Deferred sprint | S7-ContractAudit | Cross-boundary contract audit follows after smoke suite is healthy |
| Workspace preflight receipt | Deferred to orchestrator | Cannot probe Claude/Antigravity worktrees from this conductor session |

## 9. Deferred Sprint Preview — S7-ContractAudit

After S6-DiarySmoke closes with a clean smoke suite, the next sprint is
S7-ContractAudit: Yuri's requested bounded Ariadne cross-boundary contract
audit. The scope is duplicated operational facts across orchestration surfaces:

- **Artifact path identity:** Does every artifact reference (plan, review,
  completion, closeout, receipt) consistently name the same path without stale
  or conflicting paths?
- **Packet/lane identity:** Do worker lane designations (D-1, D-2, B-1, etc.)
  stay consistent across plan, dispatch, submission, and review packets?
- **Worktree/branch identity:** Do agent worktree paths, branches, and
  `handoff/current` references remain aligned across the AGENTS.md and
  orchestration docs?
- **Settings fingerprint:** Is the fingerprint recorded in the handover doc
  consistent with what the fingerprint generator produces from the committed
  `orchestration/harness_settings/` directory?
- **Model/reasoning:** Do recorded model and reasoning levels match the
  declared resource profiles in `worker_pool.yaml` and
  `deepcode_model_profile.yaml`?
- **Authority state:** Is the conductor/orchestrator/verifier authority
  separation correctly recorded in every plan and closeout?

This is a docs/orchestration quality sprint with no runtime, provider, database,
write, deployment, or production gate changes. 1–2 DeepSeek Flash lanes should
suffice.

## 10. Sprint Engine State

**Sprint engine: continuing.** The continuous sprint engine (`operating_model.yaml`)
is enabled. S5 is closed. This S6 plan defines and allocates the next sprint.
After orchestrator acceptance, execution begins without conversational handback.

No user pause condition is triggered: the sprint does not change mandate/scope,
involve a material product choice, require new security/write/deployment/release
authority, present conflicting valid evidence, involve an unresolvable boundary
disagreement, or require external credentials or human-only actions.

STATUS: complete
