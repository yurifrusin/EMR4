# Provider-free unmounted Rayleen waiting-room Context Fabric source-adapter plan

Date: 2026-08-06

Status: frozen bounded implementation plan

Parent results:

- `model_required_bureau_a4_product_read_ui_pass`;
- `raisa_provider_free_practice_context_fabric_current_operational_weave_pass`;
- `raisa_authored_synthetic_model_required_practice_context_fabric_intent_shaping_rehearsal_pass`.

Planning source HEAD: `bcd5f57842d1ba010064214634859a3ba650bb3d`

## Objective

Prove one pure, provider-free and unmounted adapter from Rayleen's already
authorised serialized A4 `emr4.waiting_room_context_frame.v1` read shape to the
accepted Context Fabric `current_waiting_room_projection` source envelope.
The adapter receives a completed read projection only after ordinary backend
authorization. It cannot open a database session, invoke the read service,
refresh a frame, subscribe to changes, call a provider or mount an API route.

The exact target result is
`raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter_pass`.

## API Spine classification

This is a read/context adapter after an existing authorised GraphQL/query
service. It adds no query root, REST path, Access AI command, mutation, event
transport or product-runtime import. The existing source remains the owner of
practice/location authorization, waiting-room truth, elapsed-time calculation
and freshness. The adapter only validates, minimizes, aliases and seals one
already materialized shape for Context Fabric assembly.

REST/OpenAPI remains the only command plane. A released source envelope or
`ContextFrameSet` has `read_only: true`, `command_authority: false` and
`provider_authority: false` and can never confirm a waiting-room action.

## Frozen input

The adapter receives exactly:

1. one closed serialized A4 `WaitingRoomContextFrame`, validated against the
   accepted repository schema;
2. the accepted sealed Current operational-weave `ContextAuthorityBinding` and
   `ContextScopeGrant`, already admitting Rayleen,
   `CURRENT_OPERATIONAL_AWARENESS`, `current_waiting_room_projection`,
   `current_waiting_room`, one practice and one location;
3. one backend-authored sealed `WaitingRoomReferenceAliasManifest` binding the
   exact source-frame digest, binding/grant/session digests, source practice and
   location, and a complete one-to-one map from every admitted source UUID to a
   request-scoped opaque Fabric reference; and
4. one caller-supplied timezone-aware `assembled_at` used by all freshness and
   proofreader checks.

The adapter does not accept a user/model-selected practice, role, purpose,
source, field, alias, TTL, retention period or authority flag. The alias
manifest is comparison/projection material, not authentication or command
authority.

## Exact transformation

Trusted code must:

- validate recursive schema closure, the exact reader, excluded-field list,
  `data_only` labels and the A4 two-minute maximum lifetime;
- require frame, fact and signal observation/expiry coordinates to agree and
  reject future, stale or expired material;
- reject duplicate facts, duplicate per-appointment signal kinds, orphan
  signals, mismatched labels, unsupported status/signal/value types and
  fabricated deterministic calculations;
- recompute elapsed minutes, threshold bands, missing-arrival/overdue
  exceptions and longest-wait ranks from the admitted A4 facts and require the
  source signals to match exactly;
- verify the complete alias manifest against source, binding, grant and
  session digests and reject missing, duplicate, unrelated or raw-identifier
  aliases;
- omit `patient_display_token`, source UUIDs, source label identifiers,
  scheduled/arrival timestamps and excluded field classes from the Fabric
  payload;
- emit only opaque appointment/practitioner references, closed status and
  available deterministic elapsed/threshold/exception/rank fields;
- preserve source observation, expiry and context revision, compute a sealed
  source-frame digest, and never extend expiry; and
- emit one exact `current_waiting_room_projection` /
  `current_waiting_room` / `emr4.waiting_room_context_frame.v1` source envelope
  plus one minimal adapter trace.

Missing arrival time is not repaired or invented. Its entry may carry only the
closed exception code; absent elapsed/threshold fields remain absent. The
accepted Current weave projector must therefore preserve optionality rather
than indexing a missing derived field.

## Authored-synthetic proof

The canonical fixture contains one newly authored synthetic arrived
appointment with exact A4 facts and signals. Its source UUIDs are mapped by the
sealed manifest to the opaque references already used by the accepted Current
operational-weave fixture. The adapter-generated waiting-room envelope replaces
only that fixture's hand-authored waiting-room envelope. The unchanged Diary,
directory and private-session envelopes then compose through the existing
assembler and same-packet proofreader to `RELEASE`.

Additional negative cases cover missing-arrival truth, expiry, cross-practice
and cross-location mismatch, stale/superseded grants, schema additions, signal
tamper, alias leakage/tamper, over-limit inputs, output byte limits and every
authority bit.

## Artifacts

- this plan, one design and one threat-model delta;
- one pure adapter/proofreader module under `scripts/`;
- one closed adapter-result schema and newly authored synthetic fixture under
  its continuity namespace;
- one provider-free acceptance generator and canonical evidence;
- focused tests and API Spine/preservation regressions;
- later independent review, closeout, Sol acceptance and continuity update.

No `app/**`, `docs/diary/**`, mounted GraphQL schema, REST/OpenAPI command,
database migration, provider/runtime controller or deployment artifact is
owned by this tranche.

## Acceptance

Acceptance requires:

1. exact recursive input/output closure and canonical digest verification;
2. exact parent binding/grant/source-triple admission before payload access;
3. deterministic recomputation of all A4 derived signals and fail-closed
   handling of absent arrival time;
4. complete request-scoped aliasing with no raw UUID, patient-display token,
   source id, excluded class or unrelated reference in the output;
5. source observation/freshness/expiry preservation with no lifetime extension;
6. one adapter-built envelope replacing the hand-authored Current-weave
   waiting source and passing the unchanged assembler plus same-packet
   proofreader;
7. tamper, cross-scope, stale, orphan, duplicate, cardinality, byte-limit and
   authority tests releasing nothing;
8. zero provider, network, database, filesystem-write, subprocess, product API,
   command, deployment, protected-evidence or protected-ref action in the pure
   path; and
9. API Spine regression evidence proving no route, mutation or command surface
   was added.

Before acceptance, the exact deterministic candidate receives one fresh
Gemini 3.6 Flash/high read-only veto in a clean non-protected worktree. The
reviewer receives authored-synthetic repository material only and gains no
implementation, acceptance, integration or protected-ref authority.

## Claim boundary

Passing proves only that one authored-synthetic serialized A4 waiting-room
shape can be validated, minimized, opaquely referenced and admitted as one
source in the already accepted provider-free Current weave. It does not prove
real-data privacy, live product integration, a database watcher, automatic
refresh, persistence, historical retention, patient identity lookup,
cross-Bureau clinical work, provider cognition, product performance or command
safety.

Patient, clinical, product-derived, financial, protected and historical-PHI
data; real database/session/feed/watcher access; event transport; persistence;
new API/runtime wiring; provider calls; requests/referrals,
prescribing/medicines, billing/claims or Consultant implementation; commands,
writes, deployment, production, release, Pages, protected evidence and
protected-ref movement remain closed. Preserve and exclude `docs/branding/`
and all unrelated untracked receipt/state/evidence/cost-ledger files. Git
staging is explicit-path only.
