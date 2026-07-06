# Sprint R27 Adversarial Review: H-Series Profile Consumption

**Reviewer:** DeepSeek Flash adversarial lane (Shen)  
**Target:** R27 profile-consumption test design — tautologies, semantic leakage, weak no-write assertions, schema drift, and deterministic boundary  
**Review date:** 2026-07-06  
**Mode:** source-safe committed-doc review only; no raw trove, no ignored JSON, no runtime provider wiring  
**Committed sources read:** `AGENTS.md`, `docs/h-series-profile-schema.md`, `docs/receptionist_review_r26.md`, `docs/adversarial/h_series_scenario_bridge_review_r26.md`, `tests/fixtures/h_series_profiles/stable_grid_small_delta_h21.yaml`, `tests/test_h_series_profile_consistency.py`, `orchestration/agent_inbox/codex/codex-r27-deepseek-profile-consumption-adversarial-review.md`

---

## 1. Current State: No Consumption Test Exists

As of R27 start, the only test referencing H-series profiles is:

- `tests/test_h_series_profile_consistency.py` — validates fixture shape, forbidden keys, and semantic promotion wording.

No test consumes profile YAML fields to make runtime assertions about diary or backend behaviour. This is correct per the R26 bridge review recommendation: "only commit profile metadata that has a passing deterministic path."

**Gate status: clean.** The H15 semantic labelling gate is not being bypassed by existing committed code.

---

## 2. Tautology Risks (If a Consumption Test Is Written)

If a future sprint writes a test that reads profile metadata and uses those same values as expected outcomes, the test cannot fail on its own terms — it would be asserting that the profile says what it says:

| Anti-pattern | Example | Why it is tautological |
|---|---|---|
| Self-referential allowed-class check | `assert "small_content_delta" in profile["neutral_event_classes"]["allowed"]` | Duplicates the YAML content check already in the consistency validator. |
| deterministic_uses as pass/fail | `assert "diary_refresh_preserves_backend_authority" in profile["deterministic_uses"]` | Tests whether the YAML author typed a string, not whether diary refresh actually preserves backend authority. |
| Count-range self-consistency | `assert profile["sample"]["snapshot_count"] >= profile["sample"]["root_count"]` | Always true for any valid profile. |

**Recommendation:** Do not write a test whose assertion target is a field already validated by `test_h_series_profile_consistency.py`. Any new consumption test must connect profile metadata to an independent external invariant (e.g., "loader rejects profile with wrong `profile_kind`", "scenario runner ignores non-scenario fixture files").

---

## 3. Semantic Leakage Vectors in Consumption Code

The consistency validator (`test_h_series_profiles_do_not_smuggle_semantics`) scans `yaml.safe_dump(profile).lower()` for `FORBIDDEN_KEYS` and `FORBIDDEN_PROMOTION_WORDS`. This only catches forbidden strings **inside the YAML file**. A separate consumption test file that imports profile fields and rephrases them in receptionist language is not subject to the same check.

### Vector A: Test docstring rephrases neutral class as appointment semantics

```python
def test_h21_small_delta_implies_no_auto_write():
    """H21 profile shows small_content_delta — no booking should auto-create."""
    profile = load_profile("stable_grid_small_delta_h21")
    # ... some assertion about diary write behaviour ...
```

The docstring "no booking should auto-create" is an appointment-semantic claim from a neutral aggregate class. The consistency validator cannot catch this because the forbidden wording lives in a test docstring, not the YAML fixture.

### Vector B: Test code maps neutral class to expected outcome

```python
def test_h21_profile_refresh_stability():
    profile = load_profile("stable_grid_small_delta_h21")
    allowed = set(profile["neutral_event_classes"]["allowed"])
    if "small_content_delta" in allowed:
        # H-data shows small changes are normal — assert refresh preserves state
        assert diary.refresh_preserves_backend_state()
```

The logic "small_content_delta is normal → refresh must preserve state" is not wrong on its face, but it uses neutral category membership to justify an assertion about backend write behaviour. The causal link between "H-series saw small content deltas" and "our system must not auto-write" is a design choice, not an H-series finding.

**Recommendation:** Any consumption test that references profile data must:
1. Use the profile's exact field names in assertions (e.g., `profile_kind == "h_series_neutral_profile"`), not repackaged receptionist language.
2. Not use neutral event class membership as a premise for appointment-behaviour assertions.
3. Be reviewed for semantic docstring wording at merge time — the same gate that catches `FORBIDDEN_PROMOTION_WORDS` in YAML.

---

## 4. Weak No-Write Assertions

The profile's `deterministic_uses` lists `scenario_fixture_may_assert_no_unconfirmed_write` as an allowed use. This describes what a *separate, authored* Bernie scenario fixture may do — it does not prove that the profile *itself* contains evidence that no write occurred.

A consumption test that reads:

```python
assert "scenario_fixture_may_assert_no_unconfirmed_write" in profile["deterministic_uses"]
```

and then interprets that as a mandate to skip or modify a write-assertion is:

- **Semantically overbroad:** the profile records aggregate shape, not transactional evidence.
- **A tautology in disguise:** it tests a metadata string, not the diary's write authority.
- **Bypassing the authorial chain:** the only safe no-unconfirmed-write fixture is one explicitly authored from fake data with a known expected outcome. Deriving it from H-series metadata shortcuts that chain.

**Recommendation:** Do not write a consumption test that reads `deterministic_uses` and changes behaviour based on its membership. The `deterministic_uses` field is human-readable design intent, not a machine-enforced permission flag.

---

## 5. Fixture/Schema Drift

The current schema (per `docs/h-series-profile-schema.md`) requires:

- `id`, `profile_kind`, `source_docs`, `sample` (with three ints), `neutral_event_classes` (allowed + excluded), `deterministic_uses`, `privacy` (five fields), `forbidden_promotions`.

If a future sprint adds an optional field (e.g., `sample.synthetic_delta_buckets`), existing consumption tests that iterate all fields or use `yaml.safe_dump(profile)` for exact-string matching will silently change behaviour. Conversely, if a consumption test accesses `profile["sample"]["adjacent_transition_count"]` as part of a scenario parameter, and that field is later renamed to `adjacent_transition_count_total`, the test breaks with no link to the schema doc.

**Recommendation:** The profile schema should be versioned in the YAML (`schema_version: "1.0"`), and any consumption test must check `schema_version` before accessing version-specific fields. The consistency validator should reject profiles with an unknown `schema_version` and should be updated when the schema version bumps.

---

## 6. H15 Gate Perimeter

The consistency test enforces that profiles live under `tests/fixtures/h_series_profiles/` and must not appear in the Bernie scenario corpus. This is correct but relies on two implicit guarantees:

1. No future commit copies a `.yaml` file into `tests/fixtures/bernie_scenarios/` from the profile directory.
2. No future test imports a profile and feeds its values into the Bernie replay harness.

**Vector:** A future test could:

```python
profile = load_profile("stable_grid_small_delta_h21")
# Use profile metadata to parameterise a Bernie scenario
harness.run("refresh_does_not_resurrect_stale_latest_message.yaml",
            profile_root_count=profile["sample"]["root_count"])
```

This blends the profile layer into executable scenarios without the profile ever leaving its directory. The consistency validator would not catch it because the profile file is untouched.

**Recommendation:** Add an explicit cross-check test (`test_h_series_profiles_are_not_consumed_as_scenarios`) that:
1. Lists all fixture files in `h_series_profiles/` and `bernie_scenarios/`.
2. Verifies no filename overlaps.
3. Verifies no file in `bernie_scenarios/` imports from `h_series_profiles/` (token-based grep, not semantic).
4. Fails if a new `bernie_scenario` YAML references an h_series profile id.

Additionally, the profile loader should refuse to load a profile if the caller passes an argument like `as_scenario=True` or any parameter that would feed profile data into the replay harness. If no such flag exists, the import boundary is architectural, not enforced.

---

## 7. What a Safe Consumption Test Looks Like

Deterministic, non-tautological tests that use H-series profiles must meet all of:

| Criterion | Rationale |
|---|---|
| Asserts about the profile layer, not through it | Test validates that profiles are loadable, that `profile_kind` is correct, that the loader catches invalid YAML — not that the profile's neutral data predicts real-world behaviour. |
| No appointment-semantic wording | Test name, docstring, assertion message, and variable names use only H-series vocabulary: `neutral_profile`, `content_delta`, `structural_change`, `snapshot_count`. No `booking`, `arrival`, `cancellation`, `waiting_room`, `practitioner`. |
| No `deterministic_uses` value drives pass/fail | The field is metadata, not test logic. A test that checks its membership should do so only to verify schema compliance (e.g., "this field is a list of strings"). |
| No scenario-harness injection | Profile data is never passed to a scenario runner, replay harness, or any function that produces a diary assertion. |
| Schema version is checked | Test verifies `schema_version` matches what it understands, and fails for unknown versions. |
| Cross-contamination guard | Test independently verifies that profile files are not duplicated or symlinked into scenario directories. |

**Two design templates that satisfy these criteria:**

**Template A — Profile loader integrity:**

```python
def test_h_series_profile_loader_rejects_bad_kind():
    bad = {"id": "bad", "profile_kind": "bernie_scenario"}
    with pytest.raises(ValueError, match="must be h_series_neutral_profile"):
        h_series_loader.validate(bad)
```

Tests the loader boundary, not the profile content.

**Template B — Fixture isolation guard:**

```python
def test_h_series_profiles_not_mixed_with_scenarios():
    h_dir = PROFILE_DIR
    s_dir = Path(__file__).resolve().parent / "fixtures" / "bernie_scenarios"
    h_ids = {load_yaml(p)["id"] for p in h_dir.glob("*.yaml")}
    s_texts = {p.read_text() for p in s_dir.glob("*.yaml") if p.name != "README.md"}
    for h_id in h_ids:
        for s_text in s_texts:
            assert h_id not in s_text, f"Scenario file references H-series profile {h_id}"
```

Tests the isolation boundary, not appointment behaviour.

---

## 8. Concrete Attack Vectors (For Ariadne's Merge Gate)

### Vector 1: `deterministic_uses` as permission switch

A test that reads `deterministic_uses` and changes assertion strictness:

```python
uses = profile["deterministic_uses"]
if "scenario_fixture_may_assert_no_unconfirmed_write" in uses:
    # "This profile says it's OK to assert no write" — relax check
    ...
else:
    assert diary.last_write is not None
```

This makes test outcomes depend on a human-edited metadata string, not on the system's actual write-authority behaviour.

### Vector 2: Profile-as-scenario-proxy via parameterisation

```python
# tests/test_h_series_diary_integration.py
@pytest.mark.parametrize("profile_path", sorted(PROFILE_DIR.glob("*.yaml")))
def test_h_derived_scenario(profile_path, diary_harness):
    profile = load_yaml(profile_path)
    root_count = profile["sample"]["root_count"]
    # ... construct a test scenario from root_count ...
```

This creates N parameterised tests whose pass/fail depends on counting fields that were never designed for scenario parameterisation. When a new profile is added, the test silently expands its matrix without explicit review.

### Vector 3: xfail for "not yet deterministic"

```python
@pytest.mark.xfail(reason="H-series profile not yet linked to executable scenario")
def test_h21_refresh_stability():
    ...
```

As warned in the R26 bridge review: if the test cannot become deterministic because the profile is aggregate evidence, it will never un-xfail. The xfail count becomes test debt, not a roadmap.

### Vector 4: Docstring semantic drift

A test with a clean function name but a docstring that rephrases neutral data in appointment language:

```python
def test_profile_adjacent_transitions():
    """H21: 156 adjacent transitions confirmed stable grid with small deltas — normal surgery day."""
```

The docstring "normal surgery day" is not in the profile YAML, so the consistency validator does not catch it. But it frames the neutral data as a clinical appointment conclusion.

---

## 9. Positive Verdict: What the R27 Consumption Layer Should Do

| Should do | Should not do |
|---|---|
| Add a `schema_version` field to the profile schema and update the consistency validator to enforce it. | Write tests that assert appointment-world outcomes from neutral profile fields. |
| Add a fixture isolation guard test (Template B above) to prevent cross-contamination. | Add parameterised scenario tests driven by profile YAML files. |
| Add a loader integrity test for the profile loader (Template A above) if one is created. | Commit docstrings that rephrase neutral event classes as receptionist or clinical semantics. |
| Review any test that touches `deterministic_uses` and ensure it treats the field as load-only metadata, not an assertion premise. | Use `xfail` on profile-derived tests whose determinism depends on aggregate data, not synthetic fixture state. |
| Document the consumption contract in `docs/h-series-profile-schema.md`: profile data may be loaded and structurally validated, but must not be fed into any scenario harness or assert appointment behaviour. | Allow consumption tests to live outside the `test_h_series_profile_consistency.py` file without a naming convention that signals "metadata test, not scenario test" (e.g. `test_h_series_*meta*.py`). |

---

## 10. Adversarial Questions for Ariadne

1. Should the profile schema get a `schema_version: "1.0"` now, before any consumption test exists, so that future schema changes forced a version check?
2. If a future sprint adds an explicit "diary refresh stability" scenario authored from synthetic fake data (not H-series aggregate profiles), should that test reference the profile as a comment/docstring only, or should the profile be loaded at test time for metadata comparison?
3. Who reviews consumption-test docstrings at merge time for semantic leakage, since the automated validator only checks YAML files?
4. Should the profile loader (if one is created) emit a deprecation warning for any caller that passes `profile_kind="h_series_neutral_profile"` to a function named `load_scenario` or `run_scenario`?

---

*This review is source-safe: no raw filenames, paths under local_data, exact source timestamps, patient/staff labels, document text, or semantic appointment labels are disclosed. Findings are derived from committed docs and existing source code only.*
