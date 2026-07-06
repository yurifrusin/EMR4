import json
import inspect
from pathlib import Path
from typing import get_args

import pytest

from app.routers import appointments
from app.config import (
    LIVE_BERNIE_INTERPRETER_PROVIDERS,
    Settings,
    assert_bernie_provider_allowed_by_runtime_gate,
)
from app.services.bernie_booking_interpreter import (
    DisabledBookingInstructionInterpreter,
    FakeBookingInstructionInterpreter,
    GeminiVertexBookingInstructionInterpreter,
    get_booking_instruction_interpreter,
)


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


def test_interpreter_factory_uses_live_provider_allowlist():
    for provider in LIVE_BERNIE_INTERPRETER_PROVIDERS:
        interpreter = get_booking_instruction_interpreter(provider)
        assert isinstance(interpreter, GeminiVertexBookingInstructionInterpreter)

    assert isinstance(
        get_booking_instruction_interpreter("fake"),
        FakeBookingInstructionInterpreter,
    )
    assert isinstance(
        get_booking_instruction_interpreter("disabled"),
        DisabledBookingInstructionInterpreter,
    )
    assert isinstance(
        get_booking_instruction_interpreter("unknown-provider"),
        DisabledBookingInstructionInterpreter,
    )


def test_provider_metadata_boundary_matches_live_provider_allowlist():
    non_live_interpreters = [
        DisabledBookingInstructionInterpreter(),
        FakeBookingInstructionInterpreter(),
    ]
    for interpreter in non_live_interpreters:
        assert interpreter.metadata.live_provider is False
        assert interpreter.metadata.provider not in LIVE_BERNIE_INTERPRETER_PROVIDERS

    live_interpreter = GeminiVertexBookingInstructionInterpreter()
    assert live_interpreter.metadata.live_provider is True
    assert live_interpreter.metadata.mode == "live"
    assert live_interpreter.metadata.provider in LIVE_BERNIE_INTERPRETER_PROVIDERS


def test_live_provider_aliases_resolve_to_one_canonical_metadata_provider():
    canonical_providers = {
        get_booking_instruction_interpreter(provider).metadata.provider
        for provider in LIVE_BERNIE_INTERPRETER_PROVIDERS
    }

    assert canonical_providers == {GeminiVertexBookingInstructionInterpreter.metadata.provider}


def test_interpreter_metadata_provider_values_are_unique_and_schema_declared():
    providers = [
        DisabledBookingInstructionInterpreter.metadata.provider,
        FakeBookingInstructionInterpreter.metadata.provider,
        GeminiVertexBookingInstructionInterpreter.metadata.provider,
    ]
    declared_provider_values = set(
        get_args(
            type(GeminiVertexBookingInstructionInterpreter.metadata).model_fields[
                "provider"
            ].annotation
        )
    )

    assert len(providers) == len(set(providers))
    assert set(providers) <= declared_provider_values


def test_interpret_route_uses_settings_provider_boundary():
    source = inspect.getsource(appointments.interpret_bernie_booking_instruction)

    assert "settings.bernie_booking_interpreter_provider" in source
    assert "get_booking_instruction_interpreter(" in source
    assert "GeminiVertexBookingInstructionInterpreter" not in source
    for provider in LIVE_BERNIE_INTERPRETER_PROVIDERS:
        assert provider not in source


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
