# EMR4 model-required Bureau A4 product-read/UI plan

Date: 2026-08-05

Status: accepted and closed

Source HEAD: `fb3cf995e03d8500c88fca7484fa04aeb0b698d9`

Parents:

- `docs/emr4-rayleen-davida-controlled-recovery-development-plan.md`
- `docs/emr4-model-required-bureau-a3-b3-request-contract-recovery-closeout.md`
- `docs/ariadne-autonomous-continuation.md`
- `orchestration/continuity/model-required-bureau-provider-free-successor-lanes/waiting-room-context-frame.schema.json`

## Decision

Yuri's standing authority and 2026-08-05 clarification make A4 the next
executable programme gate. Materiality and the older phrase `fresh product-read
decision` are not pause conditions. Sol therefore freezes the narrowest
architecture-strengthening A4 boundary and proceeds without another permission
request.

A4 is a default-off, development-only, authored-synthetic waiting-room product
read and Reception One projection. It is split into two consecutive tranches:

1. a provider-free GraphQL read/projection and UI seam with live-local browser,
   FastAPI and PostgreSQL evidence; then
2. one bounded model-required selector through the accepted Sydney Vertex
   envelope, whose candidate must pass deterministic proofreading before the
   same UI projection can be released.

Neither tranche opens a command, write, confirmation, actuator or production
surface. The ordinary Waiting Room and backend remain authoritative.

## API Spine classification

The product read is GraphQL and read-only. A separate default-off fixed-query
application-session schema may expose one bounded `rayleenWaitingRoom` root
backed by a typed service; it is not added to the shared mounted GraphQL schema
and has no Mutation, provider adapter, command bus or write-capable dependency.

The occupied selector is a separate authenticated REST/Access-AI command-style
read because provider invocation is an external auditable action. It may call
the same trusted read service internally, but GraphQL never becomes a provider
or mutation tunnel. Its result is a display projection only.

Every request is authorized before waiting-room data access by exact current
user, active role, practice, location and feature/practice allowlist. The
initial role is Receptionist only. GP, Nurse, Admin, PracticeOwner, unknown or
inactive roles, another practice, an unowned location, stale selection, extra
field or disabled gate fail closed. Later role widening is a separate planned
descendant.

## Tranche A4.1: provider-free product read and UI

The trusted read service:

- reads only today's active waiting-room appointments for one authorized
  practice/location;
- reads the minimum latest status-audit timestamp needed to derive arrival
  time and emits a typed missing-arrival-time exception rather than inventing
  elapsed wait;
- excludes contact details, date of birth, Medicare/national identifiers,
  reason, notes, clinical text, unrestricted history, credentials and raw
  provider material;
- emits bounded backend facts and deterministic elapsed-wait, threshold,
  longest-wait and flow-exception signals with source, freshness and
  `data_only` authority labels;
- binds a stable context revision to the exact minimized facts;
- admits only closed projection kinds and identifiers present in that fresh
  frame; and
- never commits, flushes, writes audit, emits events or invokes a provider.

Reception One adds a default-off Rayleen projection region inside the existing
Waiting Room surface. It must support keyboard and touch, a visible refresh,
quiet `aria-live` status, explicit stale/error state, interruption-safe request
supersession, ordinary Waiting Room fallback and no automatic speech or sound.
The displayed selector provenance must say `deterministic product read` or
`model-selected, proofreader admitted`; it must never imply reservation,
confirmation or mutation.

Provider-free acceptance includes:

- schema closure and API Spine no-Mutation checks;
- authentication, exact role/action/resource authorization and same-practice
  location scope;
- cross-practice and foreign-ID denial before disclosure;
- field minimization and no reason/note/contact/clinical leakage;
- deterministic wait/threshold/longest-wait projections and explicit unknown
  arrival-time handling;
- stale, duplicate, superseded and interrupted response behavior;
- desktop, tablet, phone, keyboard, focus and ordinary-fallback UI evidence;
- real non-intercepted local browser to FastAPI to PostgreSQL evidence labelled
  `live_local_browser_backend_postgres`; and
- unchanged appointment, audit and event truth plus complete owned cleanup.

## Tranche A4.2: occupied model-required selector

A4.2 begins automatically after A4.1 deterministic acceptance and fresh source
review. The trusted context desk converts the current authored-synthetic frame
to request-scoped opaque appointment, practitioner, waiting-area, practice and
location references. The model receives only those references, bounded waiting
signals, a bounded staff utterance and the all-false authority ceiling. It
receives no database identifier, database session, route client, bearer token,
credential, raw patient identity, notes, clinical content, whole Diary, command
or tool.

The candidate schema is closed to intent, projection kind, optional filters,
one optional focus, evidence references, context revision and an all-false
authority ceiling. The deterministic proofreader requires exact revision and
freshness, grounds every reference and discriminator, rejects invented or
cross-scope selectors, enforces projection semantics and releases only typed
display fields. No repair may weaken grounding, freshness or authority.

The exact occupied boundary is:

| Property | Frozen value |
|---|---|
| Provider/model | Google Vertex AI `gemini-2.5-flash` |
| Project | `bernie-emr4-dev` |
| Identity | `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com` through existing keyless impersonated ADC |
| Region/host | `australia-southeast1` / `australia-southeast1-aiplatform.googleapis.com` |
| Data | disposable local product context containing newly authored synthetic records only |
| Reasoning/output | `thinkingBudget: 1024`; `maxOutputTokens: 2048` |
| Calls | at most two cumulative; stop after first admitted projection |
| Cost reservation ceiling | USD 0.50 cumulative at USD 0.25 per call |
| Fallback | none |
| Tools/retrieval/cache | none |
| Raw retention | no raw prompt, response, model text, thought content, headers, token or credential |

The existing read-only ADC preflight may verify the exact identity, project,
model, region and endpoint. Codex receives no credential, IAM or cloud-
configuration mutation authority. Missing/restored credentials are a human-only
external condition; deterministic work and evidence packaging continue while
that condition is absent.

Every attempt uses a new single-use ledger and isolated one-shot cell. Sanitized
evidence may retain request/schema/context hashes, HTTP status, response hash
and byte count, model version, candidate/part/finish shape, bounded token usage,
proofreader decision, released field hashes and cleanup. A failed attempt must
release nothing. A second call is eligible only for one evidence-selected,
materially distinct in-boundary repair. No call follows admission.

Occupied acceptance requires one proofreader-admitted model-selected view to
drive the default-off Rayleen UI over the same fresh authored-synthetic product
frame, while deterministic database readback proves zero mutation. The evidence
label is `occupied_authored_synthetic_live_local_product_read_ui`; it proves the
configured/observed Sydney request path, not Australian physical or sovereign
processing, real-data safety or production suitability.

## Recovery and continuation

Mechanical implementation, transport, test, review or provider-shape failures
are recovered automatically while this exact boundary remains unchanged.
Preserve every failed artifact and register qualifying failures. Continue from
A4.1 to A4.2 and from accepted A4 to the next dependency-satisfied planned gate
without a permission handback.

Pause only for a genuinely non-inferable alternative with materially different
user-owned consequences, a human-only external action, conflicting evidence
that changes acceptance, bounded-option exhaustion, protected-evidence access,
work outside the accepted programme sequence or Yuri's explicit stop.

## Closed surfaces and claim boundary

Real patient, clinical, historical Diary, participant, protected, production or
external-client data; public or patient-facing Rayleen; commands,
confirmations, writes, actuators, provider tools, retrieval, memory/RAG,
arbitrary network, cloud/IAM mutation, update/import/migration, deployment,
production, release, Pages and protected refs remain outside A4.

`docs/branding/` and all existing Consultant, Gate-minus-one and A3/B3
pre-push receipt/state files remain preserved and excluded. Git staging is
explicit-path only.
