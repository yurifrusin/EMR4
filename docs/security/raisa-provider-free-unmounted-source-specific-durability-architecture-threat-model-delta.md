# Threat-model delta: source-specific observation durability architecture

Date: 2026-08-06

Status: frozen provider-free architecture delta

## Trust boundaries and assets

Untrusted inputs are claimed source identity, stream/event/schema values, raw
event UUID, aggregate alias/revision, position/predecessor, timestamps,
principal/binding copies, checkpoint copies, key schedule and restart/recovery
claims.

Protected assets are practice isolation, source payload confidentiality,
rollback-safe stream completeness, checkpoint integrity, monotonic frame
invalidation, reassembly-obligation idempotency, key material, privacy-safe
audit and separation of observer, durability, read and command authority.

## Threats and controls

| Threat | Control |
|---|---|
| Existing polling cursor is relabelled no-loss | Explicitly reject `(occurred_at, event_id)`, expiry and UUID ordering; require a transactionally updated per-practice/stream head plus predecessor. |
| PostgreSQL sequence rollback gap looks like data loss | Sequences and identity columns are ineligible; head update and row append roll back together in the producer transaction. |
| Outbox publication is separated from appointment commit | Append control row and update head in the same transaction as appointment, audit, idempotency and existing committed event. |
| Observer can read the payload-bearing source row | Distinct payload-free projection, exact `SELECT` privilege and practice isolation; no base-table/payload/product-table grant. |
| Direct identifiers are smuggled as control metadata | Closed fields; non-semantic raw event UUID is HMAC-normalized and discarded; backend opaque aggregate alias only; no appointment/practitioner/location/time/actor/correlation/reason value. |
| Integration principal persists state or inherits session authority | Exact read-only integration principal and `persistence_authority: false`; distinct narrow durability coordinator; application principal owns later reads. |
| Durability coordinator queries current product truth | Coordinator receives the admitted packet and may touch only durability, lifecycle, obligation and privacy-safe audit state. |
| Staff HTTP-feed identity is reused as observer identity | Exact non-human integration principal; staff JWT and application session are structurally ineligible. |
| Crash advances checkpoint before invalidation | Classified receipt, monotonic durable invalidation watermark, coalesced obligation, audit and next checkpoint commit or roll back together. |
| Architecture calls an in-memory frame mutation atomic | Frame currentness derives from persisted source epoch and `assembled_through_position` versus the durable watermark. |
| Fresh truth races a committed observation | Release only from one consistent source-head/truth snapshot or a verified before/after source-head fence. |
| Full invalidation advances past a missing source position | Coverage gaps hold the last contiguous checkpoint, consume the generation and require rebaseline; only contiguous known input may advance after complete retirement. |
| Duplicate delivery repeats invalidation | Unique practice/stream/generation/position receipt; exact redelivery returns the prior receipt without mutation. |
| Same position is replaced or digest reused | Treat mismatched same-position identity or same-observation/different-position as corruption and require full invalidation/rebaseline. |
| Concurrent consumers double-process | Serialize on the exact checkpoint row; loser rereads committed receipt and state. |
| Restart adopts frames assembled before observation coverage | Frame/manifest must cite exact stream epoch, generation, baseline and checkpoint; otherwise retire and rebuild. |
| Lost checkpoint or retained-row gap is ignored | `REBASE_REQUIRED`, full bounded invalidation, new generation and baseline; never reconstruct from payload or skip forward. |
| Fast consumer or 24-hour TTL drives unsafe purge | Retention uses the minimum eligible checkpoint plus recovery pins, key overlap and safety grace; existing delivery expiry has no durability role. |
| Backpressure samples invalidation truth | Stop admission and invalidate/rebaseline when continuity is lost; no sampling, dropping or silent checkpoint advance. |
| Aggregate revision is mistaken for stream continuity | Treat it only as aggregate freshness/anomaly metadata; source position and predecessor alone prove transport continuity. |
| HMAC rotation changes identity for retained events | Position-interval key schedule; old key retained through checkpoint/retention overlap; retroactive change or missing key consumes generation. |
| HMAC identity key is shared with auth/application secret | Dedicated key ring, explicit key id and position interval; never reuse `settings.secret_key`, integration auth or provider credentials and never try every key. |
| Key or raw event id leaks through audit/evidence | Store only key id and observation digest; key material and raw id are prohibited recursively. |
| Audit reveals active users or becomes Bureau memory | Closed digest/code/count allowlist; no alias, session inventory, frame content, actor, payload or free text; audit is not context/read/command evidence. |
| Control position is treated as current truth | Position proves only ordered committed change; fresh product truth still requires current application authority and a new no-wider grant. |
| Architecture artifact opens runtime by implication | Exact unmounted provider-free evidence label and static tests prohibiting app, migration, database, route, listener, provider, command and deployment artifacts. |

## Residual risks deliberately deferred

Migration and rollback design, PostgreSQL table/view/function/RLS/role details,
transaction isolation, lock contention, producer availability behavior,
operational credential and key storage, process ownership, monitoring,
retention duration/capacity, real crash recovery, database-backed acceptance,
deployment and privacy assessment require separate reviewed gates.

## Forbidden openings

No protected holdout, historical PHI, patient/clinical/financial/product data,
raw audit, live database/outbox/feed/watcher/listener/source read, migration,
table/view/function/trigger/sequence/role/credential, route, GraphQL/REST change,
checkpoint/persistence, provider/external retrieval, command/write, runtime,
deployment, production, release, Pages or protected-ref movement. Preserve and
exclude `docs/branding/` and unrelated untracked artifacts.
