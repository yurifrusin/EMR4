# EMR4 model-required Bureau A4 product-read/UI closeout

Date: 2026-08-05

Status: accepted

Source HEAD: `fb3cf995e03d8500c88fca7484fa04aeb0b698d9`

## Accepted result

`model_required_bureau_a4_product_read_ui_pass`

A4 now has both required halves: a default-off, Receptionist-only,
practice/location-scoped GraphQL waiting-room read over live-local FastAPI and
PostgreSQL, and one occupied model-selected projection admitted by a
deterministic proofreader and rendered in the real local Reception One Diary UI.
All records and displayed identities are newly authored synthetic data.

## A4.1 provider-free read and UI

The product read uses a dedicated application-session bridge and dedicated
runtime database roles. Authorization is checked before data access. The query
returns an explicit minimal waiting-room frame, derives arrival only from the
latest committed status audit, labels every fact and signal, and exposes no
GraphQL mutation, command bus or provider route.

The final live-local evidence is
`orchestration/continuity/model-required-bureau-a4-product-read-ui/live-local-auth-graphql-postgres-evidence.json`
with SHA-256
`93f09bbfbd09bb2708b6fe4fb802d34bf8a384eff814531ca138b9fa11d8182f`.
It has the exact label `live_local_browser_backend_postgres`, three authorized
bridge openings, unchanged appointment/audit/event truth, zero writes, zero
provider calls and complete owned cleanup. The earlier label-only veto and its
original hashes remain recorded in the evidence rather than erased.

The client state machine passes 11/11 cases, including closed response shape,
latest-read-wins, interruption, expiry clearing and the 30-second warning. Yuri
then directly confirmed the visible amber warning and red expired/cleared state
in a real browser. The exact screenshots are
`human-browser-expiry-warning.png` and `human-browser-expired-cleared.png`.
Escape closes the panel; every refresh obtains a newly observed frame; ordinary
Diary background refresh cannot pre-empt the Rayleen expiry lifecycle.

Independent A4.1 acceptance is recorded in
`orchestration/agent_inbox/codex/model-required-bureau-a4-a41-independent-review-receipt.json`.

## A4.2 occupied selector

The occupied boundary remained exactly:

- Vertex AI `gemini-2.5-flash` in `australia-southeast1` through
  `australia-southeast1-aiplatform.googleapis.com`;
- project `bernie-emr4-dev` and the existing keyless impersonated ADC for
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`;
- `thinkingBudget: 1024`, `maxOutputTokens: 2048`, at most two calls and USD
  0.50 reserved cumulatively;
- one request-scoped opaque authored-synthetic context; and
- no tools, retrieval, cache, fallback, raw prompt/response/thought/header/token
  retention, database access, command, write or actuator.

The initial call returned HTTP 200/`STOP` but the proofreader rejected its
closed-shape candidate as `selector_not_grounded` and released nothing. It used
679 prompt, 849 thinking, 192 candidate and 1,720 total provider-reported
tokens. The exact failed tranche remains at `occupied-selector-evidence.json`
with file SHA-256
`f6065ab47bca5985ef82ebbcb5fd2edfb3f422294434d3c4b2a21e643dfbc9c0`.

The frozen plan permitted one evidence-selected, materially distinct repair.
The recovery made the same-fact and singleton-evidence grounding instruction
explicit without changing or weakening the proofreader. Its provider-free
isolated rehearsal passed with zero new calls. A fresh independent source veto
then passed all 11 bound source hashes and 14/14 focused selector tests in
`model-required-bureau-a4-selector-recovery-source-review-receipt.json`.

The second and final call returned HTTP 200/`STOP`; the unchanged deterministic
proofreader admitted exactly one unique arrived/maximum-wait appointment. It
used 785 prompt, 614 thinking, 193 candidate and 1,592 total provider-reported
tokens. The cumulative ledger is consumed at exactly two calls and USD 0.50,
and all task-scoped containers, networks, images, relay processes and temporary
contexts are absent. The terminal selector evidence is
`occupied-selector-recovery-evidence.json`, file SHA-256
`9e2bfe4caccf8bfa50de896ccc6ea38abc76f8098923e1e5b19326a7c3a3fb60`,
with result `model_required_bureau_a4_occupied_selector_pass`.

## Occupied UI and freshness recovery

The first occupied UI rendering occurred inside the original lease and proved
the selected card, exact `Model-selected, proofreader admitted` provenance,
refresh, Escape, reopen and cleanup. It failed the combined harness only because
the ordinary Diary still targeted its configured ngrok backend, producing CORS
console errors unrelated to the Rayleen release. The blocked screenshots and
diagnostics are preserved.

The harness now injects only its test-local API origin into the otherwise
unchanged Diary JavaScript, serves inert local ordinary-Diary dependencies and
records console, page, HTTP and request failures. It does not use Playwright
route interception.

Because the original display lease correctly expired during diagnosis, the
harness did not extend or ignore it. A provider-free revalidation materialized
a new two-minute context and admitted freshness only after proving that the
unchanged authored-synthetic frame still had the exact same unique arrived
maximum-wait appointment, practitioner and waiting area selected by the
original model result. It changed no selector and made zero provider calls.

The final evidence is `occupied-ui-browser-evidence.json`, file SHA-256
`52211cad1785b8fd959a856ee07e2e179bf0d3bf87bde457896dbce00cdf86eb`
and canonical evidence hash
`sha256:41405c666dac72fdfd8a063e069fcdac17e538fbe7ab9a4bc315c467cb8339cb`.
It renders one card, performs three local release reads, passes refresh, Escape
and reopen, has empty console/page/HTTP/request failure arrays and proves server
and temporary-TLS cleanup. The final screenshot SHA-256 is
`29689210fb5dc92917e3582bb40f855cc8f5fc99d1dc2720b07e065108112a71`.

## Verification

- A4 plus inherited Diary composition/bridge suite: 70/70 passed.
- Ruff and Python compilation: passed.
- Provider-free UI state machine: 11/11 passed.
- A4 selector focused suite: 14/14 passed before occupied recovery.
- Final occupied evidence and screenshot hashes: independently recomputed.
- User-owned `docs/branding/` and existing Consultant, Gate-minus-one and A3/B3
  pre-push receipt/state files remain untouched and excluded.
- Protected refs remain outside this tranche; no deployment, release or Pages
  action occurred.

## Claim boundary

A4 proves one bounded authored-synthetic development product-read/UI path and
the configured/observed Sydney request route. It does not prove real-patient or
clinical safety, production suitability, Australian physical or sovereign
processing, patient-facing use, a waiting-time guarantee, a command, a write,
an actuator, deployment or release.

## Planned successor

Standing programme authority opens the next dependency-satisfied paired command
tranche after task-branch publication: the narrowest A5.1
Rayleen check-in/status proposal-confirm descendant and B4.1 Davida default-
location command-runtime descendant. Their exact backend-owned confirmation,
idempotency, atomic audit/outbox and deterministic readback boundaries must be
derived and frozen before implementation. No repeat ceremonial permission is
required; no provider call is implied by that next planning step.
