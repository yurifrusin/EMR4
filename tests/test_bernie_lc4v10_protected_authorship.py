"""Authoring-only checks for fresh protected LC4V10 Gold.

These tests must never call product extraction, policy, interpretation, replay,
or the V10 ordinary observer.
"""

from __future__ import annotations

import inspect
import hashlib
import json
from collections import Counter
from pathlib import Path

import pytest

from app.services.bernie import lc4v10_protected_authoring as authoring
from app.services.bernie.lc4v10_content_blind_framework import (
    ACTIONS,
    LANGUAGE_FORMS,
    validate_fixture,
    validate_thresholds,
)

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    (ROOT / authoring.PROTECTED_ROOT / "attempt.marker.json").exists(),
    reason="LC4V10 is consumed; protected authoring content must not be reopened",
)


def test_authored_fixture_is_structurally_and_cross_field_valid() -> None:
    fixture = authoring.build_fixture()
    assert not authoring.validate_authored_fixture(fixture)
    assert not validate_fixture(fixture, authoring.ATTEMPT_ID)


def test_authored_population_is_exact_and_fresh() -> None:
    fixture = authoring.build_fixture()
    scenarios = fixture["scenarios"]
    assert len(scenarios) == 288
    assert len({item["scenario_id"] for item in scenarios}) == 288
    assert len({item["coverage_cell"] for item in scenarios}) == 288
    assert len({item["expected"]["exact_policy_projection"]["resolved_patient"] for item in scenarios}) == 288
    assert Counter(item["action"] for item in scenarios) == Counter({action: 48 for action in ACTIONS})
    assert Counter(item["language_form"] for item in scenarios) == Counter({form: 48 for form in LANGUAGE_FORMS})
    assert Counter(item["turn_count"] for item in scenarios) == Counter({1: 216, 2: 72})


def test_each_group_has_fixed_shape() -> None:
    fixture = authoring.build_fixture()
    for group_number in range(1, 25):
        group = [item for item in fixture["scenarios"] if item["group_id"] == f"g{group_number:02d}"]
        assert len(group) == 12
        assert len({item["action"] for item in group}) == 1
        assert Counter(item["language_form"] for item in group) == Counter({form: 2 for form in LANGUAGE_FORMS})
        assert Counter(item["turn_count"] for item in group) == Counter({1: 9, 2: 3})


def test_gold_cross_fields_and_source_spans_are_lossless() -> None:
    for scenario in authoring.build_fixture()["scenarios"]:
        expected = scenario["expected"]
        projection = expected["exact_policy_projection"]
        assert expected["safety"] is expected["policy_behavior"]["safe"]
        assert expected["replay"] == {
            "downstream_outcome": projection["downstream_outcome"],
            "appointment_delta_count": projection["appointment_delta_count"],
            "audit_delta_count": projection["audit_delta_count"],
            "simulated_write": projection["simulated_write"],
        }
        for turn in expected["lossless_source_spans"]:
            original = turn["original"]
            assert original == scenario["utterances"][turn["turn"]]
            for start, end in turn["source_spans"].values():
                assert 0 <= start < end <= len(original)


def test_threshold_artifact_is_exact() -> None:
    assert not validate_thresholds(authoring.build_thresholds())


def test_committed_artifact_bytes_match_independent_authorship() -> None:
    fixture_path = ROOT / authoring.FIXTURE_PATH
    thresholds_path = ROOT / authoring.THRESHOLDS_PATH
    fixture_bytes = fixture_path.read_bytes()
    thresholds_bytes = thresholds_path.read_bytes()
    assert json.loads(fixture_bytes) == authoring.build_fixture()
    assert json.loads(thresholds_bytes) == authoring.build_thresholds()
    assert hashlib.sha256(fixture_bytes).hexdigest() == (
        "6e04bb6100fe50dec5cfd2b9c06ee980cbe2fffc824f9e3870cbf1268a38efa2"
    )
    assert hashlib.sha256(thresholds_bytes).hexdigest() == (
        "71be796a80a84b553000547b6da6607eaf64053332e02cce3508b93b816f02cf"
    )


def test_authoring_never_calls_product_observation() -> None:
    source = inspect.getsource(authoring)
    forbidden = (
        "extract_semantics(",
        "resolve_policy(",
        "interpret_receptionist_utterance(",
        "ordinary_product_observer(",
        "run_one_shot(",
    )
    assert all(token not in source for token in forbidden)
