# Practice Context Fabric intent-shaped temporal retrieval rehearsal design

Date: 2026-08-06

Status: provider-free authored-synthetic design

## API Spine classification

This tranche is an unmounted pure read-context protocol. It adds no API surface.
GraphQL remains the future read plane, REST/OpenAPI remains the command plane,
and no context result can authorise or acknowledge a mutation.

## Capability boundary

The workspace that presents a Bureau is not trusted input. Reception One and
Clinician One may each compose several independently granted Bureaus, and the
same Bureau may appear in both. The authority binding—not the brand, screen or
occupational label—decides which read components are available. Each future
Consultant, request/referral, medicines/prescribing and billing/claims command
retains a separate capability check, proofreader and human/professional gate.

## Typed objects

### `IntentRetrievalCandidate`

A sealed, non-authoritative proposal containing a candidate id, requesting
Bureau code, one closed intent code, requested component codes, requested field
profiles, an optional bounded temporal coordinate, maximum component/frame/byte
limits, an ambiguity limit, issued-at time and constant read-only/no-command
posture. It has no identity, tenant, role, practice, location, session,
retention, provider, prompt, patient or arbitrary query field.

### `IntentRetrievalAuthorityBinding`

Backend-owned and sealed. It binds the principal, practice, location, session
and session generation; allowed requesting and contributing Bureaus; purposes,
intents, components, field profiles and bilateral-sharing pairs; valid time,
expiry, policy version, freshness, cardinality and byte ceilings; and constant
`read_only: true`, `provider_authority: false`, `command_authority: false`.

### `IntentTemplate`

A code-owned mapping from one intent to exact required and optional components,
purpose codes, permitted ambiguity handling and field profiles. The mapping also
translates the accepted component vocabularies explicitly:

| Fabric concept | Accepted component vocabulary |
|---|---|
| Rayleen current operational context | `RAYLEEN` / `CURRENT_OPERATIONAL_AWARENESS` |
| Rayleen recent collective work | `rayleen` / `recent_practice_work` |
| Rayleen historical context | `RAYLEEN` / `TEMPORAL_OPERATIONAL_RECALL` |

No generic lowercase/uppercase conversion is accepted.

### `IntentRetrievalPlan`

The deterministic intersection of candidate, template and authority binding.
It records exact required and admitted components, field profiles, effective
time, bilateral-sharing decisions, disclosure ceilings, reduction reasons and
the digests of all inputs. It cannot widen any upstream grant.

### `RetrievalComponentEnvelope`

A sealed adapter around one already proofread upstream component. It records the
component code, originating Bureau, purpose, shareability, exact upstream packet
and frame-set digests, source revisions, expiry, session/binding coordinates and
the minimum projected content. The adapter never fabricates source truth.

The Current component remains atomic: its accepted four frame types are carried
together because their coherence proof depends on the complete set. A field
profile may narrow each frame's content, but selection cannot silently drop a
source.

### `IntentContextFrameSet`

An immutable output containing canonically ordered admitted components, exact
provenance and binding digests, omission/reduction codes, an ambiguity state,
safe alternatives when applicable, assembled/expiry times, and constant
read-only/no-command posture. The output has no answer text and no command.

### `IntentRetrievalProofreaderTrace`

The proofreader independently rebuilds the template, plan, component selection,
field projection, ambiguity result, temporal checks and digest tree from the
same packet. It releases all or nothing.

## Selection and minimisation

Candidate component requests are first clipped to the fixed intent template and
then to backend authority. Required components unavailable after intersection
produce uniform `NOT_AVAILABLE`. Optional components may be omitted with a safe
reason code. Counts about rejected cross-practice or cross-Bureau material are
never returned.

Field profiles are closed code-owned allowlists. They may remove fields from an
accepted upstream frame but cannot add, rename or infer values. Maximum
components, frames, alternatives and bytes are the minimum of candidate,
template, authority and upstream ceilings.

## Temporal release boundary

Historical selection retains both `valid_at` and `known_at`. Current and Memory
components must be unexpired and `CURRENT`. A temporal state of
`REASSEMBLY_REQUIRED`, `EXPIRED` or `REVOKED` blocks its associated Current set.
The retrieval engine executes no reassembly. A fresh result would need a new
frame-set digest and a new complete proofread packet.

## Ambiguity

`RECENT_OPERATIONAL_REFERENCE` operates only on admitted opaque authored-
synthetic candidates. One match may be released as context; two or more equally
ranked matches produce canonically ordered `ALTERNATIVES` plus a discriminator
code. The engine never guesses a person, patient, appointment or event. Real
identity resolution is deferred to patient/privacy-authorised descendants.

## Cross-Bureau rule

Private application-session state is never transferable to another Bureau.
Recent collective work may cross only when the binding contains the exact
requesting/contributing Bureau pair and purpose. A cross-Bureau use creates a
new typed retrieval packet with provenance; it does not copy a private
transcript or inherit the originating Bureau's authority.

## Non-authority statement

The engine selects no provider prompt, invokes no model, reads no source and
executes no command. It demonstrates only deterministic assembly and
proofreading of already accepted authored-synthetic components.
