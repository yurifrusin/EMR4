# Yuri update — CF-D2 observability-first event and cue architecture

Date: 2026-08-13

Timestamp: 2026-08-13T16:23:03+10:00 (Australia/Brisbane)

Status: accepted; sprint engine continuing

## Lay summary

We have returned to CF-D2, but with a much smaller job. Instead of asking a
watcher to remember appointment truth, it will eventually remember only that a
particular Reception One view may be out of date and needs to be refreshed.
The real database remains the referee. A delayed, repeated or missing cue can
make the screen refresh later, but it cannot make a stale booking change pass.

The useful foundation is now sharply divided. The observer records how far it
has safely inspected the source. A durable cue queue records refresh work still
to be delivered. Reception One refreshes from authoritative truth. The command
service separately decides whether any requested change is still permitted.

We have also addressed the lesson from the earlier four-hour incident. Ten
different failure points now produce ten different diagnostic signals. We
should be able to tell whether the source was not observed, classification
failed, a cue was not created, delivery fell behind, ownership was fenced or
the final fresh read failed—without guessing which internal assertion hid
behind one generic error.

## Technical summary

Accepted source `e8677b54d1c339dcd14776ce8bf15e7db2980378`
freezes a closed async/API Spine contract for:

- one fenced logical consumer per source/practice/event-family partition;
- epoch-bound monotone source positions;
- contiguous terminal classification receipts;
- atomic creation of required payload-free cue obligations before checkpoint;
- independently durable at-least-once delivery backlog;
- exact/unknown/epoch-mismatch lag semantics;
- idempotent duplicates, gap blocking and narrow coalescing; and
- fresh authorised read reconciliation with no cue-derived command authority.

All 39 hostile contract mutations, 114 focused tests and the 193-test canonical
profile pass. There was no runtime, database, provider or product-data access.
No external worker/model review was needed for the deterministic closed packet.

## Deliberately closed

This is architecture, not a watcher implementation. Database representation,
restart/unknown-commit behavior, transport, latency, retention, rotation,
product wiring, real data, patient channels, providers, deployment, production,
release, Pages and protected integration remain closed. CF-D1 stays accepted;
the stopped CF-D2 attempts stay negative evidence.

## Next

The sprint engine is continuing to a pure provider-free unmounted admission
rehearsal. It will run authored-synthetic sequences through the state rules for
duplicates, gaps, checkpointing, coalescing, fencing and reconciliation. It
will still open no watcher, database/source, persistence, provider, route or
command. Your attention is not required.
