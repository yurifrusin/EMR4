# Bernie Stage 1 Provider-Free Supervised Booking Acceptance Plan

Date: 2026-07-18

Status: **frozen_for_execution — approved by Yuri on 2026-07-18**

Authority source: Yuri accepted the strategic transition recommendation and
authorized Stage 1 on 2026-07-18, then explicitly approved candidate SHA-256
`1cb02436b161167ac4b9f0fb9d33d33a9ee9657a7b9eb2a9205188d1917cbbf3`
as frozen for execution. Execution and worker dispatch still require the fresh
Ariadne continuation receipts and exact worktree checks defined below.

## 1. Decision and purpose

Stage 1 proves or disproves one narrow product claim:

> In a local, synthetic development environment, an authenticated receptionist
> can give Bernie a bounded booking instruction in the real Diary; Bernie can
> clarify or prepare a safe proposal using the existing deterministic/fake
> provider path; and only after explicit staff confirmation can the backend
> revalidate and create exactly one appointment with its audit and typed receipt.

This is a product-vertical acceptance stage, not another language-research,
provider-selection, architecture, or production-readiness stage. The first
execution tranche is evidence-only. Existing code is changed only if the
non-intercepted run exposes a bounded defect inside this contract.

The north-star authority boundary is immutable:

- Bernie interprets, clarifies, retrieves bounded context, and proposes.
- The authenticated staff member explicitly confirms.
- FastAPI/PostgreSQL owns identity, availability, conflicts, policy,
  idempotency, the appointment write, audit, and receipt.
- The model, fake provider, Diary client, and GraphQL never acquire write or
  confirmation authority.

## 2. Frozen scope

### 2.1 Included product surface

The acceptance path uses the existing surfaces:

1. native browser Diary at `docs/diary/`;
2. authenticated development staff session and Bernie pilot eligibility;
3. `POST /api/v1/appointments/proposals/bernie/interpret-booking-instruction`;
4. `POST /api/v1/appointments/proposals/bernie/supervised-booking`;
5. `POST /api/v1/appointments/proposals/create/confirm-bernie` with an explicit
   `Idempotency-Key` header;
6. the existing appointment, appointment-audit, and idempotency-ledger records;
7. the typed `appointment.confirmation_receipt.v1`; and
8. Diary reload/readback from the authoritative backend.

Interpretation, clarification, context retrieval, slot search, candidate
selection, and proposal preview are non-mutating. `confirm-bernie` is the sole
product mutation command. No GraphQL mutation or model-to-database path is
permitted.

Bernie session state may remain process-local for Stage 1. Acceptance is limited
to one local process without restart or multi-worker continuity. Durability is
not implied and remains a later product decision.

### 2.2 Environment

Execution must use:

- loopback/local access only;
- a single local FastAPI process;
- an isolated, disposable PostgreSQL Stage 1 database populated only with the
  repository's synthetic development fixtures;
- the real static Diary client making real, non-intercepted HTTP calls to that
  backend;
- the existing `fake` provider or fully disabled external-provider boundary;
- no ngrok, ADC, `gcloud`, Vertex, external AI endpoint, or cloud setup; and
- a synthetic receptionist, practice, practitioner, patient, roster, appointment
  type, and available slot.

The database name, connection target, seed identity, pilot allowlist, and
provider setting must be resolved and recorded before the browser opens. If an
isolated database cannot be proved, execution stops before any appointment
write.

The execution harness may create scenario fixtures in that disposable database,
including a same-name synthetic patient or a competing synthetic appointment.
Those are test fixtures, not a new dialogue corpus, holdout, or product mutation.
Fixture setup and cleanup must be visibly separated from product-command counts.
No shared development, historical, staging, or production database may be used.

### 2.3 Stable reference date

The acceptance run selects `D`, the first future rostered weekday with the
required synthetic availability, during read-only preflight. The Diary's visible
date and Bernie session reference date are both pinned to `D`. The existing
product contract makes that reference date immutable across the session.

The standing release instruction is used unchanged:

> Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but
> before 3:45.

For this run, `today` must resolve to `D`; no system-clock patch, hidden time
override, or instruction rewrite is allowed. The closeout records the actual
date chosen for `D`.

## 3. Explicit exclusions

Stage 1 does not authorize:

- access to, enumeration of, execution against, or inference from protected
  holdouts v1-v10;
- inspection or download of the provenance-blocked appointment-call corpus;
- a new holdout, synthetic corpus version, certification cycle, or provider
  comparison;
- any provider call, external prompt, cloud mutation, ADC/login setup, raw
  provider response, or cost acceptance;
- patient, practice, historical-diary, protected, or external-corpus data;
- production, PII, deployment, release, DNS, ngrok, or remote access;
- a database migration, schema redesign, durable Bernie session store, RAG,
  memory, GraphRAG, or additional mutation family;
- provider runtime, Access AI runtime wiring, GraphQL mutation, autonomous
  confirmation, model write authority, or direct database access by Bernie;
- broad API, UI, policy, clarification, replay, scorer, or interpretation
  redesign; or
- modification or reinterpretation of any immutable prior result or closeout.

## 4. Evidence classes

Every result must carry one of these labels. Labels cannot be promoted by
inference.

| Label | Meaning | Permitted claim |
|---|---|---|
| `live_local_browser_backend_postgres` | Real Diary, real local HTTP, real FastAPI, isolated PostgreSQL; no route interception | Current local product vertical |
| `live_local_backend_postgres` | Real local HTTP/FastAPI/PostgreSQL without the browser | Backend command and persistence behavior |
| `route_intercepted_browser` | Browser requests fulfilled or altered by the test harness | UI behavior only |
| `in_process_backend` | TestClient/service execution in the test process | Backend contract regression only |
| `fake_provider` | Deterministic local fake; no external model | Plumbing and deterministic behavior only |
| `static_or_designed` | Source, schema, ADR, or document inspection | Design/implementation presence only |

Stage 1 passes only with `live_local_browser_backend_postgres` evidence for the
happy path. Existing route-intercepted Diary smoke and TestClient tests are
supporting regressions, not substitutes. `fake_provider` is never described as
live-provider, model-quality, reliability, or production evidence.

## 5. Required scenarios

### S0 — Fail-closed readiness

Before content or browser execution, prove:

- all Git refs required by `AGENTS.md` have been freshly verified;
- the worker/candidate source head and worktree are exact and clean apart from
  named Stage 1 artifacts;
- the isolated database contains synthetic fixtures only;
- the authenticated staff user belongs to the same practice and passes Bernie
  pilot eligibility;
- the selected practitioner is rostered on `D` and the target window is
  available;
- provider configuration is `fake` or external-provider-disabled;
- outbound provider/cloud routes are absent or blocked; and
- no ngrok, ADC, `gcloud`, external prompt, protected evidence, or historical
  diary material is involved.

Any failure stops before the appointment write.

### S1 — Non-mutating instruction-to-proposal path

Using the real Diary and exact standing instruction:

1. establish baseline counts and identifiers for appointments, appointment
   audits, and idempotency entries in the isolated practice;
2. submit the instruction with Diary date/reference date `D`;
3. show that `today`, patient, practitioner, and the 14:00–15:45 bounds are
   resolved without exposing raw UUIDs in receptionist-facing copy;
4. retrieve candidates from the real backend;
5. select a candidate and display a complete provisional proposal; and
6. prove baseline mutation counts are unchanged before staff confirmation.

The evidence must show the actual non-intercepted request sequence and sanitized
response outcomes. It must not preserve bearer tokens, passwords, raw headers,
or secret-bearing HAR/trace content in committed artifacts.

### S2 — Explicit confirmation and authoritative write

From the S1 proposal:

1. the receptionist performs a distinct, visible confirmation action;
2. the client sends the existing signed/fresh proposal evidence and an explicit
   idempotency key to `confirm-bernie`;
3. the backend revalidates practice, staff, patient, practitioner, slot,
   collision, freshness, and evidence;
4. exactly one appointment row is created by the backend;
5. exactly one corresponding appointment audit event is created;
6. the idempotency ledger completes for the command;
7. the client receives a complete `appointment.confirmation_receipt.v1`; and
8. a Diary reload/readback shows the appointment from the backend.

The receipt must not be fabricated by the client. The Diary may claim success
only when the complete authoritative receipt is present.

### S3 — Idempotent replay and exact duplicate

Two related protections are required:

- replaying the exact S2 confirmation request with the same idempotency key
  returns the same completed result/receipt and creates no second appointment or
  audit; and
- a fresh attempt to make the same booking is classified as an existing exact
  booking and does not create another appointment or expose a confirm action.

The first check may use `live_local_backend_postgres` evidence with the captured,
sanitized command body. The second must be visible in the real Diary.

### S4 — Clarification before proposal

In a fresh isolated scenario, use two same-display-name synthetic patients (or
an equivalently deterministic ordinary-development ambiguity). Bernie must ask
for bounded clarification, present no confirmation-ready proposal, and cause no
appointment, audit, or completed mutation-ledger change.

This scenario tests identity ambiguity, not medical reasoning. If the current
product cannot safely distinguish the fixtures without a new product-policy
decision, Stage 1 pauses for Yuri rather than inventing a rule.

### S5 — No slot

With the target window made unavailable by explicit synthetic fixtures before
baseline, the real Diary/backend path must return a typed no-slot or clinic-day
exhausted outcome, offer a safe next action such as another day/time, expose no
raw identifier, and perform no product mutation.

### S6 — Stale/conflicting confirmation

In a fresh scenario, obtain a valid proposal, then inject a competing synthetic
appointment through clearly labelled test-fixture setup before confirmation.
The subsequent real backend confirmation must fail closed with a typed
stale/conflict result, produce no Bernie appointment, no success receipt, and no
Bernie appointment audit. The fixture write is excluded from product-command
counts and recorded separately.

### S7 — UI and accessibility regression

The current route-intercepted Diary suite remains required for breadth. It must
continue to prove accessible confirmation/receipt behavior, typed recovery,
duplicate handling, and the absence of generic `Not Found` or raw ID copy. Its
result remains labelled `route_intercepted_browser`.

## 6. Acceptance gates

Stage 1 returns `stage1_pass` only when every gate passes:

| Gate | Acceptance boundary |
|---|---|
| G1 Boundary | Local, synthetic, provider-free, cloud-free, protected-evidence-free execution is demonstrated |
| G2 Authentication and tenancy | Real authenticated staff; practice and pilot eligibility match; cross-practice access is absent |
| G3 Proposal has no write | S1 reaches a usable proposal with zero appointment/audit/ledger mutation before confirmation |
| G4 Human authority | Confirmation is an explicit receptionist action and the client cannot silently auto-confirm |
| G5 Backend authority | Backend revalidation creates exactly one appointment, one matching audit event, and one completed idempotency result |
| G6 Receipt and readback | Complete typed receipt is returned and the reloaded Diary reflects backend truth |
| G7 Failure safety | Ambiguity, no-slot, conflict/staleness, replay, and duplicate cases fail or recover as specified without extra writes |
| G8 Evidence integrity | Evidence labels are exact; browser happy path is non-intercepted; secrets and raw auth material are not committed |
| G9 API Spine | Existing REST command remains the sole mutation; GraphQL and model/provider layers do not mutate |
| G10 Regression | Focused backend, API Spine, Diary, security, and formatting checks pass with documented baseline exclusions only |

Perfect prior certification or Silver scores cannot satisfy any missing gate.

## 7. Verification and durable evidence

### 7.1 Required verification

All repository pytest commands that load `tests/conftest.py` run serially.
At minimum the candidate must pass:

- the focused interpretation readiness release gate;
- the Sprint 98 confirmation contract and release gates;
- signed confirmation-evidence and create-confirm idempotency tests;
- supervised-booking, duplicate/recovery, accessible-confirmation, and confirmed
  flow tests;
- `tests/test_api_spine_artifacts.py` and the Bernie API Spine confirmation
  contract/preflight tests;
- the full route-intercepted Diary smoke, labelled correctly;
- a new or adapted non-intercepted Stage 1 browser acceptance harness against
  the isolated local backend/database;
- JavaScript syntax/static checks and taskpane/Diary publication parity if UI
  source changes;
- risk-proportional security checks if authentication, evidence, command, audit,
  or persistence code changes; and
- `git diff --check`.

The known runtime-isolation baseline named in `AGENTS.md` is not attributed to
Stage 1 unless the candidate changes that surface.

### 7.2 Required artifacts

Closeout evidence must contain:

- source commit, worktree, exact commands, environment classification, selected
  `D`, and sanitized configuration proof;
- pre-confirm, post-confirm, replay, duplicate, ambiguity, no-slot, and conflict
  database counts;
- the sanitized request/outcome sequence and receipt fields/hashes needed to
  reproduce the claim, without credentials or tokens;
- synthetic-only screenshots for S1, S2, S3 duplicate, S4, S5, and S6;
- test results with exact pass/fail/deselect counts;
- outbound/provider/cloud/protected-access attestation;
- every implementation amendment, if any, and why it was necessary;
- independent review evidence proportional to any changes; and
- one decision: `stage1_pass`, `partial_evidence`, `revision_required`, or
  `blocked_for_user_decision`.

`partial_evidence` does not establish the Stage 1 product claim and cannot move
Bernie to Stage 2.

## 8. Execution choreography

### Tranche A — Read-only readiness and harness proof

Sol/high owns the source/environment inventory, isolated database proof,
provider/cloud deny proof, authenticated pilot check, fixture map, and exact
non-intercepted browser plan. This tranche makes no appointment write and no
product change. It ends in `ready_for_bounded_run` or stops.

### Tranche B — Existing-product acceptance run

Run S1–S7 on the unchanged candidate first. If all gates pass, close Stage 1
without manufacturing an implementation sprint.

### Tranche C — Bounded correction only if evidence requires it

A defect may be corrected only when it is reproducible on an included Stage 1
surface and requires no new policy or authority. A packet must freeze the exact
failure, owned files, tests, forbidden surfaces, and acceptance result before a
worker starts.

- Mechanical backend/test-harness work may use DeepSeek V4 Flash/high.
- A fresh Gemini 3.5 Flash context may review material UI/API boundary changes.
- Sol owns architecture, scope, recovery, integration, and acceptance.
- Conceptual worker errors move immediately to Sol under the recovery lease;
  mechanical correction receives at most the bounded loop permitted by
  `AGENTS.md`.

Planning and final acceptance use Extra High reasoning. Bounded execution and
orchestration use High reasoning unless a material architecture, safety, or
acceptance fork requires escalation.

### Tranche D — Independent acceptance and closeout

Sol reproduces the evidence on the exact candidate, applies the API Spine and
security gates, and obtains an independent fresh-context review if material code
changed. Only a final `stage1_pass` can support a recommendation for the next
product stage. Commit, push, baton movement, and Pushover occur only in the
separate accepted closeout flow required by `AGENTS.md`.

## 9. Stop and escalation rules

Stop immediately and preserve evidence if:

- any provider endpoint, external prompt, cloud/ADC/gcloud step, ngrok tunnel,
  non-synthetic data, protected path, or blocked corpus becomes involved;
- the effective provider setting cannot be proved fake/disabled;
- the target database is not isolated or its contents are not demonstrably
  synthetic;
- any write occurs before explicit confirmation;
- confirmation creates more than one appointment, more than one matching audit,
  or a success claim without a complete receipt;
- a model, client, GraphQL resolver, or test harness rather than the backend
  becomes authoritative for the product write;
- the browser evidence depends on route interception;
- completion requires a migration, durable session store, new mutation family,
  policy choice, broad redesign, provider call, or production/security claim;
- a test or command attempts to access protected evidence; or
- a material clarification-policy, UX-authority, privacy, licence, cost, or
  product-behaviour decision is required.

Mechanical defects inside the frozen scope return `revision_required` and may
enter Tranche C. Material choices return `blocked_for_user_decision` and come
back to Yuri.

## 10. Already-decided and deferred user choices

Yuri's Stage 1 authorization binds these choices for this contract:

- provider experimentation is paused;
- evidence is local and synthetic only;
- the fake provider is plumbing, not provider-quality evidence;
- one explicit backend appointment-create mutation is permitted only after
  staff confirmation in the isolated database;
- process-local session state is acceptable only for the bounded run; and
- Stage 1 may end without code changes.

Deferred choices include durable session design, further provider work,
production/PII residency, release/security completion, field evidence, broader
Diary workflow, and any new clarification or booking policy.

## 11. Freeze effect

Yuri approved the exact freeze candidate on 2026-07-18. Therefore:

1. its status is `frozen_for_execution` with the approval date and candidate
   hash recorded above;
2. this plan becomes the active acceptance boundary for the provider pause and
   Stage 1 execution only;
3. `AGENTS.md` Current Baton and active acceptance are updated by the freeze
   handover;
4. a fresh Ariadne pre-dispatch receipt is required before any worker or
   execution run; and
5. execution begins at Tranche A, not at implementation.

Approval does not authorize a provider call, cloud mutation, deployment,
production/PII use, protected evidence, new corpus, migration, durable session,
or any work outside this plan.
