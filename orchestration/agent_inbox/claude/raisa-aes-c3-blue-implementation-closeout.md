# Raisa AES-C3 provider-free hostile containment rehearsal - DeepSeek blue implementation closeout

Date: 2026-08-11

Task ID: `raisa-aes-c3-blue-implementation-001`

Decision: `pass` (bounded implementation candidate only; no acceptance claimed)

Worker: DeepSeek V4 Flash/high through Claude Code `--bare`

## Source and candidate heads

- Required source HEAD: `d44be5cbe0774b6340c7e4f6ca76075242b2f156`
  (exact; verified clean tracked worktree before editing).
- Candidate commit: the closeout is committed in the candidate commit, so its
  final self-referential SHA is resolved from the commit receipt after commit
  and not guessed here.
- Protected refs are named exactly and were verified but never moved:
  - local `master` = `2e34bdad732fdab32fbf778280b3d3c70d66d602`
  - local `handoff/current` = `2e34bdad732fdab32fbf778280b3d3c70d66d602`
  - `origin/master` and `origin/handoff/current` are verified unchanged at the
    same protected commit; no push was performed.

## Bounded implementation performed

One bounded DeepSeek blue implementation/test candidate under the frozen
AES-C3 plan and threat-model delta. No acceptance, integration, baton,
push or protected-ref authority is conveyed. The rehearsal imports only the
exact pure C1/C2 validation, digest and simulation functions and operates over
copied closed C0/C1/C2 objects. Nothing decodes, decompresses, deserializes,
interprets, dereferences, fetches, executes or relays a hostile value.

## Exact changed files (seven owned paths only)

- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/authored-synthetic-hostile-containment-scenarios.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/provider-free-hostile-containment-evidence.json`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c3_hostile_containment.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c3.py`
- `orchestration/agent_inbox/claude/raisa-aes-c3-blue-implementation-closeout.md`

No AES-C0/C1/C2 artifact, frozen plan, threat delta, AGENTS,
`implementation_plan.md`, API Spine artifact, fast-profile configuration or
pre-existing test was modified. The worktree had no tracked changes before this
candidate and only the seven owned paths are new.

## 61-scenario accounting

Aggregate: 21 `contained`, 15 `reject`, 25 `stop`; 28 pure Python calls; 21
digest-only releases; zero external operations.

| Band | Scenario IDs | Status | Reason vocabulary | Calls | Releases |
|---|---|---|---|---|---|
| Control + opaque inert content (1-21) | `exact-inert-control-contained` + 20 inert references | contained | `exact_inert_control` (1) / `opaque_content_inert` (20) | 1 each (21) | 1 each (21 digest-only) |
| Structured attacks (22-36) | environment-key, filesystem-path, template-field, serialized-object-field, metadata-endpoint, credential-field, arbitrary-url-field, relay-destination-field, graphql-mutation-command, rest-command-route, sql-command, provider-tool-definition, product-adapter-selector, executable-selector, policy-amendment `*-reject` | reject | `closed_contract_rejection` | 0 | 0 |
| Invalid result carriers (37-41) | clear/encoded/compressed/chunked/exception `-result-egress-stop` | stop | `adapter_result_invalid` | 1 each (5) | 0 |
| Cumulative stops (42-43) | `boundary-probe-denial-sequence-stop`, `repeated-adapter-failure-sequence-stop` | stop | `denial_budget_exhausted`, `repeated_failure_budget_exhausted` | 0, 2 | 0 |
| Carrier-independent egress budget (44-48) | clear/encoded/compressed/chunked/exception `-egress-budget-overflow-stop` | stop | `egress_budget_exhausted` | 0 | 0 |
| Stale authority/replay/external stop (49-55) | generation-superseded, restart-generation-lease, cross-bureau-lease, stale-alias, stale-token replay, post-admission-revocation, post-admission-external-kill `-stop` | stop | `generation_superseded`/`authority_changed`/`external_kill_switch` | 0 | 0 |
| Context + supply-chain binding (56-61) | candidate/proofreader context mismatch, manifest/adapter-artifact/runtime-image/model-provider-contract digest mismatch `-stop` | stop | `context_binding_mismatch` / `supply_chain_identity_mismatch` | 0 | 0 |

The scenario order and exact IDs/statuses/reasons/call/release counts match the
frozen 61-scenario catalogue. Any different total is `revision_required`; the
report records `passed` with an empty `reasons` list.

## Cumulative sequences

- `boundary-probe-denial-sequence-stop`: two well-formed
  candidate-operation-identity denials progress broker-owned `denied_operations`
  and `boundary_probes` `0 -> 1 -> 2`; reaching the boundary-probe ceiling 2
  latches `exhausted`; a third exact operation stops before dispatch with
  `denial_budget_exhausted`, zero pure calls and zero releases.
- `repeated-adapter-failure-sequence-stop`: the exact malformed-result seam runs
  twice; each pure call releases nothing and increments broker-owned
  `repeated_failures`; reaching ceiling 2 latches `exhausted`; a third attempt
  makes no pure call. Total two pure calls, zero releases. State is
  broker-owned, terminal and generation-bound.

## Hostile attempt and contract mutations

- 20/20 generated hostile attempt mutations fail closed with zero released
  result (`mutation_admitted: []`). Coverage: every required/closed wrapper
  field, attack-family/carrier/mutation-ID/status/reason enums, expected counts,
  payload byte count and SHA-256, context digest and context-binding role,
  replay kind/noncredential/extra field, generation and authority identities,
  payload value type, unknown mutation ID, unknown target-path field and
  unknown carrier.
- 18/18 nested C3 contract mutations fail `validate_contract`
  (`contract_mutation_admitted: []`), including a changed inherited digest,
  an extra inherited digest, changed status/reason/attack-family/carrier/
  mutation-ID vocabularies, changed containment precedence, extended
  opaque/structural/result/context/supply rules, a changed egress ceiling, a
  changed cumulative ceiling, an extended replay policy, an opened zero-runtime
  boundary and an extra scenario-registry entry.

## Raw-payload non-release and static-boundary evidence

- Each raw hostile payload is absent from the C2 invocation, adapter result,
  returned C2 result, C3 evidence and every normalized failure surface. The
  scenarios fixture holds the newly authored synthetic payloads; final evidence
  does not. Recursive value-only scanning of the generated evidence returns zero
  payload occurrences (`raw_payload_leak_scenarios: []`,
  `opaque_payload_non_release: true`).
- The fixed C2 operation identity remains unchanged: the invocation carries only
  the admitted candidate digest and the two fixed authored-synthetic inputs.
- `static_boundary_check()` returns `[]`: no networking/HTTP/DNS,
  process/environment, database/SQL, template/HDF5/deserialization,
  archive/compression, encoding/decoding, dynamic import/execution/reflection or
  plugin-loading path exists in the C3 source. Forbidden facilities named in the
  plan (`socket`, `requests`, `httpx`, `urllib`, `subprocess`, `os.environ`,
  `pickle`, `marshal`, `shelve`, YAML object loaders, Jinja, `h5py`, `base64`,
  `gzip`, `zlib`, `bz2`, `lzma`, `tarfile`, `zipfile`, `eval`, `exec`,
  `compile`, `__import__`, reflection) are never imported or called. The only
  filesystem `open` is the deterministic minimized evidence writer `_write_lf`;
  committed fixture JSON is read through the shared `_load` helper.

## Tests and exact results

- Focused AES-C3 packet: 20/20 tests pass, covering report status, inherited
  digests, closed contract/packet, all 61 scenario expectations, replay-fixture
  non-exposure, raw-payload non-release, all hostile attempt/contract mutations,
  contract rule rejection, static boundary, scenario result schema, regenerated
  packet stability, opaque payload non-occurrence in invocation/adapter/C2
  result/evidence, structural reject-before-call, result-carrier
  call-once-release-nothing, both cumulative sequences, exact 256-byte egress
  accounting (12,033 + 256 = 12,289 > 12,288) and stale/context/supply
  zero-call stops.
- Exact serial packet (repository `conftest.py`, exact safe paths only):
  93/93 pass, exit code 0 (20 AES-C3 + 22 AES-C2 + 14 AES-C1 + 9 AES-C0 + 28
  API Spine).

## Verification

- Standalone C3 script: status `passed`, reasons `[]`, exit 0; evidence
  regenerated.
- Ruff check on the two touched Python files: pass.
- Ruff format check on the two touched Python files: pass (both files formatted).
- Compile/syntax: pass.
- `git diff --check`: clean (no tracked whitespace errors).
- Exact owned-path scope: only the seven owned paths are new; no AES-C0/C1/C2
  artifact, plan, threat delta, AGENTS, implementation plan, API Spine artifact,
  fast-profile configuration or pre-existing test changed.

## Zero-runtime/provider/data evidence

Evidence mode: `authored_synthetic_provider_free_pure_hostile_containment_rehearsal`.

- runtime_started: false
- provider_calls: 0
- real_adapters_executed: 0
- network_operations: 0
- database_operations: 0
- source_operations: 0
- filesystem_operations: 0 (only the owned evidence writer opens a file)
- executable_or_tool_operations: 0
- command_operations: 0
- real_credentials_used: false
- product_or_patient_data: false
- decoder/interpreter/dereference/transport operations: 0 (static-boundary
  proof plus value-only payload scan)

The rehearsal performs no real runtime, provider, credential, network,
database/source, filesystem-capability, decoder, executable/tool or
command/product operation. No protected evidence, historical Diary/PHI,
patient/clinical/product-derived/financial/licensed data was accessed.

## Pending acceptance items (outside worker authority)

This bounded candidate claims no acceptance. Sol final review/adoption, broader
maintained/canonical gates, a fresh Gemini exact-head veto, integration,
baton/continuity movement, Yuri mailbox handoff and publication all remain
pending and are outside worker authority. No all-plan-criteria-complete claim is
made.

## Issues found or residual risks

No unresolved finding remains in this bounded candidate. Residual risks are
inherited from the frozen plan and remain outside C3 claim scope: process/
container isolation, universal semantic prompt-injection detection, real
credential or adapter safety, provider behavior, concurrency, product-data
safety, command safety, deployment and production readiness are not proven by
this authored-synthetic pure containment rehearsal.
