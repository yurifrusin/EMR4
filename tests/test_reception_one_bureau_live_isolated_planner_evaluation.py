"""One-call visible-UI isolated planner evaluation contract."""

from __future__ import annotations

import json
from pathlib import Path

from app.services import reception_one_isolated_vertex_planner as isolated
from scripts import reception_one_bureau_live_isolated_planner_evaluation as live


ROOT = Path(__file__).resolve().parents[1]


def test_fresh_authority_is_exactly_one_call_and_no_retry() -> None:
    authority = json.loads(live.AUTHORITY_PATH.read_text(encoding="utf-8"))
    assert authority["authority_granted"] is True
    assert authority["model_id"] == "gemini-2.5-flash"
    assert authority["absolute_call_ceiling"] == 1
    assert authority["terminal_correction_call_ceiling"] == 0
    assert authority["continuity_binding"] == {
        "graph_revision": 158,
        "compass_revision": 139,
        "compass_source_graph_revision": 158,
    }
    assert "second_provider_call_or_retry" in authority["forbidden"]


def test_runtime_and_harness_enforce_authority_call_ceiling() -> None:
    service_source = Path(isolated.__file__).read_text(encoding="utf-8")
    harness_source = Path(live.__file__).read_text(encoding="utf-8")
    assert "maximum_provider_calls=call_ceiling" in service_source
    assert "provider_calls <= call_ceiling" in service_source
    assert "parent.get(\"absolute_provider_call_ceiling\") != 1" in (
        harness_source
    )
    assert "occupied-turn-002-ledger.json" in harness_source
    assert '"retry_performed": False' in harness_source


def test_child_environment_omits_every_provider_key_and_static_credential(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5434/test",
    )
    child = live._safe_child_environment("synthetic-only")
    forbidden = {
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
    }
    assert forbidden.isdisjoint(child)
    assert child[
        "RECEPTION_ONE_PRODUCT_CONTEXT_VERTEX_PLANNER_ENABLED"
    ] == "true"
    assert child[
        "BERNIE_BOOKING_INTERPRETER_FALLBACK_TO_DETERMINISTIC"
    ] == "false"


def test_browser_path_is_real_selector_to_authenticated_route() -> None:
    source = Path(live.__file__).read_text(encoding="utf-8")
    assert 'planner.select_option("isolated_vertex")' in source
    assert "page.expect_response(" in source
    assert "request_interception_used" in source
    assert "page.route(" not in source
    assert live.INSTRUCTION == (
        "Extend Margaret Thompson's appointment with Dr Alex Shera "
        "to 45 minutes."
    )


def test_exact_provider_binding_and_proposal_only_boundary() -> None:
    assert live.EXPECTED_BINDING == isolated.EXPECTED_BINDING
    assert live.GRAPH_REVISION == 158
    assert live.COMPASS_REVISION == 139
    authority = json.loads(live.AUTHORITY_PATH.read_text(encoding="utf-8"))
    boundary = authority["requested_exact_boundary"]
    assert boundary["appointment_write_authority"] is False
    assert boundary["confirmation_authority"] is False
    assert boundary["fallback"] is False
    assert boundary["global_endpoint"] is False
    assert boundary["cache_creation"] is False
