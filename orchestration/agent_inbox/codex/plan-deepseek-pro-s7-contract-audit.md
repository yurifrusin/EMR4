# Conductor Sprint Plan — S7 Cross-Boundary Contract Audit

| Field | Value |
|---|---|
| Plan ID | `plan-deepseek-pro-s7-contract-audit` |
| Sprint ID | S7 |
| Role | conductor |
| Conductor resource | `deepseek-pro-conductor-fallback` (DeepSeek 4 Pro, high reasoning, this session) |
| Date | 2026-07-13 |
| Status | awaiting_orchestrator_acceptance |
| Settings fingerprint | `sha256:5219e8da3f6fee463b5f5c0ef9c48ba3fd00ba26afed15d3de4a9d6db62db077` |
| direction_dialogue_disposition | `obvious_work_skipped` |

## 1. Sprint Purpose

Yuri requested a bounded Ariadne cross-boundary contract audit. The S6 closeout
identified six specific audit seeds that caused real friction during S6
execution. This sprint repairs the duplicated facts and executable boundaries
without adding bureaucracy.

## 2. Scope

**In scope** — the six S6 audit seeds, each with a concrete repair:

1. **`tests/test_ariadne_deepcode_adapter_settings.py`** — six stale assertions
   that assume exactly two `cli_interactive` resources (`deepseek-flash-verifier`
   and `deepseek-flash-workers`) and Flash defaults for every resource. Reconcile
   with the approved `deepseek-pro-conductor-fallback` (Pro default, high
   reasoning, conductor capability). The `worker_pool.yaml` and
   `transport_adapters.yaml` already include the third resource; the test
   contract is the only stale surface.

2. **Artifact-kind / packet marker mismatch** — `runner.mjs` validates
   `DECISION:` (canonical form), but worker artifacts can produce `VERDICT:` or
   other non-canonical markers. Add a focused contract test that asserts the
   canonical `DECISION:` marker is the only accepted decision-kind artifact
   surface, and that `VERDICT:` alone fails validation.

3. **Worktree-anchored verification receipts** — the first Lane 2 PASS was
   invalidated because the orchestrator ran a cherry-pick in the integration
   worktree instead of the review worktree. Add a contract test asserting that
   candidate-ancestry evidence (target worktree, expected branch, `git merge-base
   --is-ancestor`) is machine-checkable before accepting review output.

4. **Permission-safe test execution path** — strict DeepCode permissions
   (`deny: [read-out-cwd, write-out-cwd, network]`) blocked external-venv test
   commands classified as `unknown` or outside-worktree reads. Add a contract
   test proving the deterministic-test-plus-static-review path works without
   relaxing permissions.

5. **Scratch output containment** — worker scratch logs escaped declared
   artifact names during S6. Add a contract test asserting that only the
   declared artifact path is acceptance-bearing; scratch outputs are
   non-authoritative.

6. **Canonical test-count receipts** — worker artifacts misstated test counts
   during S6. Add a focused contract test proving that authoritative test count
   comes from `pytest --collect-only` collection, not worker self-report.

**Still out of scope:**

- No change to `app/`, backend routes, schemas, services, database, or
  migrations.
- No Bern/i D5 expansion, no provider/live-provider wiring, no memory/RAG/
  GraphRAG access.
- No H15/H-series, historical diary runtime, or `local_data` access.
- No deployment, Pages, GraphQL readiness, telemetry, or production claims.
- No external patient-client exposure.
- No terminal-status product-policy decision.
- No monetary or wall-clock caps.
- No new runtime, provider, database, write, deployment, or release authority.

**All runtime gates remain closed.**

## 3. Worker Allocation

### Claude — NOT USED

Claude subscription reported a real session limit. Fable and Opus share that
unavailable account window. Per `cost_controls.yaml` clause 17, the allocation
order is [Fable, Opus, DeepSeek Pro, GPT Sol]. Fable and Opus are unavailable.

### Antigravity — NOT USED

This sprint is a mechanical contract audit with no consumer/UX rendering surface
change. Standing down Antigravity conserves quota for a later sprint where its
distinct consumer-UI veto adds value. Per `sprint_worker_policy.yaml` clause
11, Antigravity should stand down when there is no distinct artifact or veto
surface.

### DeepSeek Flash — 2 WORKER LANES

Per `worker_pool.yaml`, `deepseek-flash-workers` allows up to 3 instances. Two
lanes are allocated here. A third is reserved for future sprints.

#### Lane 1: Implementation Owner — `deepseek-s7-contract-audit-repair`

| Field | Value |
|---|---|
| Resource | `deepseek-flash-workers` (instance 1) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY, durable artifact required) |
| Branch | `codex/s7-contract-audit-repair` |
| Role | Implementation owner |
| Capabilities | implementer, test_engineer |
| Independence label | Not independent — owns the implementation surface |

**Mission:** Repair the six audit seeds in a single cohesive changeset.

**(1) Reconcile `tests/test_ariadne_deepcode_adapter_settings.py`:**

- `test_two_deepcode_resources_defined`: Change `== 2` to `== 3` (verifier,
  workers, pro-conductor-fallback).
- `test_verifier_and_worker_resource_ids_match`: Add `deepseek-pro-conductor-fallback`
  to the sorted expected list.
- `test_all_deepcode_resources_default_model_is_flash`: Add an exception for
  `deepseek-pro-conductor-fallback`, which legitimately defaults to
  `deepseek-v4-pro` (per `worker_pool.yaml` line 61). Keep Flash requirement
  for verifier and worker lanes.
- `test_all_deepcode_resources_default_reasoning_is_high`: Pro-fallback already
  uses `high`; this test should still pass with the third resource.
- `test_no_deepcode_resource_defaults_to_pro`: **Remove.** This negative
  assertion conflicts with the approved `deepseek-pro-conductor-fallback`
  resource that legitimately defaults to Pro. Replace it with a focused
  positive test: `test_conductor_fallback_may_default_to_pro_but_workers_and_verifier_must_not`.
- `test_adapter_resource_ids_are_correct` in
  `TestTransportAdapterDeepCodeContract`: Change expected list from 2 to 3
  entries, adding `deepseek-pro-conductor-fallback` (already present in
  `transport_adapters.yaml` line 4).

**(2) Normalize artifact-kind / marker contract:**

Add a new test class `TestArtifactMarkerContract` asserting:
- `runner.mjs` line 68 regex `/^DECISION:\s*(pass|revision_required)$/i` is the
  canonical decision surface.
- `VERDICT: PASS` (upper case, different keyword) does **not** satisfy the
  decision-kind regex.
- `STATUS: complete` (lower case) does **not** satisfy the decision-kind regex.
- `DECISION: pass` (canonical) satisfies the regex.
- The `completion` artifact-kind (`/^STATUS:\s*complete$/i`) is a separate
  validation path that must not be used for decision-bearing agent artifacts.

This test should load `runner.mjs`, extract the regex, and assert these cases
programmatically so it stays in sync with the runner source.

**(3) Worktree-anchored verification receipt:**

Add a contract test in `tests/test_ariadne_deepcode_adapter_settings.py` (or a
new focused test file) asserting that candidate-ancestry evidence is
machine-checkable:
- A review worktree path must be declared.
- The review worktree HEAD must be verifiable via `git rev-parse HEAD`.
- The candidate commit must be in the worktree's ancestry via
  `git merge-base --is-ancestor <candidate> HEAD`.
- A review artifact that cannot prove ancestry is not acceptance evidence.

This is a test-only contract; it does not create a new runtime module.

**(4) Permission-safe test execution path:**

Add a contract test proving that a fixture worktree with strict DeepCode
permissions (`deny: [read-out-cwd, write-out-cwd, delete-in-cwd,
delete-out-cwd, mutate-git-log, network, mcp]`) can still run deterministic
`pytest --collect-only` and `node --check` inside its cwd. The test must assert
that these commands do not require `read-out-cwd`, `network`, or `unknown`
permission classification.

Use the existing `ensure_project_settings()` helper to construct the settings
payload and assert the permission envelope is sufficient.

**(5) Scratch output containment:**

Add a contract test asserting that only the `--artifact` path is
acceptance-bearing. The `runner.mjs` `validArtifact()` function is the single
gate. The test must assert:
- A file at the declared artifact path with valid content is accepted.
- A file at any other path (scratch logs, stdout capture, temp files) is not
  recognized as the artifact by the adapter.
- The receipt JSON's `artifact_path` field must match the declared path.

**(6) Canonical test-count receipt:**

Add a contract test asserting that authoritative test count comes from pytest
collection output (`pytest --collect-only -q` producing a final line like
`N tests collected` or `review/test_diary_smoke.py: N`), not from worker
self-report in the artifact body. The test should:
- Parse `pytest --collect-only -q` output and extract the canonical count.
- Assert that a worker artifact claiming a different count is flagged as
  mismatched (the orchestrator's collection is authoritative).
- Prove the pattern is deterministic (same collection count from any checkout at
  the same commit).

**Evidence required:**

1. Before: `pytest tests/test_ariadne_deepcode_adapter_settings.py -v` → 6
   failures (the stale assertions).
2. After: `pytest tests/test_ariadne_deepcode_adapter_settings.py -v` → 0
   failures.
3. All new contract tests pass.
4. `git diff --stat` shows only permitted files.
5. `git diff --check` → clean.
6. No `app/`, no non-test Python file changes beyond what the audit requires.
7. No runtime gate opened.

**Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s7-contract-audit-repair.md`

#### Lane 2: Independent Review/Veto — `deepseek-s7-contract-audit-review`

| Field | Value |
|---|---|
| Resource | `deepseek-flash-workers` (instance 2) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY, durable artifact required) |
| Branch | `codex/s7-contract-audit-review` |
| Role | Independent review/veto |
| Capabilities | code_reviewer, security_reviewer, test_engineer |
| Independence label | Independent — runs tests and audits boundary without touching implementation |

**Mission:** Cross-review the Lane 1 fix. Read the Lane 1 completion artifact
and diff. Run the full adapter-settings suite independently. Verify:

- All stale tests pass; no test weakening (no skip/xfail added, no assertion
  downgraded from equality to subset).
- The Pro-fallback resource exception does not leak to verifier/worker lanes.
- `DECISION:` canonical marker contract is accurate against `runner.mjs` source.
- Worktree-anchored receipt tests are machine-checkable without runtime modules.
- Permission-envelope test does not weaken or broaden cwd access.
- Scratch-output containment test does not create new acceptance paths.
- Test-count receipt test proves collection is authoritative, not worker
  self-report.
- No `app/`, no non-test-file changes beyond the declared audit surface.
- No runtime/provider/database/write/deployment gate opened.

**Evidence:**
- Independent `pytest tests/test_ariadne_deepcode_adapter_settings.py -v` → 0
  failures.
- Boundary check: no `app/` changes, no non-permitted file changes.
- `DECISION: pass` or `DECISION: revision_required` with specific findings.

**Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s7-contract-audit-review.md`

## 4. Ownership Boundaries

| Surface | Owner | Review |
|---|---|---|
| `tests/test_ariadne_deepcode_adapter_settings.py` (6 stale repairs) | Lane 1 | Lane 2 |
| New marker/receipt/permission/scratch/count contract tests | Lane 1 | Lane 2 |
| `runner.mjs` validation regex reference (read-only, for test assertions) | Neither (read reference only) | Lane 2 verifies correctness |
| `orchestration/harness_settings/*.yaml` (already correct, no edits) | Neither | Lane 2 audits no drift |

Lane 1 writes the test file(s). Lane 2 reads the diff and runs the suite
independently. No file overlap between lanes.

## 5. Acceptance Evidence

| Gate | Check | Owner |
|---|---|---|
| Adapter settings suite clean | `pytest tests/test_ariadne_deepcode_adapter_settings.py -v` → 0 failures | Lane 2 + Orchestrator |
| No test weakening | No skip/xfail added; no assertion downgraded | Lane 2 |
| Pro-fallback exception contained | Verifier/worker lanes still require Flash; only conductor-fallback may use Pro | Lane 2 |
| Marker contract correct | `DECISION:` canonical form exactly matches `runner.mjs` regex; `VERDICT:` does not | Lane 2 |
| Worktree receipt machine-checkable | Tests prove ancestry evidence is required and verifiable | Lane 2 |
| Permission envelope preserved | `deny` list unchanged; no `read-out-cwd` or `network` in `allow` | Lane 2 |
| Scratch containment | Only declared artifact path is acceptance-bearing | Lane 2 |
| Test-count authority | Collection output, not worker self-report, is canonical | Lane 2 |
| No gate openings | No D5/provider/memory/RAG/H15/trove/write/deployment gate opened | Lane 2 + Orchestrator |
| Whitespace | `git diff --check` → clean | Orchestrator |

## 6. Verification Plan (Orchestrator)

After both lanes submit:

```powershell
git fetch origin codex/s7-contract-audit-repair codex/s7-contract-audit-review
git diff origin/master...origin/codex/s7-contract-audit-repair --stat
# Expected: tests/test_ariadne_deepcode_adapter_settings.py ± new contract test files

pytest tests/test_ariadne_deepcode_adapter_settings.py -v
# Expected: 0 failures (6 stale assertions repaired, all new contracts pass)

# If new tests are in a separate file:
pytest tests/test_ariadne_deepcode_*.py -v
# Expected: all pass

git diff --check origin/master...origin/codex/s7-contract-audit-repair
# Expected: clean

# Boundary audit:
git diff origin/master...origin/codex/s7-contract-audit-repair --name-only
# Expected: no app/, no non-test/harness changes beyond the audit surface
```

## 7. Fallback Reason And Reduced Independence

**Fallback reason:** Claude subscription reported a real session limit. Fable
and Opus share that unavailable account window. The conductor allocation order
from `role_preferences.yaml` is [Fable, Opus, DeepSeek Pro, GPT Sol]. Fable and
Opus are unavailable, so DeepSeek 4 Pro via Deep Code is the active conductor.

**Reduced independence:** This conductor session cannot probe Antigravity or
DeepSeek worker availability from the current TTY-only Deep Code context. The
orchestrator retains responsibility for the workspace preflight receipt,
DeepSeek lane management, worker packet dispatch, sprint execution, integration,
and closeout. Antigravity is intentionally stood down (no consumer/UX surface in
this sprint). Two DeepSeek Flash lanes cover implementation and independent
review — within the 1–3 lane cap.

## 8. Independent LLM Verifier

**Not risk-triggered.** This sprint repairs test contract assertions and adds
focused contract tests. It creates no new security/write/deployment/release
authority. No conductor-orchestrator material disagreement. No ambiguous mandate
or scope boundary. No resource limit exception. No authority or ownership drift
signal.

Deterministic checks (full adapter settings suite, `git diff --check`, boundary
audit) remain mandatory. An independent LLM verifier is not required under the
current risk classification.

## 9. Unfilled Obligations

| Obligation | Status | Reason |
|---|---|---|
| Claude lane | Not filled | Unavailable (subscription limit) |
| Antigravity lane | Not filled | No consumer/UX surface; quota conserved |
| Independent LLM verifier | Not required | Risk classification: mechanically bounded test repair, no new authority |
| Workspace preflight receipt | Deferred to orchestrator | Cannot probe worktrees from this conductor session |

## 10. Sprint Engine State

**Sprint engine: continuing.** S6 is closed through `b1292c49` with a clean
139-test smoke suite. S7 is the next automatic sprint per
`autonomous_continuation.yaml`.

No user pause condition is triggered: the audit repair is mechanically bounded
(six stale test assertions updated, five targeted contract tests added),
preserves all existing security boundaries, and opens no runtime gate.

## 11. Next Sprint Transition

After S7 closes with a zero-failure adapter settings suite and verified contract
markers, the next sprint should be determined by the sprint engine from the
current programme state. Likely candidates include the H22 semantic gate-review
prototype, Bernie Interpretation Harness runtime wiring (gated behind H56/H63
readiness checks), or a broader Diary grammar consumer sprint now that the
orchestration contract surface is tightened.

STATUS: complete
