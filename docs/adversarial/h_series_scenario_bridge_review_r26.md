# Sprint R26 Adversarial Review: H-Series-to-Scenarios Bridge

**Reviewer:** DeepSeek Flash adversarial lane (Shen)  
**Target:** Proposed H-series neutral movement profile → deterministic Diary/Bernie scenario bridge  
**Review date:** 2026-07-06  
**Mode:** source-safe document review; no raw trove access, no ignored local data,  
no runtime provider wiring  
**Committed sources read:** `AGENTS.md`, `orchestration/parallel_workstreams.md`,  
`orchestration/bernie_reception_scenario_workstream.md`,  
`tests/bernie_scenarios/README.md`, `docs/historical-diary-trove-plan.md`,  
`docs/historical-diary-trove-semantic-labelling-gate.md`,  
`docs/historical-diary-trove-deidentification-contract.md`,  
`docs/historical-diary-trove-thursday-neutral-sampling.md`,  
`docs/historical-diary-trove-neutral-graph-report.md`,  
`tests/test_bernie_scenario_integrity.py`, `tests/bernie_scenarios/loader.py`,  
`orchestration/agent_inbox/claude/claude-r26-h-series-neutral-scenario-implementation.md`,  
`orchestration/agent_inbox/antigravity/antigravity-r26-h-series-receptionist-scenario-review.md`

---

## 1. Summary

The proposed bridge has a valid goal — turn safe neutral aggregate findings into
useful deterministic coverage — but faces three structural risks that could make
the resulting scenarios fragile, non-deterministic, or a backdoor past the H15
semantic-labelling gate. Each risk is addressable, but none is trivial.

---

## 2. Risk: Semantic Overclaiming From Neutral Count Data

H-series findings describe **structural and count movement**, not appointment
semantics. The committed neutral docs consistently preserve this boundary:

> "small_content_delta" describes content-volume change, not "a booking was made"
> "large_unexplained_delta" describes movement amplitude, not "an appointment was cancelled"

### Bridge exposure

If a Claude implementation or Antigravity review rephrases a neutral event class
as a receptionist scenario, the scenario name and expected outcome will
implicitly claim semantics that the H-series data does not prove.

**Example (hypothetical bad framing):**

```yaml
# BAD: Neutral class relabelled as appointment semantics
id: h_derived_morning_booking_burst
description: "Derived from H21 pilot_03 small_content_delta morning cluster"
turns:
  - action: normalize
    expect:
      outcome: confirmation_ready  # <-- H data says "counts moved", not "a patient booked"
```

### Acceptance criteria risk

A scenario that passes because "any neutral structural shift is valid" is not
deterministic. H-series profiles describe a range of movement across many
snapshots, not a single known-after transition. A test that asserts
`small_content_delta` without constraining *which* structural fields moved and
by *exactly how much* is a tautology.

### Recommendation

- H-derived scenario metadata must use explicit provenance labels such as
  `source="h_series_neutral", base_class="small_content_delta"` and must not
  rename neutral classes into receptionist English.
- Any scenario with `category: booking_create` or `category: booking_request`
  must derive its expected outcome from synthetic fixture state, not from an
  H-series classification alone.
- Acceptance criteria must be exact: field-path → expected-value, not
  range-based or vague. If the fixture cannot express exact values, it should
  be a profile metadata fixture, not a replay scenario.

---

## 3. Risk: H15 Semantic Gate Bypass

The H15 gate (`docs/historical-diary-trove-semantic-labelling-gate.md`) currently
reads:

> **Blocked work while the gate decision is `blocked`:**
> - committed appointment create/move/delete/status labels derived from raw
>   historical content;
> - committed redacted diary fixtures;
> - LLM/Gemini interpretation over raw diary files or extracted raw text;
> - committed examples containing original labels, notes, filenames, or exact
>   source timestamps.

### Bridge exposure

If a committed fixture YAML includes `expected.appointment_written: true` or
`forbidden_outcomes: ["appointment_written"]` and the scenario id references
an H-series movement class (e.g.,
`h_derived_pilot_01_large_unexplained_delta`), the fixture implicitly claims
that an H-series neutral delta *proves* the diary should have or should not have
committed a write. That is a semantic claim about appointment state changes.

The H15 gate forbids "appointment create/move/delete/status labels derived from
raw historical content". A bridge scenario that encodes "neutral delta X should
produce Y appointment outcome" *is* a derived semantic label — it just routes
through the scenario fixture schema instead of a labelled event log.

### Recommendation

- The bridge must add a **fourth layer** between the neutral graph and the
  scenario corpus: a YAML metadata schema (e.g.,
  `tests/fixtures/h_series_profiles/`) that records only structural movement
  profiles and delta buckets, exactly as H-series committed docs already do.
- Do not promote any H-derived profile into the executable Bernie scenario
  corpus until the H15 gate is reviewed, an explicit semantic-labelling
  acknowledgement is present, and a Yuri-approved fixture template is agreed.
- H-derived test coverage should target a new `test_h_series_profile_consistency.py`
  that verifies the profile metadata is valid and self-consistent, not a
  `test_scenario_replay.py` that asserts appointment outcomes.

---

## 4. Risk: Fixture Schema Drift

The existing loader (`tests/bernie_scenarios/loader.py`) expects:

```python
KNOWN_ACTIONS = frozenset({"normalize", "search", "select", "confirm"})
```

The existing integrity test
(`tests/test_bernie_scenario_integrity.py`) validates:

- `id`, `category`, `turns` required
- `KNOWN_ACTIONS` for executable scenarios
- `KNOWN_OUTCOMES` including `clarification_required`, `confirmation_ready`,
  `blocked`, `candidate_selection_required`, `no_matching_times`, `no_slots`,
  `roster_unavailable`, `completed`

### Bridge exposure

A scenario file that uses `small_content_delta` as a turn outcome or
`booking_clarification` as a category while encoding H-derived structural data
will either:

- **Fail the integrity test** because the outcome is not in `KNOWN_OUTCOMES`.
- **Pass the integrity test but mislead** because the loader interprets
  `normalize/search/select/confirm` actions against the Bernie session state
  machine, not against H-series movement profiles. The replay harness will
  attempt real session turns and fail in confusing ways.
- **Require schema extension** that relaxes outcome validation, implicitly
  widening the harness contract for non-deterministic reasons.

### Recommendation

- The bridge must not modify `KNOWN_ACTIONS`, `KNOWN_OUTCOMES`, or the loader
  schema to accommodate H-series profile data. Profile data belongs in a
  separate schema namespace.
- If a "profile-only" fixture is needed (no executable turns), use a non-YAML
  format (e.g., committed JSON with a separate validator) or a dedicated YAML
  directory with a distinct loader that is not registered in the replay harness.
- Do not add `h_series_*` categories to `ALLOWED_CATEGORIES` unless the
  scenario genuinely uses the Bernie session state machine.

---

## 5. Risk: Non-Deterministic Acceptance Criteria

A deterministic replay scenario asserts: *given known initial state and known
user input, the backend responds with known structured output.* H-series
profiles describe aggregate behaviour: "in this root, 21 of 39 transitions were
`no_structural_change`".

### Bridge exposure

If a bridge scenario asserts:

```yaml
turns:
  - action: normalize
    expect:
      fields:
        "event_class": "small_content_delta"
```

...the harness has no `small_content_delta` event class. Even if added, the
backend diary engine does not return event classes — it returns
`ClarificationRequest`, `CandidatesProposal`, `ConfirmationRequired`, etc.
Mapping "neutral delta class X" to "backend should return outcome Y" is a
semantic assertion unsupported by the H-series data.

### Recommendation

- Every fixture in the bridge must state its **deterministic basis**: which
  raw/fixture state produces which exact expected field values.
- If the fixture's expected outcome depends on ignored local data or a
  non-reproducible aggregate, mark it `xfail` with a reason explaining the
  non-deterministic dependency, or do not commit it at all.
- Prefer scenarios that use the existing harness machinery (known patients,
  known practitioners, known schedules) over scenarios that derive their
  expectations from a historical aggregate.

---

## 6. Risk: Accidental Normalisation of Raw Trove References

The H-series committed docs are safe because they use ignored-root identifiers
like `pilot`, `pilot_01`, `pilot_02`, `pilot_03` — opaque labels with no
filesystem path content.

### Bridge exposure

If a bridge scenario includes:

```yaml
description: "Derived from H21 pilot_03 small_content_delta"
source_h_root: "pilot_03"
source_h_class: "small_content_delta"
```

...this is safe *today* because `pilot_03` is an opaque committed identifier.
However, if a future doc ever reveals that `pilot_03` = "Thursday in May 2022
at Clinic X", the fixture metadata becomes an implicit provenance chain back to
a clinic and approximate date. The opaque-root pattern must be preserved
across all documentation.

### Recommendation

- H-derived profile metadata must use **only opaque root identifiers** that
  are already committed in the H-series safe doc set.
- Do not add new opaque labels in the bridge that do not exist in the committed
  H-series docs; this creates a separate provenance mapping that could be
  resolved later by cross-referencing ignored local data.
- Document in the fixture or profile file that "these identifiers are opaque
  trove root labels from the H-series committed docs; they carry no clinic,
  date, or semantic information."

---

## 7. Concrete Attack Vectors

### Vector 1: Semantic promotion via fixture naming

A fixture named `h_derived_booking_burst_morning.yaml` with category
`booking_create` will, over time, be treated as a real receptionist scenario.
Reviewers inspecting the fixture collection will not re-read the H-series docs
to confirm the neutral basis. The name itself becomes the semantic claim.

**Mitigation:** Naming convention that makes neutral provenance explicit and
non-receptionist, e.g.:

```
h_profile_no_structural_change_synthetic.yaml
h_profile_small_content_delta_synthetic.yaml
```

Keep these in a separate directory, not mixed with receptionist scenarios.

### Vector 2: xfail decay

Marking H-derived scenarios as `xfail` with reason "not yet deterministic"
creates a pile of allowed failures that future sprints are asked to "fix".
If the scenario cannot become deterministic because the source data is
aggregate, it will never un-xfail, and the xfail count becomes noise.

**Mitigation:** Do not commit H-derived scenarios as xfail in the executable
corpus. Only commit profile metadata that has a passing deterministic path.

### Vector 3: H15 gate hole punch

If the bridge avoids the phrase "semantic labelling" and uses "profile-driven
expected outcomes" instead, it still encodes appointment-level expectations
derived from the trove. The H15 gate must be reviewed before any fixture that
says "this H delta means appointment X should (not) happen."

**Mitigation:** Add an explicit flag `h15_gate_bypass: false` to every
H-derived fixture or leave H-derived fixtures entirely out of the executable
corpus until the gate changes.

---

## 8. Positive Verdict (What the Bridge Should Do)

The bridge is worth building if it stays in the right layer:

| Layer | What it contains | Format | Executable? |
|---|---|---|---|
| H-series committed docs | Neutral aggregate counts, delta buckets, graph nodes/edges | Markdown | No |
| **New:** H-series profile metadata | Synthetic structural profiles derived from neutral patterns (no appointment claims) | Committed JSON or separate YAML dir | No (validator only) |
| Existing Bernie scenario corpus | Deterministic replay scenarios with known initial/final state | YAML (executable harness) | Yes |
| Existing replay harness | Turn-by-turn backend assertions | pytest | Yes |

The bridge should add the middle layer only. It should:

1. Create `tests/fixtures/h_series_profiles/` or similar.
2. Add a schema validator for profile metadata (count ranges, delta classes,
   opaque root labels — no appointment fields).
3. Add `tests/test_h_series_profile_consistency.py` that validates profile
   structure, uniqueness, and self-consistency.
4. Add a doc at `docs/h-series-profile-schema.md` explaining the boundary.
5. **Do not** modify the Bernie scenario loader, corpus, or replay harness.
6. **Do not** add H-derived scenarios to the executable fixture directory.

If Ariadne or Yuri later opens the H15 gate, the profile metadata layer
becomes a natural data source for constructing semantic fixtures, but the
semantic-labelling and fixture-promotion decision stays explicit and separate.

---

## 9. Remaining Risks (After Mitigation)

- Profile metadata drift: if the H-series base classes change or new roots are
  added, the committed profile layer needs an explicit sync step, not automatic
  inference.
- Idle fixture accumulation: profile metadata without an executable consumer
  may become stale. A periodic review (every 3-4 sprints) should prune or
  freeze it.
- Schema extension pressure: a future sprint will want to add event classes or
  receptionist-domain mappings to the profile schema. This pressure should be
  resisted until the H15 gate is explicitly addressed.

---

## 10. Adversarial Questions for Ariadne

1. Does this bridge need an explicit H15 gate acknowledgment in the sprint
   closeout, even if the bridge stays in the proposed non-executable middle layer?
2. Should the profile metadata validator reject fixtures that contain
   `appointment_written`, `patient`, `practitioner`, or any field from the H5
   forbidden categories?
3. Who owns the ongoing mapping between H-series committed docs and the
   profile metadata layer when the H-series state graph is refreshed?
4. Is there a concrete plan to review the H15 gate, or is semantic fixture
   promotion permanently off the table?

---

*This review is source-safe: no raw filenames, paths under local_data, exact
source timestamps, patient/staff labels, document text, or semantic appointment
labels are disclosed. Findings are derived from committed docs and existing
source code only.*
