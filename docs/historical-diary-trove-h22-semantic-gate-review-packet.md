# Historical Diary Trove H22 Semantic Gate Review Packet

Date: 2026-07-06
Sprint: H22 semantic gate-review packet
Status: review packet only; H15 remains blocked
Privacy posture: source-safe documentation only. This packet does not use raw
diary files, ignored inventory JSON, extracted document text, filenames, exact
source timestamps, patient labels, staff labels, provider-visible prompts, or
semantic fixtures.

## Purpose

H22 is the decision packet that must exist before Yuri considers changing the
H15 semantic labelling gate from `blocked` to
`approved_for_semantic_fixture_promotion`.

This packet does not approve semantic labelling. It defines the smallest
reviewable approval surface, the local-only prototype that would need to be
run, the validator and leakage checks that must pass, and the exact stop points
that keep EMR4 from silently moving from neutral aggregate analysis into
semantic diary mining.

## Current Gate State

The authoritative gate remains:

```text
docs/historical-diary-trove-semantic-gate-template.json
```

The current committed decision is:

```text
blocked
```

The validating command remains:

```text
.venv\Scripts\python.exe scripts\historical_diary_deidentification_gate.py docs\historical-diary-trove-semantic-gate-template.json
```

H15 may move only if a reviewed payload passes that validator with:

- `decision` set to `approved_for_semantic_fixture_promotion`;
- a safe reviewer identifier such as `reviewer_1`, not a real name;
- `semantic_labelling_acknowledged` set to `true`;
- every privacy boolean still restrictive;
- every required forbidden category still present.

## Inputs Already Ready

The gate packet may rely on these committed, source-safe building blocks:

- H5 output-safety validator for neutral aggregate payloads.
- H15 blocked semantic gate validator and template.
- H-series neutral profile schema and isolation tests.
- R29 native Diary/Bernie action grammar.
- R30 deterministic synthetic replay consumer over hand-authored fake actions.
- R28 Fable verdict: grammar before labels, labels before mining, mining before
  memory.

The gate packet must not rely on:

- raw historical diary files;
- ignored local inventory JSON as committed evidence;
- neutral H-series event-class frequencies as semantic priors;
- LLM interpretation of raw or extracted diary text;
- production route, provider, or database write behavior.

## Smallest Reviewable Prototype

The next prototype, if Yuri approves running it locally, should be tiny and
abortable:

1. Select a very small local-only slice under existing H10-style caps.
2. Extract only candidate semantic buckets that map to the R29 grammar
   vocabulary.
3. Emit no raw text, source filenames, exact source timestamps, patient labels,
   staff labels, appointment notes, Medicare numbers, addresses, or phone
   numbers.
4. Replace every resource with synthetic IDs.
5. Replace dates with relative day indexes or approved shifted indexes.
6. Mark confidence as coarse labels only, such as `high`, `medium`, `low`, or
   `unknown`.
7. Send the candidate committed output through both the H5 output-safety
   validator and the H15 gate validator before it can be reviewed.
8. Stop after producing a review payload; do not add the output to Bernie
   prompts, RAG, GraphRAG, live routes, or UI.

## Required Validator Extensions

Before any semantic fixture promotion, the validators should prove these
properties with synthetic tests:

- Approved semantic payloads still reject raw or extracted diary text.
- Approved semantic payloads still reject original filenames and exact source
  timestamps.
- Approved semantic payloads still reject likely person or staff labels.
- Approved semantic payloads reject unsupported action names that are not in
  the R29 grammar.
- Approved semantic payloads reject transition labels that imply autonomous
  write authority.
- Approved semantic payloads reject H-series neutral event classes when they
  are used as semantic labels.
- Approved semantic payloads distinguish `unknown` from inferred status rather
  than filling gaps with plausible appointment meanings.
- Approved semantic payloads are loaded from an actual committed review payload
  in tests, not only from an in-memory synthetic helper.
- Approved semantic payloads include a bounded semantic scope, such as the
  root/day slice, field families, date policy, and allowed fixture families.
- Approved semantic payloads include an expiry or review interval so approval
  cannot silently become permanent scope creep.

H22 should prefer adding semantic mode alongside the H5 neutral validator
rather than weakening neutral validation. The neutral validator remains
neutral; semantic approval gets its own stricter path.

## Leakage Lint Requirements

Any candidate semantic output needs a separate leakage lint before review. At
minimum, the lint should scan keys and values for:

- Windows or POSIX paths;
- `.doc` or `.docx` filename fragments;
- exact timestamp-like strings;
- phone, Medicare, and address-like patterns;
- likely real names;
- line-broken free text;
- long natural-language note strings;
- raw Word/OLE stream names outside test fixtures;
- known neutral H-series event-class names used as semantic outcomes.

Failure should be fail-closed: the output is not committable and the sprint
pauses for review.

The lint must also cover test code and documentation, because semantic drift can
appear in comments, docstrings, test names, and Markdown before it appears in
fixture JSON. It should scan relevant `.py` and `.md` files for:

- forbidden promotion phrases such as `booked`, `booking burst`, `cancelled
  appointment`, `moved appointment`, and `patient arrived`;
- H-series neutral event-class names combined with receptionist or clinical
  framing;
- test names that combine an H-series identifier with a receptionist verb;
- wording that treats `deterministic_uses` as permission rather than metadata.

This lint is mandatory before semantic fixture promotion. It may be implemented
in a later source-safe sprint, but H15 must remain blocked until it exists and
passes.

## Approval Payload Shape

If Yuri later approves H15, the reviewed payload should be a separate file or
explicit patch to the gate template with no raw data attached. It should state:

- the approved decision;
- the safe reviewer identifier, expected to be `yuri` unless Yuri explicitly
  approves a different reviewer identifier;
- the exact semantic fixture families allowed;
- the local-only raw processing boundary;
- the committed fields allowed for that approval;
- forbidden categories that remain forbidden;
- whether date shifting or relative day indexes are used;
- how fixture confidence is represented;
- whether the output may be used only in tests, or also in approved read-only
  memory later.
- the approval expiry or review interval.

Approval for semantic fixture promotion is not approval for full-trove mining,
provider-visible prompts, fine-tuning, autonomous writes, or GraphRAG memory.
Those remain separate gates.

The current validator's `approved_for_neutral_only` state should be treated as
legacy/confusing until reviewed. Neutral work is already allowed while blocked,
so H22 recommends either removing that middle decision or documenting that it
does not open semantic work.

## Stop Points

The sprint engine must pause, with a Pushover notification that says
`sprint engine paused`, if any of these occur:

- Yuri has not approved the H15 gate payload and the next task requires
  semantic labels from the trove.
- A candidate output fails H5, H15, or leakage-lint validation.
- A worker proposes sending raw or extracted diary content to an external
  provider.
- A worker proposes committing redacted diary text rather than synthetic or
  bucketed fields.
- A proposed semantic label cannot map cleanly to the R29 action grammar.
- A proposed consumer would grant write authority outside the existing backend
  confirmation envelope.

## Recommendation

Use H22 as a human-readable approval runway, not as the approval itself. The
next safe sprint should add the validator/leakage-lint extensions using
synthetic fixtures only. The full diary trove should be touched for semantic
work only after Yuri explicitly approves H15 from a reviewed gate payload.
