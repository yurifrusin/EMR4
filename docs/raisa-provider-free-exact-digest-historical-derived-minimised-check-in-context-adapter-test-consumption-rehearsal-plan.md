# Raisa provider-free exact-digest historical-derived minimised check-in-context adapter-test consumption rehearsal — plan

Date: 2026-08-24

Timestamp: 2026-08-24T13:42:27.9853208+10:00 (Australia/Brisbane)

Status: `frozen_fail_closed_before_fixture_read`

Planning source: `a344a3ecf782d730ca7a240acec3fdeaf0aa4f2a`

Frozen plan commit: `5eaac238e8d7541ffd395a5a3f8b8464ae5b68b8`

## Objective

Consume the accepted ignored historical-derived fixture exactly once, after
verifying the digest of the same bytes that are parsed, and use only its closed
structural fields to construct one authored-synthetic, provider-free test
context for one invocation of the accepted unmounted canonical check-in
adapter.

This is a local adapter-test rehearsal. The fixture is evidence context only.
It does not authorise the command, replace current source truth, satisfy
confirmation, confer actor or practice authority, or become product/runtime
input.

## Exact accepted inputs

- published task HEAD: `a344a3ecf782d730ca7a240acec3fdeaf0aa4f2a`;
- accepted clockwork implementation: `5792a993b33a5f0dc0fea78e1c20f7f4164f2c4a`;
- accepted clockwork closeout source: `ce1f3717fc89117a9db74ca1b95509f02fef5d82`;
- accepted first-use materialisation source:
  `4740813d53ebbc4872fe8c0c08ce2578b1982770`;
- accepted first-use candidate-gate source:
  `abcd4206a363b0c565c070e0f2cb9c54d627b3b3`, whose current exact Git blob is
  `fe05dfb3b4c4e36ea3200b9532a3d40bcb30f7f7`;
- accepted consumption-subgate contract SHA-256:
  `da2507056f37482016125c3ccad909573c0495d86cdc135cd5b13714bc7c93ac`;
- immediate one-read successor-contract SHA-256:
  `6d4cfb8ae74317685a478097fa347ead932afb47033591e82ec19afbeebb9658`;
- ignored fixture path:
  `local_data/historical-diary-trove/derived-scenarios/2026-08-24-first-use-check-in-context-v1/scenario.json`;
- accepted fixture SHA-256:
  `2205ab83cec7c5639d39cc563cee80eec825ac33f17571151571d325e74f2dfe`;
- original unmounted adapter extraction ancestry:
  `8de886c5148b3259428c8c517674f10ea92d937e`;
- exact current accepted route-convergence adapter source:
  `c82c3a741053a9c8da260aa62e1a968af22bb54e`;
- exact current adapter Git blob:
  `6955dec2e31e14c0ae4847acba22f9fb0087715b`; and
- protected local/origin `master` and `handoff/current`:
  `2e34bdad732fdab32fbf778280b3d3c70d66d602`.

The current adapter must be byte-identical to the `c82c3a7...b54e` blob and
both `8de886c...937e` and `c82c3a7...b54e` must remain ancestors. This binds the
original extraction acceptance without reverting the later accepted evidence-
precedence and idempotency-ordering corrections.

## One-read state machine

The occupied path has two explicit phases.

1. `prepare` performs only public/committed source, contract, latch, Git-ref,
   output-absence and code-byte checks. It must not open or hash the fixture.
   It exclusively creates the ignored local control
   `adapter-test-consumption-control.json` beside the fixture with state
   `prepared` and logical fixture-read count zero.
2. `consume` requires that exact prepared control, atomically advances it to
   `consuming` with logical fixture-read count one **before** opening the
   fixture, opens the fixture once, calls `read()` once, hashes those bytes,
   verifies the exact accepted SHA-256, and parses those same in-memory bytes.
   No reopen, reread, retry, fallback, archive access or replacement fixture is
   permitted.

If any failure occurs after the consuming marker is durable, the terminal is
fail-closed and no retry is authorised. This deliberately prefers a possible
unused lease over an untraceable second read. A successful terminal advances
the local control to `complete`; the control remains local and ignored as the
durable no-rerun marker.

## Closed structural projection and adapter test

The candidate must validate through the exact accepted `CandidatePayload`
schema. Its utility must equal the accepted public reading: six events, four
distinct relative minutes, a nineteen-minute span, two event kinds, one
synthetic subject slot and one resource slot.

Only `event_kind`, `relative_minute`, `synthetic_subject_slot`,
`resource_slot`, `relative_day_offset` and their closed aggregate reading may
influence the in-memory test context. A one-way namespaced derivation produces
new authored-synthetic UUIDs and an idempotency key; no source identity or
mapping is retained. The structural sequence selects one synthetic `Booked`
appointment, an aware fixed synthetic instant shifted only by the relative
minute span, and no waiting-area assignment or movement.

The harness invokes `compose_product_check_in` exactly once with in-memory
dependencies. Acceptance requires all of the following:

- exact call order `claim`, `lock`, `reauthorize`, `verify`, `effect`, `audit`,
  `event`, `complete`, `commit`, `readback`;
- one authenticated synthetic Receptionist, one exact synthetic practice and
  one exact idempotency claim;
- signed-evidence verification and proposal freshness remain distinct;
- one `Booked -> Arrived` effect, one audit, one patient-free
  `diary.appointment_checked_in.v1` event, one idempotency completion, one
  commit and matching readback;
- no waiting-area assignment, removal or movement;
- exact `appointment.check_in_receipt.v1`, status `Arrived`, `confirmed_write`,
  HTTP 200 and patient-free response; and
- the fixture supplies context only: all authority, confirmation, freshness,
  idempotency, audit and readback checks remain independently exercised.

## Implementation surfaces

The candidate may add:

- `orchestration_harness/historical_diary_check_in_adapter_test_consumption.py`;
- one thin command-line wrapper under `scripts/`;
- focused tests using only temporary authored-synthetic candidate bytes and
  temporary control/output paths;
- a plan/conformance test;
- this plan and its threat-model delta; and
- tranche-local receipts and sanitised Continuity evidence.

No ordinary recurring test may open the accepted ignored fixture. Only the
single occupied `consume` command may receive that exact path.

## Sanitised occupied evidence

The committed result may retain only schema/decision labels, full accepted Git
bindings, contract and fixture digests, the six public aggregate utility
values, logical read count one, adapter invocation count one, fixed call order,
synthetic authority/idempotency assertions, status transition, receipt/event
schema labels, waiting-area preservation, patient-free assertions, and zero
counts for archive/provider/product/runtime access.

It must not retain fixture JSON, event rows, subject/resource slot values,
derived UUIDs or keys, source identities, names, contact fields, notes,
filenames, original paths, absolute source dates/timestamps, mappings, patient
or appointment data.

Evidence label:
`local_provider_free_historical_derived_minimised_fixture_adapter_test`.

Claim ceiling:
`one_exact_local_provider_free_adapter_test_consumption_no_real_practice_product_runtime_or_archive_validity_claim`.

## Verification sequence

1. Run synthetic-only focused tests, plan checks, Ruff, compileall,
   `tests/test_api_spine_artifacts.py`, `git diff --check`, and forbidden-path
   checks without reading the real fixture.
2. Commit the exact implementation candidate with explicit-path staging.
3. Rehydrate, verify full Git IDs/ancestry/blobs/refs, pass the deterministic
   pre-execution gate, and run `prepare` once.
4. Run `consume` once. Never retry it.
5. Validate the sanitised result independently against the frozen schema and
   acceptance predicates. A deterministic complete result makes external
   verifier transport unnecessary because the private fixture cannot be sent
   to a worker; a failure closes the tranche without substitution.
6. Package closeout, Sol acceptance, error-register update if qualifying, Yuri
   lay/technical summary, Continuity/Compass publication and Pushover receipt.

## Parallelism efficacy

- DeepSeek Flash: `declined_negative`; the native Harness remains paused, Claude
  is not a silent fallback, and a worker cannot own or receive the single local
  fixture read.
- Gemini: `not_applicable_neutral`; it cannot receive the local ignored fixture
  and deterministic schema/byte controls cover the bounded acceptance.
- Native subagents: `declined_negative`; dividing a one-lease one-invocation
  state machine would add custody and correction surfaces.
- GPT Sol: serial planner, implementer, occupied executor, reviewer and
  integrator for this tranche.

Reassess only if a deterministic pre-consumption implementation check fails or
at the next named tranche boundary. No lane may be silently substituted.

## Explicitly closed

No archive read; broad trove processing; provider/model/network/telemetry;
product, patient, appointment, clinical or protected data; database, route,
client, runtime or configuration; ordinary-practice enablement; feature-flag,
allowlist or default-denial change; generic-status `Arrived` grammar; first-
party client; waiting-area movement; production; deployment; release; Pages;
protected evidence; or protected-ref movement is authorised.
