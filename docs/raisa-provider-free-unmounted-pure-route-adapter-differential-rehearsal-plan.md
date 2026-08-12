# Provider-free unmounted pure route-adapter differential rehearsal plan

Date: 2026-08-12

Source HEAD: `a433eb68b5c40dd61fb4b6cf23c9af09cb0270ef`

Status: `frozen_for_provider_free_unmounted_execution`

## Purpose

Rehearse pure transformations from authored-synthetic appointment confirm and
raw compatibility envelopes into the accepted
`ConditionalAppointmentCommand` shape. Prove that complete envelopes preserve
the same command semantics across ingress adapters and that the current raw
shape fails closed with exact missing-control codes.

This tranche tests an inert adapter boundary only. It imports and executes no
application route and grants no runtime eligibility.

## Boundary classification

This is a REST/OpenAPI command-plane contract rehearsal under the API Spine:

- confirm and hypothetical complete raw envelopes may produce inert kernel
  candidates;
- current raw envelopes produce no candidate because they lack separate
  confirmation, an echoed backend precondition and command idempotency;
- canonical operation identity and adapter provenance come from the frozen
  route specification, never from caller-controlled fields;
- events and Context Frames supply no command evidence;
- proposal routes remain outside the mutation kernel; and
- no candidate is executed, persisted, authorized or passed to a runtime
  command service.

## Frozen scenario census

The rehearsal contains exactly:

- four authored-synthetic intents: create, update, status and delete;
- five complete confirm cases, including both create-confirm aliases;
- four current raw cases missing the exact three control groups;
- four hypothetical future raw-complete cases; and
- four differential groups comparing every mapped field except the sole
  provenance field, `route_adapter_id`.

The exact current-raw rejection codes are:

1. `backend_precondition_missing`;
2. `confirmation_evidence_missing`; and
3. `idempotency_identity_missing`.

These are group-level codes: backend precondition covers version plus digest;
confirmation evidence covers mode plus reference; and command idempotency
covers key digest plus canonicalization version. Audit attribution remains
present in the authored-synthetic request context and is kept distinct from
all three controls.

## Adapter rules

Every adapter:

- is selected by a closed server-side adapter identifier;
- injects the canonical operation and adapter provenance from that frozen
  specification;
- maps principal, target/conflict, digest, precondition, confirmation,
  idempotency and correlation fields without semantic rewriting;
- rejects missing control groups before emitting a kernel candidate;
- rejects unknown structure, caller-supplied operation or caller-supplied
  adapter identity;
- preserves the accepted target shape and lock plan; and
- returns `candidate_mapped` or `adapter_rejected` with no command outcome or
  effect.

A hypothetical complete raw envelope demonstrates only that a future adapter
could construct the same inert candidate. It does not make the current raw
route kernel-eligible and does not satisfy client parity, shadowing, database
fence, route convergence, deprecation or release gates.

## Owned files

- this plan;
- `docs/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-design.md`;
- `docs/security/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal-threat-model-delta.md`;
- `orchestration/continuity/raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal/contract.json`;
- its closed schema;
- `scripts/raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal.py`;
- `tests/test_raisa_provider_free_unmounted_pure_route_adapter_differential_rehearsal.py`;
- exact receipt, closeout, acceptance, Yuri mailbox, Continuity/Compass updater
  and lifecycle test artifacts if the tranche passes.

## Forbidden surfaces

- no import, invocation, edit, alias or wrapping of an application route;
- no HTTP server/client, application model, database, source, watcher, event,
  migration, transaction or production fence;
- no provider, network, credential, IAM or metadata access;
- no product-derived, patient, clinical, financial or free-text data;
- no executable tool, capability lease, command, write or mutation;
- no client switch, compatibility-mode change, deployment, production,
  release, Pages rebuild or protected-ref movement; and
- no broad staging, `docs/branding/`, protected evidence or unrelated
  untracked file.

## Acceptance

The tranche passes only when:

1. one closed schema validates one exact source-hashed contract;
2. exactly nine adapter identities bind the accepted four raw and five confirm
   routes to the four canonical operation families;
3. exactly thirteen scenarios cover five complete confirms, four current raws
   and four hypothetical complete raws;
4. every complete envelope maps all eighteen kernel fields and every current
   raw envelope produces no candidate plus exactly the three frozen gap codes;
5. the four differential groups are field-for-field equal after excluding only
   `route_adapter_id`;
6. no caller field may override canonical operation or adapter identity;
7. target shapes, per-family lock plans, eight outcome vocabulary and
   authority-first precedence match the accepted kernel contract;
8. all candidates remain inert and runtime-ineligible;
9. at least thirty independent hostile mutations fail closed;
10. focused API Spine, repository-profile and Git whitespace checks pass; and
11. protected refs and every pre-existing untracked file remain unchanged.

## Recovery and next work

A mechanical schema, fixture, evaluator or assertion defect may receive one
bounded correction without changing the frozen mapping or gap semantics. A
request to infer confirmation from authentication, infer freshness from a
same-transaction read, weaken command idempotency, add a second provenance
exception or grant runtime eligibility is conceptual and must stop this
tranche.

After acceptance, the next safe candidate is the provider-free unmounted
default-off non-enforcing shadow-comparison architecture. It may define how a
future route-local observer compares current behavior with the pure adapter
without gating, mutating or changing a response, but may not wire or execute a
route, database, source, event, watcher or command.
