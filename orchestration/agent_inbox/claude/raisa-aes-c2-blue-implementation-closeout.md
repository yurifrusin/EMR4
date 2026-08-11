# Raisa AES-C2 provider-free inert broker simulator - DeepSeek blue revision closeout

Date: 2026-08-11

Task ID: `raisa-aes-c2-blue-revision-001`

Decision: `pass` (bounded revision candidate only)

Worker: DeepSeek V4 Flash/high through Claude Code `--bare`

Incident: AER-0251 at register revision 216 (Sol rejection of the original
`52f1dbb1...` candidate).

## Source and candidate heads

- Required revision source HEAD: `52f1dbb10fd6e616d3190aa896e60d8facf5897d`
  (exact; verified clean and preflighted).
- Original corrected-plan source: `bd11333d462424b40f5f8f014b1c4a945b3a5133`.
- Candidate commit: `resolved_by_receipt` - the closeout is committed in the
  candidate commit, so its final self-referential SHA is not guessed here; the
  candidate SHA is resolved from the commit receipt after commit.
- Protected refs are named exactly and were verified but never moved:
  - local `master` = `2e34bdad732fdab32fbf778280b3d3c70d66d602`
  - local `handoff/current` = `2e34bdad732fdab32fbf778280b3d3c70d66d602`
  - `origin/master` = `2e34bdad732fdab32fbf778280b3d3c70d66d602`
  - `origin/handoff/current` = `2e34bdad732fdab32fbf778280b3d3c70d66d602`

## Bounded revision performed

This is the single mechanical same-lane revision permitted by the frozen plan.
No acceptance, recovery, integration, baton, push or protected-ref authority is
conveyed. The revision corrected the contained implementation-and-evidence
closure error:

1. `_dispatch_adapter` no longer returns `adapter_result_override` before the
   pure adapter. The sole pure adapter call is unconditional and executes
   exactly once, after every preceding gate and before the negative result seam
   is observed. A supplied result can no longer bypass the actual call. No
   second callable or dynamic selection path was added.
2. `validate_scenario_packet` now rejects every undeclared top-level packet key,
   every missing packet field, every noncanonical scenario value and every
   schema-valid result override outside the one exact malformed-result scenario.
   The committed scenario packet is bound to the exact generated 26-scenario
   catalogue (`scenarios:not_canonical_generated_catalogue`).
3. Independent tests instrument the actual `_pure_inert_render` callable and
   prove:
   - the malformed-result scenario executes it exactly once;
   - a schema-valid override cannot bypass that actual call;
   - an extra packet key plus any noncanonical packet fail validation.

## Changed files (owned paths only)

- `scripts/raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c2.py`
- `orchestration/agent_inbox/claude/raisa-aes-c2-blue-implementation-closeout.md`

The regenerated minimized evidence
(`orchestration/continuity/.../provider-free-broker-simulator-evidence.json`) is
byte-identical to the frozen evidence: the corrected source preserves the exact
2 simulated / 4 not_dispatched / 20 stop accounting and the three actual pure
calls. The frozen scenarios, contract and schema are unchanged. No AES-C0/C1
artifact, plan, threat delta, AGENTS, implementation plan, API Spine artifact,
fast-profile configuration or pre-existing test was modified.

## Exact 26-scenario accounting

Status counts: 2 `simulated`, 4 `not_dispatched`, 20 terminal `stop`.

| Scenario | Status | Reason | Calls |
|---|---|---|---|
| `exact-inert-dispatch-simulated` | simulated | `simulated_inert_adapter` | 1 |
| `exact-inert-second-within-budget-simulated` | simulated | `simulated_inert_adapter` | 1 |
| `admission-deny-not-dispatched` | not_dispatched | `admission_not_allow` | 0 |
| `admission-stop-not-dispatched` | not_dispatched | `admission_not_allow` | 0 |
| `proofreader-deny-not-dispatched` | not_dispatched | `admission_not_allow` | 0 |
| `candidate-selector-not-dispatched` | not_dispatched | `admission_not_allow` | 0 |
| `registry-missing-stop` | stop | `registry_not_exact` | 0 |
| `registry-extra-entry-stop` | stop | `registry_not_exact` | 0 |
| `registry-capability-mismatch-stop` | stop | `registry_not_exact` | 0 |
| `registry-adapter-mismatch-stop` | stop | `adapter_identity_mismatch` | 0 |
| `registry-destination-mismatch-stop` | stop | `adapter_identity_mismatch` | 0 |
| `registry-method-mismatch-stop` | stop | `adapter_identity_mismatch` | 0 |
| `registry-media-type-mismatch-stop` | stop | `adapter_identity_mismatch` | 0 |
| `registry-operation-mismatch-stop` | stop | `adapter_identity_mismatch` | 0 |
| `registry-implementation-digest-mismatch-stop` | stop | `adapter_identity_mismatch` | 0 |
| `registry-custody-binding-mismatch-stop` | stop | `credential_custody_violation` | 0 |
| `adapter-artifact-digest-mismatch-stop` | stop | `supply_chain_identity_mismatch` | 0 |
| `work-cell-custody-exposure-stop` | stop | `credential_custody_violation` | 0 |
| `generation-superseded-before-dispatch-stop` | stop | `control_state_changed` | 0 |
| `authority-changed-before-dispatch-stop` | stop | `control_state_changed` | 0 |
| `revocation-before-dispatch-stop` | stop | `control_state_changed` | 0 |
| `external-kill-before-dispatch-stop` | stop | `external_kill_switch` | 0 |
| `invocation-candidate-digest-mismatch-stop` | stop | `invocation_contract_mismatch` | 0 |
| `adapter-result-contract-mismatch-stop` | stop | `adapter_result_invalid` | 1 |
| `budget-commit-mismatch-stop` | stop | `budget_commit_mismatch` | 0 |
| `repeat-after-terminal-stop` | stop | `generation_terminal` | 0 |

Total pure-adapter calls: 3 - two released simulations plus the malformed-result
scenario, which calls once and releases nothing. Every other scenario calls zero
times. This claim is made only after instrumented proof (the focused C2 tests
wrap the real `_pure_inert_render` with a counting wrapper and assert the exact
call count across the whole committed catalogue).

## Hostile mutations

- 18/18 generated hostile attempt/result mutations fail closed with zero released
  simulated result (`mutation_admitted: []`). The mutations cover an additional
  top-level key, missing required key, wrong type, additional work-cell key,
  work-cell capability/adapter/destination/method/executable/credential and
  command-route fields, second registry entry, registry URL, filesystem path,
  SQL and executable selector, and adapter-result sensitive/command-authority
  fields.
- 14/14 nested C2 contract mutations fail `validate_contract`
  (`contract_mutation_admitted: []`), including a changed inherited digest,
  changed registry identity, second registry entry, extended
  implementation-definition, changed status/reason vocabulary, changed
  dispatch-precedence, extended custody policy, extended forbidden-field list,
  extended digest rules, extended invocation/result contracts and an opened
  zero-runtime boundary.

## Digest evidence

- Inherited adapter-artifact identity (C1 manifest/current-generation):
  `sha256:ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff` -
  exactly `sha256:` plus 64 `f` characters, matching the C1 supply-chain
  `adapter_artifact_digest`.
- Independently recomputed implementation-definition digest:
  `sha256:887429a4faee4eba7611ffbb8653fa8c9a730132446c9a7fc6e9ebab59efcb5d`
  over the closed C2 declarative adapter definition.
- The two digest values are distinct and have no equality or preimage relation.
- Invocation and adapter-result digests are independently recomputed and compared.

## Synthetic fixture custody binding

The broker-private synthetic noncredential fixture
(`synthetic-noncredential-fixture:` prefix, `real_credential: false`) is
supplied directly to the fixed pure adapter (as the second argument of the real
`_pure_inert_render` call) to prove the broker-custody rehearsal shape, but it is
never emitted into any result. Only its digest alone is compared for custody
binding (`fixture_value_digest`); the handle and value never reach the work-cell
view, admission attempt/decision, adapter invocation/result, evidence, exception
text or returned simulator result. Recursive checks prove the handle/value occur
nowhere in any emitted surface.

## Tests and exact results

- Focused AES-C2 packet: 22/22 tests pass, including the four new instrumented
  regressions:
  - malformed result executes `_pure_inert_render` exactly once;
  - schema-valid override cannot bypass the actual pure call;
  - the full 26-scenario catalogue executes `_pure_inert_render` exactly three
    times;
  - extra packet key and noncanonical scenario fail validation.
- Exact serial packet (repository `conftest.py`, exact safe paths only):
  81/81 pass, exit code 0 (22 AES-C2 + 14 AES-C1 + 9 AES-C0 + 36 API Spine).

## Verification

- Corrected simulator script: status `passed`, reasons `[]`, evidence
  regenerated.
- Ruff check and Ruff format check on the two touched Python files: pass.
- Compile/syntax for the C2 script and test: pass.
- `git diff --check`: clean.
- Exact seven-path diff check against `52f1dbb10fd6e616d3190aa896e60d8facf5897d`:
  only the seven owned paths may change; no AES-C0/C1 artifact, plan, threat
  delta, AGENTS, implementation plan, API Spine artifact, fast-profile
  configuration or pre-existing test changed.

## Zero-runtime/provider/data evidence

Evidence mode: `authored_synthetic_provider_free_in_process_inert_simulation`.

- runtime_started: false
- provider_calls: 0
- real_adapters_executed: 0
- network_operations: 0
- database_operations: 0
- source_operations: 0
- filesystem_operations: 0 (the only filesystem `open` is the deterministic
  minimized evidence writer `_write_lf`; committed fixture JSON is read through
  the shared `_load` helper)
- executable_or_tool_operations: 0
- command_operations: 0
- real_credentials_used: false
- product_or_patient_data: false

Static boundary checks prove no dynamic import, reflection, plugin loading,
candidate-indexed callable map, `eval`, `exec`, template/deserialization engine,
environment read, subprocess, socket, HTTP or database client, and no external
filesystem capability beyond the owned evidence writer.

## Pending acceptance items (outside worker authority)

This bounded revision claims no acceptance. Sol final review/adoption, broader
maintained/canonical gates, a fresh Gemini veto after deterministic admission,
integration, baton/continuity movement, Yuri mailbox handoff and publication all
remain pending and are outside worker authority. No all-plan-criteria-complete
claim is made.

## Issues found or residual risks

No unresolved finding remains in this bounded revision. Residual risks are
inherited from the frozen plan and remain outside C2 claim scope: process/
container isolation, real credential custody, real adapter safety, concurrent
atomicity, provider behavior, product-data safety, command safety, deployment
and production readiness are not proven by this in-process authored-synthetic
simulation.
