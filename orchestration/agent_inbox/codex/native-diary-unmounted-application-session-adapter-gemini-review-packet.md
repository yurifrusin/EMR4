# Fresh Gemini veto review: native-Diary application-session runtime

Role: independent runtime, API Spine and security veto reviewer only

Exact model/effort: `gemini-3.6-flash-high` / `high`

Worktree: `C:\Users\sarashera\EMR4-worktrees\native-diary-unmounted-application-session-adapter-gemini-review`

Branch: `codex/review-native-diary-unmounted-application-session-adapter`

Baseline HEAD: `0d8b2985fdae2ca488ae90e2ae1a5842190b296b`

Candidate HEAD: `ef38162afbf89f96aacc9f255bdced9a15934bf3`

Settings fingerprint: `sha256:71b4cdb0e461a900b76517a1744dd5ef45a59b2b44a478d1fb245842dc7786b9`

Review only in this exact worktree through a genuinely fresh Antigravity
project. Do not edit, create, delete, stage, commit, push, deploy, access another
worktree, or inspect any prior DeepSeek/Gemini receipt or review packet.
Protected evidence, credentials, historical provider material, patient/clinical/
product-derived/real-identity data and `docs/branding/` are forbidden.

Read `AGENTS.md` completely and the EMR4 API Steward skill/checklist completely.
Inspect only the baseline-to-candidate diff, its six committed runtime/evidence
paths, the accepted native-Diary composition plan/design/threat/contract/schema/
closeout, exact shared application-session product router/bridge and practitioner
read implementation, and the three named focused test files. Do not perform
broad repository discovery.

Adversarially review:

- default-off returns no route/docs/OpenAPI and opens no bridge/database;
- literal enablement only and unmounted isolation from `app.main`/Diary assets;
- ASGI pre-auth guard's 8192-byte bound and replay safety;
- exact POST + application/json + fixed operation/query/projection/variables;
- rejection before authentication for method/content/JSON/extra key/practiceId,
  alias/fragment/directive/introspection/mutation, field and pagination drift;
- generic 403/no-store handling without an oracle;
- exact server-side `Surface.NATIVE_DIARY` binding and reuse of the shared
  read-only router/bridge with no policy/action/resource inputs from callers;
- no bearer/localStorage or REST fallback on the enabled path;
- no Office/Bernie/Davida/proofreader/provider/write dependency;
- long-lived native same-session reads, audit-before-release, revocation denial,
  role/tenant/privacy boundaries and the honest in-flight UI claim limit;
- seed-length repair correctness and regression against actual model lengths;
- evidence is schema/claim consistent, safe, authored-synthetic and records
  complete listener/database/four-role cleanup without secrets or identifiers;
- API Spine scoped read-only conformance and absence of command/event authority.

Run serially and do not run the live acceptance script because that would write
the committed evidence file:

```powershell
C:\Users\sarashera\emr4\.venv\Scripts\python.exe -m pytest -q tests\test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py tests\test_raisa_provider_free_native_diary_application_session_practitioner_composition.py tests\test_raisa_provider_free_session_practitioner_directory_read_bridge.py
C:\Users\sarashera\emr4\.venv\Scripts\ruff.exe check app\graphql\native_diary_application_session_practitioner.py scripts\raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance.py tests\test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py
git diff --check 0d8b2985fdae2ca488ae90e2ae1a5842190b296b..ef38162afbf89f96aacc9f255bdced9a15934bf3
git status --short --branch
git rev-parse HEAD
```

Additional allowlisted read-only adversarial checks are permitted, but do not
write temp artifacts inside the worktree. List findings first by severity with
exact evidence. Name every check actually run, confirm exact unchanged HEAD and
clean worktree, distinguish observed evidence from inference, and name claims
not established. End with exactly one terminal line:
`DECISION: pass` or `DECISION: revision_required`.
