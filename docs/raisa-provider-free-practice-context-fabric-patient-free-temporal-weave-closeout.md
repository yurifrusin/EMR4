# Provider-free Practice Context Fabric patient-free temporal weave closeout

Date: 2026-08-06

Status: accepted

Result:
`raisa_provider_free_practice_context_fabric_patient_free_temporal_weave_pass`

Reviewed source HEAD:
`f32004a2f39ac769ba746afe2663813f7c422d8a`

## Outcome

The first patient-free temporal Context Fabric contract passes. It proves the
mechanism needed to keep a Bureau's admitted `ContextFrameSet` truthful during
an interaction without patching model context or treating event payloads as
replacement truth.

The pure provider-free path is:

`released immutable ContextFrameSet -> exact TemporalDependencyManifest -> backend-owned expiring TemporalWatchLease -> sealed patient-free event observation -> atomic decision + state-after + CommittedCheckpoint transition -> old set REASSEMBLY_REQUIRED -> one inert fresh-reassembly requirement -> later exact-generation/request admission`

The watcher plane does not update frame content. A relevant signal retires the
old set from new reasoning. A later separately authorised source read must
produce a completely new frame-set id/digest and pass same-packet proofreading.

## Temporal signal and checkpoint result

- Every manifest dependency binds exact parent frame, source, grant, authority
  binding, practice/session generation, policy, selector, revision and expiry.
- The watch lease can only narrow that manifest and has
  `execution_enabled: false`, `returns_data: false`, `read_only: true` and
  `command_authority: false`.
- Signals carry committed patient-free metadata only. The closed schema admits
  no payload, before/after state, patient identity, free text or replacement
  context.
- Each sealed watcher transition keeps `ObservedCursor`, classification,
  state-after and next `CommittedCheckpoint` together while retaining
  `fresh_read_executed: false`. A later read failure cannot erase the
  invalidation that made the old set stale.
- The first relevant signal emits one reassembly requirement; later relevant
  signals coalesce while retaining ordered cause digests. Irrelevant signals
  remain quiet.
- Foreign practice, undeclared schema/family, replay, equal/older revision and
  expired signals fail closed. Noninitial re-baseline, cursor mismatch,
  transaction-position gap, aggregate revision jump and late newer revision
  make continuity uncertain and require complete reassembly.
- Expiry or session/authority revocation prevents further use. Older session
  generations and request revisions cannot restore a superseded set.

The design explicitly declines a no-loss runtime claim for the accepted
Reception One `(occurred_at, event_id)` cursor. A future operational watcher
needs a monotonic transaction/outbox position because a later-inserted
backdated event can otherwise fall behind that coordinate.

## Historical operational-state result

The contract keeps historical snapshots distinct from current truth and events:

- half-open valid time records when an operational fact held;
- half-open transaction time records when that version was known;
- a late correction appends a new transaction-time version with immutable
  correction/supersession lineage;
- exact `valid_at` plus `known_at` queries reproduce both “known then” and
  “corrected later” results;
- purpose, location, source class, lookback, count, fields and retention class
  only narrow;
- explicit coverage gaps never become evidence that nothing happened; and
- event-delivery TTL is not historical-retention policy.

This is authored-synthetic in-memory semantics only. It establishes no
operational history store or production retention period.

## Branded workspace and atomic Bureau direction

Yuri's concurrent architecture decision is now durable:

- `RECEPTION ONE™` and candidate `Clinician One` are branded workspace and
  projection families, not security principals or authority partitions;
- capability authority remains atomic and backend-owned;
- alongside Consultant, separately governed future Bureau families are needed
  at minimum for requests/correspondence/referrals, prescribing/medicines and
  medication safety, and billing/claims/financial administration; and
- interweaving with Diary, waiting-room and other reception work uses typed
  Context Fabric frames and bilateral handoffs, never inherited brand authority
  or shared private model memory.

This direction is preserved in the model-required Bureau architecture,
Context Fabric direction and implementation plan. It grants none of those
future Bureaus implementation or clinical/product authority.

## Evidence and verification

The committed authored-synthetic acceptance evidence records the exact closed
schema/example, canonical-LF artifact hashes, parent immutability, relevant/
coalesced/irrelevant decisions, cursor-gap result, stale-result rejection,
bitemporal selection and zero side-effect counters.

Sol verification passed:

- 20/20 focused temporal contract tests;
- 141/141 inherited temporal, Current weave, Bureau Memory, API Spine,
  Synaptic Router and session-reconciliation tests before reviewer dispatch;
- Ruff, compileall, JSON validation and `git diff --check` clean.

The fresh Gemini 3.6 Flash/high Antigravity veto returned one
schema-constrained `pass` at unchanged clean reviewed HEAD
`f32004a2f39ac769ba746afe2663813f7c422d8a`.

Its prose claimed 67 tests across seven files and cited the contained DeepSeek
failure under a nonexistent DeepSeek inbox path. Exact collection and execution
in that same review worktree establish 120/120 passing tests and the committed
failure receipt under the Codex inbox. AER-0037 and the reconciliation receipt
make both prose claims non-authoritative without another provider call; the
architectural `pass` remains admissible.

The earlier occupied DeepSeek V4 Flash/high implementation transport created no
owned artifact or candidate commit before its bounded termination. AER-0036
contains it; the frozen packet continued through the declared Codex fallback.
No provider output was released to product or treated as acceptance authority.

## Claim and authority boundary

Passing proves a pure provider-free authored-synthetic invalidation,
checkpoint, reassembly-ticket and bitemporal-query contract. It does not prove
a live watcher, database/event transport, transactional outbox, persistence,
production retention, product authorization, patient privacy, provider-model
retrieval, runtime performance, prescribing/referral/billing capability or
command safety.

No patient, clinical, product-derived, protected or historical-PHI data; real
database/session/feed/listener; persistence, broker, worker or retention job;
provider/external retrieval; GraphQL/REST product surface; command/write;
deployment, production, release, Pages, protected evidence or protected-ref
movement was opened. `docs/branding/` and unrelated untracked artifacts remain
preserved and excluded.

## Next descendant

Under Yuri's standing uninterrupted planned-gate authority, the next safe
descendant is a separately frozen provider-free, patient-free, unmounted
intent-shaped temporal retrieval rehearsal. It may prove that a closed model-
independent request shape selects the minimum current, recent-work and
historical frames with explicit ambiguity and provenance. It receives no
patient/product data, real source, persistence, provider call, runtime route or
command authority from this closeout.
