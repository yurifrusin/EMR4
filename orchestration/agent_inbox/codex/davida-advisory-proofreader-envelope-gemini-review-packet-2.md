# Fresh corrected Gemini veto review: Davida advisory proofreader envelope

Role: independent deterministic-proofreader, API Spine and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\davida-advisory-proofreader-envelope-gemini-review-2`

Branch: `codex/review-davida-advisory-proofreader-envelope-2`

Baseline HEAD: `b957ed7623310206cf5f4970e1eb91241c73ef6f`

Candidate HEAD: `0238e675e791ba53527c99297b00e61e673a3577`

Settings fingerprint: `sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

This is the one bounded reviewer correction. The first project was rejected as
acceptance evidence because its narrative incorrectly claimed that recomputed
dangling default-location context returns `dangling_default_location`. The
candidate is unchanged. Exact precedence is:

- `_validate_context` invokes `_context_boundaries_ok` before binding,
  freshness or operation-specific resolution;
- recomputed duplicate resource references and recomputed dangling
  default-location references therefore return `context_boundary_invalid`;
- the later `duplicate_subject_ref` and `dangling_default_location` branches are
  defensive operation-specific guards but unreachable for an otherwise admitted
  exact parent context under the current boundary validator;
- do not describe either defensive branch as observed behavior.

Review only in this exact worktree through a genuinely fresh Antigravity
project. Do not edit/create/delete/stage/commit/push/deploy, inspect another
worktree, or inspect prior worker/reviewer receipts. Do not write temp artifacts
inside the worktree. Do not use `%TEMP%` syntax or run the acceptance script
directly. Protected evidence, credentials, historical provider material,
patient/clinical/product-derived/real-identity data and `docs/branding/` are
forbidden.

Read `AGENTS.md` completely and the EMR4 API Steward skill/checklist completely.
Inspect only the baseline-to-candidate ten-path diff, accepted Davida boundary/
pure-read plans/designs/threat/contracts/closeouts, exact parent context
implementation and named tests. Do not perform broad discovery.

Adversarially review:

- exactly two advisory operations, with proposal/apply/confirmation/write and
  unknown codes rejected before interpretation;
- frozen extra-forbid selector-only candidates, exact bindings, canonical JSON
  type equality, literal-false authority and no prose/count/claim/fact input;
- exact raw/canonical parent context, blocked sources, labels, ceiling,
  two-minute lifetime, count/row equality, unique refs, default-location
  resolution and independently recomputed revision, with the exact reason
  precedence above;
- caller-supplied timezone-aware half-open freshness and no clock read;
- deterministic summary and exact single-kind subject resolution;
- context-derived fields and grounding digest over source paths, revision and
  payload;
- fixed structured no-HTML/Markdown draft, exact context binding and all eleven
  release authority flags false;
- atomic released/rejected union, no partial payload, repair or retry;
- every nested contract object closed, all 143 leaf mutations rejected and
  committed evidence counts/hashes/sanitization accurate;
- no DB/network/provider/model/memory/clock/route/GraphQL/event/manifest/
  command dependency; API Spine remains non-authoritative context only.

Run only these commands; pytest cache is disabled and base temp is outside the
repository:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp C:\Users\sarashera\AppData\Local\Temp\emr4-gemini-davida-advisory-2 -q tests\test_davida_provider_free_practice_administration_advisory.py tests\test_davida_provider_free_practice_administration_pure_read.py tests\test_davida_practice_administration_boundary.py tests\test_bernie_davida_parallel_seam.py tests\test_api_spine_artifacts.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app\schemas\practice_administration_advisory.py app\services\practice\practice_administration_advisory_proofreader.py scripts\davida_provider_free_practice_administration_advisory_acceptance.py tests\test_davida_provider_free_practice_administration_advisory.py
git diff --check b957ed7623310206cf5f4970e1eb91241c73ef6f..0238e675e791ba53527c99297b00e61e673a3577
git status --short --branch
git rev-parse HEAD
```

Additional checks must be read-only and require no worktree temp. List findings
first by severity, name each check run, confirm unchanged exact HEAD and clean
worktree, distinguish observation/inference, name claims not established, and
state the exact duplicate/dangling reason precedence. End with exactly one
terminal line: `DECISION: pass` or `DECISION: revision_required`.
