# Fresh corrected Gemini veto review: Davida default-location dry-run proposal

Role: independent deterministic-proofreader, API Spine and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-default-location-dry-run-gemini-review-2`

Branch: `codex/review-davida-default-location-dry-run-2`

Baseline HEAD: `e7d209e6652106c8f69036460223259a33af19c9`

Candidate HEAD: `21e11b33e2c873be0ee2b12db0e57b599e24c8a1`

Settings fingerprint: `sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

This is one bounded reviewer correction. The first Antigravity project was
rejected as acceptance evidence because it ran an unlisted evidence-writing
command and then falsely reported 25/25 cases. The candidate is unchanged.
The committed acceptance evidence records exactly 60 cases, 60 passed, zero
failed, 2 released and 54 rejected; the remaining four cases are static or
contract checks and are not verdict invocations.

Review only in this exact worktree through one genuinely fresh Antigravity
project. Do not edit/create/delete/stage/commit/push/deploy, inspect another
worktree, inspect the first review receipt, or run the acceptance script. Do
not write temporary artifacts inside the worktree. Do not run any command not
listed below. Protected evidence, credentials, historical provider material,
patient/clinical/document/product-derived/real-identity data and
`docs/branding/` are forbidden.

Read `AGENTS.md` completely and the EMR4 API Steward skill/checklist
completely. Inspect only the baseline-to-candidate eleven-path diff, accepted
Davida boundary/pure-read/advisory artifacts, exact parent context
implementation, new plan/design/threat/contract/evidence and named tests. Treat
the worker receipt as an opaque path-integrity artifact; do not rely on its
narrative. Do not perform broad discovery.

Adversarially review:

- exactly `PROPOSE_UPDATE_PRACTITIONER_DEFAULT_LOCATION` is admitted, with
  unknown operations rejected before interpretation;
- frozen extra-forbid selector-only candidates, exact canonical JSON type
  equality and literal-false authority prevent prose, facts or effectful intent;
- the accepted parent context is independently admitted and rebound by schema,
  blocked sources, labels, source paths, authority ceiling, practice/principal/
  correlation/revision, two-minute lifetime, count/row equality, unique opaque
  references, kind separation and resolved default locations;
- caller-supplied timezone-aware half-open freshness is used with no clock read;
- exact one-practitioner/one-location resolution produces only context-derived
  before/after state, source paths, changed path and bound hashes;
- current-null is preserved, same-location rejects, and every rejection is
  atomic with no proposal, repair or retry;
- the exported result union and machine contract enumerate exactly fourteen
  producer-reachable rejection reasons: duplicate and dangling parent context
  return `context_boundary_invalid`, while truthy authority fields return
  `candidate_schema_invalid` (or `candidate_noncanonical` for coercible numeric
  false); no unreachable public reason remains;
- the released artifact is non-authoritative `proposal_candidate` /
  `dry_run_only`, requires human confirmation and carries false command-ready,
  confirmation, apply, write, provider, model, database, network and
  model-to-database authority;
- all nested contract objects are recursively closed, leaf mutations reject,
  the committed evidence accurately records the exact 60/60 case accounting
  and hashes/sanitization, and no route/DB/network/clock/provider/model/memory/
  GraphQL/event/manifest dependency appears.

Run exactly and only these commands; pytest cache is disabled and base temp is
outside the repository:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-davida-default-location-2 tests\test_davida_provider_free_practice_administration_default_location_dry_run.py tests\test_davida_provider_free_practice_administration_advisory.py tests\test_davida_provider_free_practice_administration_pure_read.py tests\test_davida_practice_administration_boundary.py tests\test_bernie_davida_parallel_seam.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app\schemas\practice_administration_default_location_proposal.py app\services\practice\practice_administration_default_location_dry_run.py scripts\davida_provider_free_practice_administration_default_location_dry_run_acceptance.py tests\test_davida_provider_free_practice_administration_default_location_dry_run.py
git diff --check e7d209e6652106c8f69036460223259a33af19c9..21e11b33e2c873be0ee2b12db0e57b599e24c8a1
git status --short --branch
git rev-parse HEAD
```

List findings first by severity, name each listed check actually run, confirm
unchanged exact HEAD and clean worktree, distinguish observation from
inference, state the exact 60-case accounting, and name claims not established.
Do not claim any unlisted command, evidence regeneration or case count. End
with exactly one terminal line: `DECISION: pass` or
`DECISION: revision_required`.
