# Independent red/veto packet: AES-C3 provider-free hostile containment

Date: 2026-08-11

Decision required: exactly one structured `pass` or `revision_required`.

## Exact checkout

- Worktree: `C:\Users\sarashera\EMR4-worktrees\r184`
- Branch: `codex/review-aes-c3-hostile-containment-c45ff191`
- Frozen plan/source base: `d44be5cbe0774b6340c7e4f6ca76075242b2f156`
- Recovered candidate: `c45ff191af420b801e9917a7efc69c17aeb5698b`
- Protected local/origin `master` and `handoff/current` must remain exactly
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

First read `AGENTS.md` completely and perform its five-source rehydration,
naming `live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree` in the review.

## Purpose

Independently challenge whether exact candidate HEAD implements the frozen
AES-C3 authored-synthetic provider-free pure hostile-containment rehearsal over
the accepted AES-C0/C1/C2 contracts. This is a security veto. Search for ways a
malformed attempt, hostile opaque value, undeclared field, invalid result,
carrier label, cumulative state, stale lease/alias/token, current-authority
change, context mismatch or supply-chain mismatch could be relabelled rather
than proved, reach the fixed pure adapter incorrectly, leak raw data, or release
a result after a stop.

## Exact allowed read surface

Read only these paths plus the exact base-to-candidate diff restricted to them:

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
- `docs/raisa-agent-execution-surface-containment-gate-aes-c2-provider-free-broker-simulator-closeout.md`
- `orchestration/agent_inbox/codex/raisa-aes-c2-provider-free-broker-simulator-sol-acceptance.md`
- `docs/raisa-agent-execution-surface-containment-gate-aes-c3-provider-free-hostile-containment-plan.md`
- `docs/security/raisa-agent-execution-surface-containment-gate-aes-c3-provider-free-hostile-containment-threat-model-delta.md`
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
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/containment-rehearsal-contract.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/authored-synthetic-hostile-containment-scenarios.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3/provider-free-hostile-containment-evidence.json`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c0_acceptance.py`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c3_hostile_containment.py`
- `scripts/verify_repository.py`
- `orchestration/harness_settings/python_source_state.json`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c0.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c1.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c2.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c3.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_plan.py`
- `tests/test_api_spine_artifacts.py`
- `tests/test_python_source_state.py`

Do not open blue worker packets or closeouts, DeepSeek receipts, Sol rejection
or recovery records, agent-error history, prior reviewer artifacts, protected
holdout/support/authoring/manifest/seal/receipt/per-case evidence, historical
Diary, branding, patient, product-derived, licensed or unrelated paths. Do not
perform a repository-wide search outside the exact surface above.

## Required adversarial challenges

Verify and report:

1. exact candidate HEAD, branch and clean checkout before and after review;
2. all eleven inherited AES-C0/C1/C2 artifact hashes remain exact and no
   inherited message, reason, admission, registry or budget vocabulary widens;
3. the C3 contract, schema, scenario packet, results and evidence are closed,
   exact and canonical, including nested replay/current identity rules;
4. all 61 exact scenarios resolve as 21 `contained`, 15 `reject` and 25
   `stop`, with exactly 28 real pure adapter calls and 21 digest-only releases;
5. non-object, missing, extra, wrong-typed or cross-bound attempts cannot raise,
   select a mutation or reuse a valid scenario label; they return a minimized
   closed rejection with zero release;
6. each scenario ID is coupled to one exact family, carrier, declared inherited
   C1/C2 base, mutation and expected result; changing or removing any binding
   rejects before evaluation, and the declared base actually controls the
   inner object;
7. opaque payloads remain bounded strings and are absent from invocation,
   adapter result, returned C2/C3 result, evidence and exception surfaces;
8. structured local-file, template/deserialization, metadata/credential,
   command, tool, SQL, product-adapter and policy fields reject before a call;
9. invalid clear/encoded/compressed/chunked/exception result carriers start
   from the exact C2 malformed-result seam, make one actual fixed pure call,
   require a schema-valid exact C2 stop and release nothing;
10. all five egress carriers charge exactly 256 bytes to the same destination,
    reach 12,289 against 12,288, require exact inherited budget stop evidence,
    make zero calls and receive no decoder or carrier-specific escape;
11. both cumulative sequences verify every exact returned transition: two
    denials then a terminal third stop, and two exact one-call/no-release
    malformed results then a terminal zero-call third stop;
12. lease, alias and token fixtures bind generation, manifest ID/digest,
    Bureau, work cell and authority; missing or rebound fixtures cannot claim a
    stale stop, cross-Bureau reason precedence is exact, and no fixture value
    reaches the work-cell view;
13. post-admission revocation and kill outrank prior allow and require exact C2
    zero-call/no-release control results;
14. candidate/proofreader/broker context digests and manifest/adapter/runtime/
    model-provider supply identities stop on exact mismatch;
15. contradictory inherited results cannot be relabelled as expected outer
    evidence: an unexpected call remains counted, result digests are withheld,
    and the outer result rejects with zero release;
16. all 33 attempt mutations and 18 contract mutations fail closed, static AST
    inspection finds no decoder/interpreter/dereference/transport/dynamic
    selection/external-effect path, and minimized evidence contains no raw
    payload, credential, patient, product or command value;
17. GraphQL remains read-only, events remain fresh-read signals, provider
    failure remains explicit `intelligence_unavailable`, and product mutations
    remain separately authorised REST/OpenAPI commands; and
18. focused tests, Ruff, exact-path diff, Git whitespace and clean postcondition
    all pass.

Run at least:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-aes-c3-gemini tests\test_raisa_agent_execution_surface_containment_gate_aes_c3.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c2.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c0.py tests\test_raisa_agent_execution_surface_containment_gate_plan.py tests\test_api_spine_artifacts.py tests\test_python_source_state.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_agent_execution_surface_containment_gate_aes_c3_hostile_containment.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c3.py scripts\verify_repository.py
git diff --check d44be5cbe0774b6340c7e4f6ca76075242b2f156..c45ff191af420b801e9917a7efc69c17aeb5698b -- orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c3 scripts/raisa_agent_execution_surface_containment_gate_aes_c3_hostile_containment.py tests/test_raisa_agent_execution_surface_containment_gate_aes_c3.py scripts/verify_repository.py orchestration/harness_settings/python_source_state.json
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

Return `revision_required` for any critical/high finding, hard-coded expected
label that can contradict inherited behavior, malformed-input exception,
cosmetic or missing replay/base binding, cumulative transition gap, raw
payload/fixture leak, wrong actual call or release count, open contract/evidence,
API Spine or runtime widening, missing required deterministic evidence, wrong
HEAD or dirty postcondition. Otherwise return `pass`. Put all findings,
commands/counts, exact HEAD and post-review cleanliness in `review`.
