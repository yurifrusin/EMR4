# Independent red/veto packet: AES-C1 provider-free admission rehearsal

Date: 2026-08-11

Decision required: exactly one structured `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\aes-c1-gemini-red`
- Branch: `codex/review-aes-c1-provider-free-admission`
- Plan baseline: `d47010743d25e05d7d758f91507179374a91bb04`
- Candidate: `285e60216cf22907e8a0f5596ece11f74f455c81`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First read `AGENTS.md` completely and perform its five-source rehydration,
naming `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree` in the review.

## Purpose

Independently challenge whether candidate HEAD implements the frozen AES-C1
provider-free, unmounted, authored-synthetic admission rehearsal against the
exact accepted AES-C0 contract. This is a security veto, not a code-style
endorsement. Search for ways malformed, undeclared, stale, revoked,
cross-generation, over-budget or candidate-controlled content could reach
`allow`, emit over-broad evidence, or silently open runtime authority.

## Exact allowed read surface

Read only these paths plus the exact baseline-to-candidate diff for them:

- `AGENTS.md`
- `implementation_plan.md`
- `docs/raisa-agent-execution-surface-containment-gate-plan.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c0-plan.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c0-architecture.md`
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c0-threat-model-delta.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c1-provider-free-admission-plan.md`
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c1-provider-free-admission-threat-model-delta.md`
- `docs/api-spine/manifest.json`
- `docs/api-spine/permission-matrix.json`
- `docs/api-spine/graphql/schema.graphql`
- `docs/api-spine/events/committed-events.json`
- `orchestration/api_spine_adr.md`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/architecture-contract.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c0/authored-synthetic-contract-examples.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/authored-synthetic-admission-scenarios.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/provider-free-admission-evidence.json`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c0_acceptance.py`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py`
- `scripts/verify_repository.py`
- `orchestration/harness_settings/python_source_state.json`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c0.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c1.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_plan.py`
- `tests/test_api_spine_artifacts.py`
- `tests/test_python_source_state.py`

Do not open blue worker packets, blue closeout, DeepSeek receipts, Sol recovery
notes, prior review artifacts, agent-error history, protected holdout/support/
authoring/manifest/seal/receipt/per-case evidence, historical Diary, branding,
patient, product-derived, licensed or unrelated paths. Do not perform a
repository-wide search outside the exact surface above.

## Required adversarial challenges

Verify and report:

1. exact candidate HEAD, branch and clean checkout before and after review;
2. the three accepted AES-C0 files match the frozen SHA-256 values and no C0
   message or reason vocabulary is widened;
3. the contract and every nested rule are closed and exact, including existing
   inherited digest values, digest rules, precedence, denial policy, all budget
   dimensions, scenario registry and zero-runtime boundary;
4. the exact 45 scenario IDs remain 2 allow, 25 deny and 18 stop, with no
   duplicate, undeclared or silently skipped scenario;
5. `allow` requires the full current manifest/grant/lease/current-generation/
   current-authority/proofreader/budget intersection; no candidate field can
   select capability, adapter, destination, method, URL, source, executable,
   credential, SQL, path, command or cleanup identity;
6. malformed objects, arbitrary nested fields and changed contract rules fail
   closed. Independently mutate both an existing inherited digest and benign
   candidate typed/proposal keys and confirm none can reach `allow`;
7. stop/deny precedence makes kill, effective revocation, generation replay,
   manifest/supply-chain mismatch, temporal invalidity and stale/mismatched
   current authority outrank an otherwise valid grant;
8. prospective/cumulative accounting covers all 19 AES-C0 counters, a zero
   ceiling disables only a requested positive counter, a reached positive
   ceiling blocks the next operation, and denial/boundary-probe exhaustion is
   terminal without transfer between generations;
9. every result is an exact AES-C0 `BrokerDecision` plus minimized
   `AuditEvidenceEnvelope`; candidate/budget/manifest digests are recomputed,
   and evidence contains no prompt, reasoning, credential, exception, patient
   or product value;
10. the evaluator has no dispatch function and performs no runtime start,
    adapter execution, provider/model call, network, database/source/watcher,
    executable tool, command/write, deployment, production or release action;
11. GraphQL remains read-only, events remain signals for fresh authorized
    reads, provider failure remains explicit `intelligence_unavailable`, and
    product commands remain separately authorised REST/OpenAPI paths; and
12. focused tests, Ruff, Git whitespace and clean postcondition all pass.

Run at least:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-aes-c1-gemini tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c0.py tests\test_raisa_agent_execution_surface_containment_gate_plan.py tests\test_api_spine_artifacts.py tests\test_python_source_state.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_agent_execution_surface_containment_gate_aes_c1_admission.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py scripts\verify_repository.py
git diff --check d47010743d25e05d7d758f91507179374a91bb04..285e60216cf22907e8a0f5596ece11f74f455c81
git rev-parse HEAD
git status --short --branch
```

## Forbidden actions

Do not edit, generate evidence, format, commit, push, start a runtime/container/
database, contact a provider or product surface, access any protected or
sensitive path, inspect `docs/branding/`, move refs or accept your own output.

## Decision rule

Return `revision_required` for any critical/high finding, default-denial bypass,
wrong digest/precedence, scenario drift, incomplete budget/revocation behavior,
over-broad evidence, API Spine/runtime widening, missing required deterministic
evidence, wrong HEAD or dirty postcondition. Otherwise return `pass`. Put all
findings, commands/counts, exact HEAD and post-review cleanliness in `review`.
