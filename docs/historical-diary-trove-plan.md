# Historical Diary Trove Utilisation Plan

This plan describes how EMR4 should use Yuri's historical original-EMR diary
snapshot trove: roughly three and a half months of diary files, about 58,000
files, where each saved copy represents the diary after a change. The period
appears to be continuous diary data, which makes it especially valuable for
mining real workflow rhythms across ordinary days, busy days, quiet days,
recurring roster patterns, and edge cases that only emerge over time.

The trove is potentially one of the most valuable evidence sources for EMR4's
native Diary and Bernie work because it records real reception workflow as a
sequence of state changes, not as abstract requirements.

## Local Storage Recommendation

Do **not** commit the raw trove to git.

Recommended local location inside the repo, now covered by `.gitignore`:

```text
C:\Users\sarashera\emr4\local_data\historical-diary-trove\raw\
```

Alternative ignored root-level locations are also safe:

```text
C:\Users\sarashera\emr4\historical_diary_trove\
C:\Users\sarashera\emr4\historical-diary-trove\
```

If disk space or backup policy is a concern, an external drive or sibling folder
outside the repo is also fine. The only hard rule is that raw files containing
PHI or clinic operational data must remain local and ignored.

## Safety Rules

- Raw historical diary files are PHI-bearing until proven otherwise.
- Do not commit raw files, screenshots, extracted patient names, phone numbers,
  Medicare numbers, addresses, free-text notes, or original filenames if they
  identify patients.
- Derived fixtures may be committed only after explicit de-identification and
  review.
- Prefer committing structural outputs: event types, anonymised resource labels,
  time offsets, status transitions, counts, and synthetic IDs.
- Keep any extraction scripts deterministic and local-first.
- Never send raw trove data to an LLM or external provider.

## Why This Data Matters

The trove can help EMR4 move from "we designed a diary state machine" to "we
validated the diary state machine against real-world diary motion".

Likely uses:

- **State-transition mining**: infer create, move, resize, cancel, DNA/no-show,
  check-in, waiting-room, identity-link, note, and administrative correction
  events from consecutive diary snapshots.
- **Legacy parity validation**: compare EMR4's native Diary event grammar against
  how the original diary actually changed during live clinic work.
- **Bernie receptionist corpus**: generate realistic natural-language scenarios
  and expected deterministic outcomes from real workflow patterns.
- **Replay harnesses**: turn de-identified diary deltas into executable tests
  that replay a day or half-day of reception churn.
- **Edge-case discovery**: find unusual but real behaviours: overlapping slots,
  double-booking patterns, late cancellations, schedule overruns, provisional
  patients, hidden breaks, and manual corrections.
- **Product prioritisation**: quantify which transitions happened most often,
  which states were rare, and which messy workflows deserve first-class support.
- **Longitudinal workflow modelling**: use the continuous multi-month sequence
  to detect weekly templates, recurring session structures, lag between booking
  changes and appointment times, same-day churn, and real receptionist load.

## Proposed Data Pipeline

### Stage 0: Local Inventory Spike

Goal: understand the trove without parsing clinical content deeply.

Tasks:

1. Count files, date folders, file extensions, filename timestamp patterns, and
   size distribution.
2. Determine whether chronological ordering is recoverable from filenames,
   filesystem timestamps, embedded document metadata, or folder structure.
3. Identify format: Word docs, HTML, XML, CSV, screenshots, PDFs, proprietary
   exports, or mixed.
4. Produce only non-PHI inventory metadata:
   - extension counts
   - files per day
   - rough timestamp gaps
   - continuity gaps or duplicated save bursts
   - weekday/session volume patterns
   - parseability summary
   - sample hash prefixes, not original names if names contain PHI

Deliverable: local-only inventory report plus a committed non-PHI summary.

### Stage 1: Parser Feasibility

Goal: determine whether snapshots can be converted into a neutral diary grid
state.

Tasks:

1. Build read-only parsers for the discovered file format.
2. Extract a canonical snapshot shape:
   - snapshot timestamp
   - visible diary date
   - resource/room columns, anonymised
   - appointment blocks with start/end/status/text buckets
   - non-appointment markers such as breaks or unavailable blocks
3. Hash or synthetic-ID appointment text locally so consecutive snapshots can be
   matched without exposing raw patient details.
4. Test on a tiny local sample, such as 5-10 consecutive snapshots.

Deliverable: parser spike and local redacted sample output.

### Stage 2: De-Identification Contract

Goal: define exactly what can leave the local raw-data area.

Allowed committed fields should usually be:

- synthetic appointment IDs
- relative or date-shifted dates
- time-of-day and duration, if not identifying by itself
- anonymised resource labels such as `resource_1`
- status/category labels
- transition labels
- counts and aggregate distributions
- redacted display buckets such as `patient_label_present=true`

Disallowed committed fields:

- patient names
- phone numbers
- Medicare numbers
- addresses
- free-text notes
- clinician/private staff notes
- original filenames if identifying
- exact rare dates if they could re-identify a real clinic day

Deliverable: `docs/historical-diary-trove-deidentification.md` or equivalent,
created before any redacted fixtures are committed.

### Stage 3: Snapshot Diff Engine

Goal: convert consecutive snapshots into event candidates.

Event candidates to infer:

- appointment created
- appointment deleted/cancelled
- appointment moved
- appointment resized
- status changed
- resource/room changed
- patient text changed
- note/detail changed
- provisional-to-linked style identity changes, if visible
- break/roster/unavailable block changes
- bulk template or day-layout changes

The diff engine should keep confidence levels:

- `exact`: stable synthetic ID or unambiguous text/time match
- `probable`: strong fuzzy match across time/resource changes
- `ambiguous`: multiple plausible matches
- `unknown`: snapshot changed but event cannot be classified safely

Deliverable: local event-candidate log for a small day slice.

### Stage 4: Redacted Fixture Promotion

Goal: commit only safe, useful structural evidence.

Candidate committed fixture shape:

```json
{
  "fixture_id": "legacy_diary_day_slice_001",
  "source": "historical_diary_trove_redacted",
  "date_policy": "date_shifted",
  "resources": ["resource_1", "resource_2"],
  "initial_state": [],
  "events": [
    {
      "event_type": "appointment_created",
      "resource": "resource_1",
      "start": "09:30",
      "end": "09:45",
      "synthetic_patient_ref": "patient_a",
      "confidence": "exact"
    }
  ],
  "assertions": [
    "no write occurs without explicit confirmation in EMR4 replay",
    "final_state_matches_redacted_snapshot"
  ]
}
```

Deliverable: one tiny redacted fixture plus tests proving EMR4 can replay it.

### Stage 5: Replay Harness

Goal: use historical workflow as deterministic regression pressure.

Potential harnesses:

- Backend-only diary event replay into EMR4 domain services.
- Frontend smoke-mode replay using synthetic fixtures.
- Bernie scenario replay: natural-language instruction derived from an event,
  expected proposal/clarify/refusal/read_request result.
- Migration parity checks for appointment statuses, durations, room/resource
  mapping, and cancellation/no-show semantics.

Deliverable: executable replay tests that run without raw trove access.

## Suggested Sprint Programme

### H1: Local Inventory and Safety Boundary

Scope:

- Add an ignored local trove path.
- Build a local inventory script that emits non-PHI counts and format metadata.
- Document observed file types and chronological ordering.

No raw content parsing beyond metadata.

### H2: Parser Feasibility on Tiny Sample

Scope:

- Parse 5-10 consecutive snapshots locally.
- Extract neutral snapshot structure.
- Confirm whether appointment blocks can be matched between saves.

No committed raw output.

### H3: Continuity and Churn Profile

Scope:

- Analyse non-PHI timestamp continuity across the full local trove.
- Measure snapshots per day, save bursts, after-hours changes, and weekday
  patterns.
- Identify candidate high-value days for later redacted replay fixtures.

No appointment text extraction unless H2 and the de-identification boundary are
already proven.

### H4: De-Identification Contract

Scope:

- Formalise field allowlist/denylist.
- Create one local redaction transform.
- Review whether dates should be shifted before fixtures are committed.

### H5: Diff Engine Prototype

Scope:

- Infer event candidates between adjacent snapshots.
- Classify confidence.
- Produce local event log for one small sequence.

### H6: First Redacted Replay Fixture

Scope:

- Commit one de-identified fixture.
- Add backend replay test against existing Diary/appointment model.
- Record gaps where EMR4 lacks a matching event/state.

### H7: Bernie Scenario Promotion

Scope:

- Convert selected historical event deltas into natural-language receptionist
  scenarios.
- Add them to the Bernie scenario corpus or replay harness.
- Preserve no-write/proposal-first boundaries.

## First Practical Step for Yuri

When convenient, copy a **small pilot subset first**, not all 58,000 files:

```text
C:\Users\sarashera\emr4\local_data\historical-diary-trove\raw\pilot\
```

Suggested pilot size:

- one clinic day if the files are clearly date-grouped; or
- 100-300 consecutive files from one day; or
- the original 414-file day already identified.

After that, Ariadne can run an inventory spike without touching the full trove.
If the pilot works, copy the remaining data into:

```text
C:\Users\sarashera\emr4\local_data\historical-diary-trove\raw\full\
```

## Open Questions

- What format are the files?
- Do filenames or metadata encode chronological order?
- Do filenames contain patient names or other PHI?
- Are snapshots full diary copies, partial exports, screenshots, or document
  saves?
- Are there multiple clinics/practitioners/resources mixed together?
- Are there known public holidays, roster changes, or unusual clinic days in
  the period that would help validate parsing?
- Should committed fixtures date-shift everything, or preserve day-of-week only?

## Recommendation

Yes, use this trove — but treat it as a local PHI-bearing evidence mine, not as
repo data. Start with a small ignored pilot subset, prove parsing and
de-identification, then promote only synthetic structural fixtures into git.

The first implementation sprint should be H1: local inventory and safety
boundary. Do not start by parsing all 58,000 files.
