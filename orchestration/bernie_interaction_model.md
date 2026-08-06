# Bernie — Interaction Model and Pipeline Architecture

> Companion to [`resource_admin_bernie_tool_design.md`](resource_admin_bernie_tool_design.md),
> which covers the tool layer, safety, audit, and command/proposal contracts.
> This document covers the *interaction model*: how Bernie receives input, what
> the LLM does vs what deterministic code does, and the persona/safety discipline.
> Captured from architectural discussion 2026-06-25.

---

## Persona

Bernie is named after Dr Shera's former head receptionist — a real person who
knew the practice, knew the patients, and made reception flow effortlessly. The
name is intentional: it sets a standard of competence, warmth, and institutional
knowledge, not a novelty chatbot. Bernie's job is to let reception staff move
faster than they could alone, not to replace their judgment.

**Rayleen** is a related but distinct present-tense operational intelligence.
The earlier auto-arrival daemon remains, at most, one deterministic observation
source; the description of Rayleen as purely automated and server-side is
superseded by the 2026-08-04 model-required Bureau architecture. Bernie focuses
on prospective scheduling. Rayleen focuses on arrivals, waiting states, queue
flow and intent-projected waiting-room views. Both require an approved provider
model for intelligent dialogue and candidate formation, and both share the
same deterministic Diary evidence, policy and command primitives without
sharing authority.

---

## Three Input Lanes

All three lanes converge on a single constraint-object pipeline. The lane
determines *how* intent arrives, not *what happens to it* once it arrives.

### Lane 1 — Text Prompt

Typed input from a dedicated Bernie chat panel. Deliberate and composed —
reception staff have time to phrase a request. Useful for complex queries,
bulk operations ("link all provisional patients for today"), and audit review.
This is the development-and-fallback surface; it is also the debugging surface
for proving the pipeline before voice is added.

### Lane 2 — Ambient Listener Window

A click-on / click-off listen window. When active, Bernie monitors audio
passively. The receptionist does not need to address Bernie directly; Bernie
hears the phone call or counter conversation and surfaces relevant proposals
without interrupting. Staff confirm or dismiss.

This lane is conversational in register — Bernie hears natural speech, not
composed commands. The constraint-object boundary is more important here
because raw utterances are noisier and Bernie must not guess at clinical or
identity details.

### Lane 3 — "Hey Bernie" Wake Word

Interruptive and urgent. The receptionist is in the middle of something and
needs an answer fast ("Hey Bernie, is Margaret free at 11?"). Short queries,
immediate response. The register is terse — no preamble, one clear action or
answer.

This lane requires the fastest path from audio capture to constraint object.
If a query produces ambiguity, Bernie should surface it as a brief spoken
confirmation request rather than a text worklist.

---

## The Pipeline: Where Provider Model Sits vs Where Code Sits

The key discipline is that **the provider model is mandatory as a translator,
not authoritative as an oracle**.
It converts natural language (from any lane) into a typed constraint object.
Everything after that constraint object is deterministic.

```
[Lane 1: text]  ─┐
[Lane 2: ambient]─┼──► LLM: intent parsing ──► CONSTRAINT OBJECT ──► deterministic slot search
[Lane 3: hey]   ─┘                                                        │
                                                                           ▼
                                                                   LLM: present options
                                                                           │
                                                                           ▼
                                                                   staff confirmation
                                                                           │
                                                                           ▼
                                                                       write (API)
```

### Stage 1 — Intent Parsing (LLM)

The LLM's job is to extract:
- **action type** (find slot / create booking / check in / take message / etc.)
- **resource** (practitioner, appointment type, duration)
- **patient identity** (name, DOB, phone — for search, not for assumption)
- **temporal constraint** (next week, 11am, before lunch)
- **confidence flags** (anything ambiguous, missing, or potentially misheard)

Output is a typed constraint object — a validated schema, not free text.
The LLM is NOT allowed to invent field values. Missing required fields →
`blocked` tier; ambiguous fields → surfaced as warnings.

### Patient Recognition vs Details Verification

Use two separate concepts:

- **Patient recognition** means the practice can recognise which patient record
  the receptionist is talking about for the purpose of preparing or confirming a
  booking. A unique current-register name match can be enough for ordinary
  booking flow, especially when supported by diary context, caller context, or
  other practice-local evidence.
- **Patient details verification** means Medicare Online, HI/IHI, OPV/PVM, or
  staff checking details such as Medicare/card data. This is important, but it
  is a separate workflow. It may occur at booking time when available, but it is
  not a mandatory precondition for every ordinary appointment booking.

The old rule "never guess at a patient's identity from a name alone" is now too
coarse. The better rule is:

- do not silently link ambiguous or low-confidence patient identity;
- do recognise a unique current patient record when the evidence is strong
  enough for reception workflow;
- keep details verification as a separate statechart and audit concern;
- reserve "confirmation" for confirming the booking itself.

### Patient-Specific Context Frame

After patient recognition, *bernie* should receive a compact deterministic
context frame for that patient rather than a broad diary dump. The first
production shape should be equivalent to:

```yaml
type: patient_booking_context
patient_id: "<uuid>"
generated_at: "2026-07-02T10:00:00+10:00"
lookback_days: 60
lookahead_days: 730
recent_bookings:
  - appointment_id: "<uuid>"
    date: "2026-07-02"
    start_time_local: "09:30"
    practitioner_id: "<uuid>"
    practitioner_label: "Alex Shera"
    status: "Booked"
future_bookings:
  - appointment_id: "<uuid>"
    date: "2026-07-13"
    start_time_local: "14:45"
    practitioner_id: "<uuid>"
    practitioner_label: "Alex Shera"
    status: "Booked"
derived_signals:
  usual_practitioner_id: "<uuid>"
  usual_practitioner_label: "Alex Shera"
  existing_future_follow_up: true
  existing_future_follow_up_summary: "Billy already has a follow-up with Dr Alex Shera on 2026-07-13 at 14:45."
```

This is the useful middle path: richer than a single selected appointment, much
smaller than dumping the whole diary, and easier to test. Availability is still
resolved by deterministic slot-search APIs, not by the LLM.

### Raisa Practice Context Fabric

The patient-specific frame is one early thread in the accepted
[`Raisa Practice Context Fabric`](../docs/raisa-practice-context-fabric-direction.md).
The longer-range interaction model should let a Bureau propose a typed
`ContextNeed` from the user's request—for example the current day's Diary, the
waiting room now, a bounded prior waiting-room state, or recent events involving
the current practice. Deterministic backend policy then narrows that request by
principal, role, practice, location, purpose, source, fields, temporal window,
freshness and result count before assembling an expiring `ContextFrameSet`.

This permits natural questions such as “Who was the person called George who
came in this morning and was attended by Priya?” without treating a provider
model as practice memory. The assembler may return a small, purpose-scoped
candidate frame with explicit match evidence and ambiguity; Bernie or Rayleen
may explain it or ask for a discriminator. Neither may query a global Diary
dump, silently assert identity, disclose unrelated patients or turn the frame
into write authority.

The model, proofreader and any intent projection must be bound to the same
admitted frame-set digest and source revisions. Committed events are signals for
fresh authorised reads, historical states require explicit temporal storage and
retention policy, per-user session state remains separate from shared recent
practice context, and a cross-Bureau handoff is a new typed scope decision—not
an informal transcript transfer.

The first provider-free Fabric/Memory contract, Current operational weave,
patient-free temporal weave and intent-shaped temporal retrieval rehearsal are
accepted. The Current weave composes exact authored-synthetic Diary,
waiting-room, active-practitioner-directory and private application-session
read shapes into one expiring same-packet-proofread bundle without adding a
product route or source. The temporal weave proves that relevant sealed event
metadata retires rather than patches that immutable bundle, preserves the
committed invalidation checkpoint, rejects continuity gaps and stale
reassembly, and keeps bitemporal snapshots outside current-truth authority.
The retrieval rehearsal proves that five closed intents select only the
minimum granted Current, recent-work and historical components, with explicit
vocabulary mapping, bilateral Bureau scope, ambiguity and upstream/same-packet
proofreading. The authored-synthetic model-required intent-shaping descendant
now also passes after one source-reviewed Sydney Vertex primary proposed the
exact closed comparison intent and deterministic code rebuilt and admitted the
parent retrieval packet. The provider-free unmounted Rayleen A4 waiting-room
source adapter is now in exact-head independent-veto repair. It consumes only
a completed authored-synthetic `emr4.waiting_room_context_frame.v1`, applies
the accepted binding/grant and backend-issued opaque aliases, and emits one
Current source envelope without invoking or refreshing the read, watching
changes, mounting a route or accessing real product data. Its corrected
boundary separates closed result/evidence schemas, recomputes the complete
expected result from authoritative inputs at one deep-copy handoff and
supports independently granted waiting fields before the unchanged parent projection.
Real event transport,
historical persistence, patient/product data, product retrieval, runtime and
command authority remain separately closed.

### Date Context Resolution

If the receptionist omits an explicit date, *bernie* should not default to
today merely because a time is present. Date resolution is a deterministic
state transition over typed context frames:

1. use the selected proposal/provisional booking date if one exists;
2. otherwise use the selected diary appointment date if one exists;
3. otherwise use the visible diary page date;
4. otherwise ask, in everyday language, which day to check.

This supports natural reception flow. If the diary is open on Thursday and the
receptionist says "book Junior Atkinson at 11:15 with Dr Shera", *bernie* can
assume Thursday and proceed. If no diary/page context is available, *bernie*
asks instead of guessing.

This rule belongs to deterministic workflow code, not the LLM prompt. The LLM
may extract the time, patient, practitioner, and explicit date words; the
transition table decides how omitted world-state details are supplied.

### Stage 2 — Deterministic Slot Search (no LLM)

Given a constraint object, `find_slots` runs against the backend using real
roster, schedule, conflict, and break data. The LLM is entirely out of this
loop. The result is a ranked list of candidate intervals with warnings
(soft break overlap, adjacent booking, provisional patient, etc.).

This is the most important discipline: **the LLM must never be in the loop for
search or availability reasoning**. Availability is a backend fact, not a
language model inference.

### Stage 3 — Presenting Options (provider model required)

For multi-result queries, the provider model presents options in natural language:
"Margaret has 15 minutes free at 10:30 or 2:15, and a 30-minute slot at 4pm."
This is advisory framing only — it does not change the typed proposal or the
autonomy tier.

For a simple query, the provider model still participates in the intelligent
interaction and explains the proofreader-admitted backend result. The ordinary
Diary UI may display the same deterministic fact independently, but that is a
manual/product control rather than a substitute Bernie intelligence. If the
provider model is unavailable, Bernie reports unavailable and does not present
a heuristic or templated response as an equivalent agentic completion.

### Stage 4 — Staff Confirmation

Any proposal-tier action requires explicit confirmation before writing.
See `resource_admin_bernie_tool_design.md §Formal Command / Proposal Layer`
for the confirmation flow and audit requirements.

The historical `execute_with_report` concept does not grant an immediate-write
shortcut. Every mutating action uses its current typed command and authority
policy, including human confirmation where required, followed by deterministic
readback. Model participation neither removes nor supplies confirmation.

### Stage 5 — Write (API)

Bernie calls the same FastAPI endpoints as the UI. No privileged path,
no direct ORM access, no raw SQL. RBAC enforced at the route layer.

---

## The "Smart Word Processor" Framing

The LLM's value is not in knowing the answer — it is in **translating between
the language humans use and the typed vocabulary the system understands**.

A receptionist says: "Can you find me something for Mrs Thompson next Tuesday
afternoon, she needs a longer appointment."

The system understands: `{ practitioner_id: ..., duration_minutes: 30,
date_from: "2026-07-01T12:00", date_to: "2026-07-01T17:00", ... }`

That translation is the LLM's entire job at the input stage. The search,
the conflict check, the break avoidance, the roster lookup — all deterministic.
The LLM adds nothing to those; it would only add noise and unpredictability.

This framing also defines what Bernie should never do:
- Never silently link ambiguous, low-confidence, or duplicate patient identity
  (use recognition/search flow and staff selection)
- Never infer availability from context clues (use `find_slots`)
- Never assume a clinical or billing field (pass `blocked` or ask)

---

## Persona Discipline

Bernie's persona serves a safety function, not just a UX function.

A named persona with a known role is easier to calibrate than a generic
"assistant". Staff learn what Bernie can and cannot do. The name sets the
expectation: "Bernie is the receptionist copilot, not the doctor's assistant,
not the billing engine."

Key constraints that flow from the persona:

1. **Bernie does not practice medicine.** Clinical content in appointment notes,
   messages, or patient queries is passed through untouched, not interpreted.
   If a voice utterance contains clinical detail, Bernie extracts only the
   scheduling/administrative elements and ignores the rest.

2. **Bernie does not impersonate staff.** Actions are attributed to the
   authenticated staff user who invoked Bernie, not to Bernie itself. Audit
   logs name the staff user + Bernie's session ID.

3. **Bernie is not patient-facing.** No patient-facing Bernie variant until the
   internal tool layer, audit model, rate limiting, and identity proofing are
   mature. The same pipeline could serve a patient self-booking portal later,
   but that is a separate client with different safety requirements.

4. **Bernie hands off, not overrides.** When Bernie cannot act safely — ambiguous
   identity, policy conflict, clinical content requiring judgment — it surfaces
   the case to staff and stops. The `handoff_to_receptionist` tool exits cleanly.

---

## Multi-Lane Coordination

When the ambient listener is active and a text prompt arrives simultaneously,
the most recent explicit request takes precedence. Lane 3 ("Hey Bernie") always
interrupts the current lane and resets to a fresh query.

Each staff user has their own Bernie session, transcript, and confirmation queue.
Practice-level views may aggregate Bernie activity, but sessions are isolated.

Shared recent-practice context, when implemented through the Context Fabric,
does not weaken this isolation. It is a separate backend-owned, role- and
purpose-filtered read projection with bounded retention and provenance. A user's
private transcript is never promoted into collective practice memory merely
because it is recent.

## State Machine Memory And Clarification Turns

Bernie needs explicit state machine memory, not just a current prompt string.
Every user prompt, Bernie response, diary navigation, candidate selection, and
booking confirmation is a state transition. The session should remember the
facts that make later turns meaningful:

```yaml
type: bernie_session_memory
session_id: "<uuid>"
state: "candidate_selection"
visible_diary_date: "2026-07-03"
request_reference_date: "2026-07-02"
active_patient_id: "<uuid>"
active_practitioner_id: "<uuid>"
candidate_snapshot_id: "<uuid>"
selected_candidate_index: 0
staged_proposal_id: "<uuid>"
proposal_fresh: true
auto_preview_enabled: true
turns:
  - actor: staff
    kind: instruction
    text: "Make an appointment for Margaret Thompson after 3 tomorrow."
  - actor: bernie
    kind: response
    text: "I found times tomorrow afternoon."
```

The text box should become a new-turn input after Bernie responds. It should not
keep behaving as though the original prompt is the live request. Clarifications
such as "make it later", "use Friday instead", "cancel that one", or "try Nurse
Chen" should apply to the current session memory, candidate snapshot, selected
proposal, and visible diary page.

This also means UI controls belong in the statechart:

- `Refresh` keeps the Bernie panel open but clears or invalidates stale response,
  candidate, and proposal state.
- `Today`, `Prev`, `Next`, and date picker transitions update visible diary
  context and should clear or mark old proposals stale unless the active session
  explicitly owns a selected absolute slot.
- `Choose another time` returns to the existing candidate snapshot; it must not
  reinterpret relative words such as "tomorrow".
- `Confirm booking` consumes the current proposal and transitions to a terminal
  confirmed state with compact success copy.

The user-facing copy should be conversational and terse. Technical evidence,
raw fields, assumptions, and confidence details belong behind a Details or See
more disclosure.

## No-Slot And Existing-Booking Behaviour

If no slots are available, Bernie should not render "Bernie found these times".
The state should be direct:

```text
I could not find a free time with Dr Shera between 3:00 and 4:30 on Friday.
```

Then Bernie can offer clickable suggestions that become the next prompt or next
state transition, for example:

- `Try Dr Shera's next available time that day`
- `Try the same window with another practitioner`
- `Try Monday afternoon`

After patient recognition, Bernie should also use `patient_booking_context` to
notice existing appointments before offering new ones. If Margaret already has
appointments in the requested window, the useful response is not another blind
slot search; it is something like:

```text
Margaret already has appointments with Dr Shera tomorrow at 3:00 and 4:00.
Do you want another appointment as well, or should I change one of those?
```

This is not a broad diary dump. It is a compact patient-specific context frame
fetched after recognition.

## Limited Auto-Mode - Future Branch

For a very small practice, a future limited auto-mode may be useful: Bernie can
self-confirm only high-confidence, low-risk bookings, then place them in a
review-later queue for the practice manager. This is not the default mode and
must remain behind explicit practice configuration, audit, provenance, and hard
exclusions.

Auto-mode design constraints:

- disabled by default;
- practice-manager-only setting;
- only recognised current patients and known practitioners;
- no ambiguous patient/practitioner/date/time;
- no clinical triage, urgent symptoms, procedure bookings, or policy exceptions;
- every auto-confirmed action is reviewable and attributable.

The ordinary receptionist flow remains proposal plus human confirmation.

---

## Build Order

The existing `resource_admin_bernie_tool_design.md` recommends finishing
check-in, resource admin, and roster admin before adding a live LLM runtime.
This interaction model follows the same order:

1. **Lane 1 (text) only**, LLM calling typed tools, proposals surfaced as JSON
   — prove the pipeline before voice.
2. **Wake word / Lane 3** — short query / fast answer path once Lane 1 is stable.
3. **Ambient listener / Lane 2** — most complex audio context; build last.

Do not add voice capture before audit logging and the proposal/confirmation
flow are solid. A voice path with no audit trail is not acceptable for a
clinical environment.

---

## Open Questions (not yet decided)

- **Where does audio capture live?** Browser microphone in a dedicated Bernie
  panel (reuses Command Centre audio infrastructure) or a headset integration?
  First build: browser microphone, same pattern as AI Scribe.
- **Wake word implementation?** Client-side keyword detection (fast, offline)
  or send all audio and detect server-side (more accurate, higher latency/cost)?
  Decision deferred until Lane 1 is running.
- **Shared confirmation queue for busy reception?** If two receptionists both
  have Bernie active, can they share a confirmation queue for the same
  appointment? Default: no — each session is independent. Shared task workflows
  are a deliberate future design, not an assumption.
- **Transcript persistence?** Bernie transcripts are a clinical environment audit
  artifact. Retention policy and storage need practice configuration, not
  hard-coded defaults.
