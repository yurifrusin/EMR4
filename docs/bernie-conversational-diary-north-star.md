# Bernie as the Conversational Twin of the Living Diary

Date: 2026-07-19

Owner: Yuri / GPT Sol Extra High

Status: `product_north_star_accepted_for_strategy_stage3_not_authorized`

## North star

Make routine Diary work possible without finding a screen, scanning a grid, or
entering a form.

*bernie* should become the continuously available conversational interface to
the living practice Diary: able to answer, clarify, prepare, confirm, and
explain scheduling work in ordinary receptionist language while the
FastAPI/PostgreSQL Diary remains the sole source of appointment truth.

The intended “death of the Diary” is therefore the death of the Diary as an
interaction burden—not the death of the authoritative scheduling system.

## Product inheritance

Dr Michael Shera's original macro-driven Word Diary was unusually usable
because it imposed almost no interaction ceremony. A receptionist could place
the cursor naturally and type, as on paper. The native browser Diary cannot
outperform that experience merely by refining cells, forms, and click targets.

EMR4 should instead remove the requirement to touch or even inspect the grid
for most routine work. The visual Diary remains valuable for spatial overview,
exception handling, verification, and fallback. It should cease to be the
mandatory doorway to every answer and action.

## What the conversational twin is

*bernie* is:

- a receptionist-facing interface over live, practice-scoped Diary facts;
- conversationally fluent in patients, practitioners, dates, relative time,
  appointment types, availability, changes, and prior turns;
- able to distinguish an authoritative answer, a proposed action, and a
  committed action with receipt evidence;
- durable across restart and retry without becoming a second source of truth;
  and
- optional language intelligence around deterministic backend authority.

*bernie* is not:

- a replicated or privately remembered appointment database;
- a model that can assert identity, availability, confirmation, or committed
  state from its own text;
- an autonomous receptionist or model-to-database mutation path;
- a reason to expose broad Diary, historical, or clinical data to a provider;
  or
- a replacement for the visual Diary where spatial review is genuinely useful.

The twin must query current backend truth at the moment of need, identify
ambiguity explicitly, and label what is live fact, staff selection, model
interpretation, proposal, block, or committed event.

## Native in the API

The accepted mixed API Spine is the product architecture:

- scoped GraphQL/read models answer connected questions about appointments,
  patients, practitioners, availability, sessions, permissions, and audit;
- explicit REST/OpenAPI commands own every auditable or state-changing action;
- typed events report what actually committed and support future proactive
  awareness;
- durable session/event state carries conversational continuity; and
- PostgreSQL tenancy, RLS, conflicts, freshness, idempotency, audit, and
  receipts remain authoritative.

The conversational layer receives minimal typed context frames, not database
dumps. A question such as “What time is Margaret Thompson's appointment in six
months with Dr Shera?” should resolve through current identity and appointment
read frames, clarify if necessary, and return a source-labelled answer with its
as-of time. It must not depend on *bernie* remembering an earlier answer.

For writes, the enduring pattern is:

`request → clarification/context → proposal → explicit staff confirmation → backend revalidation → commit → receipt`

## Experience principles

1. **Conversation first, grid optional.** Supported work should begin from
   ordinary language and finish without a grid unless the user asks for one or
   the system cannot safely proceed.
2. **Answers are not proposals; proposals are not actions.** Every response
   makes that state unmistakable in words, sound, and any supporting visual.
3. **Clarification is the safe interface.** Ambiguous people, dates, recurrence,
   duration, or practitioners become concise questions rather than guesses.
4. **Show less, reveal more on demand.** The default answer is brief; provenance,
   alternatives, warnings, audit, and the relevant Diary view remain available.
5. **Conversation must survive interruption.** Durable state, revisions,
   idempotency, and receipts allow a receptionist to resume without duplicate
   work or contradictory state.
6. **The user may always escape to the Diary.** Grid use is measured as useful
   fallback, not treated as failure when spatial reasoning is the better tool.

## Ambient does not mean indiscriminate recording

The desired property is continuous availability and selective attention—not
continuous capture or retention of practice speech.

A safe modality ladder is:

1. typed conversation using local synthetic data;
2. explicit push-to-talk or deliberate activation;
3. local wake-word and speech detection that discards non-directed audio;
4. supervised ambient use under a separately accepted privacy, consent,
   retention, false-activation, and incident-response design; and
5. only then any production voice/provider decision.

No raw room audio, live call, voice provider, PII transmission, or ambient
deployment is authorized by this north star.

## Capability ladder

### Foundation — complete

Stages 1 and 2 proved one supervised appointment-create vertical plus durable
session, transaction, tenancy, audit, correlation, retry, and recovery safety.

### Conversation-first Diary work — next decision

Validate whether reception staff can obtain authoritative answers and complete
the supported booking task without navigating the grid. Read-heavy work should
come first: finding an appointment, explaining when and with whom it is booked,
checking a practitioner's day, finding suitable availability, and explaining
what changed.

### Voice feasibility — only after conversational value

If conversation itself proves useful, test explicit activation separately from
speech recognition quality. Do not let microphone technology obscure whether
the product interaction is valuable.

### Proactive twin — later

Typed events may eventually allow *bernie* to surface relevant changes,
conflicts, callbacks, arrivals, and schedule pressure without requiring a grid
scan. Proactivity must be role-scoped, interruptible, explainable, and silent by
default where attention is not warranted.

### Provider intelligence — observed need only

Access AI should return only when Stage 3 exposes a specific language or
explanation failure the deterministic layer cannot meet. Provider output may
interpret or explain; it never owns Diary truth or mutation authority.

## Product success

The primary product measure is not visual polish. It is the proportion of
supported receptionist work completed correctly and confidently without
searching the grid or entering a form.

Supporting measures include:

- authoritative-answer correctness and freshness;
- safe clarification and recovery;
- time to answer or confirmed completion;
- grid/form escape rate and the reasons for escape;
- comprehension of answer versus proposal versus committed action;
- duplicate/unsafe-write rate;
- interruption recovery and trust; and
- accessibility across typed, spoken, and visual modes.

Critical safety requirements remain absolute: no cross-practice disclosure, no
unconfirmed appointment mutation, no false claim of commitment, and no second
write on replay.

## Direction after Stage 3

Stage 3 should determine which deeper branch has evidence:

- **Read/context gap:** deepen the appointment-first read graph and typed
  receptionist context frames.
- **Workflow gap:** add only the specific Diary action whose staff value and
  authority model were observed; every new mutation requires a fresh command
  and acceptance decision.
- **Language gap:** consider bounded Access AI only for the frozen observed
  capability.
- **Modality gap:** run an explicit-activation voice feasibility tranche before
  any ambient design.
- **Awareness gap:** design event-driven, low-interruption proactive assistance.
- **No demonstrated value:** preserve the safe foundation and do not manufacture
  provider, corpus, voice, or UI work for momentum.

This north star changes product direction, not present authority. The engine
remains paused until Yuri accepts a concrete Stage 3 protocol.
