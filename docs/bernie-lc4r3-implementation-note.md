# LC4R3 Implementation Note — Aligned Action-Surface Closure

## Summary

Extended `_detect_intended_action` in `semantic_extraction.py` with four
narrow, contextual pattern families that resolve 160/160 single-turn surface
variants (exceeding the 154 target) without regression, overmatch, or
planned-action promotion.

## Patterns Added

### 1. `create` — anchored `New booking:` (target 16)
- Pattern: `^New booking:` anchored to utterance start.
- Only matches structured note/triage forms, not bare "new booking" prose.

### 2. `cancel` — `call off ... booking/appointment` (target 13)
- Pattern: `\bcall off\b.*\b(booking|appointment)\b` requiring both keywords.
- Excludes non-diary "call off the meeting" (no booking/appointment context).

### 3. `status_change` — arrival/status label forms (target 45)
- `^Arrived:` anchored to start (not bare "arrived at the office").
- `\bstatus:.*\barrived\b` case-insensitive (requires both colon and status keyword).
- `\bconfirm arrival\b.*\b(booking|appointment)\b` requiring arrival + booking context.
- Excludes `check in ...` (the `^Arrived:` anchor and `confirm arrival ... booking`
  context requirement prevent overmatch on check-in phrasing).

### 4. `explain_schedule` — availability/appointment queries (target 80)
- `\bavailability|availabilities\b` — standalone noun "availability".
- `\bwhat\s+does\b.*\b(schedule|day|appointments?|availability)\b` — contextual "what does".
- `\bwhat\s+appointments?\b` — "what appointments".
- `\b(free|open|available)\s+(slots?|times?|appointments?)\b` — "free slots" etc.
- `^Schedule:` — anchored label.
- `\b(show|list)\b.*\b(appointments?|schedule|times?|slots?)\b` — "show me" queries.
- `\b(day.view|calendar|roster)\b` — day view queries.
- `\b(what|how).*\bday\b.*\blooks?\b` — "what does the day look like".
- `\bpull up\b.*\bschedule\b` — "pull up the schedule".

## Existing Behaviours Preserved

- Action priority: cancel > status_change > move > resize > explain_schedule > create.
- Unsafe bypass/completion refusal unchanged.
- Safe negation (prefix negation, reversal patterns) unchanged.
- Lossless normalization unchanged.
- Exact `tomorrow at 3pm` temporal route unchanged.
- `check in ...` remains unclassified as `status_change`.
- Bare narrative "a patient just arrived for an appointment" remains read/clarify.

## Anti-Overmatch Guarantees

All new patterns require specific structural context:
- Anchored patterns (`^New booking:`, `^Arrived:`, `^Schedule:`) only match at
  utterance start.
- `call off` requires booking/appointment keyword.
- `Status:` requires colon and "arrived" keyword.
- `confirm arrival` requires booking/appointment keyword.
- `explain_schedule` patterns require schedule-related keywords.

## Results

| Metric | Before | After | Delta |
|---|---|---|---|
| intended_action passes | 720/1152 | 960/1152 | +240 |
| action_semantics passes | 674/1152 | 730/1152 | +56 |
| clarification passes | 642/1152 | 698/1152 | +56 |
| safety passes | 1152/1152 | 1152/1152 | 0 |
| repeat variance | 0 | 0 | 0 |

## Report Hashes

- LC4R3 report: `9e1aecff2bd39605` (see `docs/bernie-lc4r3-report.json`)
- LC4R2 report (regenerated): see `docs/bernie-lc4r-development-gap-report.json`

## Files Changed

| File | Change |
|---|---|
| `app/services/bernie/semantic_extraction.py` | Added 4 target family patterns |
| `tests/test_bernie_lc4r3_action_surface.py` | 53 new focused tests |
| `scripts/bernie_lc4r3_report.py` | New report script |
| `docs/bernie-lc4r3-report.json` | Deterministic report output |
| `docs/bernie-lc4r3-implementation-note.md` | This note |
| `docs/bernie-lc4r-development-gap-report.json` | Regenerated (reflecting improvements) |
