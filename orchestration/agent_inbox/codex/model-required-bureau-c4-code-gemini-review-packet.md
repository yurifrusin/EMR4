# Fresh independent code veto — EMR4 C4 allowlisted-actuator simulator

Use only the launcher-bound fresh read-only worktree:

- branch `codex/review-model-required-bureau-c4-code`
- exact HEAD `955b6a566f7097f58929dcb2fa9c4ed0aaad8b29`

You are the fresh Gemini 3.6 Flash/high architecture, concurrency and security
veto reviewer. Verify the exact worktree, branch, HEAD and clean state first and
again last. Do not edit, stage, commit, push, deploy, move refs or create files
inside the worktree. Temporary pytest output may go only to the exact external
temporary path named below.

## Mandatory five-source rehydration

Read `AGENTS.md` completely. Explicitly restore and name all five sources:
`live_handover_current_baton`, `current_authority_allocation`,
`active_plan_and_acceptance`, `protected_evidence_boundaries`, and
`git_refs_and_worktree`. Then read these current source and authority artifacts
completely:

- `docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-plan.md`
- `docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-threat-model-delta.md`
- `docs/emr4-model-required-bureau-c3-d3-provider-free-architecture.md`
- `docs/emr4-model-required-bureau-c3-d3-closeout.md`
- `docs/emr4-model-required-bureau-gate-zero-shared-contract.md`
- the C4 section of
  `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `orchestration/agent_inbox/codex/model-required-bureau-c4-worker-independent-review.md`
- `orchestration/agent_inbox/codex/model-required-bureau-c4-repair-independent-audit.md`
- `docs/ariadne-agent-error-correction-register-revision-20.md`
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`
- all C4 simulator source, schemas, examples, generated acceptance evidence and
  focused tests under the owned paths.

Do not inspect other historical C4 reviewer outputs or Antigravity projects,
protected holdouts, `docs/branding/`, credentials, provider configuration,
patient/clinical/product-derived data or any product runtime.

## Exact veto question

Decide whether exact candidate `955b6a566f7097f58929dcb2fa9c4ed0aaad8b29`
fully and honestly closes all ten independently identified findings while
remaining within the frozen local, in-memory, provider-free,
authored-synthetic C4 boundary. A material concurrency gap, authority gap,
false acceptance proof, schema/API mismatch or scope expansion requires
`revision_required`.

Adversarially assess each finding separately:

1. Every scalar is type/format/bounds checked before lookup, fingerprinting,
   idempotency sealing, evidence consumption or audit; boolean is not integer.
2. Precondition, success and rollback readback compare the exact actual target
   tuple, and released target data derives from verified readback rather than
   constants.
3. Execution revalidates genuine current plan, decision, catalog, policy,
   actor, reviewer and observation sources rather than treating evidence as
   current authority.
4. Effect audit survives only exact verified success; every denial/rollback
   path restores it while monotone attempt evidence and evidence consumption
   remain.
5. Both receipt schemas close and require the exact 18 named zero-capability
   counters and reject renamed, missing, extra or non-zero counters.
6. Production issuance exposes no caller-selectable reference or nonce and
   always uses cryptographic entropy; deterministic entropy exists only by
   acceptance/test monkeypatching.
7. Issuance uniqueness is one locked check-and-insert with exact concurrent
   single-winner behavior.
8. Current reviewer authority requires exact closed role `reviewer`; a
   non-empty `revoked_but_nonempty` role denies with zero effect.
9. Current authority is locked and stable across the complete execution
   decision, simulated transition, audit, readback and any rollback, so role or
   policy mutation cannot interleave after validation and before effect.
10. Every runtime sharing one evidence store also shares one transaction lock,
    idempotency records, supersession state and monotone attempt sequence;
    cross-runtime different-key races admit exactly one attempt/effect and
    same-key replay returns the one stored terminal receipt.

Also verify:

- only fixed `restart-api-synthetic.v1` and exact rollback
  `restore-api-synthetic-lkg.v1` are callable, against only
  `isolated_authored_synthetic / service / synthetic:api-service`;
- no shell, filesystem, process, SQL, network, database, container, cloud, IAM,
  secret, provider, external-event, dynamic import, reflection, generic
  callable, path/URL/template or product-route capability is reachable;
- the OpenAPI-shaped contract stays explicit `not_mounted`, no `app.main` or
  router import exists, GraphQL remains read-only and no command/product runtime
  surface is opened;
- `execution_authorized: false` remains C3 truth and plan/reviewer/model text
  never becomes authority;
- acceptance evidence is reproducible and contains direct observed outcomes
  for the ten findings, not only assertions about source; and
- AER-0025/AER-0026 truthfully preserve both rejected worker self-passes and the
  Sol recovery lease without erasing or reclassifying their failures.

## Read-only checks

Run at least these commands from the bound worktree, using no cache provider:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe scripts\model_required_bureau_c4_acceptance.py --check
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B C:\Users\sarashera\emr4\scripts\ariadne_serial_pytest.py --timeout-seconds 300 -- tests\test_model_required_bureau_c4_simulator.py tests\test_model_required_bureau_c4_plan.py tests\test_model_required_bureau_c3_d3.py tests\test_model_required_bureau_c3_d3_continuity.py tests\test_model_required_bureau_gate_zero.py tests\test_model_required_bureau_gate_zero_continuity.py tests\test_api_spine_openapi_backend_alignment.py tests\test_ariadne_agent_error_register.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-c4-code-gemini-review-001
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check scripts/model_required_bureau_c4_simulator.py scripts/model_required_bureau_c4_acceptance.py tests/test_model_required_bureau_c4_simulator.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m bandit -q -r scripts/model_required_bureau_c4_simulator.py scripts/model_required_bureau_c4_acceptance.py
git diff --check b66b37a81120b1abd655ce65c42daf7518b8f7d5..955b6a566f7097f58929dcb2fa9c4ed0aaad8b29 -- scripts/model_required_bureau_c4_simulator.py scripts/model_required_bureau_c4_acceptance.py tests/test_model_required_bureau_c4_simulator.py orchestration/continuity/model-required-bureau-c4-allowlisted-actuator-simulator docs/api-spine/openapi/technical-control-simulator-commands.yaml
git diff --name-status b66b37a81120b1abd655ce65c42daf7518b8f7d5..955b6a566f7097f58929dcb2fa9c4ed0aaad8b29 -- scripts/model_required_bureau_c4_simulator.py scripts/model_required_bureau_c4_acceptance.py tests/test_model_required_bureau_c4_simulator.py orchestration/continuity/model-required-bureau-c4-allowlisted-actuator-simulator docs/api-spine/openapi/technical-control-simulator-commands.yaml
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first by severity with exact paths and current line
references. Name every command and its result. Explicitly distinguish observed
facts from inference and name claims not established. Account separately for
zero candidate-runtime external effects and the one authorised non-zero
Gemini/Antigravity source-review transport. Confirm final exact HEAD and clean
worktree.

Return exactly one final report after every command and background task has
completed. Do not write `DECISION:` in progress text. End with exactly one
terminal line and nothing after it:

`DECISION: pass`

or

`DECISION: revision_required`
