# Raisa demo-led appointment delivery plan v2

Owner direction: 12 October 2026. This is the single rolling-wave plan for the
combined Stage 1 booking and move milestone. It will be included as
`docs/programme/demo-led-appointment-plan-v2.md` in its exact reviewed publication
scope. Delivery stages do not replace programme gates.

## Starting subject and authority

Continue from independently accepted selected source
`5f56c186d144a173c576824fbfd8c08950b9f8a0`, tree
`a02967641318d3c140741cb70a43523a5001b6a5`, at
`C:/Users/there/EMR4-tools/g3-product-actual-v1`. Preserve the canonical checkout
at `4a3b0c3bb9dd02718ad39dac9b225be724ae98e0`. Exact comparisons of the appointment
router, schemas, model and Reception One runtime found no pending local changes
in that checkout; the accepted subject additionally contains the G2 post-delete
tenant readback correction. This is selected-file reconciliation, not a claim
of complete physical cleanliness or a whole-repository audit.

G2 remains accepted at `6fe523cdbd2e5a77c2746293269b2eaca52321ab`, with its
criterion-level qualifications and current/reused evidence preserved in the
existing checkpoint. The first offline G3 projection is accepted; full G3 is
not. The architecture review is advice, not executable admission. The owner has
resolved the former review pause and authorised the defined local synthetic
Stage 1, prospective minimum scope/profile amendments and finite renewals.

The existing executable profile is `G3_OFFLINE_APPOINTMENT_ENTRY`. It permits
only four exact offline product files. It does not admit an application, a
database, a browser, a command effect, or the new milestone by itself. Use the
supported bounded control transition, exact product admission, independent
review and ordinary recovery-branch publication route. Do not change the old
static/offline profile into an interactive one.

## Stage 1: two stories, one appointment core

Use fictional Alex Chen, Dr Rao and one fictional practice. The demo clock is
fixed and visibly labelled; next Thursday becomes an explicit calendar date
in Australia/Brisbane. No old example date is presented as today's date.

**Booking:** Alex describes a follow-up after 2 pm. The patient view clarifies
material ambiguity, displays allowed options and submits a request. Reception
One shows its constraints, source and demo identity status. A receptionist
reviews and deliberately confirms one current option through the existing
signed create proposal/confirmation path. Request submission is neither a
booking nor a reservation. Both permitted views display verified readback.

**Move:** authorised staff select the exact existing appointment and ask to
move it to an explicit afternoon time. Show before/after and unchanged patient,
practitioner, type, duration and location. Confirm the versioned time-only delta,
revalidate authority/current state/availability, update the same appointment,
and display committed readback with audit and command/result association.
The patient request acquires no staff authority or general appointment access.

Text and deliberate push-to-talk share versioned request/proposal state and
permissions. The demonstrator can connect request, book and move as one story;
independent seeded-move tests prevent a create failure masking move coverage.

### Reuse and concrete gaps

Reuse `app/routers/appointments.py` signed create/update proposals and
confirmation handlers, their physical mutation helpers, database exclusion
constraint, `app/services/appointment_idempotency.py`, existing session/freshness
bindings, audit and tenant-scoped readback. Route moves through signed update,
not raw compatibility PUT or independent delete/create. Distinct create and
move contracts remain distinct; shared mechanisms do not become a permissive
generic mutation.

The update proposal currently allows more fields than this move scope. Add a
closed time-only ingress and reject other deltas. Check the exact migration
and trigger before correcting entity version advancement. Distinguish entity
version, command identity, audit/event revision and list revision. The existing
GET/list APIs are staff-facing and do not constitute patient request scope.
`UserRole` has no patient role; demo request access therefore needs an explicit
server-bound capability/session, isolated from production configuration.

AR-02 requires an explicit source lifecycle mapping. Cancelled and unknown
statuses cannot become booked. AR-04 requires actor/source/freshness association,
bounded list completeness, timezone and version meanings, and actual rendered
checks. The accepted G3 validator/fallback remains useful, with read-only
authority and non-disclosing rejected output. AR-01/05 favour the existing
command service and small ordinary shared libraries. AR-03 clinical grounding
and logging concerns remain recorded; clinical redevelopment is outside this
appointment scope. AR-06 keeps developer grant mechanics outside patient and
staff interactions.

### Work packages and admissions

1. **G3 convergence enablement and source meaning.** Coordinator owns the exact
   bounded successor control/profile/scope and this plan; Sol/medium authors
   the directly relevant pure lifecycle, projection and create/move contracts,
   authored example and tests. Preserve prior profiles and acceptance bytes.
   Independent Sol/high reviews the exact scope/candidate and launch binding.
   Initial control changes are the two existing bounded policy libraries,
   state, gates, recovery overlay, AGENTS, one exact new scope and one direct
   entry test. Source preparation is inert until actual admission succeeds.
2. **Complete actual G3 obligations.** Demonstrate closed versioned intent,
   command, event and projection contracts; constrained grammar; meaningful
   risk/confirmation; provider-free read-only projection; invalid/stale/
   overprivileged rejection; equal safe fallback semantics. Rendered evidence
   needs its independently reviewed read-only local profile, not an offline
   equality claim. Record criterion contributions and gaps. Obtain required
   exact independent acceptance and supported G3-to-G4 transition before
   executable mutation integration. Do not declare broader gates passed from
   one component or owner scope.
3. **Seeded staff move first.** Integrate narrow time-only proposal/confirmation
   into the established appointment path. Reuse current-state and scheduling
   checks, including self-overlap exclusion. Add only necessary receipt/version
   corrections after source/migration inspection. Sol/medium owns the bounded
   implementation; coordinator integrates and serialises shared resources;
   independent reviewer checks authority, rollback boundary and exact subject.
4. **Thin durable request and staff-confirmed create.** Reuse suitable existing
   session/state facilities; add an additive request object/migration only if
   necessary. Preserve request, communication, appointment and command facts
   as different concepts. Patient session can access its request and options
   only. Staff uses the existing create command and current offers. Two patient
   scopes plus staff/other-tenant negatives are required. No new booking engine.
5. **Shared modality adapter.** Build text first, then deliberate press-to-talk,
   visible recording/stop/cancel, editable transcript, safe delayed-result
   handling and spoken/visible replies from the same validated result. Identify
   actual browser/runtime and approved processing route. Human microphone
   permission is required before capture. No interim/cancelled speech effects,
   recaptured playback or content-bearing telemetry. Unsupported/denied/audio
   failure keeps a usable text path. Deterministic/recorded mode is labelled;
   it does not establish live intelligence or genuine voice acceptance.
6. **Reusable patient and Reception One surfaces.** Keep the existing frontend
   stack. Show pending proposals separately from committed facts; add a compact
   Diary/list, truthful progress and optional inspectable 'How it works'.
   Controlled ambiguity, taken slot, changed/cancelled target, interrupted
   response and intelligence unavailable must change scenario state. Check
   keyboard/focus, readable live status, mobile/tablet and reduced motion.
   Build a separately labelled public-safe simulation adapter using shared
   contracts and conformance checks; hosting is a later decision. Simulated
   notifications are optional and explicitly labelled.
7. **Combined acceptance, publication and handoff.** Independently review exact
   final source and both journeys, correct concrete findings and publish through
   the existing candidate/lease/readback procedure. Deliver exact local launch
   instructions, booking/move scripts, permitted screenshots, tests/reviews,
   simulation/live distinctions, limitations and the next eligible task.

These are dependency-ordered engineering packages, not seven new gates. Show
useful intermediate progress; both journeys and the identified genuine voice
route are required for the finished Stage 1. Map G4's synthetic journey,
database exclusion, stale-mutation rejection, attributable tenant-safe actions,
two-surface equivalence, AI-off usability and current global-gate evidence.
Map G5's modality/surface, stale or revoked binding, accessibility/privacy and
fallback requirements when admitting voice. A delivery milestone does not
claim G4/G5 completion without their actual independent acceptance.

### Acceptance predicates

- Patient request appears at reception before booking; only authorised staff
  confirmation creates the intended appointment and verified permitted views.
- Move preserves appointment ID and all non-time fields; accepted time matches
  committed time; audit/result/version association and fresh readback agree.
- A post-claim conflict or injected transaction failure actually enters the
  claimed boundary and leaves original, audit/event and success records intact
  or absent as appropriate. Pre-transaction rejection is not rollback proof.
- Changed target, cancellation, availability or authority invalidates affected
  confirmations. Cancelled never becomes booked. No silent alternative time.
- Duplicate and lost-response reconciliation uses the existing command/result;
  one logical effect, changed-payload refusal and honest uncertainty are tested.
- Patient/staff and tenant/session negatives are enforced at the server;
  demonstrator role selection never creates a client-controlled authority claim.
- Normal and fallback expose identical authorised facts/restrictions; rejected
  data remains absent. Rendered accessibility is checked within stated scope.
- Spoken patient and staff-move requests use the identified permitted route;
  corrections, cancellation, denial and text alternative behave truthfully.
- Actual execution, recorded intelligence, simulation, publication and
  deployment remain distinct. No full-suite/hosted-CI PASS or unmeasured speed,
  accuracy, reliability or staff-time saving follows from focused evidence.

### Boundaries, finite work and recovery

One integration writer and one disposable synthetic database/schema at a time.
All product/frontend listeners bind loopback and use the separately reviewed
demo profile. No real patient/identity/clinical data, sealed holdouts, historical
diary, secrets, providers, public access, live messaging, protected refs or
deployment. Exact selected ordinary source only; preserve unrelated changes.

Initial pure control verification: one native launch and one focused run,
up to 300 seconds, no network/database/browser or spawned subprocesses, using
the existing 1 CPU / 1,024 MiB / 32-process offline envelope where enforceable.
Record actual enforcement limitations; do not claim hard caps without evidence.
Each later collection/integration/demo launch gets a finite reviewed binding
before execution. Reuse existing contained runtime and cleanup mechanisms and
their applicable resource ceilings, with exact endpoints/processes and output
limits; local availability does not enlarge overall spending. No separate
supervisory/grant framework is introduced. Justified finite renewals are the
coordinator's delegated decisions, including future IDs and resumed attempts.

Preserve old grants/outcomes. Two consecutive same-cause failures without
progress stop affected execution for diagnosis and independent review of the
changed approach. Preserve ambiguous results and reconcile the existing attempt;
do not replay blindly. Fail closed on missing state, drift, containment or
cleanup uncertainty. Stop/reconcile services at their reviewed boundary; no
unintended persistent runtime. Recovery is isolated source rollback or an
additive correction, never canonical reset or deletion of unique evidence.

Reserved owner decisions: genuinely ambiguous/protected material, new external
model/audio processing, live messaging/webhooks/accounts/DNS, public exposure,
real identity/data, paid services or spending expansion, protected/production
effects and destructive unrelated work. Identify the exact route, data,
privacy/retention/account/cost and independent work remaining for any decision.
No secrets in chat. Lack of a qualified voice route makes the milestone partial;
text/domain/UI work continues.

## Stage 2: email into the same request

At medium detail: one dedicated test address, controlled senders, fictional
plain text and no attachments feed the existing request lifecycle. Prefer a
thin inbound service adapter to a mail server or general inbox agent. Sender
address and webhook signature are not patient identity; scope request links
and reply disclosures accordingly. Record receipt, request, offer, booking,
notification sent and delivery as separate facts. Deduplicate redelivery and
handle rejection/delivery failure. Start with acknowledgement plus an expiring
scoped link if simpler than multi-turn email. Preserve staff approval.

Before implementation, compare only enough current official provider evidence
to recommend a small route, account/region/privacy and bounded cost. Provisioning,
credentials, DNS, webhook exposure and sending require their concrete decision.
Acceptance: one message creates one intended request, duplicate creates none,
reply/link reveals only allowed state, delivery failure is honest, and booking
still uses the shared command. Do not delay Stage 1 or choose a vendor now.

## Stage 3: continue one request across channels

Reply to offers, revise time preferences and continue in the patient view with
explicit request/account linkage, stale-offer handling and confirmation. Reuse
Stage 1 move machinery. Patient-initiated rescheduling and real SMS require
separate admitted identity/channel scope. Similar names or text do not link
identities. Refine from the working email journey, not a speculative backlog.

## Stage 4: showcase and operational qualification

Propose public-safe release after a suitable accepted milestone, with abuse,
privacy, usage limits and feedback; public release needs a separate decision.
Real patient authentication, record/family access, provider/data qualification
and operational readiness are later product work. Keep telephony, ambient
capture, prescribing/billing automation, general Memory Bank/Context Fabric,
additional Bureaus and Jev outside this committed milestone unless new evidence
and separately authorised scope justify them.

## Allocation and current status

`/root/g3_contract_refs`: retained GPT-6 Luna / low, literal pin/locator work.
`/root/g3_projection_author`: retained GPT-6 Sol / medium, bounded engineering
and pure source preparation. `/root/g3_entry_review`: retained GPT-6 Sol / high,
independent coupled scope/admission/safety judgment. Coordinator owns integration
and control authorship. Settings are the recorded supported spawn selections,
not backend telemetry or UI changes. No Astra children or nested delegation.

Current: owner scope recorded; exact source reconciliation and first scope
review in preparation. No new application/database/browser/provider execution,
mutation journey acceptance or Stage 1 completion is claimed. Use the existing
coordinator checkpoint for exact candidates, grants, results and next action.
