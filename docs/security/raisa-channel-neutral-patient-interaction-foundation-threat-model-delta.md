# Threat-model delta — channel-neutral patient interaction foundation

Date: 2026-08-13

Timestamp: 2026-08-13T14:37:36+10:00 (Australia/Brisbane)

Status: architecture-only, provider-free and unmounted

Parent boundaries: EMR4 API Spine, shared application-authentication boundary,
Practice Context Fabric, AES-C0 containment contract and accepted appointment
proposal-confirm command path

## Scope

This delta covers the static identity, assurance, recovery and channel-neutral
interaction grammar for future patients. No public route, patient account,
identity provider, passkey, message channel, product data, command, database or
runtime exists in this tranche.

## Assets and trust boundaries

Future protected assets include the identity subject, practice/patient link,
authenticator and channel bindings, proxy grants, interaction session,
projections, confirmation challenges, recovery state, command receipts and
audit evidence.

Every external channel and its content is outside the trust boundary. The
backend identity/assurance kernel, Context Fabric and REST command plane are
separate trust boundaries. A channel adapter may normalize input but cannot
cross any of them by assertion.

## Threats and frozen controls

| Threat | Failure mode | Frozen control |
|---|---|---|
| Account or patient enumeration | Different responses reveal whether a patient, phone or email exists | Generic external outcomes, rate limits before runtime and no patient detail below verified assurance |
| Recycled number, SIM swap or port-out | Possession of a phone number is mistaken for the patient | Channel recognition ceiling only; no identity proof or high-assurance recovery from one channel |
| Shared or compromised mailbox/device | Another person sees projections or acts from an established channel | Minimum disclosure, neutral messages, expiry and step-up before patient-specific or consequential actions |
| Phishing or relay | Patient types password/OTP or follows a counterfeit confirmation | Passkey-first phishing-resistant authentication; email is not OOB authentication; manual OTP does not raise assurance silently |
| Forwarded or leaked secure link | Bearer link becomes patient or command authority | Short expiry, exact session/subject/audience binding, single use, no reusable credential and current assurance recheck |
| Transport replay | Duplicate webhook or reply creates duplicate booking | Transport dedupe remains separate from REST command idempotency and atomic receipt replay |
| Stale candidate race | Old email/SMS candidate is committed after availability changes | Projection is not truth or reservation; source revision and expiry; command-time authoritative recheck; loser receives refreshed projection |
| Cross-practice confused deputy | Identity or assistant grant from one practice reads or writes another | Exact current practice/patient binding and per-command scope recheck; no cross-practice implication |
| Proxy/guardian scope drift | Carer authority persists after revocation or applies to the wrong action | Distinct principal, exact patient/practice/action/expiry grant, current recheck and revocation |
| Delegated-assistant overreach | General chatbot receives EMR credentials or a generic command tunnel | Registered separate client, minimum audience-bound scope, PKCE, revocation, per-command confirmation, no patient credential disclosure |
| Recovery takeover | Support or fallback process becomes weaker than authentication | Recovery-restricted state, independently combined evidence or reproofing, session/authenticator revocation, notification, cooling-off and audit |
| Support social engineering | Attacker persuades staff using DOB, Medicare or appointment knowledge | Health/demographic knowledge is forbidden as proof; attended/repeated approved proofing and reason-coded procedure |
| Passkey sync-fabric recovery compromise | Cloud-account recovery exposes a synced passkey | Synced passkeys are not treated as infallible; multiple authenticators, notifications, revocation and reproofing remain available |
| Webhook forgery | Fake messaging-provider callback injects a patient selection | Future integration principal/signature or mTLS, idempotency, untrusted-input label and backend session correlation required |
| Prompt injection from message content | Email/SMS/voice text instructs a model or tool to bypass policy | Content remains untrusted candidate; AES admission, closed schemas, deterministic proofreader and no model-to-command authority |
| Notification over-disclosure | Lock-screen, shared inbox or transcript exposes PHI | Neutral/minimized asynchronous content; no clinical reason or direct identifier in transport event; thin-web handoff for sensitive display |
| Transcript/provider memory authority | Channel or model remembers stale state and acts on it | Backend owns typed expiring session; fresh ContextNeed/FrameSet; transcript and provider memory are non-authoritative |
| Dynamic-email/client inconsistency | Unsupported client hides safety or confirmation semantics | Plain-text universal fallback; dynamic cards are optional renderers; same backend confirmation contract |
| Denial-of-service and recovery lockout | Rate limits or recovery abuse block the real patient | Bounded risk controls, assisted practice path and non-digital exception required before runtime |
| Audit becomes a secondary sensitive store | Logs copy addresses, message bodies, credentials or health values | Opaque references, closed reason codes and minimized evidence; explicit forbidden-field list |

## Security invariants

- No identifier, demographic field, appointment knowledge or channel address is
  an authenticator.
- No channel, adapter, event, model output, projection, selection or challenge
  is command authority.
- No stronger assurance results from fallback, model interpretation or adapter
  assertion.
- No recovery proceeds as an ordinary authenticated session.
- No success exists without the authoritative command's atomic audit and
  idempotency receipt.
- No event or transport receipt substitutes for a fresh authorised read or
  command receipt.
- No proxy or software-client delegation shares a patient credential.
- Missing, stale, ambiguous or cross-practice evidence denies without
  enumeration.

## Privacy considerations

Health information remains sensitive even when the immediate interaction is
administrative. The future programme requires a privacy impact assessment,
purpose limitation, retention and deletion policy, provider/channel contract
review, accessibility review and evidence that notifications remain safe on
shared devices.

Identity proofing must minimize evidence collection. DVS or another identity
service, if selected later, is a distinct consented integration and must return
only the proofing result needed for the binding decision rather than copied
identity-document material.

## Residual risks and later gates

The contract cannot determine real-world false acceptance/rejection rates,
passkey recovery usability, practice support burden, channel metadata exposure,
provider jurisdiction, guardian-law edge cases or accessibility outcomes.
Those require a future dedicated patient-identity/client programme, legal and
privacy review, representative patient testing and controlled runtime evidence.

No live identity proofing, channel/provider integration, real patient data,
route, database, command, deployment, production or release is opened by this
delta.
