"""Synthetic replay tests for the R29 diary action grammar."""

from __future__ import annotations

import inspect
from dataclasses import replace

import pytest

from app.services.diary.action_grammar import (
    DIARY_ACTION_GRAMMAR,
    DiaryActionVerb,
    DiaryActionVerbDescriptor,
)
from app.services.diary.capabilities import BernieCapabilityTier

from . import loader, replay


def _scripts() -> list[dict]:
    return loader.discover_day_scripts()


@pytest.mark.parametrize("script", _scripts(), ids=lambda script: script["id"])
def test_synthetic_day_script_replays_against_action_grammar(script):
    result = replay.run_day_script(script)
    assert result.passed, "\n".join(result.failures)


def test_loader_rejects_h_series_profile_shape():
    payload = {
        "id": "bad",
        "schema_version": "h_series.neutral_profile.v1",
        "profile_kind": "h_series_neutral_profile",
        "source": "authored_synthetic",
        "actions": [{"raw_name": "find_slots", "expected_dispatch": "route_read_only"}],
    }
    text = __import__("json").dumps(payload)
    path = pytest.MonkeyPatch.context()
    with path:
        import tempfile
        from pathlib import Path

        temp_dir = tempfile.TemporaryDirectory()
        path_obj = Path(temp_dir.name) / "bad.json"
        path_obj.write_text(text, encoding="utf-8")
        with pytest.raises(ValueError, match="H-series"):
            loader.load_day_script(path_obj)
        temp_dir.cleanup()


def test_consumer_dispatch_uses_descriptor_fields_not_enum_membership():
    base = DIARY_ACTION_GRAMMAR[DiaryActionVerb.slot_search]
    synthetic = DiaryActionVerbDescriptor(
        verb=base.verb,
        tier=BernieCapabilityTier.confirm,
        mutating=True,
        requires_staff_confirmation=True,
        confirm_actions=(),
        capability_name=base.capability_name,
        implemented=False,
        confirm_affordance_notes="synthetic descriptor for consumer dispatch test",
    )

    assert replay.consumer_dispatch_decision(base) is replay.ConsumerDispatch.route_read_only
    assert replay.consumer_dispatch_decision(synthetic) is replay.ConsumerDispatch.refuse_not_implemented

    implemented_synthetic = replace(
        synthetic,
        implemented=True,
        confirm_actions=DIARY_ACTION_GRAMMAR[DiaryActionVerb.create].confirm_actions,
    )
    assert (
        replay.consumer_dispatch_decision(implemented_synthetic)
        is replay.ConsumerDispatch.route_to_confirm
    )


def test_confirm_affordance_cases_call_runtime_gate_not_notes_text():
    blocked = replay.resolve_action("confirm_booking", affordance_case="blocked_guardrail")
    assert blocked.dispatch is replay.ConsumerDispatch.route_to_confirm
    assert blocked.confirm_affordance_allowed is False
    assert blocked.confirm_affordance_gate == "blocked_guardrail"

    allowed = replay.resolve_action("confirm_booking", affordance_case="allowed")
    assert allowed.confirm_affordance_allowed is True
    assert allowed.confirm_affordance_gate == "allowed"


def test_replay_modules_do_not_import_provider_routes_or_database_models():
    source = inspect.getsource(replay)
    forbidden = [
        "app.routers",
        "app.models",
        "app.services.ai",
        "TestClient",
        "SessionLocal",
        "local_data",
    ]
    for fragment in forbidden:
        assert fragment not in source


def test_replay_modules_do_not_reference_h_series_or_neutral_events():
    fixture_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(loader.FIXTURE_DIR.glob("*.json"))
    ).lower()
    source = inspect.getsource(replay).lower()
    forbidden = [
        "no_structural_change",
        "small_content_delta",
        "large_unexplained_delta",
        "time_grid_delta",
        "ordered_neutral_snapshots",
    ]
    for fragment in forbidden:
        assert fragment not in source
        assert fragment not in fixture_text
