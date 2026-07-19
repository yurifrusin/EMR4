# Bernie Stage 3 — Conversational Diary Workflow Decision

Date: 2026-07-19

Owner: GPT Sol Extra High

Decision status: `decision_ready_not_authorized`

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

## Recommended Stage 3 boundary

Run a supervised, local, synthetic, provider-disabled workflow study. Begin
typed-first so speech recognition and microphone privacy do not confound the
value of the conversational interaction. Explicit push-to-talk may be a later
bounded sub-stage only if separately authorized.

Stage 3 is evidence-first. It may identify product corrections but does not
automatically authorize them, new appointment actions, providers, voice
capture, PII, production, deployment, release, or autonomous confirmation.
It also does not authorize an event broker, outbox migration, background
consumer, proactive UI runtime, or Claude Fable engagement.

## Proposed task population

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

Each task should have a conversational route and an ordinary Diary/grid route.
Order should be counterbalanced where practical so familiarity does not make
one modality appear artificially faster.

Event scenarios must use authored synthetic data and explicit evidence labels.
A deterministic fixture/intercepted signal is not a committed live-backend
event. Any future local-backend evidence must prove the source transaction
committed before delivery and that rollback produced no user-visible notice.

## Evidence to collect

Store only synthetic scenario ids, structured task outcomes, timings, typed
clarifications, projection identifiers, event-type/relevance outcomes,
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

## Recommended acceptance defaults

The exact thresholds remain Yuri's decision. A credible starting proposal is:

- 100% correct practice scope and zero cross-practice disclosure;
- zero appointment writes before explicit confirmation;
- exactly one appointment/audit/command result after a successful confirmation;
- 100% participant recognition of answer versus proposal versus committed
  action in critical scenarios;
- at least 80% correct grid-free completion across supported conversational
  tasks;
- at least 90% safe recovery from deliberately ambiguous tasks;
- 100% suppression of foreign-practice, uncommitted, and rolled-back event
  signals and zero duplicate user-visible effect on replay;
- 100% traceability of a proactive notice to a committed typed source plus a
  current authorised read;
- at least 90% correct scope and content for supported intent-projected views
  and relevant-event notices, with no identity ambiguity silently resolved;
- conversational lookup no slower than grid lookup overall, with a target of
  materially faster completion for appointment-recall tasks; and
- every failure classified as read/context, workflow, language, modality,
  usability, or safety rather than collapsed into a single score.

Safety gates are absolute; usability targets may return an accurately labelled
partial result rather than trigger threshold weakening.

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

## Stage 3 decision requested from Yuri

To start Stage 3, Yuri must explicitly decide:

1. **Participants:** Yuri-only formative validation or an approved small cohort
   of representative reception staff.
2. **Protocol:** approve the synthetic task population, intent-projection and
   committed-event scenarios, whether comparison with the ordinary grid is
   within-subject and counterbalanced, and whether Stage 3 is split around the
   deferred fluid UX design tranche.
3. **Thresholds:** accept or revise the proposed safety, grid-free completion,
   projection, event suppression/relevance, interruption, recovery,
   comprehension, and timing criteria.
4. **Modality:** recommended typed-first; decide whether explicit push-to-talk
   is excluded or separately admitted later.
5. **Observation retention:** approve structured outcomes only and decide
   whether any de-identified participant language may be retained.
6. **Correction authority:** evidence-only first, or permit narrowly necessary
   usability/read-model corrections while returning any new mutation,
   privacy, provider, or policy fork to Yuri.

Until those six points are accepted, the engine remains paused.

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
