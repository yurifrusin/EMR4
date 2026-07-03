# Bernie Native Diary Agent Notes

This file records Ariadne/Yuri architecture discussion while the Fable 5
consulting plan is under review. It is not an implementation packet and does
not authorize code changes.

## 2026-07-03 - N1 Amendment Under Review

Fable's consult recommends a first implementation sprint, N1, that creates a
new `app/services/diary/` domain package and rehomes the diary action catalog,
typed action envelopes, and temporal policy there while leaving
`frames.py`/`policy.py` in `app/services/bernie/` unless the ordinary diary UI
starts building frame sets itself.

Ariadne and Yuri currently lean toward moving the reception evidence frames and
deterministic reception policy into the new diary domain immediately, because
the target architecture is for Bernie, the ordinary receptionist UI, Rayleen,
and later Davida to share the same diary/reception evidence language.

Proposed amended N1 direction:

- Create `app/services/diary/` as the native diary/reception domain home.
- Move or facade the following into that domain in a no-behaviour-change slice:
  - native diary action catalog
  - action intent/proposal/confirmation envelopes
  - diary event vocabulary
  - canonical temporal/date policy
  - typed reception evidence frames
  - deterministic policy over those frames
- Keep `app/services/bernie/` focused on:
  - natural-language interpretation into diary action intents
  - Bernie conversation/session statechart
  - Bernie narration/voice over typed outcomes
  - compatibility facades during migration

Architecture distinction to preserve:

- **Diary/reception frames** are evidence about proposed diary work: recognised
  patient, requested action, roster checked, slot search result, conflict,
  advisory future booking, proposal prepared, guardrail outcome.
- **Bernie session state** is conversational memory: awaiting clarification,
  candidate selected, proposal previewed, confirmation requested, stale after
  navigation, terminal/abandoned.

The goal of the amendment is to avoid building the shared diary/reception
grammar in Bernie's private namespace and then extracting it later after other
agents or UI paths have depended on it.

