# Threat-model delta: PostgreSQL-backed Office-host authentication compatibility

Date: 2026-08-01

Parent controls: accepted shared-auth PostgreSQL persistence, runtime-role
secure transport, operational hardening and in-memory Office cookie
compatibility results.

Status: frozen pre-implementation delta

## Security objective

Prove that the real installed-Word and Word Online cookie lifecycle continues
to fail closed when the accepted transport is backed by disposable PostgreSQL
and exercised only through a separate finite LOGIN principal that activates
the exact NOLOGIN capability role.

The exercise must not transform authored-synthetic compatibility evidence into
an identity, product-data, deployment or production claim.

## Assets introduced or placed at risk

- runtime-only bootstrap, parent, surface, CSRF and evidence-nonce values;
- hash-only authored-synthetic session and audit rows;
- exact practice scope and generation/revocation state;
- the task-owned LOGIN password and role identifiers;
- the local PostgreSQL server and its unrelated databases/roles;
- the Office add-in developer registration and reserved HTTPS relay; and
- the integrity of protected Git refs and the user-owned branding directory.

## Trust-boundary delta

The prior Office proof stopped at process-local memory. This descendant crosses
three already accepted boundaries together:

1. Office taskpane to same-origin HTTPS FastAPI routes with partitioned Secure
   HttpOnly cookies and independent CSRF;
2. FastAPI transport to a finite SQLAlchemy pool authenticated as a task-owned
   LOGIN role; and
3. pool checkout to exact `SET ROLE` capability access, forced RLS, the narrow
   hash resolver and append-only metadata audit.

Owner database access is outside the runtime boundary and is restricted to
uniquely named setup, aggregate evidence readback and exact cleanup.

## Threats and required controls

### T1 - Office host or surface confusion

An online taskpane could submit a desktop bootstrap, or a manifest could be
opened in the wrong host.

Controls: fresh manifest IDs; exact surface query; Office host/platform check
before bootstrap submission; bootstrap-hash-to-surface binding; exact origin
binding; generic denial; deterministic cross-surface tests.

### T2 - cookie loss or insecure fallback

Third-party partition behavior could drop cookies and tempt a bearer, storage,
query or second-origin workaround.

Controls: ordinary credentialed same-origin fetch only; Secure, HttpOnly,
SameSite=None, Partitioned `__Host-` cookies; HttpOnly values never exposed to
JavaScript; failure is terminal and candid; static source bans for cookie and
browser storage APIs and bearer fallback.

### T3 - raw secret persistence or evidence leakage

Bootstraps, session values, CSRF, nonces, database passwords or target names
could reach PostgreSQL, logs or durable evidence.

Controls: accepted hash-only schema; one-use process-local bootstrap registry;
no access logging; runtime-only generated password; bounded local raw-value
negative scan; schema-closed evidence with counts/booleans only; no raw request
or database target values in errors.

### T4 - login-role privilege escalation or missing capability activation

The LOGIN role could inherit table grants, bypass RLS, or a pooled connection
could run without the required role.

Controls: accepted `NOINHERIT` LOGIN contract with no direct table grants;
exact allowlisted checkout `SET ROLE`; NOLOGIN/NOBYPASSRLS capability role;
fresh `session_user`/`current_user` readback; pool size bounded by connection
limit; transaction-local practice context and timeouts.

### T5 - cross-practice row exposure

A resolver or context defect could hydrate or reveal another synthetic
practice's rows.

Controls: exact hash resolver; forced RLS; principal-generation row lock;
transaction-local practice setting; per-practice aggregate readback through a
fresh capability-scoped session; wrong-practice deterministic probes.

### T6 - stale or replayed authority

A consumed bootstrap, rotated cookie or logged-out cookie could remain usable
after a new database session.

Controls: one-use registry; persisted replacement/revocation state; old-cookie
and post-logout 401 checks; fresh-session database readback; generic retained
denial audit.

### T7 - missing audit/state atomicity

The real-host flow could mutate durable session state without required audit.

Controls: the accepted PostgreSQL coordinator and in-transaction audit buffer
remain unchanged; exact expected lifecycle/audit counts; append-only trigger;
existing forced-audit-failure regressions remain required.

### T8 - forwarded-client spoofing or denial-audit amplification

The HTTPS relay could introduce ambiguous proxy chains or allow unbounded
denial records.

Controls: loopback is the only trusted direct proxy; one canonical forwarded
address plus HTTPS proto; multi-hop, duplicate, malformed and incomplete
headers fail closed; finite per-process limiter; first-block audit coalescing;
HMAC-only client reference.

### T9 - destructive or incomplete cleanup

The harness could drop an unrelated database/role or leave its password,
listener, roles or database behind.

Controls: cryptographically unique names constrained by accepted regular
expressions; preexistence checks; no glob or broad cleanup; exact connection
termination only for the task database; pool disposal before drops; verified
absence of both exact roles and exact database; task-owned process command-line
checks before stopping listeners.

### T10 - accidental publication or concurrent-work capture

Protected integration would publish `docs/` through GitHub Pages, or broad
staging could absorb user-owned Raisa branding.

Controls: no protected-ref movement without separate deployment authority;
explicit-path staging only; cached-path check before every commit; never use
`git add .`, `git add -A` or `git clean`; preserve `docs/branding/raisa/`
exactly and exclude it from tests and evidence.

## Residual risk and excluded claims

- The real runs cover one Windows Office installation and one signed-in Word
  Online environment, not every tenant/browser/WebView policy.
- The limiter remains per process and is not distributed abuse protection.
- The task password is disposable process memory, not a production secret
  provisioning or rotation proof.
- Owner setup/readback is an acceptance-only control surface, not runtime
  authority.
- No real identity establishment, federation, product authorization, product
  data, organisational deployment, production monitoring or release path is
  tested or opened.
