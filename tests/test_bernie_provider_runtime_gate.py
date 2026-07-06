import json
from pathlib import Path

import pytest

from app.config import (
    LIVE_BERNIE_INTERPRETER_PROVIDERS,
    Settings,
    assert_bernie_provider_allowed_by_runtime_gate,
)
from app.services.bernie_booking_interpreter import GeminiVertexBookingInstructionInterpreter


def _write_gate(path: Path, *, decision: str = "blocked", provider_scope: bool = False):
    payload = {
        "schema_version": "bernie.interpretation_harness_runtime_gate.v1",
        "decision": decision,
        "reviewer": "" if decision == "blocked" else "yuri",
        "reviewed_on": "" if decision == "blocked" else "2026-07-07",
        "scope": {
            "interpretation_harness_runtime_wiring": False,
            "provider_dry_run_wiring": provider_scope,
            "route_integration": provider_scope,
            "database_access": False,
            "memory_or_rag_access": False,
            "historical_diary_material_access": False,
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_fake_and_disabled_bernie_providers_do_not_need_runtime_gate(tmp_path):
    missing_gate = tmp_path / "missing.json"

    assert_bernie_provider_allowed_by_runtime_gate("disabled", missing_gate)
    assert_bernie_provider_allowed_by_runtime_gate("fake", missing_gate)


def test_live_bernie_provider_fails_closed_when_gate_is_blocked(tmp_path):
    gate_path = tmp_path / "gate.json"
    _write_gate(gate_path, decision="blocked", provider_scope=False)

    with pytest.raises(RuntimeError, match="live-provider configuration is blocked"):
        assert_bernie_provider_allowed_by_runtime_gate("gemini_vertex", gate_path)


def test_live_bernie_provider_aliases_fail_closed_when_gate_is_blocked(tmp_path):
    gate_path = tmp_path / "gate.json"
    _write_gate(gate_path, decision="blocked", provider_scope=False)

    for provider in LIVE_BERNIE_INTERPRETER_PROVIDERS:
        with pytest.raises(RuntimeError, match="live-provider configuration is blocked"):
            assert_bernie_provider_allowed_by_runtime_gate(provider, gate_path)


def test_live_bernie_provider_allowlist_tracks_interpreter_aliases():
    assert LIVE_BERNIE_INTERPRETER_PROVIDERS == {
        "gemini",
        "gemini_vertex",
        "vertex",
        "vertex_gemini",
    }
    assert GeminiVertexBookingInstructionInterpreter.metadata.provider == "gemini_vertex"


def test_live_bernie_provider_fails_closed_when_gate_file_missing(tmp_path):
    with pytest.raises(RuntimeError, match="gate could not be read"):
        assert_bernie_provider_allowed_by_runtime_gate(
            "gemini_vertex",
            tmp_path / "missing.json",
        )


def test_live_bernie_provider_requires_nonblocked_provider_scope(tmp_path):
    gate_path = tmp_path / "gate.json"
    _write_gate(gate_path, decision="approved_for_review", provider_scope=False)

    with pytest.raises(RuntimeError, match="live-provider configuration is blocked"):
        assert_bernie_provider_allowed_by_runtime_gate("gemini_vertex", gate_path)


def test_live_bernie_provider_can_only_pass_with_explicit_provider_scope(tmp_path):
    gate_path = tmp_path / "gate.json"
    _write_gate(gate_path, decision="approved_for_review", provider_scope=True)

    assert_bernie_provider_allowed_by_runtime_gate("gemini_vertex", gate_path)


def test_settings_startup_blocks_live_bernie_provider_while_committed_gate_blocked():
    with pytest.raises(RuntimeError, match="live-provider configuration is blocked"):
        Settings(
            _env_file=None,
            bernie_booking_interpreter_provider="gemini_vertex",
        )


def test_settings_startup_allows_default_disabled_bernie_provider():
    settings = Settings(_env_file=None)

    assert settings.bernie_booking_interpreter_provider == "disabled"
