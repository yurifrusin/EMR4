# Provider-free default-off canonical check-in route-adapter convergence rehearsal plan

Date: 2026-08-18

Timestamp: 2026-08-18T12:05:29+10:00 (Australia/Brisbane)

Status: `frozen`

Source HEAD: `ad523968713e58f0b42c3a428556c968f61d6d3c`

Accepted adapter source: `8de886c5148b3259428c8c517674f10ea92d937e`

Target result:
`raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence_rehearsal_pass`

Reasoning level: Extra High for plan freeze because this changes the transport
boundary of a state-changing REST command and must preserve the accepted
idempotency and response contract exactly. High is sufficient for the bounded
implementation, deterministic admission and check-gated closeout while this
contract remains unchanged.

## Objective

Replace only the duplicated confirmation composition inside the existing
default-off A5.1 check-in route with one call to the accepted
`compose_product_check_in` adapter. Preserve the route path, FastAPI request and
response models, Receptionist dependency, feature flag, authored-synthetic
practice allowlist, default denial, HTTP outcome mapping, idempotency precedence
and patient-free success envelope.

The proposal route remains non-mutating and unchanged. This tranche admits no
ordinary-practice command, generic-status `Arrived`, action grammar, first-party
client or waiting-area movement. No route is called against product data or a
production runtime.

## Exact frozen inputs

All hashes are SHA-256 over canonical LF bytes at source HEAD.

| Existing source | Posture | SHA-256 |
|---|---|---|
| `app/routers/appointments.py` | editable only in the A5.1 adapter import, dependency binder, result mapper and confirmation handler | `87a67fd718ac9233f6b1e089d708969749afda0124713e8621d542939f5d605f` |
| `app/services/appointment_check_in_product_adapter.py` | one narrow idempotency-precedence amendment only | `4f548ec6dfa8398d609d102daa574a3e981c78b476f00e6052cab41ed6b74a59` |
| `tests/test_raisa_provider_free_unmounted_canonical_check_in_product_adapter.py` | one narrow compatibility regression permitted | `52e15838a512c8173f2336aec486d82ac40d6a1c718e501868fe451c9881085b` |
| `tests/test_model_required_bureau_a5_1_check_in_runtime.py` | read-only exact HTTP/runtime regression | `758bbcf786a0ee806b25fa5fae33480d3158605ea0594e2178b41b854cc3e5b5` |
| `app/config.py` | read-only | `f0cafc21a88babd0d60d6ce30067a30d23b4030ad5dd4d26bb841096c62c1f2e` |
| `app/schemas/appointments.py` | read-only | `ce7a9819e4947fb288c79009a08b7d9f2502b8d096ff5e2eb005796a250aee90` |
| `app/models/appointments.py` | read-only | `4ae06eeb87c6d5212e354c39c01a8da397cfa2c21bd1031c24e1467d86c77794` |
| `app/models/tenancy.py` | read-only | `e411c816565bdddfbb25beca62439c5bba7a44a90e348cd7e9f4296a65fb65e2` |
| `app/models/diary.py` | read-only | `257960e5ac5222b0fef319f1c34cabbd55c785230a8697cc7f685484040b8e87` |
| `app/services/appointment_idempotency.py` | read-only | `c52b24be780a89459bff0522611f8b7fc9d074ca84fde22f02fc8cf28dfc3410` |
| `app/services/diary_committed_events.py` | read-only | `7a2caaa1fc862821cc9f8a666e945ddb5e5e837825978bcdcb5f7445cd7a219f` |
| `docs/api-spine/openapi/appointment-commands.yaml` | read-only exact public contract | `0dfbce13f3d8933d0cd2355fb41e70612c1550e75c452b95c1528576ac1c8622` |
| predecessor extraction plan | read-only | `85738aca8deb419f9d6a57837489cc0f50dee19e21d1ebc788163b83a3c16d3a` |
| predecessor extraction closeout | read-only | `2b83090b4241cde3d50cb1a3c4e9a2b1f2d476ced6105ac062cdaa9be84de4c5` |
| predecessor Sol acceptance | read-only | `7d6e626ccd8712411287548c6f0feb7b7246c0030c093dd76abe19440a87d392` |

After freeze, implementation reads are limited to these exact sources, this
plan, its threat delta and the worker packet. Protected fixtures and historical
diary material remain excluded and must not be enumerated.

## Exact implementation

1. Import `CheckInDependencies`, `CheckInAdapterResult` and
   `compose_product_check_in` into the appointment router. Do not change the
   proposal route, schemas, settings or OpenAPI.
2. Keep `_a5_check_in_gate_open(current_user)` as the first handler action and
   keep `_normalize_idempotency_key` before adapter construction. No dependency
   callback may run while the feature is disabled or the authenticated practice
   is absent from the exact authored-synthetic allowlist.
3. Build one route-owned `CheckInDependencies` bundle over the existing request
   transaction. Its callbacks may only: claim the dedicated check-in command;
   lock the exact practice appointment; reload the exact active practice actor;
   resolve one exact waiting area; verify the existing opaque evidence; stage
   the accepted status/area effect; call the existing audit/event/completion
   functions; commit/rollback; and perform one bounded post-commit readback.
4. The binder must treat the adapter plans as the sole composition authority.
   It may translate their typed fields to existing service calls but must not
   recompute command meaning or expose a generic executor. Transaction-time
   actor reload is an additional fail-closed authority check.
5. Amend the accepted adapter only enough to preserve A5.1 idempotency
   precedence: after basic server/time checks, derive the optional evidence hash
   and classify same-key replay, conflict, in-progress, stale and prior failure
   before closed-envelope validation. A newly started row whose envelope fails
   validation is rolled back. Replay remains exact and occurs before lock or
   effect. No other adapter contract may change.
6. The confirmation handler calls `compose_product_check_in` exactly once and
   contains no direct claim, appointment lock, authority query, evidence
   verification, mutation, audit, event, completion or commit fallback.
7. A transport-only result mapper preserves the existing HTTP contract:
   confirmed write and replay validate the existing
   `AppointmentConfirmCheckInProposalOut` and return HTTP 200; missing or
   cross-practice target remains a non-enumerating 404; idempotency conflict,
   in-progress, stale, prior failure and evidence reuse retain their exact
   existing status/detail codes; confirmation, freshness, status, evidence and
   waiting-area denials remain typed HTTP-200 blocked envelopes; internal
   claim/composition/commit/readback failures release no success and retain the
   existing server-error posture.
8. The mapper may derive the legacy blocked code for false confirmation, unsafe
   proposal or missing evidence from the already parsed body. It cannot perform
   a write, override an accepted adapter success or turn an uncertain outcome
   into success.
9. Preserve the exact patient-free receipt and existing committed-event service.
   Waiting-area assignment/preservation remains inside check-in; movement or
   removal remains closed.
10. Leave generic status confirmation, raw compatibility routes, action grammar,
    Reception One, ordinary Diary and every client byte-for-byte unchanged.

## Owned implementation package

DeepSeek V4 Flash/high owns exactly:

- the bounded A5.1 changes in `app/routers/appointments.py`;
- the single ordering amendment in
  `app/services/appointment_check_in_product_adapter.py`;
- one compatibility assertion in the existing adapter test; and
- `tests/test_raisa_provider_free_default_off_canonical_check_in_route_adapter_convergence.py`.

Sol owns plan/threat/continuity/evidence, worker review or recovery, deterministic
admission, independent review, acceptance and Git. DeepSeek must not edit any
other existing file, execute a live route, connect to a database, or perform
repository-wide discovery.

## Deterministic acceptance

Authored-synthetic and static tests must prove at least:

- default-off and non-allowlisted requests stop before adapter/dependency work;
- the public path, request model, response model, operation id and OpenAPI bytes
  remain exact;
- the handler invokes the accepted adapter exactly once and owns no write
  fallback;
- the dependency binder forwards the exact operation/family, server practice,
  current actor, opaque evidence hash, 10-minute stale threshold and existing
  backend secret without releasing them;
- actor reauthorization, appointment and waiting-area reads are exact-practice
  scoped, with the appointment locked before effect;
- status/area, audit, event, completion, commit and readback execute exactly once
  in accepted order for Booked and Confirmed success;
- same-key replay returns the exact stored response before lock/effect;
- same-key changed invalid envelope remains `idempotency_key_conflict`, proving
  classification precedes envelope rejection;
- existing 404, 409, 503 and typed HTTP-200 blocked mappings remain exact for
  representative target, idempotency, confirmation, evidence, freshness,
  authority and waiting-area outcomes;
- injected pre-commit, commit and readback failures release no successful body;
- the accepted 68 hostile adapter mutations still fail closed; and
- the existing A5.1 runtime test file remains hash-exact and passes unchanged
  when the repository test PostgreSQL fixture is available.

Focused route/adapter tests, relevant API Spine tests, canonical fast profile,
Ruff, maintained-source compilation, Diary JavaScript syntax, latch/baton checks
and `git diff --check` must pass. One fresh Gemini 3.7 Flash/high exact-candidate
veto is mandatory after deterministic admission.

## API Spine classification

- Boundary: existing single-purpose, state-changing REST/OpenAPI appointment
  command; GraphQL remains read-only and unchanged.
- Accepted pattern: authenticated current human plus explicit typed
  confirmation; idempotency claim before effect; locked current truth and
  in-transaction authority recheck; one attributable audit; event only as a
  committed acceleration hint; bounded patient-free receipt.
- Security: exact practice scope, Receptionist role, opaque one-use evidence,
  stable idempotency, rollback and no cross-tenant target disclosure.
- Avoided gates: no new manifest, async authority, provider, model write,
  external patient client, historical/protected evidence, live product data,
  deployment or production surface.
- Prototype impact: no OpenAPI or schema artifact changes because the public
  route contract is preserved byte-for-byte.

## Parallelism allocation

- **Sol:** plan, architecture and response-compatibility freeze, worker review
  or recovery, deterministic admission, acceptance, continuity and Git.
- **DeepSeek V4 Flash/high:** positively selected for the exact bounded
  route/adapter/tests implementation package after a passing pre-dispatch
  receipt.
- **Gemini 3.7 Flash/high:** reserved for the required fresh exact-candidate veto
  after deterministic admission.
- **Native subagents:** declined because current developer policy prohibits
  proactive native delegation.

The lanes are serial at their authority boundaries: this freeze precedes
DeepSeek; Sol admission precedes Gemini; Sol alone accepts and integrates.

## Claim, recovery and closed surfaces

Passing proves only provider-free convergence of the existing default-off A5.1
confirmation handler onto the accepted adapter with authored-synthetic/static
and repository-local test evidence. It does not enable an ordinary practice,
prove a production database, concurrency beyond existing tests, restart,
unknown-commit recovery, client use, deployment or production.

One mechanical worker defect may receive one bounded same-lane correction. A
conceptual response-contract defect, need for a second write path, adapter
meaning change, product-data access or authority expansion moves immediately to
Sol recovery and cannot silently broaden this plan.

No ordinary-practice enablement, generic-status `Arrived`, action grammar,
first-party client, waiting-area movement/removal, product/patient/clinical/
historical/protected data, live provider, ADC, credential/IAM, external network,
production runtime, deployment, release, Pages or protected-ref movement is
authorised. Local/origin `master` and `handoff/current` remain exact
`2e34bdad732fdab32fbf778280b3d3c70d66d602`. Preserve `docs/branding/` and all
unrelated untracked files; stage explicit paths only.

