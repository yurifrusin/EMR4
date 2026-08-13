# Channel-neutral patient interaction foundation plan

Date: 2026-08-13

Timestamp: 2026-08-13T14:28:04+10:00 (Australia/Brisbane)

Status: frozen

Revision: 1

Task baseline: `17bcf96778582e208e43f2c639090511f1ddb45c`

Accepted status-confirm source: `b414eb256853c301099d9cf7797a69cd3ec077c5`

Reasoning level: external-patient identity and command-boundary architecture — Extra High

## Objective

Lay one provider-free, unmounted foundation slab before visible Reception One
work resumes. Freeze a channel-neutral patient interaction contract that:

- separates patient-record matching, identity proofing, authentication,
  authorisation, delegation and recovery;
- adopts `passkey_first_not_passkey_only` without requiring a password vault;
- treats SMS, email, thin web, WhatsApp, voice and future delegated assistants
  as replaceable, untrusted adapters;
- permits only expiring, minimized Diary projections and proposal-shaped
  selections at the channel edge;
- converges every future booking mutation on the existing backend-owned
  REST/OpenAPI proposal-confirm command path; and
- makes recovery a separately assured, notified and auditable lifecycle rather
  than a silent downgrade to knowledge questions or possession of one channel.

The tranche records architecture and deterministic authored-synthetic contract
evidence only. It does not create an external patient client or authenticate a
real patient.

## Governing decisions

1. A domain patient record, IHI, Medicare number, date of birth, address,
   telephone number or email address is never an authenticator.
2. A channel binding can recognize a previously enrolled contact route but
   cannot prove identity, grant patient-record access or confirm a command.
3. Initial proofing prefers an attended practice relationship. Later approved
   remote attended, accredited federated or document-verification methods may
   produce proofing evidence, but none is enabled here.
4. Passkeys are the preferred phishing-resistant authenticator. The account
   must support multiple authenticators, inclusive alternatives and explicit
   recovery; a synced passkey, device-bound passkey, physical key or password
   manager is a patient choice, not a product mandate.
5. Email is not an out-of-band authenticator. SMS, voice and encrypted messaging
   possession may contribute only to an explicitly lower assurance or recovery
   combination; they never silently satisfy a stronger action.
6. The backend owns a typed, expiring interaction session. Neither a channel
   transcript nor model/provider memory owns conversational authority.
7. A displayed candidate is not reserved. A selection is proposal-only. A
   confirmation challenge is single-use, transaction-bound and non-authoritative
   until the command plane freshly rechecks principal, practice, proxy scope,
   assurance, proposal evidence, source generation and availability.
8. Transport deduplication and command idempotency are distinct. Delivery or
   webhook receipts are not appointment receipts.
9. Patient, parent, guardian, carer and future delegated software client are
   distinct principals with exact practice/patient/action grants. Credentials
   are never shared.
10. Missing, stale, ambiguous, cross-practice, downgraded or recovery-affected
    authority denies without confirming whether a patient record exists.

## Frozen evidence and implementation boundary

Only newly authored files explicitly named below and the active-operation latch
may change before the contract passes. Existing application, router, schema,
database, migration, frontend, Office, Diary, provider, deployment and API
runtime files are read-only.

| Existing source | Posture | SHA-256 |
|---|---|---|
| `orchestration/api_spine_adr.md` | read-only | `d0fa77aec371d634284f81bf1fd6cfd49bb5a52fbe14003a17c5e35dcaf0283e` |
| `orchestration/api_spine_programme.md` | read-only | `5532f9ccc0efc326d34bc0d33f9f650d3f5322f8f4b22271fc8970b0dad31946` |
| `orchestration/bernie_release_gates.md` | read-only | `3b0fc2674eea7df2f28520dda5e101403a0b7166f644f820ecc16f6ed9a4e943` |
| `docs/raisa-practice-context-fabric-direction.md` | read-only | `3dc267eec7e0e7011a021b56d8db075355cff44d0761904105e2727ef2392642` |
| `docs/bernie-identity-verification-readiness.md` | read-only | `366da6d82053082f714e7f25622be42ebf4943447c122d3af1469c9f43dd448c` |
| `docs/api-spine/security/permission-matrix.yaml` | read-only | `00f2792bcd5b555942183022307dffae1f0e991671787f32268ac9f99abdf945` |
| `docs/api-spine/openapi/application-identity-federation-session-bridge.yaml` | read-only | `2851efdb8437c867b7134c6d688f1afb92b7ae59f68a3e73109eed449bb0f306` |
| `orchestration/continuity/raisa-real-identity-microsoft-federation-boundary/federation-policy.json` | read-only | `c4fdcdfda9cdbc476f05608445f92b23193ebbacbf025e2ecc832fad069e3f48` |
| accepted status-confirm closeout and Sol acceptance | read-only | `69c3bbe767118815663ea4cd1417148be17a83abf1c0203e663ef47571aed528` / `6c9a5b3bb8403bbe100e09d3628d0444c91e029334bf8de7a0acab4dcd19672b` |

Protected evidence paths remain excluded and must not be enumerated.

## Exact owned outputs

- this frozen plan;
- `docs/raisa-channel-neutral-patient-interaction-foundation-architecture.md`;
- `docs/security/raisa-channel-neutral-patient-interaction-foundation-threat-model-delta.md`;
- one closed canonical architecture contract, Draft 2020-12 schema,
  authored-synthetic message packet and sanitized acceptance evidence under
  `orchestration/continuity/raisa-channel-neutral-patient-interaction-foundation/`;
- `scripts/raisa_channel_neutral_patient_interaction_foundation_acceptance.py`;
- focused contract and plan tests;
- timestamped closeout, Sol acceptance and Yuri lay/technical summary;
- only the bounded Continuity/Compass, implementation-plan, live-baton and
  active-operation-latch updates needed to record acceptance; and
- preplanning, precommit and pre-push receipt/state pairs, left untracked.

No application runtime, OpenAPI route, GraphQL schema, permission-matrix allow
entry, model, migration, frontend or channel connector may change.

## Required closed message types

The schema must close and examples must validate exactly these eight message
families:

1. `PatientIdentityBinding`
2. `IdentityAssuranceDecision`
3. `PatientInteractionEnvelope`
4. `PatientDiaryProjection`
5. `PatientSelection`
6. `PatientConfirmationChallenge`
7. `PatientCommandOutcome`
8. `PatientRecoveryCase`

Future delegated assistants are represented by a static exact-scope policy in
the canonical contract, not an enabled token or ninth runtime message.

## Assurance ladder

| Level | Maximum posture in this architecture |
|---|---|
| `public` | generic, minimized availability only; no patient recognition claim |
| `recognized_channel` | neutral continuity or notification; no patient record or command authority |
| `verified_patient` | future proofed subject plus accepted authenticator; own-practice, own-patient scoped interactions only |
| `stepped_up` | future transaction-bound stronger assurance for sensitive identity, delegation or command changes |
| `recovery_restricted` | no ordinary command authority while recovery is unresolved; reproofing or independently combined recovery evidence required |

The action policy is default-deny. A stronger action may demand a stronger
level, but no adapter or model can raise assurance.

## Channel capability boundary

The canonical matrix must cover SMS, email, thin web, WhatsApp, voice and a
delegated assistant. Each remains `future_closed`; each may later render only
the intersection of its capability and the backend projection. Plain text is
the universal fallback. Thin web is the future secure escape hatch for richer
display and phishing-resistant authentication, not a second source of truth.
Dynamic email, messaging buttons and voice are progressive renderers only.

## Recovery boundary

Recovery must support multiple bound authenticators, independent notification,
revocation of old sessions/authenticators, bounded cooling-off for sensitive
changes and attended or otherwise approved reproofing. Knowledge of health or
demographic attributes is forbidden as proof. Recovery evidence cannot be
reused as ordinary command confirmation, and a recovery flow cannot establish
a parent/guardian/carer grant.

## Deterministic scenarios

| ID | Required proof |
|---|---|
| `PIF-S01` | canonical contract and all eight closed message schemas validate |
| `PIF-S02` | record matching, proofing, authentication, authorisation, delegation and recovery remain distinct |
| `PIF-S03` | passkey-first posture supports multiple authenticators and no vault requirement |
| `PIF-S04` | all six channels remain future-closed, untrusted and without command authority |
| `PIF-S05` | generic availability, recognition, verified interaction, step-up and recovery restrictions form a monotonic default-deny ladder |
| `PIF-S06` | projections expire, carry source revision, minimize disclosure and never reserve a candidate |
| `PIF-S07` | selections remain proposal-only and confirmation challenges remain single-use, current-authority-bound and non-authoritative |
| `PIF-S08` | command outcomes distinguish commit/replay from stale, blocked and unavailable results and require backend receipt/audit references for successful effects |
| `PIF-S09` | transport identifiers never substitute for command idempotency or audit receipts |
| `PIF-S10` | recovery cannot use demographic/health knowledge, silently downgrade assurance or omit independent notification and revocation |
| `PIF-S11` | proxy and delegated-agent policy is exact-scope, expiring, revocable and never shares a patient credential |
| `PIF-S12` | at least 60 hostile mutations fail closed and evidence contains no patient, credential, channel-address, message-body or token value |

## Acceptance

Pass only if:

- both the canonical contract and schema are closed and valid;
- the exact eight authored-synthetic messages validate;
- every invariant and all twelve scenarios pass;
- at least 60 independent hostile mutations are rejected;
- focused tests, API Spine artifact tests, the canonical fast profile, Ruff,
  maintained-source compilation, Diary JavaScript syntax and Git whitespace
  pass; and
- Git proves no unowned tracked file changed and all pre-existing untracked
  files remain preserved.

Evidence may retain only schema/message names, decisions, reason codes, counts,
digests and closed-boundary booleans. It must not contain real or synthetic
patient identifiers, contact addresses, message bodies, authenticators,
credentials, tokens, recovery secrets, document values, command payloads,
provider output or unrestricted exceptions.

## Claim, recovery and next-work boundary

Passing proves only a provider-free, unmounted, authored-synthetic architecture
contract. It does not prove identity proofing, passkey usability, patient
recognition, SMS/email/WhatsApp/voice delivery, delegated agents, a browser
client, a booking command, patient privacy compliance, representative-user
usability, deployment or production.

Mechanical contract defects may receive a narrow local repair. A need to select
an identity provider, central-versus-practice account topology, biometric or
document-proofing vendor, recovery service level, real channel/provider,
product/patient data, command policy, deployment or production posture is a
genuine future decision and remains closed.

After acceptance and task-branch publication, the previously planned bounded
visible native Diary status-confirm tranche becomes next again. It will consume
the same channel-neutral projection/confirmation principles but remains a staff
surface; this foundation does not turn Reception One into a patient client.

No protected evidence, patient/clinical/product data, provider call,
credential/IAM change, network, database/source, executable tool, command/write,
deployment, production, release, Pages or protected-ref movement is authorised.
`docs/branding/` and every unrelated untracked file remain preserved; staging is
explicit-path only.
