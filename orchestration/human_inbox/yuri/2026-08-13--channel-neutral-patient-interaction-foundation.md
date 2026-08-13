# Channel-neutral patient interaction foundation

Date: 2026-08-13

Timestamp: 2026-08-13T14:54:31+10:00 (Australia/Brisbane)

Status: accepted; sprint engine continuing

## Lay summary

The small extra foundation slab is laid. Raisa can now be designed to meet a
patient through ordinary email, SMS, a thin browser page, WhatsApp, voice or a
future trusted assistant without any one of those channels becoming the place
where identity or booking truth lives.

The identity posture is passkey-first, not passkey-only. Patients will be able
to have more than one way in and a humane, separately controlled recovery path;
they will not be required to master a password vault. Medicare numbers, IHI,
birth dates, addresses, health facts and knowledge of an appointment are never
treated as secret proof of identity.

Availability shown to a patient will be an expiring view, not a reservation.
Choosing a time remains provisional. At confirmation, the backend must check
the patient's current authority and the live Diary again. If another person has
won a race for that slot, the records remain correct and Raisa returns the
updated truth.

No patient-facing service has been built or switched on. The next work returns
to the visible Reception One staff interface as planned; your attention is not
required.

## Technical summary

Accepted source `17d9da1844e59406eecda44b5029e839b2e8a573` freezes eight closed
message families, five assurance states and six future-closed channel adapters.
The contract separates record matching, proofing, binding, authentication,
authorisation, delegation and recovery; preserves backend-owned Context Fabric
retrieval and the REST/OpenAPI command boundary; and distinguishes transport
deduplication from command idempotency and delivery receipts from atomic
command receipts.

All 12 deterministic scenarios pass. All 143 hostile mutations fail closed.
Focused tests pass 16/16, the combined foundation/API/latch packet passes
100/100 and the canonical fast profile passes 193/193. No runtime, provider,
patient/product data, database/source, route, command or write was opened.

## Issues and deliberately closed surfaces

No acceptance issue remains. Identity topology, proofing/federation vendor,
first external channel, practice self-booking policy, exact action-assurance
mapping, recovery service levels and production posture remain deliberately
unselected. External patient clients and channels, real identity, product data,
providers, credentials/IAM, deployment, production, release, Pages and
protected refs remain closed.

## Place in Raisa and next tranche

This slab preserves the minimalist “use the software patients already have”
direction while keeping one backend authority model. It avoids a future UI
jackhammer by fixing identity, projection, proposal, confirmation and recovery
semantics before patient-client implementation.

Next: bounded provider-free visible native Diary status-confirm wiring for
Reception One staff against the already accepted backend route. CF-D2 remains a
later observability-first event/cue durability extension.

Yuri attention required: no.
