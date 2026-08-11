# Raisa AES-C1 provider-free admission rehearsal — blue implementation closeout

Date: 2026-08-11
Worker: DeepSeek V4 Flash/high through Claude Code `--bare` (blue lane)
Task ID: `raisa-aes-c1-blue-implementation-001`

## Decision

`decision: pass`

## Exact HEADs

- Source HEAD: `d47010743d25e05d7d758f91507179374a91bb04`
- Final candidate HEAD: the commit created on `codex/aes-c1-blue-deepseek` with
  message `Implement AES-C1 provider-free admission rehearsal`
- Protected `master`, `handoff/current`, `origin/master`,
  `origin/handoff/current` all verified at
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`; never moved.

## Rehydration

- `AGENTS.md` read completely; protected-evidence (Section 5) and
  user-decision (Section 6) boundaries restored.
- Frozen AES-C1 plan and threat-model delta read completely.
- Accepted AES-C0 plan, architecture, threat-model delta, closeout, contract,
  schema, examples and acceptance validator read completely.
- Verified exact branch (`codex/aes-c1-blue-deepseek`), clean worktree and
  source HEAD `d47010743d25e05d7d758f91507179374a91bb04`.
- Only exact named paths were used; no protected fixture/support/authoring/
  manifest/seal/receipt/per-case surface was enumerated, searched or opened.

## Plan challenge against AES-C0

The frozen AES-C1 plan was challenged against the accepted AES-C0 contract
before implementation. No conceptual or authority contradiction was found:

- The AES-C0 `BrokerDecision.capability_class` enum is restricted to the three
  leaseable classes, so a forbidden-capability request is carried as the
  broker-observed `requested_capability_class` (untrusted harness observation)
  while the emitted `BrokerDecision.capability_class` remains a leaseable class;
  the deny reason is the exact AES-C0 `forbidden_capability_class`.
- The AES-C0 `BrokerDecision.candidate_supplied_operation_identity` is
  `const: false`; even the `candidate-operation-identity-deny` scenario records
  `false` because the rejected candidate identity is never adopted.
- Zero ceilings are representable only in the egress/action dimensions by the
  AES-C0 schema; scenario 43 uses `action.max_inert_tool_operations = 0`.
- Temporal, revocation and manifest-expiry stops are mapped to exact closed
  AES-C0 reason codes and documented in the contract.

## Changed files (exactly the seven owned paths)

1. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json` (new)
2. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json` (new)
3. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/authored-synthetic-admission-scenarios.json` (new, deterministically authored)
4. `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/provider-free-admission-evidence.json` (new, written by the rehearsal run)
5. `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py` (new)
6. `tests/test_raisa_agent_execution_surface_containment_gate_aes_c1.py` (new)
7. `orchestration/agent_inbox/claude/raisa-aes-c1-blue-implementation-closeout.md` (this file)

## Implementation summary

- Reuses the AES-C0 closed validator (`validate_instance` plus the exact
  `$defs` for `GenerationManifest`, `CapabilityLease`, `BudgetState`,
  `BrokerDecision`, `RevocationRecord`, `AuditEvidenceEnvelope` and
  `SupplyChainIdentity`).
- Checks the three inherited AES-C0 SHA-256 values before scenario evaluation
  (terminal `revision_required` on mismatch).
- Implements the sentinel-normalized canonical manifest SHA-256 rule and
  independently recomputes candidate and budget-before/budget-after digests.
- Validates a closed `AdmissionAttempt` wrapper and closed current-generation,
  current-authority, proofreader, candidate and broker-observation subobjects.
- Treats the evaluator clock, current-generation state, current-authority state
  and kill-switch observation as authored-synthetic trusted harness inputs,
  never candidate content.
- Fixed ordered stop/deny/allow precedence with the exact AES-C0 reason
  vocabulary; a record that cannot safely populate an AES-C0 decision fails
  closed (none did).
- Prospective accounting across all 19 AES-C0 budget counters; a zero ceiling
  disables only the requested capability counter without pre-exhausting
  unrelated zero counters; a reached positive denial ceiling returns the current
  deny plus a terminal after-state and blocks the following attempt.
- Validates and executes the exact 45 scenario IDs and expected decisions;
  rejects undeclared, duplicate or silently skipped scenarios.
- 22 independent malformed/additional/missing/wrong-type and semantic hostile
  mutations with zero admission.
- No operation admitted is executed; there is no dispatch function and no
  runtime, adapter, provider, database/source, tool or command capability.

## Scenario and mutation counts

- 45 scenarios: 2 `allow`, 25 `deny`, 18 `stop`.
  - 2 allows: `exact-inert-intersection-allow`,
    `exact-inert-second-within-budget-allow`.
  - 24 default denials (scenarios 3-26) plus scenario 44
    `denial-ceiling-reached-after-deny` (current `deny`, terminal after-state)
    = 25 deny.
  - 18 terminal stops (scenarios 27-43 and 45); scenario 44 is the deny pairing
    whose terminal after-state is consumed by scenario 45.
- Mutation count: 22; rejected 22; admitted 0.
- Every scenario result contains an exact AES-C0 `BrokerDecision` and minimized
  `AuditEvidenceEnvelope`, both validated against the AES-C0 schema for each of
  the 45 scenarios.

## Tests and exact results

Ran serially (repository conftest loads the shared PostgreSQL test schema):

```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_agent_execution_surface_containment_gate_aes_c1_admission.py
```
-> `status: passed`, `reasons: []`.

```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\ariadne_serial_pytest.py --timeout-seconds 180 tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c0.py tests\test_api_spine_artifacts.py -q
```
-> 56 tests passed (11 AES-C1 + 9 AES-C0 + 36 API Spine), zero failures.

```
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_agent_execution_surface_containment_gate_aes_c1_admission.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py
```
-> All checks passed.

```
git diff --check
```
-> clean.

Compile/syntax: `python -m py_compile` of the new script passed.

## Zero-runtime/provider/data evidence

The report states and the focused tests assert:

- `runtime_started: false`
- `provider_calls: 0`
- `adapters_executed: 0`
- `network_operations: 0`, `database_operations: 0`, `source_operations: 0`
- `tool_operations: 0`, `command_operations: 0`
- `product_or_patient_data: false`

The module performs no provider/model call, no database/source access, no
filesystem/tool/shell/command capability, no deployment/production/release/
Pages and no protected-ref movement. It reads only the committed JSON fixtures
and writes the deterministic evidence JSON. Evidence contains only closed
identifiers, decisions, exact reason codes, cumulative counts and digests; a
recursive forbidden-key scan over the evidence found no prompt, reasoning,
credential, exception, patient or product value.

## Issues found and resolved

- `_flatten_ceilings` initially used `"max_" + counter`, which mismatches the
  AES-C0 key vocabulary (e.g. `request_count` -> `max_requests`,
  `denied_operations` -> `max_denials`); switched to the AES-C0 `_ceiling_pairs`
  helper.
- `validate_attempt` initially raised `KeyError` on a hostile mutation that
  deletes `generation_manifest`; made it fail closed with schema errors.
- The denial/boundary-probe counter policy made two probe-type denials terminal
  (`boundary_probes` reached its ceiling of 1); raised the authored-synthetic
  `max_boundary_probes` ceiling to 2 so the 24 default denials remain
  non-terminal while scenario 44's `denied_operations` ceiling still drives the
  terminal pairing.
- Removed an unused `EXAMPLES_PATH` import to satisfy Ruff F401.

## Residual risks (unchanged from the frozen plan)

- Passing AES-C1 proves only deterministic admission evaluation over
  authored-synthetic unmounted objects.
- It does not prove a broker process, adapter custody, container/kernel
  isolation, atomic distributed budgets, provider behavior, product-data
  safety, command safety, deployment or production readiness.

## Acceptance items status

- Items 1-10 of the frozen plan are satisfied by the blue artifact.
- Item 11 (focused packet, Ruff, compile/syntax and Git whitespace) passes;
  the maintained static CI packet and canonical fast profile were left to Sol
  to avoid repository-wide discovery over protected paths.
- Item 12 (dual-review) — the blue artifact is ready; the fresh exact-head
  Gemini red/veto decision is Sol-owned and not yet run.
- Item 13 (tracked scope exact, untracked preserved, protected refs unchanged)
  is verified by this worker.

## Unfulfilled acceptance items

- None attributable to the blue artifact. The fresh red/veto review and Sol
  acceptance remain to be executed by Sol.

## Staged scope and refs

Only the seven owned paths are staged. Pre-existing untracked files are
preserved. Protected refs remain at
`2e34bdad732fdab32fbf778280b3d3c70d66d602`.
