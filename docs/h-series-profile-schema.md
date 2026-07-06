# H-Series Neutral Profile Schema

Date: 2026-07-06
Sprint: R26 H-series neutral scenario bridge
Status: source-safe middle layer only

## Purpose

H-series neutral profiles convert committed historical-diary-trove findings into
small, deterministic, source-safe fixtures. They are designed to help future
Diary/Bernie regression sprints remember the shape of observed diary movement
without exposing raw diary content or pretending neutral aggregate movement has
appointment meaning.

Profiles live outside the Bernie scenario corpus:

```text
tests/fixtures/h_series_profiles/
```

This separation is intentional. H-series profiles are not executable booking
scenarios, not provider prompts, and not semantic labels.

## Required Shape

Each profile is YAML with:

- `id`: unique fixture id.
- `profile_kind`: always `h_series_neutral_profile`.
- `source_docs`: committed H-series documentation only.
- `sample`: positive aggregate counts, such as root, snapshot, and transition counts.
- `neutral_event_classes`: allowed and excluded neutral event classes.
- `deterministic_uses`: safe future test uses.
- `privacy`: explicit prohibitions on raw trove access, external providers, semantic labels, and raw identifiers.
- `forbidden_promotions`: examples of meanings that must not be inferred from neutral counts.

## Safety Rules

- Do not read `local_data` or ignored H-series JSON when authoring committed profiles.
- Do not include raw paths, filenames, exact source timestamps, document text, patient labels, or staff labels.
- Do not rename `small_content_delta` into receptionist semantics such as booking, cancellation, movement, arrival, or administrative-note intent.
- Do not put H-series profiles under `tests/fixtures/bernie_scenarios/` until the H15 gate is explicitly reviewed and approved.
- Do not use these fixtures as provider prompt content.

## Allowed Uses

Profiles may support deterministic tests that assert:

- H-derived fixtures remain source-safe and non-semantic.
- Future synthetic scenario families clearly distinguish fake authored data from H-series evidence.
- Diary refresh, backend-authority, and no-unconfirmed-write invariants remain explicit.

## Blocked Uses

Profiles must not be used to assert:

- a real appointment was booked, moved, cancelled, extended, or checked in;
- a practitioner, patient, or staff member was involved;
- receptionist intent can be reconstructed from count movement;
- Bernie may retrieve or reason over raw historical diary content.

## Verification

Run:

```powershell
.\.venv\Scripts\pytest.exe tests\test_h_series_profile_consistency.py -q
```

The validator is deliberately conservative. If a future sprint needs richer
semantics, it should update the H15 gate first rather than weakening this schema.
