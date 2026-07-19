# Bernie Stage 3A — Yuri Formative Validation Plan

Date: 2026-07-19

Owner: Yuri / GPT Sol Extra High

Decision: `approved_scope_frozen_for_preparation_and_yuri_run`

## 1. Purpose

Stage 3A asks whether the accepted conversational Diary direction is already
operationally useful before EMR4 invests in its full visual language:

> Can Yuri complete representative receptionist tasks through typed
> conversation and functional, just-in-time Diary projections; correctly
> distinguish an answer, proposal, and committed action; and trust a carefully
> filtered simulation of committed-event attention without having to navigate a
> fixed grid?

This is formative evidence, not a population usability claim. It prepares and
runs one supervised Yuri-only study with authored synthetic data. It may refine
the bounded study surface, but it cannot stand in for representative reception
staff evidence.

## 2. Authority

Yuri approved the six Stage 3 decisions on 2026-07-19 and then directed Sol to
follow the recommended package and move forward.

Stage 3A is authorized as:

- Yuri-only;
- typed-only;
- local and deliberately synthetic;
- provider-disabled;
- functionally low-fidelity;
- based on deterministic read, projection, and committed-event fixtures; and
- adaptive only within the correction boundary in section 10.

Stage 3B, external participants, voice, push-to-talk, ambient listening,
Claude Fable, subscriptions, provider transmission, PII, production,
deployment, release, new mutations, GraphQL mutations, and committed-event runtime
remain closed.

## 3. Study split

Stage 3A has two evidence planes that must not be conflated.

### 3A-F — functional interaction study

An isolated local browser surface presents authored synthetic Diary state,
deterministic typed interpretations, reversible intent projections, an
ordinary-grid comparator, and deterministic event-attention fixtures. It makes
no API command and performs no appointment write.

Evidence label: `authored_synthetic_fixture_browser`.

### 3A-C — authoritative confirmation safety check

The already accepted local synthetic Diary → FastAPI → PostgreSQL create path
is exercised separately through its ordinary visible confirmation control. It
must use real non-intercepted local API calls and database readback.

Evidence label, only when the exact boundary is proven:
`live_local_browser_backend_postgres`.

The functional harness must never simulate a receipt and call it committed.
Fixture examples may explain the difference between proposal and commitment,
but the one-write invariant belongs to 3A-C.

## 4. Frozen task population

| ID | Task | Primary evidence |
|---|---|---|
| S3A-01 | Find a named patient's future appointment described by relative time and practitioner | answer + patient projection |
| S3A-02 | State the date, time, location, practitioner, and status of an existing appointment | authoritative-answer comprehension |
| S3A-03 | Show one practitioner's bounded day/time window | practitioner/date/time projection |
| S3A-04 | Find suitable availability without creating an appointment | availability projection + zero write |
| S3A-05 | Prepare an appointment proposal | proposal labelling + zero write |
| S3A-06 | Explicitly confirm the supported create proposal | 3A-C receipt and exact database readback |
| S3A-07 | Recover from ambiguous patient, practitioner, date, or duration | concise clarification, no silent resolution |
| S3A-08 | Explain a stale, conflicting, blocked, or replayed request | typed safe explanation |
| S3A-09 | Resume an interrupted retained session | no duplicate committed action |
| S3A-10 | Open Dr Shera's afternoon appointments on Friday week | precise reversible projection |
| S3A-11 | Show all of Margaret Thompson's upcoming appointments | patient-centred projection |
| S3A-12 | Surface a relevant committed-change fixture at the correct attention level | notice + offered projection, no action |
| S3A-13 | Suppress unrelated, foreign-practice, uncommitted, and rolled-back fixtures | no visible notice |
| S3A-14 | Deduplicate replay and reconcile delayed/out-of-order/superseded fixtures through a fresh synthetic read | one visible effect + current projection |

Every supported read task receives a conversational route and an ordinary-grid
route. The run alternates which route comes first across paired tasks. The
order and outcome are stored as structured observations; prompt or transcript
text is not retained.

## 5. Functional projection contract

Stage 3A intentionally does not attempt the final meta-grid design. Its views
must nevertheless prove the interaction semantics:

- a persistent statement of patient/practitioner/date/time/location scope;
- an explicit evidence label and as-of time;
- clear answer, proposal, block, and committed-receipt states;
- reversible refinement and return-to-previous-context controls;
- no display before required identity/date clarification;
- a visible explanation of why an event fixture was surfaced or suppressed;
- no hidden appointment mutation or generic command tunnel; and
- keyboard-operable controls with readable focus and reduced-motion behavior.

Visual polish, production component architecture, animation language, dense
grid ergonomics, and final responsive behavior belong to the deferred fluid UX
meta-grid tranche.

## 6. Event-attention fixture contract

Fixtures represent already-authored typed signals; they are not an outbox,
broker, producer, consumer, subscription, WebSocket, or background runtime.
Each fixture includes only allowlisted opaque identifiers, times, status/reason
codes, practice scope, event identity, aggregate revision, and evidence mode.

The deterministic attention function must prove:

1. foreign-practice, uncommitted, and rolled-back fixtures are suppressed;
2. unrelated fixtures are silent or passive, never interruptive;
3. stable event identity prevents duplicate visible effects;
4. lower aggregate revisions cannot replace newer state;
5. a current synthetic read, not the event payload, supplies displayed Diary
   facts;
6. relevant low-consequence changes use silent, passive, or concise attention;
7. no Stage 3A fixture produces an interruptive alert; and
8. a notice may offer a projection or proposal but cannot act.

## 7. Accepted Stage 3A gates

Safety and semantics are absolute scenario gates:

- 100% correct practice scope and zero cross-practice disclosure;
- zero writes before explicit confirmation;
- exactly one appointment, audit row, completed command result, confirmation
  outcome, and stored receipt after successful 3A-C confirmation;
- 100% correct recognition of answer versus proposal versus committed action;
- 100% suppression of foreign-practice, uncommitted, and rolled-back fixtures;
- zero duplicate visible effects on replay;
- zero false interruptive alerts;
- every visible notice traceable to a committed typed fixture and a fresh
  authorized synthetic read; and
- no identity ambiguity silently resolved.

Usability observations are formative in Stage 3A. Grid-free completion,
timing, clarification burden, projection reversibility, trust, and grid fallback
reasons are recorded without claiming staff-population thresholds.

## 8. Provisional Stage 3B thresholds

These are preserved for the later representative-staff decision and are not
Stage 3A pass criteria:

- at least 80% grid-free completion;
- at least 90% safe ambiguity recovery;
- at least 90% correct, visibly scoped, reversible projections;
- at least 90% precision and recall for relevant low-interruption notices;
- median conversational completion no slower than the grid; and
- a non-blocking target of at least 20% faster appointment recall.

Safety gates cannot be weakened to meet a usability threshold.

## 9. Observation and retention contract

The Stage 3A harness keeps observations in memory until Yuri explicitly
downloads them. It does not use `localStorage`, cookies, a backend endpoint, or
automatic telemetry.

The export may contain only:

- study/session and scenario identifiers;
- assigned route order;
- structured completion state and elapsed time;
- clarification, refinement, return, and grid-fallback counts;
- projection identifiers;
- event relevance/suppression/interruption decisions;
- answer/proposal/commitment comprehension choices; and
- structured rating or reason codes.

It must not contain typed prompt text, complete transcripts, names not already
part of the authored synthetic fixture, audio, credentials, headers, free-text
event payloads, provider output, or real patient/practice data. A future staff
study may retain selected de-identified language only after a new explicit
save/consent/deletion decision.

## 10. Correction authority

Stage 3A is adaptive. Sol may make and record narrowly necessary corrections
to:

- synthetic read models and fixtures;
- deterministic projection and attention logic;
- deterministic language routes;
- explanation and state-labelling copy;
- accessibility and keyboard behavior; and
- the structured observation instrument.

Every correction must identify the triggering scenario and rerun its affected
population. No correction may add a mutation, event runtime, provider, PII,
voice, autonomous behavior, retention expansion, privacy-policy choice, or
silently changed safety threshold. Those return to Yuri.

Stage 3B, when separately authorized, is frozen during participant execution;
only an immediate safety stop is permitted, and findings become a later
tranche.

## 11. Execution sequence

1. Freeze this plan and the accepted six-decision record.
2. Build the isolated Stage 3A functional study surface and synthetic fixtures.
3. Prove static authority/retention contracts and rendered interaction behavior.
4. Return `stage3a_study_ready` only if the harness is ready for Yuri; do not
   claim participant evidence.
5. Yuri runs the counterbalanced tasks while the facilitator records only the
   approved structured outcomes.
6. Run the independent 3A-C authoritative confirmation safety check.
7. Classify every failure as read/context, workflow, language, projection,
   event attention, modality, usability, or safety.
8. Return `stage3a_pass`, `stage3a_partial`, or `revision_required` with an exact
   evidence boundary and a recommendation for the next separately authorized
   tranche.

## 12. Preparation acceptance

The preparation tranche passes only when:

- the six decisions and this scope are durable in the live baton;
- the harness is isolated, local, synthetic, typed, provider-disabled, and
  mutation-free;
- fixture evidence is visibly labelled and cannot be mistaken for committed
  live-backend evidence;
- the counterbalanced route order and all 14 scenario purposes are represented;
- the observation export satisfies section 9;
- deterministic contract tests and rendered browser checks pass; and
- the handoff tells Yuri exactly how to begin without claiming results on
  Yuri's behalf.
