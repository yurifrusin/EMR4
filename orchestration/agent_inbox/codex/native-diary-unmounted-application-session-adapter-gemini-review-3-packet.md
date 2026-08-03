# Fresh Gemini veto review 3: native-Diary application-session runtime

Role: independent runtime, API Spine and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\native-diary-unmounted-application-session-adapter-gemini-review-3`

Branch: `codex/review-native-diary-unmounted-application-session-adapter-3`

Baseline HEAD: `0d8b2985fdae2ca488ae90e2ae1a5842190b296b`

Candidate HEAD: `ef38162afbf89f96aacc9f255bdced9a15934bf3`

Settings fingerprint: `sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

This is the final bounded fresh attempt. Do not inspect any prior review or
worker output, prior review packet, or another worktree. Review only in this
exact worktree. Do not edit/create/delete/stage/commit/push/deploy. Protected
evidence, credentials, patient/clinical/product-derived/real-identity data,
providers and `docs/branding/` are forbidden.

Read `AGENTS.md` and the EMR4 API Steward skill/checklist completely. Inspect
only the baseline-to-candidate diff, six candidate paths, accepted Diary
composition artifacts, exact shared application-session router/bridge,
practitioner model/read definitions and three named focused tests.

Adversarially review default-off/unmounted behavior; exact bounded/replay-safe
ASGI pre-auth request gate; generic no-store rejection; exact native surface and
read-only router binding; absence of caller authority inputs/fallbacks/Office/
agent/provider/write dependencies; long-lived read, audit, revocation, role,
tenant and privacy behavior; the in-flight UI claim limit; evidence safety and
cleanup claims; and API Spine read-only conformance.

Run these commands serially; do not run the live acceptance script:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py tests\test_raisa_provider_free_native_diary_application_session_practitioner_composition.py tests\test_raisa_provider_free_session_practitioner_directory_read_bridge.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app\graphql\native_diary_application_session_practitioner.py scripts\raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance.py tests\test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -c "import json; from app.models.tenancy import Practitioner; from scripts.raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance import PRACTITIONER_SEED_MARKERS as m; print(json.dumps({'columns': {k: Practitioner.__table__.c[k].type.length for k in m}, 'markers': {k: {'value': v, 'length': len(v)} for k, v in m.items()}}, sort_keys=True))"
git diff --check 0d8b2985fdae2ca488ae90e2ae1a5842190b296b..ef38162afbf89f96aacc9f255bdced9a15934bf3
git status --short --branch
git rev-parse HEAD
```

Your report must reproduce the one-line JSON emitted by the third command
verbatim. Do not manually recalculate or paraphrase its lengths. Then quote the
source regression mechanism that checks each `len(marker)` against
`Practitioner.__table__.c[column_name].type.length`. Any discrepancy forces
`revision_required`.

List findings first by severity and exact evidence, name checks actually run,
separate observations from inference, confirm exact clean unchanged worktree and
HEAD, and state claims not established. End with exactly one terminal line:
`DECISION: pass` or `DECISION: revision_required`.
