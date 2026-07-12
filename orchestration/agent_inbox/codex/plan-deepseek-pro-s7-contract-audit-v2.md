# Conductor Sprint Plan — S7 Cross-Boundary Contract Audit (V2)

| Field | Value |
|---|---|
| Plan ID | `plan-deepseek-pro-s7-contract-audit-v2` |
| Sprint ID | S7 |
| Role | conductor |
| Conductor resource | `deepseek-pro-conductor-fallback` (DeepSeek 4 Pro, high reasoning, this session) |
| Date | 2026-07-13 |
| Status | amended_from_orchestrator_rejoinder |
| Settings fingerprint | `sha256:5219e8da3f6fee463b5f5c0ef9c48ba3fd00ba26afed15d3de4a9d6db62db077` |
| direction_dialogue_disposition | `fable_rejoinder_accepted_with_amendment` |

## 1. Rejoinder Summary

Sol (GPT orchestrator) returned a one-permitted rejoinder under
`direction_collaboration.yaml` raising 6 concrete issues with the original
Conductor plan. The Conductor has final say. Every issue is accepted and
addressed; the plan shape shifts from test-only contracts to a thin executable
acceptance module + CLI with focused tests, plus the revealed stale-settings
omissions.

## 2. What Changes From V1

| V1 Approach | V1 Issue | V2 Resolution |
|---|---|---|
| Test-only contract assertions about review acceptance | Sol #1: Tests don't stop wrong-worktree acceptance | Thin `orchestration_harness/review_acceptance.py` + CLI that **executes** the checks before acceptance |
| Test references `artifact_path` field | Sol #2: PTY receipts use `artifact`, not `artifact_path` | All new code uses `artifact` (matching `runner.mjs` line 277) |
| Test asserts `unknown` classification won't happen | Sol #3: Cannot prove model/tool-supplied classification | Codify dual path: executable review in authorized envelope, or static LLM veto over deterministic evidence receipt |
| Marker contract described in tests only | Sol #4: Marker check needed before launch/acceptance | Acceptance module checks `decision`/`completion` markers from `runner.mjs` regexes before acceptance |
| Test-only scratch/output containment | Sol #5: Executable contract must reject scratch + worker counts | Acceptance module enforces: only declared `artifact` + orchestrator-collected evidence are authoritative |
| Six stale assertions reconciled (6/6) | Sol #6: `permission_prompts_are_not_authority` omission | V2 covers 7 repairs: 6 stale assertions + 1 missing quirk on `deepseek-pro-conductor-fallback` |

## 3. Sprint Purpose

Same as V1 but with an executable acceptance spine instead of test-only contracts.
S7 repairs the duplicated facts and executable boundaries that caused S6 friction
without adding bureaucracy. The key deliverable is a thin
`orchestration_harness/review_acceptance.py` module with a `scripts/` CLI that the
orchestrator can run before accepting any worker review artifact.

## 4. Scope

**In scope** — seven concrete repairs (V1's six plus the quirk omission):

1. **Reconcile `tests/test_ariadne_deepcode_adapter_settings.py`** — six stale
   assertions (detailed in §5.1).

2. **Add `permission_prompts_are_not_authority` quirk** to
   `deepseek-pro-conductor-fallback` in `worker_pool.yaml`. Verifier (line 86)
   and workers (line 99) have it; the pro-conductor-fallback (line 60) is missing
   it. This is a genuine omission: every `cli_interactive` resource must carry
   this quirk because permission prompts are transport decisions, not authority.

3. **Artifact-kind / marker contract** — moved from test-only to the acceptance
   module. The module extracts `decision` and `completion` regexes from
   `runner.mjs` and validates artifacts against the canonical form before
   acceptance.

4. **Worktree-anchored verification receipt** — executable check via the
   acceptance module: declared worktree path, `git rev-parse HEAD`,
   `git merge-base --is-ancestor <candidate> HEAD`. Test proves the module
   rejects wrong-worktree, wrong-branch, and non-ancestor candidates.

5. **Permission-safe dual execution path** — codified in the acceptance module
   rather than asserted as impossible. Path A: executable review when commands
   stay in the authorized permission envelope (`allow: [read-in-cwd,
   write-in-cwd, query-git-log]`, `deny: [read-out-cwd, write-out-cwd,
   delete-in-cwd, delete-out-cwd, mutate-git-log, network, mcp]`). Path B: static
   LLM veto over orchestrator-produced deterministic evidence receipt when shell
   execution is permission-blocked. Neither path may auto-answer prompts or
   broaden filesystem/network access.

6. **Scratch output containment** — the acceptance module's
   `validate_review_artifact()` only accepts the declared `artifact` path; any
   other file (scratch logs, stdout captures, temp files) is rejected. A
   dedicated negative test proves this.

7. **Canonical test-count receipt** — the acceptance module parses `pytest
   --collect-only -q` output and extracts the authoritative count. Worker
   self-reported counts are flagged as mismatched. The module does not accept
   worker-reported counts as evidence.

**Still out of scope (unchanged from V1):**

- No change to `app/`, backend routes, schemas, services, database, or migrations.
- No Bernie D5 expansion, no provider/live-provider wiring, no memory/RAG/GraphRAG access.
- No H15/H-series, historical diary runtime, or `local_data` access.
- No deployment, Pages, GraphQL readiness, telemetry, or production claims.
- No external patient-client exposure.
- No terminal-status product-policy decision.
- No monetary or wall-clock caps.
- No new runtime, provider, database, write, deployment, or release authority.

**All runtime gates remain closed.**

## 5. Detailed Repairs

### 5.1 Stale Settings Assertions (Repairs 1–7)

File: `tests/test_ariadne_deepcode_adapter_settings.py`

| # | Test | Current assertion | V2 change | Reason |
|---|---|---|---|---|
| 1 | `test_two_deepcode_resources_defined` | `== 2` | `== 3` | pro-conductor-fallback is a third `cli_interactive` resource |
| 2 | `test_verifier_and_worker_resource_ids_match` | `[deepseek-flash-verifier, deepseek-flash-workers]` | Add `deepseek-pro-conductor-fallback` to sorted expected list | Third resource already exists in `worker_pool.yaml` |
| 3 | `test_all_deepcode_resources_default_model_is_flash` | All must be Flash | Add exception for `deepseek-pro-conductor-fallback` (defaults to `deepseek-v4-pro` per `worker_pool.yaml` line 61); keep Flash for verifier and worker lanes | Approved Pro default is intentional |
| 4 | `test_all_deepcode_resources_default_reasoning_is_high` | All must be `high` | No change needed — Pro-fallback already uses `high` | Assertion remains correct with third resource |
| 5 | `test_no_deepcode_resource_defaults_to_pro` | No resource may default to Pro | **Remove.** Replace with `test_conductor_fallback_may_default_to_pro_but_workers_and_verifier_must_not` | Negative assertion conflicts with approved Pro-fallback resource |
| 6 | `test_adapter_resource_ids_are_correct` | `[deepseek-flash-verifier, deepseek-flash-workers]` | `[deepseek-flash-verifier, deepseek-flash-workers, deepseek-pro-conductor-fallback]` | `transport_adapters.yaml` line 4 already includes it |
| 7 | `test_all_deepcode_resources_deny_integration_authority` | Asserts `permission_prompts_are_not_authority` on every `cli_interactive` resource | **No test change.** But the data in `worker_pool.yaml` must also gain the quirk on `deepseek-pro-conductor-fallback` (line 60) | Quirk is genuinely absent — Sol #6 identified a real omission |

**Worker pool data change (repair 7 companion):** Add `permission_prompts_are_not_authority` to `deepseek-pro-conductor-fallback.transport_quirks` in `orchestration/harness_settings/worker_pool.yaml` line 60. This makes the existing `test_all_deepcode_resources_deny_integration_authority` test pass for the third resource instead of silently passing because it wasn't in the `cli_interactive` filter. Existing test line 147 filters by `transport == "cli_interactive"` — the pro-conductor-fallback is already included in that filter, so the test would fail once it's a third resource unless the quirk is present.

### 5.2 New Acceptance Module: `orchestration_harness/review_acceptance.py`

A thin Python module with one exported function and one CLI entry point. This
is the spine of S7 — it replaces the V1 test-only posture with an executable
gate that the orchestrator (or any review-acceptance workflow) runs before
accepting a worker artifact.

```python
def validate_review_artifact(
    *,
    artifact: Path,
    artifact_kind: Literal["decision", "completion"],
    review_worktree: Path,
    expected_branch: str,
    candidate_commit: str,
    pytest_collect_output: str,
) -> dict[str, Any]:
```

**Checks performed (in order, fail-fast):**

1. **Artifact existence and path:** `artifact` must exist; must match the declared
   path exactly. The field name is `artifact` (matching `runner.mjs` line 277),
   not `artifact_path`.

2. **Artifact validity:** Content must satisfy `validArtifact()` logic from
   `runner.mjs`:
   - `artifact_kind == "decision"` → must contain a line matching
     `/^DECISION:\s*(pass|revision_required)$/i`
   - `artifact_kind == "completion"` → must contain a line matching
     `/^STATUS:\s*complete$/i`
   - `VERDICT: PASS`, `STATUS: complete` on a decision artifact, or
     `DECISION: pass` on a completion artifact are all rejected.

3. **Worktree verification:**
   - `review_worktree` must exist and be a directory.
   - `git rev-parse HEAD` in the worktree must succeed.
   - `git merge-base --is-ancestor <candidate_commit> HEAD` in the worktree must
     return exit code 0 (the candidate is in the worktree's ancestry).

4. **Pytest collection as authoritative evidence:**
   - Parse `pytest --collect-only -q` output, extract `N tests collected` or
     `filename.py: N` count.
   - The orchestrator's collection output is the authoritative test count.
   - Worker self-reported counts are explicitly flagged as non-authoritative.

5. **Scratch output rejection:**
   - Only the declared `artifact` path is acceptance-bearing.
   - The function does not look at any other file; it cannot accidentally
     accept scratch logs, stdout captures, or temp files.

**Return value:**
```json
{
  "schema_version": "ariadne.review_acceptance.v1",
  "status": "accepted" | "rejected",
  "artifact": "<relative path>",
  "artifact_kind": "decision" | "completion",
  "artifact_decision": "pass" | "revision_required" | null,
  "worktree_verified": true | false,
  "ancestry_verified": true | false,
  "pytest_count": <int> | null,
  "pytest_collection_authoritative": true,
  "scratch_outputs_ignored": true,
  "rejection_reasons": [...]
}
```

**CLI:** `scripts/ariadne_review_acceptance.py`
```bash
.venv\Scripts\python.exe scripts\ariadne_review_acceptance.py \
  --artifact <path> \
  --artifact-kind decision \
  --review-worktree <path> \
  --expected-branch codex/s7-contract-audit-repair \
  --candidate-commit <sha> \
  --pytest-collect <path_or_cmd>
```

Returns exit code 0 on `accepted`, 1 on `rejected`, 2 on internal error.

### 5.3 Permission-Safe Dual Execution Path

Codified in the acceptance module but implemented through the existing
`ensure_project_settings()` permission envelope:

**Path A — Executable review (commands stay in authorized envelope):**
Commands that only need `read-in-cwd`, `write-in-cwd`, `query-git-log` run
directly through the PTY adapter. The acceptance module's `validate_review_artifact()`
is itself an example: it reads files, writes only the receipt, and queries git log.

**Path B — Static LLM veto (shell execution is permission-blocked):**
When a command would require `read-out-cwd`, `network`, or `unknown`
classification, the orchestrator produces a deterministic evidence receipt
(collection output parsed from a permitted checkout, git log output, diff stats)
and presents it to the LLM for a static veto. The LLM may only review the
provided deterministic evidence; it cannot call tools, browse files, or access
the network.

**Dual-path test (in `tests/test_ariadne_review_acceptance.py`):**
- Test that Path A commands (`git rev-parse`, `pytest --collect-only` inside cwd)
  pass through without unknown/permission classification.
- Test that Path B refuses to auto-answer prompts and requires the orchestrator
  to supply deterministic evidence.
- Test that neither path broadens the `allow` list or removes from `deny`.

### 5.4 Marker Compatibility at Launch (Not Only After)

The acceptance module's `validate_review_artifact()` is the pre-acceptance gate.
It uses the actual `decision`/`completion` regexes from `runner.mjs` lines 67–68.
This means:

- Before dispatch: the conductor confirms the artifact-kind matches the worker
  packet's expected marker.
- Before acceptance: `validate_review_artifact()` checks the artifact against the
  canonical regex.
- After completion: the adapter receipt's `artifact` field (not `artifact_path`)
  is cross-referenced.

Tests in `tests/test_ariadne_review_acceptance.py` prove:
- `DECISION: pass` → `status: accepted`, `artifact_decision: pass`
- `DECISION: revision_required` → `status: accepted`, `artifact_decision: revision_required`
- `STATUS: complete` on completion artifact → `status: accepted`
- `VERDICT: PASS` on decision artifact → `status: rejected`
- `DECISION: pass` on completion artifact → `status: rejected`
- `STATUS: complete` on decision artifact → `status: rejected`
- Markdown table cell with `DECISION: pass` → still matches (runner.mjs splits on `|`)

## 6. Worker Allocation

### Claude — NOT USED

Claude subscription reported a real session limit. Fable and Opus share that
unavailable account window. Per cost-control allocation order
[Fable, Opus, DeepSeek Pro, GPT Sol], Fable and Opus are unavailable.

### Antigravity — NOT USED

This sprint is a mechanical contract audit with no consumer/UX rendering surface
change. Standing down Antigravity conserves quota for a later sprint where its
distinct consumer-UI veto adds value.

### DeepSeek Flash — 2 WORKER LANES

Per `worker_pool.yaml`, `deepseek-flash-workers` allows up to 3 instances. Two
lanes allocated; one reserved.

#### Lane 1: Implementation Owner — `deepseek-s7-contract-audit-v2-repair`

| Field | Value |
|---|---|
| Resource | `deepseek-flash-workers` (instance 1) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY, durable artifact required) |
| Branch | `codex/s7-contract-audit-v2-repair` |
| Role | Implementation owner |
| Capabilities | implementer, test_engineer |
| Independence label | Not independent — owns the implementation surface |

**Mission:** Implement all seven repairs in a single cohesive changeset.

**Files touched:**

1. `tests/test_ariadne_deepcode_adapter_settings.py` — six stale assertion repairs
   (rows 1–6 in §5.1 table).
2. `orchestration/harness_settings/worker_pool.yaml` — add
   `permission_prompts_are_not_authority` to `deepseek-pro-conductor-fallback`
   quirks (line 60).
3. `orchestration_harness/review_acceptance.py` — new thin acceptance module.
4. `scripts/ariadne_review_acceptance.py` — new CLI entry point.
5. `tests/test_ariadne_review_acceptance.py` — new focused acceptance tests.
6. `tests/test_ariadne_deepcode_adapter_settings.py` — add `TestArtifactMarkerContract`
   (now extracting from `runner.mjs` source plus exercising acceptance module).

**Evidence required:**

1. Before: `pytest tests/test_ariadne_deepcode_adapter_settings.py -v` → 7
   failures (6 stale assertions + 1 quirk omission surfacing through the
   existing `test_all_deepcode_resources_deny_integration_authority`).
2. After: `pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -v` → 0 failures.
3. `git diff --stat` shows only permitted files.
4. `git diff --check` → clean.
5. No `app/`, no non-test/harness Python file changes beyond the declared audit surface.
6. No runtime gate opened.

**Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s7-contract-audit-v2-repair.md`

#### Lane 2: Independent Review/Veto — `deepseek-s7-contract-audit-v2-review`

| Field | Value |
|---|---|
| Resource | `deepseek-flash-workers` (instance 2) |
| Model | `deepseek-v4-flash` / high |
| Transport | Deep Code (interactive TTY, durable artifact required) |
| Branch | `codex/s7-contract-audit-v2-review` |
| Role | Independent review/veto |
| Capabilities | code_reviewer, security_reviewer, test_engineer |
| Independence label | Independent — runs tests and audits boundary without touching implementation |

**Mission:** Cross-review the Lane 1 fix. Read the Lane 1 completion artifact
and diff. Run the full adapter-settings + acceptance suite independently. Verify:

- All seven stale repairs pass; no test weakening (no skip/xfail, no assertion
  downgrade from equality to subset).
- Pro-fallback resource now carries `permission_prompts_are_not_authority` quirk;
  verifier/worker lanes still require Flash.
- Acceptance module correctly rejects `VERDICT:`, wrong-kind markers, non-ancestor
  candidates, wrong-worktree paths, scratch outputs, and worker self-reported counts.
- Acceptance module uses field `artifact` (not `artifact_path`).
- Dual-path contract is tested: Path A commands are in the authorized envelope;
  Path B refuses auto-answer and requires orchestrator evidence.
- No `app/`, no non-test-file changes beyond the declared audit surface.
- No runtime/provider/database/write/deployment gate opened.

**Evidence:**
- Independent `pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -v` → 0 failures.
- Manual run of `scripts/ariadne_review_acceptance.py` with a valid fixture artifact → exit 0.
- Manual run of `scripts/ariadne_review_acceptance.py` with a `VERDICT:` artifact → exit 1.
- Boundary check: no `app/` changes, no non-permitted file changes.
- `DECISION: pass` or `DECISION: revision_required` with specific findings.

**Worker packet:** `orchestration/agent_inbox/deepcode/deepcode-s7-contract-audit-v2-review.md`

## 7. Ownership Boundaries

| Surface | Owner | Review |
|---|---|---|
| `tests/test_ariadne_deepcode_adapter_settings.py` (6 stale repairs) | Lane 1 | Lane 2 |
| `orchestration/harness_settings/worker_pool.yaml` (quirk addition) | Lane 1 | Lane 2 |
| `orchestration_harness/review_acceptance.py` (new) | Lane 1 | Lane 2 |
| `scripts/ariadne_review_acceptance.py` (new) | Lane 1 | Lane 2 |
| `tests/test_ariadne_review_acceptance.py` (new) | Lane 1 | Lane 2 |
| `orchestration/deepcode_pty/runner.mjs` (read-only, regex source) | Neither | Lane 2 verifies correctness |

Lane 1 writes all files. Lane 2 reads the diff and runs the suite independently.
No file overlap between lanes.

## 8. Acceptance Evidence

| Gate | Check | Owner |
|---|---|---|
| Adapter settings suite clean | `pytest tests/test_ariadne_deepcode_adapter_settings.py -v` → 0 failures | Lane 2 + Orchestrator |
| Acceptance module tests clean | `pytest tests/test_ariadne_review_acceptance.py -v` → 0 failures | Lane 2 + Orchestrator |
| No test weakening | No skip/xfail added; no assertion downgraded | Lane 2 |
| Pro-fallback quirk present | `permission_prompts_are_not_authority` on every `cli_interactive` resource | Lane 2 |
| Pro-fallback exception contained | Verifier/worker lanes still require Flash; only conductor-fallback may use Pro | Lane 2 |
| Marker contract correct | `DECISION:` canonical form exactly matches `runner.mjs` regex; `VERDICT:` rejected | Lane 2 |
| Field naming correct | All new code uses `artifact` (not `artifact_path`) | Lane 2 |
| Worktree receipt executable | Acceptance module rejects wrong-worktree, wrong-branch, non-ancestor candidates | Lane 2 |
| Dual-path contract tested | Path A stays in envelope; Path B refuses auto-answer; neither broadens access | Lane 2 |
| Scratch containment | Only declared `artifact` path is acceptance-bearing | Lane 2 |
| Test-count authority | Collection output, not worker self-report, is canonical | Lane 2 |
| No gate openings | No D5/provider/memory/RAG/H15/trove/write/deployment gate opened | Lane 2 + Orchestrator |
| Whitespace | `git diff --check` → clean | Orchestrator |

## 9. Verification Plan (Orchestrator)

After both lanes submit:

```powershell
git fetch origin codex/s7-contract-audit-v2-repair codex/s7-contract-audit-v2-review
git diff origin/master...origin/codex/s7-contract-audit-v2-repair --stat
# Expected: tests/test_ariadne_deepcode_adapter_settings.py
#           orchestration/harness_settings/worker_pool.yaml
#           orchestration_harness/review_acceptance.py
#           scripts/ariadne_review_acceptance.py
#           tests/test_ariadne_review_acceptance.py

pytest tests/test_ariadne_deepcode_adapter_settings.py tests/test_ariadne_review_acceptance.py -v
# Expected: 0 failures

git diff --check origin/master...origin/codex/s7-contract-audit-v2-repair
# Expected: clean

# Boundary audit:
git diff origin/master...origin/codex/s7-contract-audit-v2-repair --name-only
# Expected: no app/, no non-test/harness changes beyond the audit surface

# Acceptance module CLI smoke:
.venv\Scripts\python.exe scripts\ariadne_review_acceptance.py --help
# Expected: usage output

# Fixture-driven CLI tests (orchestrator produces these fixtures):
.venv\Scripts\python.exe scripts\ariadne_review_acceptance.py \
  --artifact tests/fixtures/review_acceptance/valid_decision_pass.md \
  --artifact-kind decision \
  --review-worktree . \
  --expected-branch master \
  --candidate-commit $(git rev-parse HEAD) \
  --pytest-collect "tests/fixtures/review_acceptance/collect_output.txt"
# Expected: exit 0, status "accepted"
```

## 10. Fallback Reason And Reduced Independence

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

## 11. Independent LLM Verifier

**Not risk-triggered.** This sprint adds a thin executable acceptance module,
focused tests, and repairs seven stale settings assertions. It creates no new
security/write/deployment/release authority. No conductor-orchestrator material
disagreement (the rejoinder's six issues are all accepted). No ambiguous mandate
or scope boundary. No resource limit exception. No authority or ownership drift
signal.

Deterministic checks (full adapter settings + acceptance suite, `git diff --check`,
boundary audit) remain mandatory. An independent LLM verifier is not required
under the current risk classification.

## 12. Unfilled Obligations

| Obligation | Status | Reason |
|---|---|---|
| Claude lane | Not filled | Unavailable (subscription limit) |
| Antigravity lane | Not filled | No consumer/UX surface; quota conserved |
| Independent LLM verifier | Not required | Risk classification: mechanically bounded test + module repair, no new authority |
| Workspace preflight receipt | Deferred to orchestrator | Cannot probe worktrees from this conductor session |

## 13. Sprint Engine State

**Sprint engine: continuing.** S6 is closed through `b1292c49` with a clean
139-test smoke suite. S7 is the next automatic sprint per
`autonomous_continuation.yaml`. The V2 plan addresses all six rejoinder issues
without expanding scope or introducing new bureaucracy.

No user pause condition is triggered: the audit repair is mechanically bounded
(seven stale settings reconciled, thin executable acceptance module added),
preserves all existing security boundaries, and opens no runtime gate.

## 14. Next Sprint Transition

After S7 closes with a zero-failure adapter settings + acceptance suite and
verified executable acceptance gate, the next sprint should be determined by the
sprint engine from the current programme state. Likely candidates include the
H22 semantic gate-review prototype, Bernie Interpretation Harness runtime wiring
(gated behind H56/H63 readiness checks), or a broader Diary grammar consumer
sprint now that the orchestration contract surface is tightened.

## 15. Rejoinder Disposition

| Sol Issue | Conductor Response | V2 Change |
|---|---|---|
| #1: Tests alone don't stop wrong-worktree acceptance | Accepted | Thin `orchestration_harness/review_acceptance.py` + CLI added |
| #2: PTY receipts use `artifact` not `artifact_path` | Accepted | All new code uses `artifact` |
| #3: Cannot prove `unknown` classification impossible | Accepted | Dual path codified: executable review in envelope, or static LLM veto over deterministic evidence |
| #4: Marker check needed before launch/acceptance | Accepted | Acceptance module extracts `runner.mjs` regexes; checks at acceptance time |
| #5: Scratch + worker counts rejected by executable contract | Accepted | `validate_review_artifact()` enforces: only declared artifact + orchestrator collection evidence |
| #6: `permission_prompts_are_not_authority` omission | Accepted (and found real) | Repair 7 adds the quirk to `deepseek-pro-conductor-fallback`; existing test would fail without it |

STATUS: complete
