# DeepSeek implementation packet — Ariadne risk-weighted workflow reform

Date: 2026-08-16

Timestamp: 2026-08-16T08:58:00+10:00 (Australia/Brisbane)

Role: bounded mechanical implementation/test worker only

Model: DeepSeek V4 Flash/high through Claude Code `--bare`

Source HEAD: `721f4cf1dd7bce27429ed97fdeb6028ba85ed954`

Worktree: `C:\Users\sarashera\EMR4-worktrees\ariadne-risk-weighted-worker-721f4cf1`

Branch: `codex/worker-ariadne-risk-weighted-721f4cf1`

## Authority

Read and implement the exact frozen contract in
`docs/ariadne-risk-weighted-workflow-reform-plan.md` and
`docs/security/ariadne-risk-weighted-workflow-reform-threat-model-delta.md`.
Do not revise their meaning. Sol alone owns semantics, acceptance, integration,
continuity, Git publication and protected refs.

## Exact owned paths

You may create or edit only:

- `orchestration/harness_settings/risk_weighted_workflow.yaml`
- `orchestration_harness/risk_weighted_workflow.py`
- `scripts/ariadne_risk_weighted_workflow.py`
- `scripts/ariadne_verifier_worktree_preflight.py`
- `scripts/ariadne_serial_pytest.py`
- `tests/test_ariadne_risk_weighted_workflow.py`
- `tests/test_ariadne_verifier_worktree_preflight.py`
- `tests/test_ariadne_serial_pytest.py`
- `orchestration/continuity/ariadne-risk-weighted-workflow-reform/tranche-profile.schema.json`
- `orchestration/continuity/ariadne-risk-weighted-workflow-reform/tranche-result.schema.json`
- `orchestration/continuity/ariadne-risk-weighted-workflow-reform/tranche-profile.example.json`
- `orchestration/continuity/ariadne-risk-weighted-workflow-reform/tranche-result.example.json`
- `orchestration/continuity/ariadne-risk-weighted-workflow-reform/provider-free-authored-synthetic-evidence.json`

Do not edit the plan, threat delta, AGENTS, current latch, existing Ariadne
settings, error register, receipts, closeout documents or any product path.

## Required implementation

1. Add a standard-library-only pure module that validates the exact tranche
   profile/result schemas, derives the highest risk tier, computes required
   baseline/gates/review, validates semantic versus volatile bindings, returns
   the union rerun decision, verifies named-threat coverage, incident grouping
   and safe tail deferral, and admits a result only when its tier-required
   evidence is complete.
2. Add a thin CLI that reads only explicitly supplied JSON and provides
   validation/classification/rerun/admission operations. A render operation may
   write only explicit output paths for closeout, Sol acceptance, Yuri summary,
   Continuity payload and Compass payload. It executes no command and applies
   no authority update.
3. Add the machine policy and exact JSON schemas/examples/evidence.
4. Extend `ariadne_serial_pytest.py` with an explicit resolved `--repo-root`.
   Default compatibility remains. The root must be a repository containing
   `tests/conftest.py`, and subprocess cwd must be that root.
5. Extend verifier-worktree preflight with optional exact v1 command-manifest
   and typed repository-path bindings. Validate existence, kind and containment
   without execution. A serial runner outside the review worktree must bind
   `--repo-root` exactly to the review worktree; relative candidate tests behind
   a different root must fail.
6. Add focused tests covering every threat `RWW-001` through `RWW-018` and at
   least fifty named hostile semantic mutations. Numeric volume alone is not
   acceptance.

## Verification

Run only serial commands in this worktree:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest tests/test_ariadne_risk_weighted_workflow.py tests/test_ariadne_verifier_worktree_preflight.py tests/test_ariadne_serial_pytest.py -q
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m ruff check orchestration_harness/risk_weighted_workflow.py scripts/ariadne_risk_weighted_workflow.py scripts/ariadne_verifier_worktree_preflight.py scripts/ariadne_serial_pytest.py tests/test_ariadne_risk_weighted_workflow.py tests/test_ariadne_verifier_worktree_preflight.py tests/test_ariadne_serial_pytest.py
git diff --check 721f4cf1dd7bce27429ed97fdeb6028ba85ed954 HEAD
```

You may add focused deterministic schema/evidence checks inside the owned test
file. Do not run a provider, database, browser, deployment or product command.

## Forbidden surfaces

No Raisa application/API/UI/migration edit; no database, SQL, Docker, product or
patient data; no provider/model call beyond this implementation transport; no
credentials/IAM, browser/network adapter, product tool/command, deployment,
production, release, Pages or protected ref. Do not discover or touch protected
fixtures. Do not stage `docs/branding/` or any unrelated path.

## Required result

Commit only owned paths to the worker branch. Return one JSON result naming:

- decision: `candidate_ready` or `revision_required`;
- exact commit and changed paths;
- tests and exit codes;
- threat IDs covered and hostile mutation count;
- any ambiguity or deviation; and
- confirmation that no forbidden surface was touched.

Your self-result is candidate evidence only and never acceptance.
