# Bernie Synthetic Silver Action/Temporal Classification

Date: 2026-07-17

Status: `classification_complete`

Pre-repair report hash:
`sha256:1bf572c3906fe108cd81332953ae3333d033b6afc2f34827b2cdd0f1154e3822`

## Classification rules

- `supported_extraction_gap`: the dialogue explicitly states a bounded staff
  action that the current action reducer or vocabulary misses.
- `supported_normalization_gap`: the dialogue explicitly states a temporal
  operator that is reduced to an exact point.
- `language_adapter_gap`: the cloned source oracle expects a value that the
  admitted candidate does not surface and was not required to preserve, or
  the source policy fields are internally inconsistent with the dialogue.
- `replay_gap`: extraction is already correct and the mismatch is confined to
  deterministic delta/audit mapping.

The categories are not mutually exclusive. A parser gap may be remediated
while a hidden-oracle or replay residual keeps the whole candidate incomplete.

## Per-candidate classification

| Candidate | Supported finding | Residual classification | Disposition |
|---|---|---|---|
| `081_01` | schedule-read vocabulary: `diary rundown` | source oracle requires unsurfaced time and duration | repair action only |
| `082_02` | schedule-read vocabulary: `talk me through it` after a preface | source oracle requires unsurfaced time and duration | repair action only |
| `083_01` | schedule-read vocabulary: `diary rundown` | unsurfaced time/duration and ambiguous-to-exact practitioner label mismatch | repair action only |
| `088_02` | schedule-read vocabulary: `run me through it` in a restart | source oracle requires unsurfaced time and duration | repair action only |
| `033_01` | possessive appointment resize to an explicit duration | source expects clarification tools despite a clear resize and no expected clarification | repair action only |
| `043_02` | `appt length` / `make it 15 mins` resize shorthand | ambiguous-to-exact practitioner correction is labelled `corrected`; replay cascades | repair action only |
| `065_02` | `status ... arrived` staff shorthand | duration remains in the source oracle but is neither surfaced nor required | repair action only |
| `075_01` | corrected `status arrived` staff shorthand | unsurfaced duration and practitioner transition-label mismatch | repair action only |
| `002_01` | action appears in the second turn after a preface | later ambiguous entities and source clarification/policy fields are inconsistent | repair action only |
| `018_02` | action appears in the second turn after a preface | duration remains in the source oracle but is neither surfaced nor required | repair action only |
| `056_01` | `take out ... appt` cancel shorthand | unsurfaced duration plus ambiguous-entity clarification/policy inconsistency | repair action and temporal operator only |
| `032_02` | no intended-action miss; the primary bucket is caused by action-semantics policy scoring | unsurfaced duration and clarification/policy inconsistency | diagnostic only |
| `004_01` | `3pm or later` -> `not_before` | none after bounded repair | repair temporal operator |
| `007_02` | `by 5pm` -> `not_after` | none after bounded repair | repair temporal operator |
| `021_01` | `3pm or later` -> `not_before` | duration remains in the source oracle but is neither surfaced nor required | repair temporal operator only |
| `024_02` | `by 5pm` -> `not_after` | duration remains in the source oracle but is neither surfaced nor required | repair temporal operator only |
| `029_01` | corrected `around 3pm` must replace earlier `at 4pm` as `approximate` | duration remains in the source oracle but is neither surfaced nor required | repair temporal operator only |
| `029_02` | corrected `around 3pm` must replace earlier `at 4pm` as `approximate` | duration remains in the source oracle but is neither surfaced nor required | repair temporal operator only |
| `039_01` | `by 5pm` -> `not_after` | source expects clarification tools despite a clear resize | repair temporal operator only |
| `052_02` | `3pm or later` -> `not_before` | duration remains in the source oracle but is neither surfaced nor required | repair temporal operator only |
| `070_01` | `3pm or later` -> `not_before` | duration remains in the source oracle but is neither surfaced nor required | repair temporal operator only |
| `072_02` | `by 5pm` -> `not_after` | duration remains in the source oracle but is neither surfaced nor required | repair temporal operator only |
| `012_01` | extraction already complete | expected `create_requested` audit versus replay `created` | replay diagnostic only |
| `047_01` | extraction already complete | resize delta shape and `resize_requested` audit mismatch | replay diagnostic only |

## Accepted remediation boundary

The evidence supports 11 action-language repairs and 10 temporal-operator
repairs. It does not support inventing missing duration/time values, changing
ambiguous-entity clarification policy, relabelling entity transitions, or
rewriting replay deltas in this tranche. Those residuals remain visible.
