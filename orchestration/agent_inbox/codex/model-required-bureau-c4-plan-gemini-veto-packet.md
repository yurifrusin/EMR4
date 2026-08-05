# Fresh independent veto — EMR4 C4 allowlisted-actuator simulator plan

You are the fresh Gemini 3.6 Flash/high architecture and security veto
reviewer. Work read-only in the exact worktree and branch supplied by the
launcher. Verify that candidate HEAD is exactly
`febe4c47094e626ae58f1a84514fc86a43fa9b26` and keep it clean and unchanged.

## Mandatory rehydration

Read `AGENTS.md` completely, then read these current authority and source files
completely:

- `docs/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-plan.md`
- `docs/security/emr4-model-required-bureau-c4-allowlisted-actuator-simulator-threat-model-delta.md`
- `docs/emr4-model-required-bureau-c3-d3-provider-free-architecture.md`
- `docs/security/emr4-model-required-bureau-c3-d3-threat-model-delta.md`
- `docs/emr4-model-required-bureau-c3-d3-closeout.md`
- `docs/emr4-model-required-bureau-gate-zero-shared-contract.md`
- `docs/emr4-model-required-deterministic-authority-bureau-architecture.md`
- the C4 section of
  `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `orchestration/api_spine_adr.md`
- `orchestration/api_spine_programme.md`
- `tests/test_model_required_bureau_c4_plan.py`
- `orchestration/harness_settings/orchestrator_requirements.yaml`
- `orchestration/continuity/ariadne-agent-error-register/agent-error-register.json`
- `docs/ariadne-agent-error-correction-register-revision-17.md`

Exclude all prior candidate review or packet artifacts from reasoning,
including every file matching
`orchestration/agent_inbox/**/*c4*review*`, `*c4*packet*` or
`*c4*preflight*`. Do not inspect historical Antigravity projects, protected
holdouts, `docs/branding/`, patient/clinical/product-derived data, secrets or
provider runtime configuration.

## Exact review question

Decide whether the frozen C4 plan is sufficiently exact, internally consistent
and architecture-strengthening to dispatch one bounded implementation worker
without widening C3's non-execution claim or creating any real actuator.

Adversarially test at least:

1. The only forward capability is exact `restart-api-synthetic.v1` against
   `isolated_authored_synthetic / service / synthetic:api-service`, with exact
   empty parameters and one pure in-memory `degraded -> healthy` transition.
2. The only rollback capability is exact `restore-api-synthetic-lkg.v1`; no
   real process, file, database, network, cloud, IAM, product route, event
   consumer, provider product-runtime call or external effect is reachable.
3. C3's `execution_authorized: false` remains intact; plan candidate, reviewer
   assertion, hash and text never become authority. Distinct backend authority
   and a server-held opaque random one-use execution-evidence reference are
   mandatory.
4. Plan, decision, catalog, policy, actor/role, target/revision, observation,
   nonce, supersession and earliest-expiry bindings fail closed under mismatch,
   drift, role loss, tampering, replay or concurrency.
5. One fixed code-level callable map makes shell, SQL, URL, path, template,
   dynamic import/reflection, arbitrary callable names, generic dispatch and
   unknown parameters structurally unreachable.
6. Admission, idempotency, evidence consumption and attempt evidence are
   monotone; simulated effect state and effect audit have an explicit snapshot
   boundary; no fault reopens evidence or releases false success.
7. Success requires a separately invoked fresh read. Failed postcondition uses
   only the exact rollback and a second fresh read, with verified rollback and
   inconclusive rollback distinct and neither represented as success.
8. Same-key/same-fingerprint replay, same-key conflict, in-progress behavior,
   different-key evidence replay and concurrent single-winner behavior are
   deterministic and do not leak the evidence reference or ambient state.
9. Closed Draft 2020-12 schemas, canonical encoding and stable sanitized denial
   taxonomy are sufficiently specified for implementation and adversarial
   mutation tests, including rejection before authority lookup where required.
10. API Spine ownership is honest: no mounted FastAPI/REST/GraphQL route or
    external event is added, GraphQL remains read-only, and any declarative
    OpenAPI-shaped future contract is explicitly `not_mounted`.
11. The exact evidence label stops at
    `provider_free_authored_synthetic_allowlisted_actuator_simulation` and
    cannot support live recovery, real database, deployment, production or
    release claims.
12. AER-0023 honestly preserves the failed unsupported pre-planning event and
    admits only the distinct corrected five-source receipt, without implying a
    repository, transport or model fault.

Run only read-only checks that create no worktree output. At minimum run:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -B C:\Users\sarashera\emr4\scripts\ariadne_serial_pytest.py --timeout-seconds 240 -- tests\test_model_required_bureau_c4_plan.py tests\test_ariadne_agent_error_register.py tests\test_model_required_bureau_c3_d3.py tests\test_model_required_bureau_gate_zero.py tests\test_api_spine_artifacts.py tests\test_api_spine_blueprint_first_boundary.py tests\test_ariadne_verifier_worktree_preflight.py tests\test_ariadne_antigravity.py -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-c4-plan-gemini-review-001
git diff --check 4c3a682e6c1076d8b5cfdc6143a4a07a57d63a57..febe4c47094e626ae58f1a84514fc86a43fa9b26
git diff --name-status 4c3a682e6c1076d8b5cfdc6143a4a07a57d63a57..febe4c47094e626ae58f1a84514fc86a43fa9b26
git status --short --branch
git rev-parse HEAD
```

Report actionable findings first by severity with exact current paths and line
references. Name every command run, confirm exact unchanged HEAD and clean
status, distinguish observation from inference, state claims not established,
and account separately for zero candidate-runtime side effects and the
non-zero Gemini/Antigravity source-review transport. A material ambiguity,
security omission or scope conflict requires revision. If there are no material
findings, say so. End with exactly one terminal line and no other `DECISION:`
line:

`DECISION: pass`

or

`DECISION: revision_required`

Do not edit, write receipts, implement, commit, push, deploy or move refs.
