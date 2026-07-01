# plan-codex-codex-sprint99-confidence-acceptance-review

| Item | Value |
|---|---|
| To | codex |
| From | codex |
| Branch | `codex/sprint99-confidence-acceptance-review` |
| Source Task | `codex-sprint99-confidence-acceptance-review` |
| Status | pending_plan_review |
| Created | 2026-07-01 17:02 +1000 |
| Source HEAD | `0ffeb20` |

## Plan Summary

Sprint 99 confidence acceptance review

## My Understanding

Sprint 99 should turn Bernie booking interpretation from one broad confidence
score and ad hoc warnings into a typed confidence and response policy. The
current problem is receptionist trust: Bernie should assume ordinary low-risk
facts only when evidence is adequate, ask a human-like clarification when
uncertainty matters, block only for safety or contract failures, and keep raw
technical detail behind debug mode or a deliberate Details disclosure.

The existing flow is non-mutating until explicit staff confirmation:
booking-instruction interpretation, supervised booking/candidate search,
candidate selection, and finally the existing confirm endpoint. Sprint 99 should
tighten that flow, not broaden Bernie into autonomous booking or external
identity/phone integrations.

## Intended Surface / Boundary

Affected surface: Bernie booking interpretation API contracts and the Diary
Bernie review panel/card only.

Nearby surfaces that must not change:

- Main diary appointment geometry, stacking, drag/resize, and status controls.
- Waiting Room cards, tabs, check-in state, and queue/status vocabulary.
- Booking create/edit modal outside the Bernie review flow.
- Taskpane, Command Centre, clinical scribe, billing, resource admin, SMS, and
  deployment/runtime setup.

The word "slot" in this sprint means a Bernie candidate booking time in the
Diary Bernie panel and proposed appointment preview, not a global change to the
diary grid layout. The word "status" means Bernie review result/status copy, not
appointment lifecycle status.

## Out Of Scope

Out of scope for Sprint 99 implementation release:

- Live phone/Caller ID, voice transcription, Medicare, OPV/PVM/IHI, or other
  identity-provider integrations.
- Broad API-spine, GraphQL, YAML operating-layer, audit-table, or capability
  manifest redesign beyond capturing follow-up boundaries.
- Patient-facing booking, autonomous create/confirm writes, or any bypass of
  explicit staff confirmation.
- New production-code work from this Codex worker. This worker submits acceptance
  review criteria only.

Future speech/transcription and external identity-provider confidence axes may
be named as reserved or inactive placeholders only if the API makes clear they
are not live evidence.

## Files I Expect To Edit

This Codex worker edits only coordination artifacts:

- `orchestration/agent_inbox/codex/plan-codex-codex-sprint99-confidence-acceptance-review.md`
- `orchestration/agent_inbox/codex/codex-sprint99-confidence-acceptance-review.md`

Expected implementation files for Claude/Antigravity plans to justify, but not
edited by this worker:

- `app/schemas/appointments.py`
- `app/routers/appointments.py`
- `app/services/bernie_booking_interpreter.py`
- `tests/test_bernie_interpret_booking_instruction.py`
- `tests/test_bernie_sprint98_release_gates.py`
- `orchestration/bernie_release_gates.md`
- `docs/diary/diary.js`
- `docs/diary/diary.css`
- `review/test_diary_smoke.py`

## Implementation Steps

Acceptance review guidance for Ariadne before implementation release:

1. Require explicit confidence axes, not one aggregate score. Minimum axes:
   `intent_parse`, `temporal`, `practitioner_match`, `patient_identity`,
   `slot_validity`, and `response_policy`. Reserved future axes such as
   `speech_transcription` and `external_identity` must be labelled inactive or
   not verified.
2. Require stable decision bands. Suggested bands: `assume`,
   `assume_with_staff_check`, `clarify`, and `block`. Low confidence should not
   automatically become a scary block; it should become clarification unless
   there is an actual safety/contract failure.
3. Require backend fields that the UI can consume without parsing warning-code
   strings: response policy/band, assumptions, clarifying question, Details
   evidence, and per-axis confidence/evidence.
4. Require omitted-date inference to be explicit. If staff omit a date and the
   active/reference diary date is available, Bernie may infer it only with a
   visible assumption message such as "I've assumed today" or "I've assumed this
   diary date." If no reference date exists, Bernie must ask which day.
5. Require same-day temporal validity. For requests for today, candidate search
   should not offer past slots. If the requested same-day window has already
   passed, Bernie should ask for a later time/day rather than returning stale
   candidates.
6. Require bounded practitioner fuzzy matching. Minor typos may resolve only when
   there is one clear active-practice match. Multiple near matches must ask
   "Do you mean Dr X or Dr Y?" rather than choosing silently.
7. Require conservative patient identity handling. A unique patient-name match
   may be used for candidate search with a visible staff check, but duplicate or
   ambiguous patient names must not silently select one patient. They should ask
   for DOB/phone or show candidate identities, depending on the worker plan.
8. Require first-person receptionist copy where appropriate: "I've assumed...",
   "I found...", "Do you mean...?" Ordinary mode must keep "Nothing is booked
   until you confirm" and must not expose UUIDs, raw field names, snake_case
   codes, provider setup text, or raw HTTP errors.
9. Require a Details disclosure policy. High-confidence ordinary flow should be
   compact by default with Details collapsed; ambiguous/clarification states
   should expose enough evidence to resolve the uncertainty. Developer debug
   diagnostics are not a substitute for receptionist Details.
10. Require the implementation plans from Claude/Antigravity to state Sprint 99
    versus deferred scope explicitly. Reject plans that broaden into API-spine,
    voice, phone, OPV/PVM, Medicare, or autonomous write work.

## Visual / Behavioural Acceptance Checks

Concrete acceptance gates:

1. The ordinary release prompt still passes interpretation and supervised slot
   search without pre-confirm writes:
   `Make an appointment for Margaret Thompson with Dr Shera today after 2 pm but before 3:45`.
2. `Make an appointment for Margaret Thompson after 3` with an active/reference
   diary date infers the date and shows a first-person assumption.
3. The same omitted-date request without a usable reference date asks which day.
4. Practitioner typo examples such as `Dr Shira` resolve only when there is one
   clear active-practice match; near ties ask a choice.
5. Duplicate `Margaret Thompson` fixtures produce ambiguity/candidate/DOB-or-phone
   clarification, not silent patient selection.
6. High-confidence candidate flow is compact by default, keeps Details collapsed,
   and still shows enough patient/practitioner/slot information to confirm.
7. Ambiguous or clarification flow expands enough evidence to let reception fix
   the request without reading debug metadata.
8. Ordinary UI text excludes `practitioner_id`, `patient_id`, UUIDs,
   `missing_practitioner_id`, snake_case warning codes, `Not Found`, raw provider
   setup text, and raw HTTP responses.
9. Candidate selection still stages a proposed appointment and provides the
   existing path back to candidate times; no confirm call occurs on that path.
10. Confirm remains the only appointment-write path. Backend tests should assert
    appointment and appointment-audit row counts before confirm.
11. Route-intercepted UI tests are labelled as route-intercepted. Any live-provider
    claim must include evidence such as `live_provider: true`.
12. If `docs/diary` runtime assets change, cache-bust versions must be bumped and
    checked.

Recommended tests:

- Backend pytest for confidence axes shape, omitted-date inference, no-reference
  clarification, same-day past-slot clamp, practitioner typo clear/ambiguous
  cases, duplicate patient ambiguity, ordinary release prompt, and no-write row
  counts.
- Diary smoke tests for first-person copy, Details collapsed/expanded states,
  raw-code exclusion in ordinary mode, candidate-to-selected-to-choose-another
  loop, confirm failure calm copy, and no confirm call before explicit staff
  confirmation.
- Static checks: `node --check docs\diary\diary.js`, focused Bernie pytest,
  `pytest review/test_diary_smoke.py -q`, and `git diff --check`.

## Risks / Ambiguities

Hidden risks:

- A single aggregate confidence can hide mixed evidence, for example high
  practitioner confidence with low patient identity confidence.
- UI parsing of warning codes will become brittle and can accidentally leak
  internal vocabulary.
- "Today" inference can offer past slots late in the day unless temporal policy
  is explicit.
- Fuzzy matching can pick the wrong Dr Shera when names are similar, inactive
  practitioners exist, or aliases are introduced later.
- Unique patient-name matching is not safe in a large practice without DOB/phone
  evidence and a visible staff check.
- Details can become a debug dump if it is not separated from dev diagnostics.
- First-person copy can overstate certainty unless it is bound to the backend
  response policy.
- Mocked/fake provider evidence can be misreported as live evidence.

Resubmission criteria for Claude/Antigravity plans:

- Resubmit if the plan collapses axes into one scalar confidence.
- Resubmit if low confidence becomes a generic block instead of clarification.
- Resubmit if the UI must parse warning-code strings to decide ordinary copy.
- Resubmit if raw IDs/codes/debug data appear in ordinary receptionist mode.
- Resubmit if staff confirmation/no-write gates are weakened.
- Resubmit if the plan expands into live phone, OPV/PVM, Medicare, voice, or
  broad API-spine work.

Dissent: Sprint 99 should tighten the existing internal supervised Bernie flow
first. External identity and voice integrations should wait until this confidence
contract is boring, typed, and test-gated.

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
