# Historical Diary Trove De-Identification Contract

Date: 2026-07-06
Sprint: H5 de-identification contract and redaction harness
Scope: committed-output safety for historical diary tooling
Privacy posture: synthetic tests only; no raw diary files, filenames, document
text, exact document timestamps, patient details, staff labels, or visible diary
content used in tests or committed outputs.

## Contract

Historical diary tooling may commit only aggregate neutral layout facts.

Allowed committed-output categories:

- counts and count ranges;
- table and cell dimensions;
- neutral structure classes;
- neutral signature distributions built from counts only;
- inferred interval modes in minutes;
- adjacent neutral delta ranges;
- explicit privacy booleans;
- root labels that are local cohort labels, not filenames or paths.

Forbidden committed-output categories:

- filenames or full/relative file paths;
- exact source document timestamps;
- document text, snippets, OCR/conversion output, or metadata strings;
- patient, staff, provider, doctor, room-label, appointment-label, or visible
  diary labels;
- long free-form string values;
- raw extraction output from Word, LibreOffice, OCR, or future parsers.

## Validator Added

Safe committed validator:

```text
scripts/historical_diary_output_safety.py
```

The validator recursively checks historical diary aggregate JSON for:

- keys outside the committed-output allowlist;
- key names that suggest raw paths, filenames, metadata, document text, patient
  labels, staff/provider labels, or appointment text;
- string values that look like Windows paths or `.doc`/`.docx` paths;
- exact timestamp-looking values outside `generated_at_utc`;
- likely person/staff labels;
- line-broken or overly long free-form strings.

The validator reads UTF-8 with or without BOM because PowerShell JSON outputs
may include a BOM.

## Tests Added

Synthetic-only test suite:

```text
tests/test_historical_diary_output_safety.py
```

The tests prove that:

- safe aggregate classifier payloads pass;
- unknown keys fail closed;
- filename fields fail;
- raw path values fail;
- document text fields fail;
- exact document timestamp fields fail;
- likely person/staff labels fail;
- long free-form values fail even under otherwise allowed keys.

## Current Local Validation

The validator accepts the current ignored H4 aggregate output:

```text
local_data/historical-diary-trove/inventory/structure_classifier_h4.json
```

This output remains ignored and uncommitted.

## H15 Semantic Labelling Gate

H15 adds an explicit gate before any semantic appointment labelling is derived
from historical diary trove data.

Gate validator:

```text
scripts/historical_diary_deidentification_gate.py
```

Default blocked template:

```text
docs/historical-diary-trove-semantic-gate-template.json
```

Current rule: semantic fixture promotion remains blocked until a gate payload
passes validation with `decision` set to
`approved_for_semantic_fixture_promotion`, a safe reviewer identifier, and
explicit semantic-labelling acknowledgement. Neutral structural work may
continue while the gate remains blocked.

The gate is separate from the H5 aggregate-output validator. H5 protects
committed neutral outputs; H15 prevents future semantic-labelling sprints from
starting without an explicit privacy-review decision.

## H16 Recommendation

Next sprint: **H16 Neutral Broadening or Gate Review Packet**.

Recommended scope:

1. Continue broadening neutral-only ordered samples under H10 caps; or
2. Prepare a concrete Yuri review packet for changing the semantic gate from
   `blocked` to a stricter approved mode.
3. Do not create committed semantic fixtures until the H15 gate passes in an
   approved state.

## H6 Historical Recommendation

Next sprint: **H6 Safe Local Timeline Delta Prototype**.

Recommended scope:

1. Use the H5 validator as a mandatory gate for any committed aggregate output.
2. Run local-only classification over a slightly larger but still bounded pilot
   window, such as one dense day from each pilot.
3. Emit only validator-approved aggregate transition facts: signature counts,
   delta distributions, run lengths, and possible edit cadence.
4. Do not emit filenames, exact timestamps, source text, labels, or event
   content.
5. Stop before full 58k-file processing until H6 shows that transition signals
   stay useful after validation.
