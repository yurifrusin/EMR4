# Channel-neutral patient interaction foundation closeout

Date: 2026-08-13

Timestamp: 2026-08-13T14:54:31+10:00 (Australia/Brisbane)

Status: accepted

Accepted source: `17d9da1844e59406eecda44b5029e839b2e8a573`

Result: `raisa_channel_neutral_patient_interaction_foundation_pass`

## Outcome

The small extra foundation slab is complete. Raisa now has a closed,
renderer-neutral architecture for future patient interactions through software
patients already use, without making SMS, email, thin web, WhatsApp, voice or a
delegated assistant an identity authority, source of truth or command plane.

The contract separates record resolution, proofing, binding, authentication,
authorisation, delegation and recovery. It adopts
`passkey_first_not_passkey_only`, supports multiple authenticators and humane
assisted recovery, and forbids IHI, Medicare number, demographics, contact
details, health knowledge or appointment knowledge from acting as
authenticators.

Every future channel remains `future_closed`. A channel may eventually render
only a minimized, expiring backend projection. A displayed candidate is not a
reservation, selection remains proposal-only and a single-use confirmation
challenge has no command authority. Any future booking effect must converge on
the existing REST/OpenAPI proposal-confirm family, where current principal,
practice, proxy scope, assurance, proposal evidence, source revision and Diary
truth are freshly rechecked before atomic audit, idempotency and receipt.

## Evidence

- The closed Draft 2020-12 contract schema admits exactly eight
  authored-synthetic message families across five assurance states and six
  future-closed channels.
- All twelve frozen scenarios pass.
- All 143 hostile mutations are rejected; none is admitted.
- Focused contract/plan tests pass 16/16.
- The combined foundation, API Spine and active-latch packet passes 100/100.
- The canonical fast profile passes 193/193, including Ruff, in-memory
  compilation of 209 maintained Python files without protected-path
  enumeration, Diary JavaScript syntax and Git whitespace.
- No runtime, patient client, provider, product or patient data, database,
  source access, command or write was opened.

The sanitized result is
`orchestration/continuity/raisa-channel-neutral-patient-interaction-foundation/provider-free-acceptance-evidence.json`.

## Decisions deliberately left open

This tranche does not choose central versus practice-scoped identity topology,
a proofing/federation/DVS/Digital ID provider, the first external channel,
practice self-booking policy, exact higher-risk assurance mapping, recovery
service levels or production hosting and retention posture. Those belong to a
future external-patient-client programme and require their own evidence.

## Claim boundary and next work

This proves architecture only. It does not recognise or authenticate a real
patient, register a passkey, deliver a message, expose a patient client, execute
a booking, establish privacy compliance, deploy or release anything.

The next dependency-satisfied tranche is the already planned bounded visible
native Diary status-confirm wiring for staff, against accepted backend source
`b414eb256853c301099d9cf7797a69cd3ec077c5`. The patient foundation informs its
projection and confirmation semantics but does not turn Reception One into a
patient client. CF-D2 remains a later observability-first event/cue durability
extension informed by the visible consumer boundary.

Protected evidence, patient/clinical/product data, external identity and
channel services, providers, credentials/IAM, deployment, production, release,
Pages and protected refs remain closed. `docs/branding/` and every unrelated
untracked file remain preserved.
