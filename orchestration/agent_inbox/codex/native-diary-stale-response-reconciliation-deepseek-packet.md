# Native-Diary stale-response reconciliation — DeepSeek worker packet

Source head: `b957ed7623310206cf5f4970e1eb91241c73ef6f`

Worktree: `C:\Users\sarashera\EMR4-worktrees\native-diary-stale-response-reconciliation`

Branch: `codex/native-diary-stale-response-reconciliation`

Model/transport: exact DeepSeek V4 Flash/high through Claude Code `--bare`.
No fallback is authorised.

## Mandatory source pass

Read `AGENTS.md` completely and state the exact five rehydration sources. Read
the EMR4 API Steward skill and its review checklist completely. Read this
packet, the accepted Bernie/Davida seam, native-Diary composition/runtime
plans, designs, threat deltas, contracts and closeouts, plus the exact existing
Python runtime named below. Verify the exact branch/source and clean worktree
before editing.

Yuri has clarified the continuous-tranche protocol: after a successful
continuing Pushover closeout, the conductor starts the next already-authorised
tranche immediately. That grants no additional product, data, provider, Git or
deployment authority to this worker.

## Task

Implement the smallest provider-free, unmounted and browserless client
reconciliation boundary for the accepted fixed native-Diary practitioner read.
It is a pure JavaScript latest-read-wins state machine plus deterministic
acceptance harness. It must reject every already-returned stale, superseded,
revoked, replayed, foreign or malformed result before any render callback.

The current HTTP runtime authenticates against backend session generation but
does not expose that generation in its response. This tranche therefore proves
only a trusted client lifecycle generation plus per-read revision race gate. It
must not claim a cryptographic/server-bound backend generation. If implementation
requires adding response metadata or editing the shared router/bridge, stop with
`revision_required`; do not derive generation from cookies, CSRF, response rows,
correlation identifiers or caller-controlled request data.

## Owned files

- `docs/raisa-provider-free-native-diary-application-session-practitioner-reconciliation-plan.md`
- `docs/security/raisa-provider-free-native-diary-application-session-practitioner-reconciliation-threat-model-delta.md`
- `orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-reconciliation/client-reconciler.mjs`
- `scripts/raisa_provider_free_native_diary_application_session_practitioner_reconciliation_acceptance.mjs`
- `tests/test_raisa_provider_free_native_diary_application_session_practitioner_reconciliation.py`

The acceptance script may write evidence only when root later invokes it with
an explicit output path:
`orchestration/continuity/raisa-provider-free-native-diary-application-session-practitioner-reconciliation/provider-free-client-state-machine-evidence.json`.
Do not create or commit that evidence now.

Do not edit any other path. Especially forbidden: `AGENTS.md`, all accepted
parent artifacts, `app/graphql/native_diary_application_session_practitioner.py`,
shared auth/product-read/GraphQL code, `app/main.py`, routes, models, migrations,
API Spine artifacts, `docs/diary/**`, `docs/branding/**`, Davida paths, workflows,
harness settings, Continuity/Compass global maps, protected evidence and refs.

## Frozen state-machine contract

- Trusted composition code establishes one positive monotonically increasing
  `sessionGeneration`. Generation is freshness/suppression metadata only; it is
  never authentication, authorization, audit or command authority.
- `beginRead()` creates an opaque instance-bound frozen ticket containing only
  the current `sessionGeneration` and a monotonically increasing
  `requestRevision`. Every newer read immediately supersedes the earlier ticket.
- `invalidateSession()` invalidates every outstanding ticket. A later session
  must be established explicitly; no result from the invalidated generation may
  render.
- `advanceSessionGeneration(newGeneration)` requires a strict increase and
  invalidates every outstanding ticket. Equal, lower, non-integer or otherwise
  invalid generation values fail closed.
- `reconcileAndRender(ticket, returnedResult, synchronousRender)` is the sole
  egress. Before exposing rows it rechecks ticket provenance, active session,
  exact current generation, exact latest request revision, pending/one-use
  state and one strictly admitted fixed-read result. Consume the ticket before
  invoking the synchronous callback. A callback exception must not make the
  ticket replayable.
- Rejection returns only a typed sanitized disposition/reason and never invokes
  render/update. Exact closed reasons are `session_inactive`,
  `session_generation_stale`, `request_superseded`, `ticket_unknown`,
  `ticket_replayed`, and `response_not_admissible`.
- Do not retain response rows, cookies, CSRF, session identifiers, principal or
  practice values in adapter state or evidence. Snapshot/observability contains
  bounded counts and generation/revision metadata only.
- The module performs no fetch, HTTP, browser, DOM, database, provider, model,
  memory, command, event, write or audit action. It consumes only the already
  accepted fixed read result supplied by trusted composition code.

The returned-result admission shape must be strict and minimal. It may carry a
successful fixed-read status plus display-safe practitioner rows already
validated by the accepted server contract. Unknown fields, non-array rows,
malformed rows, authority/session fields or unsuccessful results fail closed.
Do not broaden the accepted projection or persist raw rows in evidence.

## Deterministic acceptance

Exercise at least:

- A begins, then B begins; B renders exactly once and late A renders zero;
- a response returns, then generation advances before the final gate;
- a response returns, then a newer read begins before the final gate;
- invalidation before the final gate;
- successful latest-current render exactly once and replay rejection;
- forged, cross-instance, malformed and unknown tickets;
- equal/lower/invalid generation advance;
- unsuccessful, malformed, extra-field and authority-bearing results;
- render callback exception still consumes the ticket;
- no rejected row is retained and no sensitive value appears in snapshot or
  evidence;
- static absence of fetch/browser/HTTP/PostgreSQL/provider/write/Office/Bernie/
  Davida/proofreader/app-main dependencies and zero `docs/diary/**` changes.

Evidence label is exactly `provider_free_unmounted_client_state_machine` with
`data_class=authored_synthetic`. State explicitly that it is not live, browser,
route-intercepted, HTTP/backend/PostgreSQL, mounted-runtime or usability
evidence. Proposed terminal result:
`provider_free_native_diary_application_session_practitioner_reconciliation_pass`.

## API Spine

The adapter consumes only the accepted fixed read result. Add no GraphQL field,
schema, mutation, REST route/command, event actuator, manifest, idempotency,
database or audit path. Server authentication, authorization and required read
audit remain authoritative; local rejection counters are observability only.

## Verification and commit

Do not run repository pytest or PostgreSQL; root owns the serial test lease. You
may run Node syntax/direct deterministic checks, Python compile/static checks,
Ruff on the focused Python test, and diff hygiene. Commit only the five owned
files with explicit `git add -- <path...>`. Verify the cached list is exact and
contains no `docs/branding/`. Never use `git add -A` or `git add .`. Do not
fetch, merge, rebase, switch or push.

At most one later mechanical repair is eligible. Any need to expose server
generation, change shared auth/runtime, mount a product consumer or reinterpret
authority is conceptual and must return immediately to Sol.

Return the five-source statement, exact commit/files/checks/blockers and finish
with exactly one terminal `DECISION: pass` or `DECISION: revision_required`.
