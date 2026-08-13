# Sol acceptance — unmounted CF-D2 event and cue admission rehearsal

Date: 2026-08-13

Timestamp: 2026-08-13T17:00:06+10:00 (Australia/Brisbane)

Decision: accepted

Accepted source: `a7c6f7a66b06fbc065ae8a6eede7fa8baaee1b6b`

Accepted result: `raisa_provider_free_unmounted_cf_d2_event_cue_admission_rehearsal_pass`

I accept the exact provider-free unmounted rehearsal. It converts the accepted
observability architecture into small deterministic transition rules without
crossing into persistence or runtime. Receipt identity, obligation identity,
checkpoint meaning, coalescing limits, ownership fencing, lag states and fresh-
read reconciliation are now executable rather than merely described.

The state machine fails closed at every important boundary. Shape or payload
smuggling, invalid positions, stale generation, missing classification, absent
required obligation, invalid reason and divergent identity all preserve the
complete prior state. Checkpointing never depends on delivery and never crosses
a gap. Delivery and reconciliation have separate typed state, and a cue cannot
be mistaken for display truth or future freshness.

Acceptance is supported by 22 passing canonical scenarios, 60 rejected hostile
variants, 91 focused lineage checks and the 193-test canonical fast profile.
The parent closed schema and API Spine authority contract remain valid. No
external review was needed because the pure deterministic state transition and
hostile mutation gates fully decide the bounded claim.

No watcher, database/source, persistence, operational retention, product or
patient data, provider, credential/IAM/network, route, tool, command/write,
deployment, production, release, Pages or protected-ref authority is opened.
The next safe descendant is an inert provider-free unmounted representation
architecture for these exact admitted facts; it has no database connection or
migration-execution authority.
