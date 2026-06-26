# plan-claude-claude-claude-bernie-slot-command-normalizer-contract

| Item | Value |
|---|---|
| To | codex |
| From | claude |
| Branch | `claude/current` |
| Source Task | `claude-claude-bernie-slot-command-normalizer-contract` |
| Status | integrated |
| Created | 2026-06-26 21:38 +1000 |
| Source HEAD | `5f7e62f` |

## Plan Summary

Add a deterministic, non-mutating backend command-normalizer that turns a Bernie/LLM-like slot-search command dict into the existing SlotSearchProposalIn constraint shape plus warnings/blocks/summary. Pure function, no LLM, no slot-search execution, no DB writes, no UI.

## My Understanding

Bernie pipeline: LLM parses NL into a loose typed command dict, then a DETERMINISTIC normalizer cleans/validates it into the existing SlotSearchProposalIn constraint shape, then the Sprint 38 POST /proposals/slot-search runs the read-only search, then present/confirm/create. This sprint builds ONLY the deterministic normalization stage as a pure contract: structured or LLM-like dict in, SlotSearchProposalIn-compatible constraint plus warnings/blocks/summary out. No LLM call, no slot-search/create call, no appointment or audit mutation, no UI.

## Intended Surface / Boundary

Backend only. New permissive input schema SlotSearchCommandIn and result schema SlotSearchCommandResult in app/schemas/appointments.py, plus a new pure helper module app/services/bernie_slot_normalizer.py exposing normalize_slot_search_command(payload, *, reference_date=None). Reuses existing SlotSearchProposalIn (validated constraint) and AppointmentProposalIssue (warning/block items), same safe/warnings/blocks/summary idiom as the other proposal contracts. No DB session, no network, no LLM. No route added this sprint. slots/candidates/booking slot/diary grid/waiting room/status are NOT visual surfaces here; nothing in the diary grid, waiting room, booking modal, taskpane, or Command Centre is touched. JSON-in/JSON-out only.

## Out Of Scope

Diary UI, live Bernie runtime, Gemini/LLM calls, autonomous tool execution, running the slot search, appointment creation, taskpane, Command Centre, SMS, billing, patient demographics, resource admin, DB migrations, and DB-backed identifier resolution (name->UUID lookups). Any appointment or audit-row mutation is forbidden.

## Files I Expect To Edit

app/schemas/appointments.py (new SlotSearchCommandIn permissive input + SlotSearchCommandResult output); app/services/bernie_slot_normalizer.py (new pure deterministic normalize_slot_search_command); tests/test_bernie_slot_normalizer.py (new focused tests).

## Implementation Steps

1) SlotSearchCommandIn accepts the loose Bernie/LLM command: practitioner_id/appointment_type_id/location_id/patient_id as str|UUID; date_from/date_to as str(ISO YYYY-MM-DD)|date; earliest_time/latest_time as str(HH:MM/HH:MM:SS)|time; duration_minutes/limit as int|str; permissive (extra=ignore) so unknown LLM keys do not crash. 2) normalize_slot_search_command(payload, *, reference_date=None) is a pure function: coerce/strip each field; parse UUID strings (malformed -> block invalid_practitioner_id etc.); parse ISO dates and HH:MM times (malformed -> block); coerce ints; clamp limit to <=100 with a warning; default date_to->date_from; optional deterministic relative tokens today/tomorrow ONLY when reference_date supplied else block; require practitioner_id+date_from (missing -> block). On success construct SlotSearchProposalIn (its model_validator enforces <=14-day range; ValueError there becomes a block). Emit summary describing the normalized constraint. 3) SlotSearchCommandResult: safe bool, constraint Optional[SlotSearchProposalIn] present only when safe, warnings/blocks list[AppointmentProposalIssue], summary str; no side effects. 4) Tests as in acceptance.

## Visual / Behavioural Acceptance Checks

JSON contract only, no rendered surface changes. tests/test_bernie_slot_normalizer.py proves: well-formed dict -> valid SlotSearchProposalIn with correct typed values; string UUIDs/dates/times coerced correctly; malformed UUID / bad date / bad time / non-positive duration -> safe=False with typed block and constraint is None; missing practitioner_id or date_from -> block; date_to<date_from and >14-day range -> block (delegated to SlotSearchProposalIn); limit>100 clamped with warning; unknown extra keys ignored; NON-MUTATION/PURITY proof: function takes no DB session and does no I/O (no LLM, no search, no DB import in the module) and is idempotent on repeated calls.

## Risks / Ambiguities

a) 'Normalize identifiers where possible' read as deterministic UUID/format parsing, NOT DB name->UUID resolution (needs a session, risks coupling); downstream /proposals/slot-search already does _ensure_* existence checks; flagged if name resolution was wanted. b) Relative-date tokens today/tomorrow are deterministic only against an injected reference_date, kept minimal and gated to avoid anything LLM-ish; easy to drop for ISO-only. c) No endpoint added, keeping it a pure service so non-mutation is trivially true and fully unit-testable; exposing a route is a clean later step. d) Time parsing restricted to ISO-ish HH:MM[:SS] (no 9am-style NL parsing, that is the LLM's job upstream).

## Codex Plan Review

- Review result: Accepted. Scope is pure backend schema/service/test normalization only, with no route, DB, LLM, slot-search execution, appointment mutation, audit mutation, or UI surface.
- Required changes before implementation: None.
- Approved to proceed: yes; implementation released by Ariadne via Claude headless driver.
