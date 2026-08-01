from __future__ import annotations

import json
from pathlib import Path

from scripts import (
    reception_one_bureau_cost_bounded_provider_blocked as provider_blocked,
    reception_one_bureau_cost_bounded_occupied_retry as retry,
)


ROOT = Path(__file__).resolve().parents[1]


def test_authority_freezes_exact_one_call_dialogue_and_usd_one_total() -> None:
    authority = json.loads(
        retry.AUTHORITY_PATH.read_text(encoding="utf-8")
    )
    assert authority["authority_granted"] is True
    assert authority["provider"] == "google_vertex_ai"
    assert authority["model_id"] == "gemini-2.5-flash"
    assert authority["project"] == "bernie-emr4-dev"
    assert authority["service_account"] == (
        "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
    )
    assert authority["authentication"] == (
        "keyless_impersonated_service_account_adc"
    )
    assert authority["location"] == "australia-southeast1"
    assert authority["endpoint_hostname"] == (
        "australia-southeast1-aiplatform.googleapis.com"
    )
    assert authority["absolute_call_ceiling"] == 1
    assert authority["terminal_correction_call_ceiling"] == 0
    assert authority["cumulative_cost_ceiling_usd"] == 1
    assert authority["pre_call_reservation_usd"] == 0.02
    assert authority["unchanged_duplicate_calls_permitted"] is False
    assert authority["call_after_first_admission_permitted"] is False


def test_plan_requires_visible_selection_and_proposal_only_release() -> None:
    plan = (
        ROOT
        / "docs"
        / "bernie-reception-one-bureau-cost-bounded-occupied-retry-plan.md"
    ).read_text(encoding="utf-8")
    assert "aria-selected=true" in plan
    assert "proposal-only" in plan
    assert "No provider call may follow the first admitted proposal" in plan
    assert "USD 0.0038049" in plan
    assert "USD 0.02" in plan


def test_browser_path_clicks_before_isolated_submission() -> None:
    source = Path(retry.__file__).read_text(encoding="utf-8")
    click_at = source.index("selected.click()")
    selected_at = source.index(
        'selected.get_attribute("aria-selected") == "true"'
    )
    planner_at = source.index(
        'planner.select_option("isolated_vertex")'
    )
    submit_at = source.index('request_box.press("Enter")')
    assert click_at < selected_at < planner_at < submit_at
    assert "extended_selected_appointment_id" in source
    assert '"selected_appointment_id_retained": False' in source


def test_child_environment_keeps_existing_credential_omission() -> None:
    source = Path(retry.base.__file__).read_text(encoding="utf-8")
    assert '"RECEPTION_ONE_PRODUCT_CONTEXT_VERTEX_PLANNER_ENABLED": "true"' in source
    assert "GOOGLE_APPLICATION_CREDENTIALS" not in (
        source[
            source.index("def _safe_child_environment"):
            source.index("def _remove_runtime_dir")
        ]
    )
    assert "GEMINI_API_KEY" not in (
        source[
            source.index("def _safe_child_environment"):
            source.index("def _remove_runtime_dir")
        ]
    )
    assert "GOOGLE_API_KEY" not in (
        source[
            source.index("def _safe_child_environment"):
            source.index("def _remove_runtime_dir")
        ]
    )


def test_attempt_binding_is_preserved_after_preprovider_closeout() -> None:
    authority = json.loads(
        retry.AUTHORITY_PATH.read_text(encoding="utf-8")
    )
    graph = json.loads(
        (
            ROOT
            / "orchestration"
            / "continuity"
            / "emr4-continuity-graph.json"
        ).read_text(encoding="utf-8")
    )
    compass = json.loads(
        (
            ROOT
            / "orchestration"
            / "continuity"
            / "emr4-compass.json"
        ).read_text(encoding="utf-8")
    )
    binding = authority["continuity_binding"]
    assert binding == {
        "graph_revision": 163,
        "compass_revision": 144,
        "compass_source_graph_revision": 163,
    }
    assert graph["graph_revision"] > binding["graph_revision"]
    assert compass["map_revision"] > binding["compass_revision"]
    assert compass["source_graph_revision"] == graph["graph_revision"]
    nodes = {node["id"]: node for node in graph["nodes"]}
    assert (
        nodes["reception-one-bureau-cost-bounded-occupied-retry"][
            "status"
        ]
        == "rejected"
    )


def test_provider_blocked_gate_has_zero_call_contract() -> None:
    source = Path(provider_blocked.__file__).read_text(encoding="utf-8")
    assert '"provider_calls": 0' in source
    assert '"credential_reads": 0' in source
    assert "v68.build_provider_blocked_evidence()" in source
