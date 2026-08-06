# Independent architecture challenge — source-specific durability

Date: 2026-08-06

Status: completed read-only challenge; no acceptance authority

## Material findings

The challenger agreed that the current payload-bearing committed-event feed and
its `(occurred_at, event_id)` cursor cannot become a no-loss source. It supported
a per-practice/event-family transactional head row whose update and payload-free
projection append roll back with the existing command transaction. PostgreSQL
sequence/identity, timestamp, UUID, transaction-id and incidental WAL ordering
were rejected.

The challenge identified one material tightening before freeze: atomicity cannot
be claimed when checkpoint state is durable but frame retirement is only an
in-memory object. The corrected architecture therefore uses a monotonic durable
invalidation watermark. Every dependent frame generation cites stream epoch,
observer generation and `assembled_through_position`; a newer watermark makes
it permanently non-current. A future replacement frame must also fence its
truth read against the source head in one database snapshot or an exact
before/after equality check.

## Other accepted corrections

- the observation integration principal may not reuse the staff feed JWT;
- the internal durability coordinator remains a distinct narrow principal;
- aggregate revision is freshness/anomaly metadata, not reschedule-stream
  continuity, because the current producer counts all appointment audit rows;
- exact redelivery is keyed by epoch/position and receipt, not HMAC alone;
- the identity HMAC key ring is dedicated, position-fenced and never reuses an
  application, integration-authentication or provider secret;
- retention for source rows, checkpoint/decision state and audit remains
  separate and never inherits the current 24-hour delivery expiry; and
- audit uses closed count buckets and excludes payload, product links, active
  session inventory and free text.

## Preserved later-gate risks

Migration/RLS/roles, producer modification, transaction isolation, lock
contention, credential/key storage, retention durations and capacity,
database-backed crash recovery, process ownership, monitoring, deployment and
privacy assessment remain later live-runtime decisions. No file was edited by
the challenger and no Git, provider, source, database or runtime action occurred.
