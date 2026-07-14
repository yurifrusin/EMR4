# LC4R3 Implementation Note — Aligned Action-Surface Closure (Revision)

## Summary

Revised the LC4R3 candidate to narrow explanation matching to the 80 evidenced
aligned surfaces only, anchor the `Status: ... ARRIVED` pattern at utterance
start, freeze the report family definition to the 154 original aligned failures,
measure repeat variance by two-run deterministic audit, correct protected-evidence
wording, and add negative anti-overmatch test cases.

## Patterns Added from Candidate (Retained)

### 1. `create` — anchored `New booking:` (target 16)
- Pattern: `^New booking:` anchored to utterance start.
- Only matches structured note/triage forms, not bare "new booking" prose.

### 2. `cancel` — `call off ... booking/appointment` (target 13)
- Pattern: `\bcall off\b.*\b(booking|appointment)\b` requiring both keywords.
- Excludes non-diary "call off the meeting" (no booking/appointment context).

### 3. `status_change` — arrival/status label forms (target 45)
- `^Arrived:` anchored to start (not bare "arrived at the office").
- `^Status: ... ARRIVED` anchored at utterance start (not `\bstatus:`, which
  could match mid-utterance).
- `\bconfirm arrival\b.*\b(booking|appointment)\b` requiring arrival + booking
  context.

### 4. `explain_schedule` — practitioner-required availability/appointment queries (target 80)
- Five narrow patterns requiring practitioner reference (Dr X or "some doctor"):
  - Practitioner possessive availability: `\b(?:dr [a-z]+|some doctor)'s availability\b`
  - "what appointments does Dr [X|some doctor] have"
  - "what Dr [X|some doctor]'s day looks like"
  - "when Dr [X|some doctor] has free slots"
  - "show me Dr [X|some doctor]'s available times"
- Removed standalone availability, `^Schedule:`, generic show/list, day-view,
  calendar/roster, pull-up schedule, generic "what ... day looks like", and
  other unowned additions.

## Changes from Candidate

### Narrowed Explanation Matching
Replaced 11 broad _EXPLAIN_PATTERNS with 5 narrow patterns requiring both a
practitioner reference and a relevant query relationship. Reduced explain
overmatch from 192/192 to 96/192 (only suffixes 01, 02, 03, 04, 06, 08).

### Anchored `Status:` Pattern
Changed `\bstatus:.*\barrived\b` to `^status:.*\barrived\b` so it only matches
at utterance start.

### Frozen Report Family Definition (154/154)
Report script now uses explicit frozen group ranges for the 154 original
aligned failures:
- create: 16 (suffix 03, surface, groups 001-016)
- cancel: 13 (suffix 06, surface, groups 049-057 and 061-064)
- explain: 80 (suffixes 02/03/04/06/08, surface, groups 081-096)
- explicit status: 45 (suffix 03/07 groups 065-080 plus suffix 06 groups
  065-073 and 077-080)
- deferred check-in: 13 (suffix 04, groups 065-073 and 077-080)
- deferred bare arrival: 13 (multi-turn suffix 01, groups 065-067, 069-073,
  075-079)

All counts and exact group memberships are tested so an equal-size case
substitution cannot pass. Separate target/deferred selection hashes are
included for reproducibility. Case IDs are not emitted in the report.

### Measured Repeat Variance
The candidate-quality audit fingerprints each of the 1,152 development
variants on two repeats (2,304 samples). Measured per-scenario observation and
safety variance is zero. This is stronger than comparing aggregate totals,
which could conceal equal and opposite per-case changes.

### Protected-Evidence Disclosure
During Sol's post-compaction orientation, a broad filename command enumerated
protected fixture path names. No protected file was opened, read, imported,
evaluated, or tuned against; no semantic content or labels were exposed.
Disclosed as a metadata-enumeration process incident. No protected evidence
was accessed as a worker action.

### Anti-Overmatch Tests
The test that asserted generic meeting availability is `explain_schedule` was
replaced: it now asserts `None` (unclassified). Added 14 negative test cases
for generic calendar/roster/day-view/pull-up/status/schedule-label uses to
prove removed patterns cannot return.

## Results

| Metric | Pre-LC4R3 | Candidate | Revision |
|---|---|---|---|
| intended_action passes | 720/1152 | 960/1152 | 880/1152 |
| action_semantics passes | 674/1152 | 730/1152 | 730/1152 |
| clarification passes | 642/1152 | 698/1152 | 698/1152 |
| safety passes | 1152/1152 | 1152/1152 | 1152/1152 |
| repeat variance (measured) | — | — | 0 |

### Target Families

| Family | Pass | Total |
|---|---|---|
| create (New booking:) | 16 | 16 |
| cancel (call off ... booking/appointment) | 13 | 13 |
| status_change (Arrived:, ^Status:, confirm arrival) | 45 | 45 |
| explain_schedule (practitioner-required queries) | 80 | 80 |
| **Total** | **154** | **154** |

### Deferred Families

| Family | Outcome |
|---|---|
| check_in NOT status_change | 13/13 deferred |
| bare narrative NOT mutation | 13/13 deferred |

### Note on intended_action Count (880 vs 874)
The revision achieves 880/1152 intended_action passes (exceeding the 874 floor).
The extra 6 above 874 come from non-frozen surface variants that match the same
patterns as the frozen targets: cancel suffix-06 groups 058-060 and status
suffix-06 groups 074-076. Their action surfaces are textually explicit, but
other contract dimensions kept them outside the original aligned-failure
subset. The frozen report definition correctly limits target evidence to 13
and 45 respectively without suppressing those six legitimate recognitions.

## Report Hashes

- LC4R3 report: regenerated after Sol's evidence-only recovery amendment (see
  `docs/bernie-lc4r3-report.json`)
- LC4R2 report (restored): `cba97acd3f23d2ec` (see `docs/bernie-lc4r-development-gap-report.json`)
- Corpus hash: `f73a35b8843beb66`
- Target/deferred selection hashes: recorded separately in the report

## Files Changed

| File | Change |
|---|---|
| `app/services/bernie/semantic_extraction.py` | Narrowed explain patterns to practitioner-required; anchored Status: |
| `tests/test_bernie_lc4r3_action_surface.py` | Fixed anti-overmatch, added 14 negative cases, updated explain tests |
| `scripts/bernie_lc4r3_report.py` | Exact aligned/deferred selections, per-scenario measured variance, baseline assertions |
| `tests/test_bernie_lc4r3_report.py` | Sol recovery regressions for exact case membership and evidence disclosure |
| `docs/bernie-lc4r3-report.json` | Revised deterministic report |
| `docs/bernie-lc4r3-implementation-note.md` | This note |
| `docs/bernie-lc4r-development-gap-report.json` | Preserved exactly from base (`643cdaa9`) |
