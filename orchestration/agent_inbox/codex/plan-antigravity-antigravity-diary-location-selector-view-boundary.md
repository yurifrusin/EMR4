# plan-antigravity-antigravity-diary-location-selector-view-boundary

| Item | Value |
|---|---|
| To | codex |
| From | antigravity |
| Branch | `antigravity/current` |
| Source Task | `antigravity-diary-location-selector-view-boundary` |
| Status | pending_plan_review |
| Created | 2026-06-22 18:38 +1000 |
| Source HEAD | `1e9444c` |

## Plan Summary

Add diary physical location selector and fallback UI (Revised).

## My Understanding

We need to provide a restrained UI dropdown in the header sub-row inline with the practice name to select the active physical location. In live mode, we keep a stable one-location fallback and do NOT filter client-side. Client-side filtering is restricted to smoke/mock mode only.

## Intended Surface / Boundary

Diary header and filtering in docs/diary/ (html, css, js). Visually adjacent surfaces that must NOT change: main diary grid slots, columns, waiting room panel tabs/accordions, and booking modals.

## Out Of Scope

No backend migrations, models, or routes. No taskpane, Command Centre, or Bernie changes.

## Files I Expect To Edit

docs/diary/diary.html, docs/diary/diary.css, docs/diary/diary.js

## Implementation Steps

1. Wrap practice name and add location select element in diary.html. 2. Style the location select element as a restrained inline dropdown in diary.css. 3. Track activeLocationId and persist/load from localStorage. 4. Populate selector with mock locations in smoke mode, fallback to single location in live mode. 5. Filter appointments by activeLocationId only in smoke mode. 6. Update mock appointments to assign location_id to select entries.

## Visual / Behavioural Acceptance Checks

1. One-location fallback shows Main Clinic stably in live mode. 2. Smoke mode loads multiple locations. 3. Selector change filters grid and sidebar only in smoke mode. 4. State is sticky on page reload.

## Risks / Ambiguities

1. Lack of backend location-aware diary APIs (mitigated by using a stable one-location fallback and avoiding client-side faking in live mode).

## Codex Plan Review

- Review result:
- Required changes before implementation:
- Approved to proceed: no
