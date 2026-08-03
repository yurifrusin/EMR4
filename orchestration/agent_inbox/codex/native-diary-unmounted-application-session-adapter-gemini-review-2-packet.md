# Fresh Gemini veto review 2: native-Diary application-session runtime

Role: independent runtime, API Spine and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\native-diary-unmounted-application-session-adapter-gemini-review-2`

Branch: `codex/review-native-diary-unmounted-application-session-adapter-2`

Baseline HEAD: `0d8b2985fdae2ca488ae90e2ae1a5842190b296b`

Candidate HEAD: `ef38162afbf89f96aacc9f255bdced9a15934bf3`

Settings fingerprint: `sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

This is a genuinely fresh review. Do not inspect any prior reviewer/worker
receipt, prior review packet, or another worktree. Review only in this exact
worktree and do not edit/create/delete/stage/commit/push/deploy. Protected
evidence, credentials, patient/clinical/product-derived/real-identity data,
providers and `docs/branding/` are forbidden.

Read `AGENTS.md` and the EMR4 API Steward skill/checklist completely. Inspect
only the baseline-to-candidate diff, the six candidate paths, accepted Diary
composition artifacts, exact shared application-session router/bridge,
practitioner model/read definitions, and three named focused tests.

Perform the full adversarial review required by the first-order contract:
default-off/unmounted behavior; exact ASGI pre-auth body/method/content/query/
variables/projection gate and replay; generic no-store rejection; exact native
surface/read-only router binding; no caller authority inputs or fallbacks; no
Office/agent/provider/write coupling; long-lived reads and revocation/audit/
privacy behavior; honest in-flight UI limit; safe evidence and complete cleanup;
API Spine read-only conformance.

For source-grounding integrity, your report must additionally quote exactly,
from the candidate source (not memory or inference):

- the declared SQLAlchemy length of each of `provider_number`,
  `prescriber_number`, `ahpra_number`, and `hpi_i`;
- the exact four values in `PRACTITIONER_SEED_MARKERS` and their character
  lengths;
- the exact assertion mechanism used by
  `test_practitioner_seed_markers_stay_within_model_limits`.

If any reported value differs from source, return `revision_required` for
reviewer evidence integrity even if tests pass.

Run serially; do not run the live acceptance script because it writes evidence:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py tests\test_raisa_provider_free_native_diary_application_session_practitioner_composition.py tests\test_raisa_provider_free_session_practitioner_directory_read_bridge.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app\graphql\native_diary_application_session_practitioner.py scripts\raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance.py tests\test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py
git diff --check 0d8b2985fdae2ca488ae90e2ae1a5842190b296b..ef38162afbf89f96aacc9f255bdced9a15934bf3
git status --short --branch
git rev-parse HEAD
```

List findings first by severity and exact evidence, name checks actually run,
separate observation from inference, confirm exact clean unchanged worktree/HEAD,
and state claims not established. End with exactly one terminal line:
`DECISION: pass` or `DECISION: revision_required`.
