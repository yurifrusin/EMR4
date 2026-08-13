# Sol acceptance — CF-D2 observability-first event and cue architecture

Date: 2026-08-13

Timestamp: 2026-08-13T16:23:03+10:00 (Australia/Brisbane)

Decision: accepted

Accepted source: `e8677b54d1c339dcd14776ce8bf15e7db2980378`

Accepted result: `raisa_provider_free_cf_d2_observability_first_event_cue_architecture_pass`

I accept the exact provider-free unmounted architecture. It preserves source-
owned truth and command-time correctness while giving the later durable cue
extension a minimal job: retain a payload-free fresh-read obligation through a
contiguous source position.

The checkpoint rule is coherent and fail closed. Each observed position needs
one immutable terminal classification receipt; `cue_required` also needs its
obligation created atomically. Delivery is a separate durable backlog, so a
slow client cannot block observation and a checkpoint cannot erase a required
cue. Duplicate and divergent identities, gaps, rejected schemas, stale fencing
and reconciliation failures have typed non-success behavior.

The ten-stage operator contract repairs the central evidentiary weakness of the
stopped CF-D2 work: each stage has a distinct observable and distinct safe
response. This does not claim the old PostgreSQL anchor cause is known. CF-D1
and all stopped CF-D2 artifacts retain their original status.

Acceptance is supported by 39 rejected hostile mutations, 114 focused tests,
the 193-test canonical fast profile, Ruff, formatting, compilation, Diary
syntax and whitespace. No external review was required because the closed
schema and deterministic mutation gate fully decide this repository-only
contract without a competing authority interpretation.

No watcher, database/source, persistence, operational retention, product or
patient data, provider, credential/IAM/network, route, tool, command/write,
deployment, production, release, Pages or protected-ref authority is opened.
The next safe descendant is the pure provider-free unmounted event/cue
admission rehearsal against this exact accepted source.
