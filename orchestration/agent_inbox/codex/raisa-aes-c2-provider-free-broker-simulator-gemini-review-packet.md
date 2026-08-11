# Independent red/veto packet: AES-C2 provider-free inert broker simulator

Date: 2026-08-11

Decision required: exactly one structured `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r183`
- Branch: `codex/review-aes-c2-broker-simulator-d54f0476`
- Corrected plan/current implementation base: `bd11333d462424b40f5f8f014b1c4a945b3a5133`
- Candidate: `d54f0476448f1218cd55477d42b958721359eae8`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First read `AGENTS.md` completely and perform its five-source rehydration,
naming `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree` in the review.

## Purpose

Independently challenge whether candidate HEAD implements the frozen AES-C2
provider-free, authored-synthetic, in-process inert broker simulation over the
exact accepted AES-C0/C1 contract. This is a security veto, not a code-style
endorsement. Search for ways malformed, stale, revoked, candidate-controlled,
open or over-budget content could bypass fresh admission, choose the operation,
reach the pure adapter more than once, leak custody material, or release an
invalid result.

## Exact allowed read surface

Read only these paths plus the exact base-to-candidate diff for them:

- `AGENTS.md`
- `implementation_plan.md`
- `docs/raisa-agent-execution-surface-containment-gate-plan.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c0-plan.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c0-architecture.md`
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c0-threat-model-delta.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c1-provider-free-admission-plan.md`
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c1-provider-free-admission-threat-model-delta.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c2-provider-free-broker-simulator-plan.md`
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c2-provider-free-broker-simulator-threat-model-delta.md`
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
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/authored-synthetic-broker-simulator-scenarios.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/provider-free-broker-simulator-evidence.json`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c0_acceptance.py`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py`
- `scripts/verify_repository.py`
- `orchestration/harness_settings/python_source_state.json`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c0.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c1.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c2.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_plan.py`
- `tests/test_api_spine_artifacts.py`
- `tests/test_python_source_state.py`

Do not open blue worker packets or closeouts, DeepSeek receipts, Sol rejection
or recovery framing, prior reviewer artifacts, agent-error history, protected
holdout/support/authoring/manifest/seal/receipt/per-case evidence, historical
Diary, branding, patient, product-derived, licensed or unrelated paths. Do not
perform a repository-wide search outside the exact surface above.

## Required adversarial challenges

Verify and report:

1. exact candidate HEAD, branch and clean checkout before and after review;
2. all five inherited AES-C1 artifacts match the frozen hashes and the C1/C0
   message, reason, admission and budget vocabularies are not widened;
3. the C2 contract, schema, registry, scenarios, results and evidence are closed
   and exact, including every nested rule, digest, status/reason vocabulary and
   the distinction between inherited adapter-artifact identity and the
   independently recomputed implementation-definition identity;
4. the exact 26 scenario IDs remain two `simulated`, four `not_dispatched` and
   20 `stop`, with no duplicate, undeclared or silently skipped scenario;
5. the adapter call is reached only after a fresh exact AES-C1 allow, exact
   registry identity, fresh generation/current-authority/revocation/kill
   recheck and exact cumulative budget-after commit;
6. operation, capability, adapter, implementation, destination, method and
   media type come only from the one immutable broker registry entry, never
   from candidate content, work-cell fields or dynamic callable selection;
7. the work-cell view cannot receive a lease, registry, credential fixture,
   destination, method, executable, path, URL, SQL, tool, command route,
   cleanup target or policy field, including through extra top-level or nested
   scenario-packet fields;
8. the authored-synthetic noncredential fixture and its handle remain private;
   no value or handle reaches an invocation, result, evidence or exception;
9. the dispatcher invokes the fixed pure adapter exactly once whenever the
   malformed-result override exercises result validation, records the actual
   count truthfully, releases nothing invalid, and cannot bypass the real pure
   call through an override;
10. exact result validation rejects extra, missing, wrong-typed, sensitive or
    command-authority fields; all 18 attempt/result mutations and all frozen
    nested contract mutations fail closed without released simulation;
11. any terminal state blocks following attempts and no budget, fixture or
    lease transfers across generations;
12. AST/static inspection finds no external-effect import, dynamic import,
    reflection, plugin loader, registry lookup by candidate text, `eval`,
    `exec`, template/deserializer, filesystem, subprocess, socket, HTTP,
    database, environment, metadata, executable tool or command path;
13. minimized evidence contains zero raw candidate, prompt, reasoning,
    exception, fixture, credential, patient, product or command value and
    records zero real runtime/provider/network/database/filesystem/tool/command
    operation;
14. GraphQL remains read-only, events remain fresh-read signals, provider
    failure remains explicit `intelligence_unavailable`, and product mutations
    remain separately authorised REST/OpenAPI commands; and
15. focused tests, Ruff, Git whitespace and clean postcondition all pass.

Run at least:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-aes-c2-gemini tests\test_raisa_agent_execution_surface_containment_gate_aes_c2.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c0.py tests\test_raisa_agent_execution_surface_containment_gate_plan.py tests\test_api_spine_artifacts.py tests\test_python_source_state.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c2.py scripts\verify_repository.py
git diff --check bd11333d462424b40f5f8f014b1c4a945b3a5133..d54f0476448f1218cd55477d42b958721359eae8
git rev-parse HEAD
git status --short --branch
```

You may design additional read-only probes within the exact allowed path set.

## Forbidden actions

Do not edit, generate repository evidence, format, commit, push, start a runtime,
container or database, contact a provider or product surface, access any
protected or sensitive path, inspect `docs/branding/`, move refs or accept your
own output.

## Decision rule

Return `revision_required` for any critical/high finding, admission/recheck/
budget bypass, candidate-selected operation, fixture leakage, wrong actual
invocation count, invalid released result, open contract/evidence, API Spine or
runtime widening, missing required deterministic evidence, wrong HEAD or dirty
postcondition. Otherwise return `pass`. Put all findings, commands/counts,
exact HEAD and post-review cleanliness in `review`.
