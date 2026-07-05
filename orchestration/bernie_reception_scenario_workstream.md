# Bernie Reception Scenario Corpus And Replay Harness

This document formalises the receptionist-domain testing workstream for Bernie.
It turns Yuri's exploratory diary testing into executable project memory without
waiting for the whole Bernie/Diary architecture to be finished.

## Purpose

Bernie is being developed as a native diary/reception agent, not as a separate
chatbot bolted onto the Diary UI. That means receptionist phrasing, diary state,
clarification turns, slot search, confirmation, and mutation safety all need a
shared deterministic model.

Manual testing is still essential because Yuri's receptionist-domain intuition
finds real practice-shaped failures before an abstract test suite would. The
workstream's job is to convert those discoveries into a durable scenario corpus
and replay harness so each lesson is retained and regression-locked.

## Timing

This work should start now, but at a deliberately thin depth.

The current deterministic diary mechanisms are mature enough that regressions
matter:

- patient recognition
- practitioner recognition
- date and time parsing
- slot search and roster-aware availability
- confirmation gating
- server-side Bernie sessions
- clarification turns
- early appointment update/extend flows

The corpus should not yet become a large natural-language benchmark, production
log replay system, GraphRAG evaluation suite, or full simulated clinic day. It
should begin as a small set of high-value receptionist scenarios that verify the
state machine and diary domain are preserving the right facts across turns.

## Workstream Principle

Manual testing discovers the practice grammar.

The corpus records it.

The replay harness protects it.

The diary state machine implements it.

The UI expresses it.

## Initial Scope

Create a version-controlled scenario corpus and backend replay harness for
Bernie/Diary behaviours that are already meant to exist or are immediately next
in the native diary-agent plan.

Initial scenario categories:

- booking requests with patient, practitioner, date, time, and duration
- clarification turns that fill one missing field without losing known fields
- ambiguous duration phrases such as `long appointment`
- extension requests where "extend by 15 minutes" differs from "make it 30
  minutes total"
- no-slot outcomes that only say no matching slots when a slot search really ran
  and failed
- roster unavailable outcomes that explain practitioner availability separately
  from slot availability
- patient future-booking advisories that do not block or warn for unrelated days
- confirmation-required invariants before any diary mutation
- stale session/navigation cases that must not render old Bernie messages as
  current advice

## Out Of Scope For The Foundation Sprint

- A broad receptionist ontology.
- Production PHI/log ingestion.
- GraphRAG retrieval integration.
- Rare or complex clinical reasoning.
- Exhaustive natural-language paraphrase coverage.
- Direct UI screenshot replay as the primary harness.
- Auto-mode or unconfirmed diary writes.

## Scenario Shape

The first corpus can be YAML or JSON. Prefer a compact schema that is easy for
humans and workers to extend.

Example:

```yaml
id: booking_clarify_long_duration_preserves_practitioner
category: booking_clarification
reference_date: 2026-07-05
initial_state:
  diary_date: 2026-07-05
  practice: emr4_dev_main
turns:
  - user: "Make a long appointment for Margaret Thompson with Dr Shera next Tuesday at 3.30"
    expect:
      outcome: clarification_required
      missing: ["duration_minutes"]
      preserved:
        patient: "Margaret Thompson"
        practitioner: "Dr Shera"
        date: "2026-07-14"
        time: "15:30"
  - user: "A long appointment is 30 minutes"
    expect:
      outcome: confirmation_ready
      preserved:
        patient: "Margaret Thompson"
        practitioner: "Dr Shera"
        date: "2026-07-14"
        time: "15:30"
        duration_minutes: 30
forbidden:
  - "ask for doctor or nurse again"
  - "lose patient identity"
  - "search a different date"
  - "mutate the diary before confirmation"
```

## Replay Harness Requirements

The first harness should target the backend/session/domain layer before the
visual Diary UI. It should run under pytest and emit compact pass/fail evidence.

Recommended command shape:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\bernie_scenarios -q
```

The harness should:

1. Seed or select a known dev diary state.
2. Start a Bernie session.
3. Submit each user turn in order.
4. Assert the structured request frame after each turn.
5. Assert the explicit outcome state: clarification, candidates, confirmation,
   blocked, unavailable, or terminal.
6. Assert forbidden outcomes did not occur.
7. Optionally hand selected scenarios to the existing Diary smoke harness for
   narrow UI rendering checks after the backend behaviour is locked.

## Seed Scenarios

Start with 8-12 scenarios. The first batch should include failures already found
by user testing:

| Scenario | Reason |
|---|---|
| `booking_clarify_long_duration_preserves_practitioner` | Bernie asked again for the doctor after Yuri clarified that a long appointment means 30 minutes. |
| `booking_clarify_long_duration_preserves_patient_date_time` | Same class of bug, explicitly protecting patient/date/time. |
| `booking_tomorrow_not_blocked_by_patient_booking_today` | Prevents recurrence of same-day future-booking advisory spillover. |
| `booking_no_matching_times_only_after_slot_search_empty` | Stops "no times" copy appearing for non-slot-search reasons. |
| `booking_roster_unavailable_distinct_from_no_slots` | Bernie should explain when the practitioner is not rostered, not pretend slots were searched. |
| `extend_by_15_minutes_distinct_from_make_30_total` | Locks extension semantics and clarification copy. |
| `clarification_reply_merges_missing_field_only` | General invariant behind the long-appointment bug. |
| `confirm_required_before_create_or_update` | Diary mutation must remain evidence-gated and staff-confirmed. |
| `refresh_does_not_resurrect_stale_latest_message` | Protects against stale visible Bernie output after navigation/refresh. |

## Development Process

When Yuri reports a meaningful Bernie/Diary behaviour:

1. Ariadne classifies it as a bug, expected limitation, or product decision.
2. If it matters to ordinary reception workflow, add or update a corpus
   scenario before or alongside the code fix.
3. The implementation sprint fixes the deterministic diary/session behaviour.
4. The replay harness proves the scenario now passes.
5. Future UI tests only need to verify that the already-correct backend outcome
   is rendered clearly.

## Recommended Sprint Sequence

### Sprint R1: Reception Scenario Corpus Foundation

Goal: establish the corpus schema and replay harness without fixing every known
Bernie behaviour in the same sprint.

In scope:

- `tests/fixtures/bernie_scenarios/` or equivalent corpus directory.
- A small schema/loader.
- Pytest replay harness for backend Bernie session turns.
- 8-12 seed scenarios, including at least one expected-failing or xfail scenario
  for the long-appointment clarification bug if the fix is not included.
- Documentation for adding new scenarios.

Out of scope:

- Broad UI redesign.
- Large prompt engineering changes.
- GraphRAG.
- Production data.
- Auto-mode.

### Sprint R2: Clarification Merge Semantics

Goal: make clarification turns merge only missing or ambiguous fields into the
existing request frame.

Acceptance:

- A clarification such as "A long appointment is 30 minutes" preserves known
  patient, practitioner, date, and time from the prior turn.
- Bernie does not ask again for a doctor/nurse when a practitioner is already
  resolved.
- R1 scenario suite passes for clarification-preservation cases.

## Agent Roles

- Ariadne/Codex owns orchestration, scenario triage, final integration, and
  keeping the corpus aligned with the native diary-agent architecture.
- Claude is a good fit for the backend harness/schema and state-machine contract
  review.
- Antigravity/Gemini should review the seed scenarios as receptionist workflow
  and UX copy cases, not only visual UI.
- DeepSeek Flash is a good cheap worker for adding corpus entries, checking
  scenario consistency, and extending replay coverage once the harness exists.

## Long-Run Direction

This thin corpus can later become the evaluation layer for richer reception
knowledge, retrieval, and multi-agent diary work. Bernie is the right place to
pilot this method because the knowledge base is small enough for humans to judge
but realistic enough to stress the same event/state/retrieval boundaries that
Scribe, Consultant, Davida, and Rayleen will eventually need.
