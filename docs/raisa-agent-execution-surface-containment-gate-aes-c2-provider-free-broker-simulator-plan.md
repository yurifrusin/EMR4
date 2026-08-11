# Raisa AES-C2 provider-free inert broker simulator plan

Date: 2026-08-11

Source HEAD: `789e37fb43c2ad1ae57e4a59bf7e945a5dd6208e`

Status: `frozen_for_authored_synthetic_provider_free_in_process_simulation`

## Purpose

Prove the smallest broker-owned dispatch step beneath the accepted AES-C0
authority contract and AES-C1 admission result. AES-C2 may call exactly one
fixed pure inert adapter function in-process after a fresh exact AES-C1 allow.
It may not start a broker or work-cell process, mount a real adapter, perform
external I/O, or create provider, product, data, credential, tool or command
authority.

The evidence label is
`authored_synthetic_provider_free_in_process_inert_simulation`. The adapter has
no external effect and all values are newly authored synthetic. An adapter
invocation in this plan means one ordinary Python function call, not a runtime
service, executable tool, provider-executed tool or product adapter.

## Exact inherited inputs

AES-C2 consumes these accepted AES-C1 artifacts without changing them:

| Artifact | Required SHA-256 |
|---|---|
| `admission-rehearsal-contract.json` | `241f081b1c3346ef50e80eb495c9bfb6ea3b99f67956b439c7c7638962069f90` |
| `admission-rehearsal-contract.schema.json` | `2e6c5b83d379f5b6f900fa0a26a8733b6fe09496ff8e1c52d5ed40123603e9b6` |
| `authored-synthetic-admission-scenarios.json` | `e6e427efa32fb27387598042f0d1b1f19c4472b09288f7c8d3ed321a7309945c` |
| `provider-free-admission-evidence.json` | `f7d1a2f60ef4b6f46242cfff7a12b36b6e20405a07ad788854c877851a0bbd4c` |
| `raisa_agent_execution_surface_containment_gate_aes_c1_admission.py` | `4407646c98dee84e8ef4210b0e06aa500178b5a2e2094ca02003b43fbf0acda6` |

The simulator imports only AES-C1's pure validation, digest and admission
functions. A mismatch in any inherited digest stops the report as
`revision_required`; C2 cannot rewrite C1 or reinterpret its reason vocabulary.

## One exact simulated adapter

The simulator registry contains exactly one immutable entry:

| Field | Frozen value |
|---|---|
| capability class | `inert_tool_adapter` |
| capability ID | `capability-synthetic-inert` |
| adapter ID | `synthetic-inert-adapter` |
| operation ID | `render-inert-adapter` |
| destination ID | `synthetic-inert-destination` |
| method | `POST` |
| media type | `application/json` |
| source class | `authored_synthetic` |
| implementation ID | `aes-c2-pure-inert-render-v1` |
| effect class | `none` |
| external I/O | `false` |
| command authority | `false` |

Its implementation digest is calculated over one closed declarative adapter
definition and must equal the manifest's pinned adapter-artifact identity. The
definition contains no URL, host, port, path, SQL, executable, command route,
tool definition, cleanup target, environment variable or provider identifier.

The pure adapter accepts a broker-created closed invocation containing only a
broker-generated invocation ID, the fixed operation identity, the admitted
candidate digest and two allowed authored-synthetic input fields. It returns a
closed result containing one fixed result code and digests only. It cannot
interpret templates, paths, serialized objects, URLs, code or commands.

## Credential-custody rehearsal

C2 uses one explicit `SyntheticCredentialFixture` whose value begins
`synthetic-noncredential-fixture:` and whose contract asserts
`real_credential: false`. It is not a token, password, key, identity, secret or
usable credential. It exists only to prove the shape of broker custody.

The fixture is held in broker-private simulator state and supplied directly to
the one pure adapter function. Neither its handle nor value may occur in the
work-cell view, candidate, proofreader result, AES-C1 decision, adapter request,
adapter result, evidence envelope, exception text or returned simulator result.
Only a SHA-256 binding inside broker-private validation may be compared. The
work cell receives no registry, lease or credential fixture and cannot request
credential enumeration.

## Closed inputs and outputs

One closed `BrokerSimulationAttempt` separates:

- `work_cell_view`: the exact closed candidate and proofreader result only;
- `broker_admission_attempt`: an exact AES-C1 `AdmissionAttempt` whose candidate
  and proofreader values equal the work-cell view;
- `post_admission_control_state`: a fresh authored-synthetic generation,
  authority, revocation and external-kill observation at dispatch time;
- `broker_registry`: the exact single immutable entry and private synthetic
  custody binding; and
- `expected_budget_commit`: the exact AES-C1 budget-after digest and cumulative
  counts that must be committed before dispatch.

The closed `BrokerSimulationResult` contains only IDs, status, fixed reason
codes, artifact/decision/invocation/result/budget digests, simulated invocation
count and boolean boundary assertions. It contains no raw candidate value,
fixture value, prompt, reasoning, exception, patient, product or credential
value.

The exact C2 status vocabulary is `simulated`, `not_dispatched` and `stop`.
The exact reason vocabulary is:

- `simulated_inert_adapter`;
- `admission_not_allow`;
- `registry_not_exact`;
- `adapter_identity_mismatch`;
- `supply_chain_identity_mismatch`;
- `credential_custody_violation`;
- `control_state_changed`;
- `external_kill_switch`;
- `invocation_contract_mismatch`;
- `adapter_result_invalid`;
- `budget_commit_mismatch`; and
- `generation_terminal`.

## Ordered fail-closed simulation

The simulator uses this fixed precedence:

1. reject malformed or open contract, attempt, registry, result or evidence;
2. stop on any inherited AES-C1 artifact or simulator-contract digest mismatch;
3. recompute and run exact AES-C1 admission over the broker-side attempt;
4. return `not_dispatched` when AES-C1 returns `deny` or `stop`;
5. stop unless the registry contains exactly the one frozen adapter definition
   and every identity equals the admitted broker-observed operation;
6. stop if the work-cell view contains a lease, registry, capability,
   operation, adapter, destination, method, media type, executable, credential,
   path, URL, SQL, tool, command route, cleanup target or policy field;
7. recheck generation, manifest, authority, revocation and external kill at the
   dispatch instant; any change after admission stops before invocation;
8. verify and commit the exact AES-C1 budget-after digest and cumulative counts
   before invocation; mismatch or terminal state stops;
9. build the invocation entirely from the fixed registry plus admitted candidate
   digest and allowlisted fields; candidate content selects no operation identity;
10. compare the broker-private synthetic custody binding without copying its
    handle or value into any non-private object;
11. call the single fixed pure adapter function at most once;
12. validate its exact result before returning minimized evidence; and
13. make any stop or exhausted generation terminal for a following attempt,
    with no budget, lease or fixture transfer to another generation.

No dynamic import, reflection, plugin loading, registry lookup by candidate
text, `eval`, `exec`, template engine, deserializer, filesystem, subprocess,
socket, HTTP client, database client, environment lookup or external tool is
permitted.

## Frozen scenario catalogue

The exact authored-synthetic catalogue contains 26 scenarios.

### Simulated

1. `exact-inert-dispatch-simulated`;
2. `exact-inert-second-within-budget-simulated`.

### Not dispatched by AES-C1

3. `admission-deny-not-dispatched`;
4. `admission-stop-not-dispatched`;
5. `proofreader-deny-not-dispatched`;
6. `candidate-selector-not-dispatched`.

### Terminal stop before or after the pure call

7. `registry-missing-stop`;
8. `registry-extra-entry-stop`;
9. `registry-capability-mismatch-stop`;
10. `registry-adapter-mismatch-stop`;
11. `registry-destination-mismatch-stop`;
12. `registry-method-mismatch-stop`;
13. `registry-media-type-mismatch-stop`;
14. `registry-operation-mismatch-stop`;
15. `registry-implementation-digest-mismatch-stop`;
16. `registry-custody-binding-mismatch-stop`;
17. `adapter-artifact-digest-mismatch-stop`;
18. `work-cell-custody-exposure-stop`;
19. `generation-superseded-before-dispatch-stop`;
20. `authority-changed-before-dispatch-stop`;
21. `revocation-before-dispatch-stop`;
22. `external-kill-before-dispatch-stop`;
23. `invocation-candidate-digest-mismatch-stop`;
24. `adapter-result-contract-mismatch-stop`;
25. `budget-commit-mismatch-stop`;
26. `repeat-after-terminal-stop`.

The registry and expected status/reason for every scenario are exact. No
undeclared scenario may be ignored. The two simulated scenarios invoke the
pure adapter exactly once each; all other scenarios invoke it zero times except
the deliberately malformed-result scenario, which may call it once but releases
no result and returns terminal `stop`.

## Generated hostile mutations

The acceptance harness generates at least these exact 18 independent mutations
from the canonical success attempt: additional top-level key; missing required
key; wrong type; additional work-cell key; work-cell capability, adapter,
destination, method, executable, credential and command-route fields; second
registry entry; registry URL; registry filesystem path; registry SQL; registry
executable selector; adapter-result sensitive field; and adapter-result command
authority. Every mutation must fail closed with zero released simulated result.

It also mutates each inherited digest and every frozen nested rule in the C2
contract. Every contract mutation must fail `validate_contract`; well-formed
but changed digest values are not accepted.

## API Spine classification

AES-C2 is an internal capability/security simulation only.

- GraphQL remains read-only and is never invoked.
- Events remain signals for fresh authorized reads and are never consumed.
- Access AI remains a future backend-brokered provider boundary; C2 makes no
  provider call and has no provider adapter.
- REST/OpenAPI commands remain separately authorized, human/policy-gated,
  idempotent, audited and deterministically read back. The simulator cannot
  prepare, confirm or call one.
- The fixed Python registry is not a generic plugin system or executable rules
  language. Declarative JSON cannot create a callable adapter.

## Security review tier and allocation

AES-C2 is `dual_review` because it exercises authorization, synthetic custody,
broker-owned operation identity, supply-chain binding, budget commit and future
tool/provider containment controls.

- GPT Sol owns this frozen boundary, final implementation review, recovery,
  acceptance and Git closeout.
- DeepSeek V4 Flash/high through Claude Code `--bare` owns one bounded blue
  implementation/test candidate in an exact disposable worktree. It receives
  no acceptance or integration authority and may not read the later red artifact.
- Gemini 3.6 Flash/high through a fresh Antigravity project owns one exact-head,
  read-only red/veto review after deterministic gates pass. It receives no
  implementation authority, may not read blue review framing, and must emit
  exactly one `pass` or `revision_required` decision.
- Sol may adopt a rejected candidate only under the recorded recovery lease;
  one mechanical DeepSeek revision is the maximum before Sol recovery.

## Owned files

- this plan;
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c2-provider-free-broker-simulator-threat-model-delta.md`;
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/`;
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py`;
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c2.py`;
- exact C2 receipts, worker/reviewer packets and decisions; and
- a closeout, Sol acceptance, Yuri mailbox message, continuity updater/tests and
  exact live-baton/verification bindings only after acceptance.

AES-C0 and AES-C1 artifacts are read-only inherited inputs. The 494 pre-existing
untracked paths are not owned, including `docs/branding/` and every earlier
pre-push receipt/state pair.

## Forbidden surfaces

- no protected-evidence access, enumeration, search, import, execution or
  inference;
- no historical Diary or local PHI access;
- no patient, clinical, product-derived, financial or licensed content;
- no real broker, work-cell process, container, adapter, plugin, route,
  listener or watcher;
- no provider/model call, raw prompt/response, real credential, IAM, metadata,
  network, socket, HTTP, DNS or external retrieval;
- no database/source access, migration, persistence, SQL or filesystem
  capability;
- no executable tool, shell/process, dynamic import, command/write or cleanup
  actuator;
- no deployment, production, release, Pages or protected-ref movement; and
- no broad staging, `git add .`, `git add -A`, `docs/branding/` staging or
  adoption of unrelated untracked evidence.

## Deterministic acceptance

AES-C2 passes only when:

1. all five inherited AES-C1 files match their frozen hashes and full C1/C0
   acceptance remains green;
2. the C2 contract, schema, registry, scenarios, results and evidence are closed
   and exact;
3. only the two exact success scenarios call the fixed pure adapter and return
   `simulated`, subject to the malformed-result exception releasing nothing;
4. all C1 deny/stop scenarios invoke no adapter and preserve exact admission
   decision/reason evidence;
5. the registry has exactly one entry and all operation identity comes from it,
   never from the candidate or work-cell view;
6. the synthetic noncredential fixture stays broker-private and no handle or
   value reaches any work-cell, request, result, evidence or exception surface;
7. generation, authority, revocation and kill are rechecked immediately before
   dispatch and always outrank a prior allow;
8. the exact C1 budget-after state is committed before dispatch and no following
   operation occurs after terminal state;
9. invocation and adapter-result digests are independently recomputed and exact;
10. all 26 scenarios match their exact status, reason and invocation count;
11. all 18 generated hostile attempt/result mutations and all nested contract
    mutations fail closed with zero released result;
12. static inspection proves no external-effect import or callable-selection
    path, and evidence records zero real runtime, provider, network,
    database/source, filesystem, executable, tool, command or product/patient
    operation;
13. focused AES-C2/C1/C0/API tests, maintained static CI tests, canonical fast
    profile, Ruff, compile/syntax and Git whitespace pass;
14. DeepSeek blue and fresh Gemini veto satisfy dual-review with no unresolved
    critical/high issue; and
15. exact tracked scope, original 494 untracked-path hash and all four protected
    refs remain unchanged.

## Recovery, stop and cleanup

A deterministic failure blocks external review. One mechanical blue revision
is permitted; conceptual authority/custody defects move directly to Sol's
recovery lease. A real adapter, process, provider, data, credential or external-
effect need is scope expansion and stops C2.

There is no runtime cleanup because no process or service starts and the pure
function has no external state. Closeout must show zero external effects, no
fixture leakage, exact invocation counts, original untracked preservation and
unchanged protected refs.

## Claim boundary and next work

Passing C2 will prove only deterministic broker-owned identity selection,
synthetic custody non-disclosure, immediate control-state recheck, budget commit
and one pure inert function call over authored-synthetic in-process fixtures. It
will not prove process/container isolation, real credential custody, real
adapter safety, concurrent atomicity, provider behavior, product-data safety,
command safety, deployment or production readiness.

AES-C3 hostile containment rehearsal is the next planned candidate after C2.
It must receive a fresh five-source receipt and freeze attacks across local-file,
template/deserialization, metadata, arbitrary relay/egress, encoded leakage,
cumulative probing, stale lease and cross-generation replay surfaces. C2 grants
no C3 runtime, provider, data, credential, network, tool or command authority.
