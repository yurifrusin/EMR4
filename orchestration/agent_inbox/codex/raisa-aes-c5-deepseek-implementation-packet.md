# DeepSeek implementation packet — AES-C5 pure containment core

Task id: `raisa-aes-c5-deepseek-pure-core-001`

Worker: DeepSeek V4 Flash/high through Claude Code `--bare`

Source HEAD: `1e2756f15eb3ff3fe051b72855d773b4a82ff6a6`

Worktree: `C:\Users\sarashera\EMR4-worktrees\aes-c5-deepseek-blue`

Branch: `codex/aes-c5-blue-deepseek`

## Mandatory start

1. Read `AGENTS.md` completely before any other action.
2. Verify the exact worktree, branch, clean status and source HEAD above.
3. Read these exact accepted inputs completely:
   - `docs/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-plan.md`;
   - `docs/security/raisa-agent-execution-surface-containment-gate-aes-c5-product-runtime-admission-threat-model-delta.md`;
   - `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/product-runtime-envelope.json`;
   - `orchestration/continuity/raisa-agent-execution-surface-containment-gate-aes-c5/product-runtime-envelope.schema.json`;
   - `scripts/raisa_agent_execution_surface_containment_gate_aes_c1_admission.py` only for its public admission/digest contract; and
   - `scripts/raisa_agent_execution_surface_containment_gate_aes_c4_provider_proof.py` only for reusable deterministic JSON, provider-adapter and ledger patterns.
4. Do not perform repository-wide discovery. Inspect only direct imports and the exact named files above.

## Owned files

Create and own only:

- `scripts/raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission.py`;
- `tests/test_raisa_agent_execution_surface_containment_gate_aes_c5.py`; and
- one commit on the worker branch containing exactly those files.

Do not edit the frozen plan, envelope, threat model, AGENTS.md, application
route/service/schema/dependencies, conftest, API Spine artifacts, continuity
maps, evidence JSON, ledgers or any other file.

## Implementation contract

Implement a provider-free, database-free pure containment core with injectable
source/provider adapters. Sol will later add or bind the real local route and
live Vertex execution only after review. Your implementation must not contact a
database, application route, cloud service or provider.

Required public behavior:

- validate the exact AES-C5 envelope against its schema and exact frozen values;
- verify exact inherited AES-C0 through AES-C4 contract/source artifact
  digests, deriving the current expected digests from the committed source only
  during implementation and then freezing them in the new script;
- build one immutable generation with exactly two grants:
  `authoritative_read` for the frozen practitioner-directory GET and
  `provider_inference` for the exact Sydney Vertex POST;
- build two distinct broker-owned single-use leases and sequential AES-C1
  admission attempts with cumulative budget state;
- ensure the first admission remains active and the second exhausts the model-
  call budget; current authority, generation, supply chain and revocation are
  checked before both;
- accept an injected exact route-response list and strictly validate exactly
  three rows with keys `id`, `displayName`, `roleLabel`, `active`,
  `defaultLocation`;
- require UUID ids, unique ids/names, active true, nonblank bounded synthetic
  names, optional bounded role labels, no fourth row and no unknown/nested
  sensitive fields;
- minimize into order-derived opaque aliases plus `display_name` and optional
  `role_label`; never place UUID, active, location or alias-map values in the
  work-cell/provider/evidence boundary;
- build a typed, source-labelled, digest-bound, 60-second ContextFrameSet and
  enforce a 30-second source-to-provider-dispatch age;
- build a closed Vertex request over the minimized frame and the authored-
  synthetic target `Marlow Quill`; candidate/model content cannot choose any
  operation identity;
- deterministically proofread a provider result with exactly
  `decision_code`, `selected_practitioner_ref`,
  `context_frame_set_digest`, `command_authority`; accept only the exact target
  alias grounded in the admitted frame and `command_authority: false`;
- supply provider-free source and provider fixtures only; no network, ADC,
  token, TestClient, SQLAlchemy engine/session or subprocess execution;
- maintain separate single-use source/provider ledgers and consume/revoke them
  on every terminal path;
- emit minimized evidence containing digests/counts/reason codes only, never
  names, UUIDs, route values, JWTs, prompts, provider text or environment data;
- expose a CLI that runs provider-free only. Any request for local-source or
  live mode must fail before I/O with a closed reason code;
- no repair, retry, fallback, command or write path.

## Required hostile tests

Test at least:

- envelope/schema and inherited-digest drift;
- missing/extra grant, wrong class/route/method/query/provider/destination;
- candidate-selected selector/URL/SQL/path/tool/command/credential fields;
- wrong, duplicate, malformed or non-UUID ids;
- inactive, missing/extra/fourth row;
- blank, duplicate, oversized or non-string display name;
- malformed/oversized role label;
- unexpected route field and nested sensitive field;
- raw UUID/name/alias-map leakage into minimized evidence;
- stale/expired ContextFrameSet and wrong manifest/source/context digest;
- wrong target alias, extra/missing/wrong provider output fields, duplicate JSON
  keys, wrong command authority;
- cumulative budget exhaustion, stale lease, supersession, authority change,
  external kill/revocation and replay;
- ledger consumption and cleanup after allow and every denial/failure;
- CLI live/local-source denial before adapter invocation.

Tests must be deterministic, provider-free, database-free and use newly authored
synthetic values only. Do not import or inspect protected holdouts, historical
Diary material, readiness fixtures or broad test/support roots.

## Verification

Run serially:

```powershell
.venv\Scripts\python.exe -m pytest tests\test_raisa_agent_execution_surface_containment_gate_aes_c5.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5_plan.py -q
.venv\Scripts\python.exe -m ruff check scripts\raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5.py
.venv\Scripts\python.exe -m py_compile scripts\raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission.py tests\test_raisa_agent_execution_surface_containment_gate_aes_c5.py
git diff --check
```

If the worktree lacks `.venv`, invoke the exact root interpreter
`C:\Users\sarashera\emr4\.venv\Scripts\python.exe` while keeping cwd in the
worker worktree.

## Commit and return contract

Stage only the two owned files with explicit paths. Never use `git add .` or
`git add -A`. Commit with message:

`Implement AES-C5 provider-free containment core`

Return a concise report naming:

- decision: `candidate_ready` or `revision_required`;
- exact commit SHA;
- changed files;
- test/Ruff/compile/diff results;
- hostile-test count;
- provider calls, product reads and database operations, all of which must be
  zero; and
- blockers or deviations.

You do not have acceptance, integration, push, protected-ref, provider,
product-data, database, credential, deployment, production or release authority.

## Forbidden surfaces

Never list, search, open, hash, import or execute any protected fixture,
support module, holdout, authoring surface, manifest, seal, receipt or per-case
report. Do not inspect `docs/branding/` or any unrelated untracked path. Do not
touch master, handoff/current, origin refs, network/provider/cloud credentials,
application/database runtime, real or product data, patient/clinical data,
commands/writes, deployment, production, Pages or release surfaces.
