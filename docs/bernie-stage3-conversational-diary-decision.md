# Bernie Stage 3 — Conversational Diary Workflow Decision

Date: 2026-07-19

Owner: GPT Sol Extra High

Decision status: `stage3a_authorized_stage3b_deferred`

## Reshaped purpose

Stage 3 should no longer ask only whether receptionists understand the current
booking interface. It should test the product hypothesis established by
`docs/bernie-conversational-diary-north-star.md`:

> Can reception staff safely understand and operate the supported living Diary
> through conversation and precise just-in-time visual projections, while a
> low-interruption twin correctly notices relevant committed changes, without
> requiring manual navigation of a fixed grid or entry into a form?

The visual Diary is the comparison, verification, and fallback surface. The
primary object of study is *bernie* as the conversational twin of current
backend truth.

Yuri has accepted intent-projected views and committed-event awareness as
foundational product properties. Stage 3 therefore tests their safety and
usability; it no longer treats their product value as an optional future
hypothesis. The controlling design is
`docs/bernie-intent-projected-event-aware-diary-design.md`.

## Accepted Stage 3 boundary

Run a supervised, local, synthetic, provider-disabled workflow study. Begin
typed-first so speech recognition and microphone privacy do not confound the
value of the conversational interaction. Explicit push-to-talk may be a later
bounded sub-stage only if separately authorized.

Yuri accepted the recommended six-decision package on 2026-07-19. Stage 3A is
therefore authorized as a Yuri-only formative study using functional
low-fidelity projections and deterministic committed-event fixtures. The exact
contract is `docs/bernie-stage3a-yuri-formative-validation-plan.md`.

Stage 3 is evidence-first. It may identify product corrections but does not
automatically authorize them, new appointment actions, providers, voice
capture, PII, production, deployment, release, or autonomous confirmation.
It also does not authorize an event broker, outbox migration, background
consumer, proactive UI runtime, or Claude Fable engagement.

## Frozen Stage 3 task population

Use deliberately synthetic patients, staff, practitioners, appointments, and
practice data. The frozen protocol should include at least:

1. find a named patient's future appointment described by relative time and
   preferred practitioner;
2. answer the date, time, location, practitioner, and status of an existing
   appointment;
3. explain a practitioner's bounded day or requested time window;
4. find suitable availability without creating an appointment;
5. reach a booking proposal with zero write;
6. explicitly confirm the already supported create proposal and verify the
   authoritative receipt;
7. recover safely from ambiguous patient, practitioner, date, or duration;
8. explain a stale, conflicting, duplicate, blocked, or replayed request; and
9. resume an interrupted retained session without repeating a committed action;
10. open and safely scope a practitioner/date/time projection, such as Dr
    Shera's afternoon appointments on Friday week;
11. construct a patient-centred upcoming-appointment projection, refine it, and
    return to the prior context;
12. surface a relevant post-commit Diary change at the appropriate attention
    level and offer the corresponding view without performing an action;
13. suppress unrelated, foreign-practice, uncommitted, and rolled-back changes;
    and
14. deduplicate replayed delivery and reconcile delayed, out-of-order, or
    superseded event signals through a fresh scoped read.

Each supported read task has a conversational route and an ordinary Diary/grid
route. Order is counterbalanced where practical so familiarity does not make
one modality appear artificially faster. Event-attention and authoritative
confirmation tasks retain their own exact evidence routes.

Event scenarios must use authored synthetic data and explicit evidence labels.
A deterministic fixture/intercepted signal is not a committed live-backend
event. Any future local-backend evidence must prove the source transaction
committed before delivery and that rollback produced no user-visible notice.

## Evidence to collect

Store only synthetic scenario ids, structured task outcomes, timings,
clarification counts/reason codes, projection identifiers, event-type/relevance outcomes,
interruption-level decisions, grid-fallback reasons, and participant feedback
approved by the protocol. Do not retain raw audio, naturally occurring
practice calls, real names, patient data, credentials, event free text, or
unrelated room conversation.

Measure:

- correct authoritative answer or task completion;
- time to answer, proposal, and confirmed receipt;
- completion without viewing or manipulating the grid;
- correctness, visible scope, reversibility, and usefulness of the
  intent-projected view;
- number and usefulness of clarifications;
- recovery from ambiguity, interruption, stale state, and replay;
- correct suppression of unrelated, unauthorised, uncommitted, rolled-back,
  duplicate, stale, and superseded events;
- relevant-notice precision, time-to-awareness, chosen interruption level,
  dismiss/snooze/mute behaviour, and interruption burden;
- comprehension of answer, proposal, confirmation, and committed receipt;
- accessibility, workload, confidence, and trust; and
- every reason the user chose or needed the visual Diary.

## Accepted Stage 3A gates and provisional Stage 3B defaults

Stage 3A uses absolute per-scenario safety and semantic gates:

- 100% correct practice scope and zero cross-practice disclosure;
- zero appointment writes before explicit confirmation;
- exactly one appointment/audit/command result after a successful confirmation;
- 100% participant recognition of answer versus proposal versus committed
  action in critical scenarios;
- 100% safe recovery from deliberately ambiguous Stage 3A tasks;
- 100% suppression of foreign-practice, uncommitted, and rolled-back event
  signals and zero duplicate user-visible effect on replay;
- 100% traceability of a proactive Stage 3A notice to a committed typed fixture
  plus a current authorised synthetic read;
- 100% correct scope and content for supported Stage 3A intent-projected views
  and relevant-event notices, with no identity ambiguity silently resolved;
- every failure classified as read/context, workflow, language, modality,
  usability, or safety rather than collapsed into a single score.

Stage 3A records grid-free completion and timing as formative observations. For
later Stage 3B, Yuri provisionally accepts at least 80% grid-free completion,
90% safe ambiguity recovery, 90% correct projection scope/reversibility, 90%
notice precision/recall, median conversation no slower than the grid, and a
non-blocking target of 20% faster appointment recall. Safety gates remain
absolute and cannot be weakened to satisfy usability thresholds.

## API Spine and authority

- Appointment, patient, practitioner, availability, session, permission, and
  audit questions use practice-scoped read models/context frames.
- GraphQL remains read-only and cannot invoke a provider or mutate the Diary.
- The existing REST confirmation command remains the sole Stage 3 appointment
  mutation.
- FastAPI/PostgreSQL owns identity, availability, conflicts, freshness,
  idempotency, the appointment write, audit, and receipt.
- *bernie* may interpret, clarify, explain, and propose; staff confirms.
- No response may rely on *bernie*'s remembered appointment state when a live
  read is available.
- A committed typed event is a signal that state changed, not a portable Diary
  record or command grant; before display, the consumer rechecks current
  authority and retrieves the current scoped read model.
- Event transport may be at least once, but stable event identity and aggregate
  revision must prevent duplicate user-visible effects.
- A proactive notice may refresh or offer an intent-projected view and may lead
  to a proposal; it cannot itself create, move, cancel, confirm, or otherwise
  mutate an appointment.

## Yuri's six-decision record

Yuri accepted the following package on 2026-07-19:

1. **Participants:** Yuri-only Stage 3A. A Stage 3B cohort of four to six
   representative reception staff returns for approval after functional
   corrections and the deferred visual-design tranche; external participants
   are not pre-authorized.
2. **Protocol:** authored synthetic tasks; typed/local/provider-disabled
   operation; functional low-fidelity projections; deterministic committed-
   event fixtures; a within-subject counterbalanced grid comparison; and a
   Stage 3A/visual-design/Stage 3B split.
3. **Thresholds:** the Stage 3A absolute gates and Stage 3B provisional defaults
   recorded above.
4. **Modality:** typed-only for Stage 3A and Stage 3B. Push-to-talk is a possible
   later Stage 3V decision; ambient listening is later again.
5. **Observation retention:** structured synthetic outcomes only, no raw audio
   or complete transcripts. Any later selected language requires explicit
   save, consent, de-identification, and deletion rules.
6. **Correction authority:** Stage 3A permits logged narrow corrections to read
   models, deterministic projection/language logic, copy, accessibility, and
   synthetic fixtures with affected-scenario reruns. Stage 3B is frozen during
   participant execution except for an immediate safety stop. Any new mutation,
   event runtime, provider, privacy, voice, or autonomous behavior returns to
   Yuri.

The Stage 3A preparation and Yuri-only run may proceed. Stage 3B and every
deferred boundary above remain paused.

## What Stage 3 may unlock

- If conversational value passes and gaps are read-model based: an
  appointment-first Diary read/context tranche.
- If one missing Diary action is repeatedly valuable: a separately authorized
  proposal/confirmation command tranche for that action.
- If deterministic language handling is the measured limiter: a bounded Access
  AI decision based on the exact observed capability.
- If explicit voice adds value: a privacy-first activation and local-discard
  feasibility tranche before ambient listening.
- A dedicated fluid UX meta-grid tranche when Yuri explicitly opens the Claude
  Fable, subscription, synthetic design-context, and cost decisions.
- A bounded committed-event runtime tranche ordered by the observed event
  families and interruption patterns. Event awareness is already foundational;
  Stage 3 determines safe implementation shape and priority, not whether the
  product should possess it.

Stage 3 does not itself authorize any of these branches.
