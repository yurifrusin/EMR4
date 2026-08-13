# Sol acceptance — channel-neutral patient interaction foundation

Date: 2026-08-13

Timestamp: 2026-08-13T14:54:31+10:00 (Australia/Brisbane)

Decision: accepted

Accepted source: `17d9da1844e59406eecda44b5029e839b2e8a573`

Accepted result: `raisa_channel_neutral_patient_interaction_foundation_pass`

I accept the exact provider-free, unmounted, authored-synthetic architecture
result. The EMR4 API Spine remains intact: read projections are minimized and
non-authoritative, state changes remain explicit REST/OpenAPI commands, and
transport events or delivery receipts cannot become commands, idempotency
receipts or audit evidence.

The accepted contract cleanly separates record resolution, identity proofing,
binding, authentication, authorisation, delegation and recovery. It is
passkey-first but not passkey-only; it supports multiple authenticators and a
separately restricted, notified, revoking recovery lifecycle. Six future
channels remain untrusted, disabled renderers. A projection never reserves a
slot, a selection is proposal-only and a confirmation challenge remains
single-use and non-authoritative until the backend command freshly rechecks all
current authority and source truth.

Acceptance is supported by eight closed message families, five assurance
states, six future-closed channels, 12/12 deterministic scenarios, 143/143
hostile rejections, 16/16 focused tests, 100/100 combined foundation/API/latch
tests and the passing 193-test canonical fast profile. No runtime, provider,
patient client, identity service, patient/product data, database/source,
command or write was used.

The next safe tranche is bounded visible native Diary status-confirm wiring for
staff against accepted backend source
`b414eb256853c301099d9cf7797a69cd3ec077c5`. External patient-client design
choices and all real identity/channel operations remain separately closed.
