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

**Rayleen** is a related but distinct concept already in the codebase — the
auto-arrival daemon that scans upcoming diary pages for unconfirmed names and
flags not-found ones bright red. Rayleen is purely automated and server-side.
Bernie is interactive and staff-facing. They are separate components that may
share tool primitives.

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

## The Pipeline: Where LLM Sits vs Where Code Sits

The key discipline is that **the LLM is a translator, not an oracle**.
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

### Stage 2 — Deterministic Slot Search (no LLM)

Given a constraint object, `find_slots` runs against the backend using real
roster, schedule, conflict, and break data. The LLM is entirely out of this
loop. The result is a ranked list of candidate intervals with warnings
(soft break overlap, adjacent booking, provisional patient, etc.).

This is the most important discipline: **the LLM must never be in the loop for
search or availability reasoning**. Availability is a backend fact, not a
language model inference.

### Stage 3 — Presenting Options (LLM, optional)

For multi-result queries, the LLM can present options in natural language:
"Margaret has 15 minutes free at 10:30 or 2:15, and a 30-minute slot at 4pm."
This is advisory framing only — it does not change the typed proposal or the
autonomy tier.

For simple queries ("is there a slot at 11?"), the LLM can be skipped; the
backend result is surfaced directly.

### Stage 4 — Staff Confirmation

Any proposal-tier action requires explicit confirmation before writing.
See `resource_admin_bernie_tool_design.md §Formal Command / Proposal Layer`
for the confirmation flow and audit requirements.

For `execute_with_report` tier actions (exact-match check-in, deterministic
provisional linking), Bernie writes immediately and reports the outcome.
These are low-risk, reversible, operationally routine.

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
