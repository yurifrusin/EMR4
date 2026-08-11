# Worker packet: AES-C1 provider-free admission rehearsal

Task ID: `raisa-aes-c1-blue-implementation-001`

Role: DeepSeek V4 Flash/high blue implementation and defensive test worker
through Claude Code `--bare`

Authorized worktree:
`C:\Users\sarashera\EMR4-worktrees\aes-c1-deepseek-blue`

Authorized branch: `codex/aes-c1-blue-deepseek`

Required source HEAD: `d47010743d25e05d7d758f91507179374a91bb04`

## Mandatory rehydration before editing

1. Read `AGENTS.md` completely.
2. Read the frozen AES-C1 plan and threat-model delta completely.
3. Read the accepted AES-C0 plan, architecture, threat-model delta, closeout,
   exact contract/schema/examples and acceptance validator needed for the
   implementation.
4. Restore Sections 5 and 6 protected-evidence and user-decision boundaries.
5. Verify your exact branch, clean worktree and source HEAD. Verify but never
   move local/origin `master` or `handoff/current`, which must remain
   `2e34bdad732fdab32fbf778280b3d3c70d66d602`.
6. Use only exact named paths. Do not enumerate, search, open or infer any
   protected fixture/support/authoring/manifest/seal/receipt/per-case surface.

## Mission

Implement the frozen AES-C1 pure, provider-free, unmounted admission rehearsal
and its defensive tests. The implementation must evaluate the full exact
manifest/grant/lease/current-generation/current-authority/proofreader/budget/
revocation intersection and emit only deterministic closed decision/evidence
objects. It must never execute an admitted operation.

First challenge the plan against the accepted AES-C0 contract. If a conceptual
or authority contradiction exists, stop without implementation and record
`revision_required` in the durable closeout. Do not silently reinterpret the
plan.

## Owned paths

You may create or edit only:

- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/admission-rehearsal-contract.schema.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/authored-synthetic-admission-scenarios.json`
- `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c1/provider-free-admission-evidence.json`
- `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py`
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c1.py`
- `orchestration/agent_inbox/claude/raisa-aes-c1-blue-implementation-closeout.md`

Do not modify the frozen plan or threat delta. Do not modify AES-C0 artifacts,
global Continuity/Compass, AGENTS, implementation_plan, API Spine artifacts,
fast-profile configuration or any pre-existing test.

## Exact implementation contract

- Check the three inherited AES-C0 SHA-256 values from the plan before any
  scenario evaluation.
- Reuse the AES-C0 closed message validator rather than weakening or copying its
  definitions.
- Implement the plan's sentinel-normalized canonical manifest SHA-256 rule and
  independently calculate candidate and budget before/after digests.
- Validate a closed `AdmissionAttempt` wrapper and closed current-generation,
  current-authority, proofreader, candidate and broker-observation subobjects.
- Treat the evaluator clock and current control states as authored-synthetic
  trusted harness inputs, never candidate content.
- Preserve the exact ordered stop/deny/allow precedence and exact AES-C0 reason
  vocabulary. A record that cannot safely populate an AES-C0 decision must fail
  the scenario packet closed; never invent a permissive placeholder.
- Compute prospective counters across every AES-C0 budget dimension. A zero
  ceiling disables the requested capability counter without pre-exhausting
  unrelated zero counters. Reaching a positive denial ceiling returns the
  current deny plus a terminal after-state; the paired following attempt stops.
- Validate and execute the exact 45 scenario IDs and expected decisions from the
  plan. Reject undeclared, duplicate or silently skipped scenarios.
- Generate independent malformed/additional/missing/wrong-type and semantic
  hostile mutations with zero admission.
- The report must state zero runtime starts, provider calls, adapters executed,
  network/database/source/tool/command operations and patient/product data.
- Evidence must contain only closed identifiers, decisions, exact reason codes,
  counts and digests. Do not record raw prompts, reasoning, credentials,
  exceptions, source content or sensitive values.

## Forbidden surfaces

- protected evidence and historical Diary PHI;
- patient, clinical, product-derived, financial or licensed data;
- runtime broker, work cell, container, adapter, route, listener or watcher;
- provider/model calls, credentials, IAM, metadata, network or external
  retrieval;
- database/source access, persistence, migration or SQL;
- filesystem capability, executable tool, shell/process capability, product
  command/write or cleanup actuator;
- deployment, production, release, Pages or protected refs;
- package installation or environment mutation;
- edits outside the seven owned paths;
- `git add .`, `git add -A`, force operations or pushing any ref.

Shell commands used for repository checks are development actions, not a
simulated leaseable work-cell capability. Keep them exact and within the
authorized worktree.

## Verification

Use the existing interpreter only:
`C:\Users\sarashera\emr4\.venv\Scripts\python.exe`.

Run at minimum, serially where pytest loads repository `conftest.py`:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\raisa_agent_execution_surface_containment_gate_aes_c1_admission.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\ariadne_serial_pytest.py --timeout-seconds 180 tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c0.py tests\test_api_spine_artifacts.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts\raisa_agent_execution_surface_containment_gate_aes_c1_admission.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c1.py
git diff --check
```

Do not run repository-wide discovery over protected paths. If a broader check
cannot be expressed with exact safe paths, leave it to Sol.

## Commit and completion

Write the durable closeout at the owned closeout path. It must state:

- `decision: pass` or `decision: revision_required`;
- exact source and final candidate HEADs;
- changed files;
- scenario/mutation counts and decisions;
- tests and exact results;
- issues found or residual risks;
- explicit zero-runtime/provider/data/adapter/tool/command evidence; and
- any unfulfilled acceptance item.

If all requested checks pass, stage only the seven owned paths explicitly and
commit on `codex/aes-c1-blue-deepseek` with message
`Implement AES-C1 provider-free admission rehearsal`. Do not push.

Your terminal response must be concise and must not claim acceptance. Sol alone
decides whether to adopt the candidate.
