# Worker packet: AES-C2 provider-free inert broker simulator

Task ID: `raisa-aes-c2-blue-implementation-001`

Role: DeepSeek V4 Flash/high blue implementation and defensive test worker
through Claude Code `--bare`

Authorized worktree:
`C:\Users\sarashera\EMR4-worktrees\aes-c2-deepseek-blue`

Authorized branch: `codex/aes-c2-blue-deepseek`

Required source HEAD: `bd11333d462424b40f5f8f014b1c4a945b3a5133`

## Mandatory rehydration before editing

1. Read `AGENTS.md` completely.
2. Read the frozen corrected AES-C2 plan, its plan-correction note and threat-
   model delta completely.
3. Read the accepted AES-C1 plan, threat delta, closeout, Sol acceptance, exact
   contract/schema/scenarios/evidence and implementation needed by C2.
4. Read the accepted AES-C0 contract/schema/examples and validator surfaces
   reached through AES-C1. Do not change either predecessor.
5. Restore AGENTS Sections 5 and 6 protected-evidence and user-decision
   boundaries.
6. Verify the exact branch, clean worktree and required source HEAD. Verify but
   never move local/origin `master` or `handoff/current`, which must remain
   `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
7. Use only exact named paths. Do not enumerate, search, open or infer any
   protected fixture/support/authoring/manifest/seal/receipt/per-case surface.

## Mission

Implement the frozen AES-C2 authored-synthetic, provider-free, in-process inert
broker simulator and defensive tests. The broker-side simulator may call
exactly one statically selected pure inert Python function at most once after a
fresh exact AES-C1 `allow`. It must prove that the work-cell view never receives
a lease, registry, credential fixture or operation selector and cannot choose a
capability, adapter, destination, method, media type, implementation or
executable.

First challenge the corrected plan against the exact accepted AES-C1/C0
contracts. If a conceptual, digest-layer or authority contradiction remains,
stop without implementation and write `decision: revision_required` in the
durable closeout. Do not silently reinterpret the plan.

## Owned paths

You may create or edit only:

- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/broker-simulator-contract.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/authored-synthetic-broker-simulator-scenarios.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c2/provider-free-broker-simulator-evidence.json`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c2.py`
- `orchestration/agent_inbox/claude/raisa-aes-c2-blue-implementation-closeout.md`

Do not modify the frozen plan, plan-correction note or threat delta. Do not
modify AES-C0/C1 artifacts, global Continuity/Compass, AGENTS,
`implementation_plan.md`, API Spine artifacts, fast-profile configuration or
any pre-existing test.

## Exact implementation contract

- Check all five inherited AES-C1 SHA-256 values from the plan before any
  simulation and reuse the exact C1 validation, digest and admission functions.
- Preserve C1's exact closed contract, decision and reason vocabulary. C2 may
  not weaken C1 or admit a C1 denial/stop.
- Freeze exactly one immutable registry entry with every identity and boundary
  field specified by the plan. Candidate/work-cell content selects none of it.
- Keep two digest layers separate:
  - the registry `adapter_artifact_digest` must exactly equal the C1 manifest
    and current-generation authored-synthetic identity `sha256:` followed by 64
    `f` characters; and
  - `implementation_definition_digest` must be recomputed over the one closed
    C2 declarative adapter definition and compared only with its own registry
    field.
  There is no equality or preimage relation between those values.
- Define exactly one fixed pure adapter function in source. Use no dynamic
  import, reflection, plugin loading, candidate-indexed callable map, `eval`,
  `exec`, template/deserialization engine, environment read, filesystem,
  subprocess, socket, HTTP or database client.
- Use only the explicit `synthetic-noncredential-fixture:` fixture with
  `real_credential: false`. It remains broker-private and is unusable as a real
  secret, token, key, password or identity.
- Recursively prove the fixture handle/value never occurs in the work-cell
  view, admission attempt or decision, adapter invocation/result, evidence,
  exception text or returned simulator result. Only the broker-private digest
  comparison may observe it.
- Recompute exact AES-C1 admission, then immediately recheck generation,
  manifest, current authority, revocation and external kill before invocation.
  Any post-admission change stops before the pure call.
- Verify and commit the exact C1 budget-after digest and all cumulative counts
  before invocation. Terminal/exhausted state permits no following operation or
  cross-generation transfer.
- Construct the closed invocation entirely from the one registry plus admitted
  candidate digest and the two allowlisted authored-synthetic values. Validate
  invocation and result digests independently.
- Execute the exact 26 scenario IDs with exact status/reason/call counts: two
  `simulated`, four `not_dispatched` and twenty terminal `stop`. Only the two
  success scenarios call once, except the exact malformed-result scenario may
  call once but must release nothing and stop. Every other scenario calls zero
  times.
- Generate all exact 18 independent hostile attempt/result mutations from the
  plan and nested C2 contract mutations. Every one fails closed with zero
  released simulated result.
- Emit closed minimized evidence only. Do not record raw candidate values,
  prompts, reasoning, fixture values, credentials, exceptions, patient/product
  data or source content.
- Evidence must state zero real runtime starts, provider/model calls, network,
  database/source, filesystem, executable/tool/command/product operations and
  zero real credentials or patient/product data.

## Forbidden surfaces

- protected evidence and historical Diary PHI;
- patient, clinical, product-derived, financial or licensed data;
- real broker, work-cell process, container, adapter, plugin, route, listener
  or watcher;
- provider/model calls, real credentials, IAM, metadata, network or external
  retrieval;
- database/source access, persistence, migration or SQL;
- filesystem capability, executable tool, shell/process capability, product
  command/write or cleanup actuator;
- deployment, production, release, Pages or protected refs;
- package installation or environment mutation;
- edits outside the seven owned paths;
- `git add .`, `git add -A`, force operations or pushing any ref.

Shell commands used for exact repository checks are ordinary development
actions, not simulated leaseable work-cell capabilities. Keep them exact and
within the authorized worktree.

## Verification

Use the existing interpreter only:
`C:\Users\sarashera\emr4\.venv\Scripts\python.exe`.

Run at minimum, serially where pytest loads repository `conftest.py`:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\ariadne_serial_pytest.py --timeout-seconds 180 tests\test_raisa_agent_execution_surface_containment_gate_aes_c2.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c0.py tests\test_api_spine_artifacts.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_agent_execution_surface_containment_gate_aes_c2_broker_simulator.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c2.py
git diff --check
```

Also inspect the final diff against the required source HEAD and fail if any
path outside the seven owned paths changed. Do not run repository-wide
discovery over protected paths. If a broader check cannot be expressed with
exact safe paths, leave it to Sol.

## Commit and completion

Write the durable closeout at the owned closeout path. It must state:

- `decision: pass` or `decision: revision_required`;
- exact source and final candidate HEADs;
- changed files;
- exact 26-scenario status/reason/invocation accounting;
- hostile attempt/result and contract-mutation counts;
- tests and exact results;
- separate inherited artifact-identity and computed definition-digest evidence;
- issues found or residual risks;
- explicit zero-runtime/provider/data/real-credential/network/database/tool/
  command evidence; and
- any unfulfilled acceptance item.

If all requested checks pass, stage only the seven owned paths explicitly and
commit on `codex/aes-c2-blue-deepseek` with message
`Implement AES-C2 provider-free broker simulator`. Do not push.

Your terminal response must be concise and must not claim acceptance. Sol alone
decides whether to adopt the candidate.
