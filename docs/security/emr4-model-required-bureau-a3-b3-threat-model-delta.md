# EMR4 model-required Bureau A3/B3 threat-model delta

Date: 2026-08-04

Status: occupied authored-synthetic development-rehearsal delta; no product,
write, deployment or protected-ref authority

Source HEAD: `2de467e23ce44574395ad6115e7205ca27c96fb2`

Parent plan:
`docs/emr4-model-required-bureau-a3-b3-occupied-rehearsal-plan.md`

Parent security architecture:
`docs/security/emr4-model-required-bureau-gate-zero-threat-model-delta.md`

## Scope and security claim

This delta covers two serial, one-task, authored-synthetic occupied advisory
rehearsals:

- A3 Rayleen waiting-room interpretation and projection selection; and
- B3 Davida practice-administration interpretation and advisory selection.

Each lane may send one primary request through the exact authorised Sydney
Vertex boundary and may make at most one separately regated correction request
only for an eligible closed schema/contract-conformance failure. The provider
model remains an untrusted candidate generator. Deterministic code owns
request admission, immutable bindings, hostile-byte parsing, schema validation,
grounding, policy, proofreading, release and cleanup.

The security claim is narrow: an accepted result proves one exact
`gemini-2.5-flash` authored-synthetic provider turn in each lane and the release
of one closed, grounded, proofreader-admitted advisory candidate per lane. It
does not establish a live product path, patient-data safety, production
suitability, Australian physical or sovereign processing, a command, a write,
an actuator, deployment or release.

## Assets

- Immutable A3 and B3 authored-synthetic context frames and staff/manager
  utterances.
- Task, context, schema, provider-policy, prompt-template and dry-run hashes.
- Broker-owned attempt, cell-generation, lane, practice/environment,
  correlation, expiry, authority and cost bindings.
- Exact provider identity: Google Cloud Vertex AI, model
  `gemini-2.5-flash`, project `bernie-emr4-dev`, service account
  `emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`, keyless
  impersonated ADC, `australia-southeast1`, and
  `australia-southeast1-aiplatform.googleapis.com`.
- One-use call and cost ledgers, proofreader decisions, sanitized invocation
  metadata and teardown/residue evidence.
- Proofreader-admitted Rayleen projection and Davida advisory candidates.

Raw prompts, raw context payloads, raw provider responses, access tokens and
credential material are transient non-assets: they must not become durable
repository, application, audit or diagnostic content.

## Trust boundaries and principals

1. **Sol/orchestrator to deterministic preflight.** The orchestrator selects
   the accepted plan and exact candidate, but cannot waive a failed
   deterministic gate or mint provider evidence.
2. **Host-only credential broker.** Existing impersonated ADC remains on the
   host and is readable only by the short-lived broker. It never enters the
   cell, prompt, model body, durable evidence or repository.
3. **Broker to provider.** The broker constructs one canonical request and may
   contact only the exact regional Vertex endpoint, project and model after an
   atomic ledger/cost reservation.
4. **Provider to hostile-byte parser.** Returned bytes are untrusted. They have
   no authority and cannot be interpreted as code, paths, URLs, markup,
   templates, commands or facts.
5. **Parser to deterministic proofreader.** Only a closed, canonical,
   schema-valid selector/body can cross. Immutable scope, identity, time,
   hashes and labels are broker-owned and assembled outside model output.
6. **Proofreader to evidence/release.** The proofreader may emit one admitted
   advisory candidate, one eligible correction ticket or one terminal denial.
   It cannot call the product, create a backend command or assert an effect.
7. **Cell and broker to teardown.** Closure is incomplete until one-use tokens,
   channels, processes, listeners, mounts and owned temporary artifacts are
   absent and recorded as zero residue.

Rayleen and Davida are separate security domains. Their context, schemas,
task hashes, attempt identities, ledgers, candidate kinds, proofreaders and
release sinks are not interchangeable even though they share broker and
Gate-zero primitives.

## Mandatory invariants

- The model authors only the lane-specific minimal body. It cannot author or
  echo as authoritative an attempt id, cell id, practice/environment scope,
  context hash/revision, timestamp, label, authority ceiling, ledger, cost,
  confirmation, command, write, success or readback field.
- The broker assembles the outer Gate-zero candidate from immutable admitted
  state and labels every model-authored value `untrusted_model` with a
  candidate-only authority ceiling.
- A3 accepts only Rayleen grammar, projection kinds and identifiers grounded in
  its waiting-room frame. B3 accepts only Davida grammar and identifiers/
  deterministic dry-run evidence grounded in its administration frame.
- Every provider call consumes a distinct, atomically reserved one-use ledger.
  No call follows a lane's first admitted result.
- Correction never changes utterance, context, data class, provider, model,
  region, identity, authority ceiling or task semantics.
- Provider, model, project, service account, regional endpoint, disabled-cache
  posture, call ceiling and cost ceiling are equality constraints, not model-
  or environment-selected preferences.
- No raw prompt or provider response is retained. Durable records use hashes,
  allowlisted metadata, usage/cost measurements, verdicts and admitted typed
  fields only.
- A passing proofreader result is still not a command. No command envelope,
  product read/write, database access, actuator or success readback is created.

## Threats and required controls

### T1: Model body forges immutable authority or context

**Attack.** The provider returns scope, identity, timestamps, hashes, labels,
confirmation, command or success fields and attempts to make them appear to be
trusted envelope metadata.

**Controls.** Use strict selector/body separation. Lane-specific model-body
schemas are closed with `additionalProperties: false` and contain only the
minimal intent/advisory selectors and grounded reference identifiers. The
broker constructs the outer candidate independently from admitted immutable
state. Any authority-shaped or duplicate field is rejected before release.
The proofreader constructs released values from the accepted context rather
than copying provider prose or claimed facts.

**Required proof.** Negative cases for unknown properties, forged scope/hash/
time/label fields, confirmation, command, write and success claims all release
nothing.

### T2: Prompt injection changes policy, invokes tools or escapes the task

**Attack.** Synthetic utterance/context text or provider output instructs the
model to ignore the schema, reveal hidden material, fetch a URL, use a tool,
cross domains, issue a command or claim an effect.

**Controls.** Prompts contain only one minimal typed lane frame, one utterance,
one closed response contract and one task. Provider tools, function calling,
grounding, retrieval, URLs, callbacks, code execution and cached content are
absent. The cell sees only once-readable typed input and once-writable typed
output. The parser treats strings as data, never evaluates/interpolates them,
and rejects trailing/duplicate/unknown content. Deterministic policy rejects
clinical reasoning, private actions, delegated confirmation, shell/SQL,
free-form command material and write/success language.

**Required proof.** Direct and indirect instruction-injection fixtures fail at
schema, policy or grounding with zero downstream release/effect. A model
refusal or injection detector is defense in depth, never authority evidence.

### T3: Cross-lane candidate, context or proofreader substitution

**Attack.** A Rayleen attempt receives Davida context or candidate fields, a
Davida result is routed to the Rayleen release sink, or one lane reuses the
other's ledger/correction ticket.

**Controls.** Bind lane/domain, task hash, context schema/hash, candidate kind,
proofreader policy hash, release schema, attempt id, cell generation and ledger
id into the immutable request and evidence. Use disjoint lane-specific body and
release schemas and exact sink allowlists. The broker and proofreader require
domain equality at every transition. Cross-lane correlation, ledger, context,
candidate and correction-ticket reuse is terminal and not correction-eligible.

**Required proof.** A complete A3-as-B3 and B3-as-A3 substitution matrix fails
closed before proofreading/release, with call and cost accounting preserved.

### T4: Stale, superseded or mismatched bindings

**Attack.** A response from an earlier frame, task, policy, schema, attempt or
cell generation arrives after a revision/expiry and is admitted against newer
state.

**Controls.** Bind request and response to exact task, context, policy and
schema hashes, context revision, attempt/cell generation and earliest expiry.
Use caller-supplied timezone-aware evaluation time and a half-open freshness
interval. Supersession is terminal: it kills the generation and cannot be
repaired by the model, correction turn or human confirmation. Late responses
are hashed/audited as rejected and never reach a release sink.

**Required proof.** Boundary-time, stale revision, superseded generation,
wrong task hash, wrong context hash and late-response races release nothing.

### T5: Provider request differs from the deterministically approved dry run

**Attack.** The occupied request silently changes prompt bytes, schema,
generation parameters, endpoint, model or data after provider-free review.

**Controls.** Canonicalize the complete credential-free request during the
provider-free dry run and record its SHA-256. Immediately before send, the
broker reconstructs the request from frozen inputs and requires exact equality
with the precomputed dry-run hash. Only the short-lived authorization header or
transport token may be added outside the hash; it must not alter request
semantics. Any correction turn has its own canonical request and precomputed
hash after the closed correction ticket is issued and regated.

**Required proof.** Mutating one prompt byte, schema version, generation
parameter, cache field, task/context hash or correction field makes the send
ineligible with zero provider calls.

### T6: Regional redirect, fallback or model drift

**Attack.** DNS/client behavior, configuration or an error path redirects to a
global/other-region endpoint, substitutes a model/provider/project, or silently
falls back to a deterministic or alternate planner.

**Controls.** Exact equality-check provider, model, project, service account,
location, endpoint hostname and regional API path before each call. Disable
automatic provider/model/region/global-endpoint and deterministic-planner
fallback. Reject redirects rather than following them. Record observed request
host/path and provider/model metadata in sanitized evidence. A catalogue or
entitlement mismatch fails before prompt transmission; an unexpected response
identity fails after the call and releases nothing.

**Required proof.** Global endpoint, other region/model/project, HTTP redirect,
fallback flag and missing/changed observed-model cases fail closed.

### T7: Credential exposure to the isolated cell or durable evidence

**Attack.** ADC, an access token, service-account assertion, environment
variable, metadata endpoint or authorization header becomes visible to the
cell/model or is persisted in logs/evidence.

**Controls.** The cognitive cell is credential-free and network-none except
for typed broker channels. Only the host broker may read the existing keyless
impersonated ADC and contact the exact provider endpoint. Do not copy host
credential files, token caches or credential-bearing environment variables
into the cell. Cell-visible bridges are exactly typed input/output; credential,
metadata, filesystem, host-path and ambient-network bridges are forbidden.
Evidence uses only the approved service-account identifier and authentication
method, never credential material. Redaction scans fail closure on token/header
patterns.

**Required proof.** Cell inspection reports zero credentials/environment token
material, metadata access is unavailable, durable artifacts pass secret scans,
and host-only ADC remains outside the cell lifecycle.

### T8: One-use reservation race or replay

**Attack.** Concurrent launchers consume the same ledger, a timed-out call is
retried without a new ledger, a response is admitted twice, or a call occurs
after a lane has already admitted a candidate.

**Controls.** Atomically transition a ledger from eligible to reserved before
network send and then to exactly one terminal state. Bind it to lane, attempt,
turn, request hash and cost reservation. A reserved/consumed/expired ledger
cannot be reused. Admission atomically closes the lane before release. Treat
unknown transport outcome as consumed unless exact evidence proves no send;
never issue an unchanged duplicate call.

**Required proof.** Concurrent reserve, replay, timeout/unknown-outcome,
duplicate response and post-admission call attempts result in at most one send
and one release, with every ledger terminal.

### T9: Retry or cost ceiling bypass

**Attack.** A semantic/policy failure is mislabeled as syntactic correction,
the correction changes task meaning, a third call occurs, or parallel lanes
individually pass while exceeding the shared USD 1/four-call ceiling.

**Controls.** Correction eligibility is a closed allowlist of response-form
schema/contract violations only. Grounding, scope, freshness, safety,
authority, provider, credential, transport and ambiguous-semantic failures are
terminal. The correction ticket is deterministic, hash-bound, expiring,
replacement-only, and contains no new facts or suggested answer. Reserve the
worst-case cost atomically against both lane and parent cumulative budgets
before every send. Enforce at most two calls per lane, four cumulatively, one
correction turn and no call after admission.

**Required proof.** Ineligible correction codes, changed utterance/context/
semantics, ledger reuse, third-call, per-lane overflow and cumulative-cost race
all fail before send.

### T10: Raw-content retention or diagnostic leakage

**Attack.** Raw prompts, frames, provider bodies, headers or exception objects
are committed, logged, placed in ledgers, included in verifier packets or left
in temporary files after parsing.

**Controls.** Keep raw request/response bytes only in bounded memory inside the
active attempt. Convert immediately to hashes, allowlisted provider metadata,
usage/cost counts, sanitized reason codes and admitted typed fields. Disable
request/response logging and provider-managed caching. Exception handling must
emit stable codes, never raw bodies/headers. Independent source review receives
repository source and authored-synthetic fixtures, not occupied raw content.

**Required proof.** Artifact allowlist and leakage scans find no raw prompt,
raw response, token, authorization header, credential or unapproved context;
evidence states raw persistence and caching are false.

### T11: Incomplete teardown leaves reusable authority or data

**Attack.** A process, listener, relay, mount, token, credential reference,
temporary request/response file or container remains after failure/success and
can be reused by a later attempt.

**Controls.** Run residue checks before occupancy and after every terminal
path. Revoke the one-use token, close channels/listeners, kill owned processes,
remove owned ephemeral storage and prove no credential was copied into the
cell. Residue failure changes the result to terminal rejection and blocks the
next lane/call; cleanup evidence cannot be inferred from process exit alone.

**Required proof.** Success, parser failure, proofreader denial, timeout,
broker failure and correction paths all end with zero owned processes,
listeners, mounts, tokens, credentials and temporary artifacts.

### T12: Proofreader admission is treated as product or command authority

**Attack.** A valid advisory candidate is routed into GraphQL, a product UI,
existing status/waiting-area/default-location commands, database code, event
handlers or an actuator; or evidence calls it a successful operational action.

**Controls.** Classify this tranche as an Access AI external command at a
repository-local development-harness boundary. It is not GraphQL and mounts no
REST route. GraphQL remains read-only and cannot invoke the provider. The
released schemas contain literal-false command, confirmation, apply, write,
database, network, event, actuator and success/readback fields. No product
adapter is imported or callable. Any future mounted provider invocation or
effect requires a separately authorised single-purpose REST/OpenAPI command,
backend reauthorization and independent readback.

**Required proof.** Static imports/route inventory and runtime counters show
zero product reads, database access, command-envelope creation, confirmation,
writes, events and actuators. Evidence describes release as advisory only.

### T13: Development review transport is confused with candidate runtime

**Attack.** Gemini/Antigravity source-review transmission is counted as an A3/
B3 provider-model call, or candidate-runtime calls are hidden inside the
source-review category.

**Controls.** Record two disjoint evidence scopes: non-zero authorised
development source-review transport and A3/B3 candidate-runtime provider calls.
Bind each to its own model, purpose, worktree, ledger and data class. A source
review cannot satisfy the occupied A3/B3 acceptance condition, and an occupied
call cannot self-review its implementation.

**Required proof.** Closeout reports separate counts, provider/model identities,
purposes and artifacts for the two scopes.

## API Spine posture

The occupied call is an external operation and therefore belongs to the
REST/OpenAPI Access AI command plane conceptually, even though this tranche is
an unmounted repository-local harness. It must bind capability, method, actor/
operator, environment/practice scope, correlation, idempotency/ledger,
authorized data class, context hash and freshness, provider/model/project/
region, cost ceiling and typed audit policy.

GraphQL cannot invoke either lane, expose raw prompts/responses, mutate state or
act as a command tunnel. Events cannot trigger a call or supply command
authority. YAML/JSON policy files are declarative inputs; typed code performs
all admission, equality, budget, grounding and release decisions. A model
candidate, proofreader admission or human observation cannot bypass a future
backend command and readback path.

## Acceptance evidence required by this delta

- Closed schemas and examples for lane body, broker-assembled candidate,
  release/denial union, correction ticket, one-use ledger, parent cost ledger
  and teardown receipt.
- Provider-free negative matrices for all threats above, including cross-lane,
  stale/superseded, request-hash drift, redirect/fallback, ledger races,
  correction/cost overflow, raw leakage and residue.
- A credential-free/network-none cell proof and a host-broker-only ADC proof
  without credential disclosure.
- Exact zero-call preflight for identity, project, prediction permission,
  model, region, regional endpoint, disabled cache, audit readiness, call/cost
  reservation and pre-call residue.
- Independent source-only veto after deterministic gates and before occupied
  execution, with source-review transport separated from candidate runtime.
- For each occupied turn: exact request hash, provider/region/model metadata,
  HTTP outcome, usage/cost, terminal ledger, proofreader verdict, admitted
  field/hash/grounding evidence or sanitized denial, and complete cleanup.
- Literal zero counters for patient/clinical/product/protected data, product
  reads, database access, command envelopes, confirmations, writes, actuators,
  cloud/IAM mutation, update/import/migration, deployment, production, release,
  Pages and protected-ref movement.

## Closed boundaries

The following remain explicitly out of scope and unauthorized:

- patient, clinical, historical Diary, participant, protected, product-derived
  and production data;
- live waiting-room or practice-administration reads;
- mounted product/API/UI runtime wiring;
- appointment, arrival, status, waiting-area, default-location or other
  administrative command, confirmation, apply or write;
- database, shell, SQL, callback, arbitrary network, provider tools, retrieval,
  grounding, code execution or actuator access;
- credential creation/replacement/reconfiguration, IAM change, API enablement,
  provider configuration or cloud mutation;
- update download/import, migration, activation, backup/restore or recovery;
- deployment, production, release, public branding, Pages rebuild, protected-
  ref movement and protected-evidence access.

`docs/branding/` remains preserved and excluded. The protected refs remain at
`2e34bdad732fdab32fbf778280b3d3c70d66d602` unless a separate explicit
protected-integration authority is later granted.

## Residual risks and claim limits

- Configured and observed Sydney routing does not prove Australian physical or
  sovereign processing.
- Authored-synthetic success does not establish privacy, safety, usability or
  correctness for real waiting-room, practice-administration or patient data.
- A deterministic proofreader is only as complete as its frozen schema,
  grounding and policy rules; independent negative evidence is required and a
  future product context would require a fresh threat model.
- A provider HTTP success is neither proofreader admission nor end-to-end
  success. A proofreader admission is neither human approval nor an effect.
- Failure of either lane prevents the combined
  `model_required_bureau_a3_b3_occupied_advisory_rehearsal_pass` claim. A
  truthful partial or blocked result remains useful evidence but cannot be
  promoted.

This delta grants no acceptance authority. GPT Sol retains architecture,
recovery, acceptance, publication and protected-integration control.
