# Fresh Gemini veto review: Davida advisory proofreader envelope

Role: independent deterministic-proofreader, API Spine and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-advisory-proofreader-envelope-gemini-review`

Branch: `codex/review-davida-advisory-proofreader-envelope`

Baseline HEAD: `b957ed7623310206cf5f4970e1eb91241c73ef6f`

Candidate HEAD: `0238e675e791ba53527c99297b00e61e673a3577`

Settings fingerprint: `sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

Review only in this exact worktree through a genuinely fresh Antigravity
project. Do not edit, create, delete, stage, commit, push, deploy, inspect
another worktree, or inspect prior worker/reviewer receipts. Protected evidence,
credentials, historical provider material, patient/clinical/product-derived/
real-identity data and `docs/branding/` are forbidden.

Read `AGENTS.md` completely and the EMR4 API Steward skill/checklist completely.
Inspect only the baseline-to-candidate diff and its ten committed paths, the
accepted Davida boundary/pure-read plans/designs/threat/contracts/closeouts,
exact parent context implementation and the named focused tests. Do not perform
broad repository discovery.

The external implementation transport timed out without a transferable worker
closeout. Sol recovered candidate source under the repository recovery lease.
Review the code/evidence independently; do not treat this provenance statement
as acceptance.

Adversarially review:

- the operation type admits exactly the two advisory codes and rejects all
  proposal/apply/confirmation/write/unknown operations before interpretation;
- frozen extra-forbid selector-only candidates, exact bindings, canonical JSON
  type equality, literal-false authority and no prose/count/claim/fact input;
- exact parent-context model, raw/canonical equality, blocked sources, labels,
  ceiling, two-minute lifetime, count/row equality, unique opaque refs,
  default-location resolution and independently recomputed revision;
- caller-supplied timezone-aware half-open freshness with no clock read;
- exact single-kind subject resolution and deterministic summary derivation;
- every released field derives from context; grounding digest binds exact
  source paths, context revision and payload; context binding is exact;
- one fixed structured no-HTML/Markdown draft, every released authority flag
  false, and no arbitrary prose or command-shaped release;
- strict atomic released/rejected union, no partial rejection payload, no
  repair/retry/inference/lookup;
- contract schema closes every nested object and rejects all 143 contract-leaf
  mutations; evidence hashes and 5-release/49-rejection counts are accurate and
  sanitized;
- no SQLAlchemy/model/database/network/provider/memory/clock/route/GraphQL/
  event/manifest/command dependency and API Spine remains non-authoritative
  context only.

Run serially; do not run the acceptance script directly because that would
overwrite committed evidence. Do not use `%TEMP%` syntax and do not write any
temporary artifact inside the worktree. The explicit pytest base temp below is
outside the repository and the cache plugin is disabled:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-davida-advisory -q tests\test_davida_provider_free_practice_administration_advisory.py tests\test_davida_provider_free_practice_administration_pure_read.py tests\test_davida_practice_administration_boundary.py tests\test_bernie_davida_parallel_seam.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app\schemas\practice_administration_advisory.py app\services\practice\practice_administration_advisory_proofreader.py scripts\davida_provider_free_practice_administration_advisory_acceptance.py tests\test_davida_provider_free_practice_administration_advisory.py
git diff --check b957ed7623310206cf5f4970e1eb91241c73ef6f..0238e675e791ba53527c99297b00e61e673a3577
git status --short --branch
git rev-parse HEAD
```

Additional allowlisted read-only adversarial checks are permitted, but write no
temp artifact inside the worktree. List findings first by severity, name every
check actually run, confirm exact unchanged HEAD and clean worktree, separate
observed evidence from inference, and name claims not established. End with
exactly one terminal line: `DECISION: pass` or
`DECISION: revision_required`.
