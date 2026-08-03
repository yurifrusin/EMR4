# Native-Diary unmounted application-session adapter — DeepSeek worker packet

Source head: `0d8b2985fdae2ca488ae90e2ae1a5842190b296b`

Worktree: `C:\Users\sarashera\EMR4-worktrees\native-diary-unmounted-application-session-adapter`

Branch: `codex/native-diary-unmounted-application-session-adapter`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No fallback is authorised.

## Mandatory source pass

Read `AGENTS.md` completely and state the exact five rehydration sources. Read
the EMR4 API Steward skill/checklist completely. Read the accepted native-Diary
architecture plan/design/threat/contract/schema/closeout and only the exact
shared runtime sources named below. Verify exact branch/source and a clean
worktree before editing.

## Task

Implement the next bounded Diary descendant as one new-file-only, provider-free,
unmounted/default-off native-Diary application-session composition wrapper plus
direct loopback HTTP/PostgreSQL authored-synthetic acceptance harness.

The shared router is not strict enough by itself: it intentionally accepts
`practiceId`, display-safe field subsets and bounded pagination variations. The
accepted native-Diary contract instead requires one fixed request with no
client-selected practice or projection. Add a stricter outer pre-auth admission
guard and reuse the accepted bridge/router unchanged underneath it.

## Permitted reads

- `AGENTS.md` and this packet;
- the accepted native-Diary architecture artifacts and seam contract;
- `app/graphql/application_auth_product.py`;
- `app/services/application_auth_product_read.py`;
- `app/services/application_auth_runtime.py`, limited to surface/policy/session
  and revocation behavior;
- `app/services/application_auth_transport.py`, limited to cookie/header names;
- existing application-auth and product-read operational/database-role modules;
- `app/services/practice/practitioner_directory_read.py`;
- `app/graphql/schema.py`, limited to the practitioner read resolver;
- tenancy/auth models needed by the authored-synthetic harness;
- `scripts/raisa_provider_free_session_practitioner_directory_read_bridge_acceptance.py`,
  only as a lifecycle/helper precedent; do not reuse its Word-specific
  `run_acceptance` or query;
- `scripts/raisa_postgresql_oidc_operational_connection_boundary_acceptance.py`,
  limited to disposable database/Alembic helpers;
- `_start_server` in the accepted grant-redemption harness;
- focused parent tests named by the accepted architecture.

Do not perform broad repository discovery or inspect protected/historical
evidence.

## Owned implementation files

- `app/graphql/native_diary_application_session_practitioner.py`
- `docs/raisa-provider-free-native-diary-application-session-practitioner-runtime-plan.md`
- `docs/security/raisa-provider-free-native-diary-application-session-practitioner-runtime-threat-model-delta.md`
- `scripts/raisa_provider_free_native_diary_application_session_practitioner_runtime_acceptance.py`
- `tests/test_raisa_provider_free_native_diary_application_session_practitioner_runtime.py`

The acceptance script must write its evidence only when root later runs it to:
`orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-runtime/live-local-backend-postgres-evidence.json`.
Do not create or commit that evidence now.

Do not edit any other file. Especially forbidden: `AGENTS.md`, every previously
accepted artifact, `app/main.py`, shared auth/product-read/GraphQL modules,
models, migrations, API Spine artifacts, `docs/diary/**`, `docs/branding/**`,
workflows, harness settings, protected evidence and other-agent files.

## Exact runtime contract

- Expose one new factory for a task-local FastAPI/ASGI app. Default disabled
  returns an app with no product route, docs or OpenAPI and opens no DB/session.
  Only literal explicit enablement constructs the accepted shared practitioner
  router bound server-side to exactly `Surface.NATIVE_DIARY`.
- Add a bounded ASGI-level pre-auth guard for the exact product path. It must
  safely buffer/replay at most 8192 bytes and require POST,
  `application/json`, the fixed query constant, exact variables
  `{activeOnly: true, limit: 200, offset: 0}`, no `practiceId`, no alias,
  fragment, directive, introspection, mutation, field subset/extra field,
  pagination drift or extra JSON key. Reject generically with 403 and
  `Cache-Control: no-store` before bridge authentication.
- Use the exact projection `{id, displayName, roleLabel, active,
  defaultLocation {id, name}}`. Accept no policy/action/resource/surface/query
  arguments from callers.
- Import neither the Office consumer adapter nor Bernie/Davida/proofreader/
  provider code. Add no bearer/localStorage fallback and no REST fallback on the
  enabled application-session path.
- Preserve the shared bridge and current native Diary assets byte-for-byte.

## Direct acceptance harness

- Use a unique allowlisted disposable PostgreSQL database; upgrade to current
  head and check it, with no migration change.
- Create unique finite auth LOGIN/NOLOGIN and product-read LOGIN/NOLOGIN roles
  using the accepted role builders; seed only authored-synthetic current,
  inactive and foreign-practice adversaries.
- Create a `Surface.NATIVE_DIARY` session at one exact synthetic HTTPS origin,
  separate auth/product pools, the accepted registry/bridge, and an explicitly
  enabled task app on a real loopback socket.
- Prove two sequential exact reads succeed on the same session with two active
  same-practice rows, exact projection, no-store and required allow audit before
  release; this is long-lived native behavior, not Office terminal behavior.
- Revoke the session and prove the next request is 401 with no product row.
- Fail closed on wrong origin, missing/mismatched CSRF, Word-surface session,
  unknown/unmapped session, stale role, inactive user, required-audit outage,
  GET, mutation/introspection, practiceId, field subset/extra field,
  activeOnly/limit/offset drift and query/operation drift.
- Prove inactive/foreign/sensitive columns absent and direct role privilege
  escalation/writes denied. Persist counts, booleans, safe reason/status codes
  and hashes only—never DSN, database/role names, passwords, UUIDs, names,
  cookie/session/CSRF values or authority envelopes.
- Stop listener/thread, dispose all engines, drop database and four roles in
  reverse order, and verify complete absence even after failure.
- Evidence label is exactly `live_local_backend_postgres`; zero provider,
  browser, real identity, patient/clinical, product write, deployment or
  production claims.
- State explicitly that request-time freshness and post-revocation denial do
  not prove rejection of an already-returned in-flight response before UI
  render; that remains a later UI reconciliation obligation.

## Verification and commit

Do not run pytest, PostgreSQL or the acceptance script; root holds the serial
database/test lease. You may run Ruff, py_compile, AST/static checks and diff
hygiene. Commit only the five owned files using explicit `git add` paths.
Verify the cached list is exact and has no `docs/branding/`. Never use
`git add -A` or `git add .`. Do not fetch, merge, rebase, switch or push.

Return the five-source statement, exact commit/files/checks/blockers and finish
with exactly one `DECISION: pass` or `DECISION: revision_required`.
