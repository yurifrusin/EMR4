"""Focused guards for the Reception One visual-synthesis descendant."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path

from google.cloud import aiplatform_v1
from google.protobuf.json_format import ParseDict

from scripts import reception_one_visual_synthesis_contracts as contracts
from scripts import reception_one_visual_synthesis_launcher as launcher


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "bernie-reception-one-visual-interaction-synthesis-plan.md"
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
DIARY = ROOT / "docs" / "diary"
BROWSER_EVIDENCE = (
    ROOT
    / "orchestration"
    / "prototypes"
    / "reception-one-visual-synthesis"
    / "browser-acceptance-evidence.json"
)
OCCUPIED_AUDIT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "reception-one-visual-synthesis"
    / "occupied-external-audit.json"
)


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _node(graph: dict, node_id: str) -> dict:
    matches = [node for node in graph["nodes"] if node["id"] == node_id]
    assert len(matches) == 1
    return matches[0]


def test_plan_freezes_unoccupied_ui_and_exact_vertex_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "The user-facing UI remains deterministic and unoccupied." in text
    assert "`gemini-2.5-flash`" in text
    assert "`bernie-emr4-dev`" in text
    assert (
        "`emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com`"
        in text
    )
    assert "`keyless_impersonated_service_account_adc`" in text
    assert "`australia-southeast1`" in text
    assert "Absolute Vertex call ceiling: two." in text
    assert "Application cost ceiling: USD 1." in text
    assert "No FastAPI route, GraphQL field or mutation" in text


def test_continuity_and_compass_bind_the_accepted_descendant() -> None:
    graph = _json(GRAPH)
    compass = _json(COMPASS)
    node = _node(graph, "reception-one-visual-interaction-synthesis")

    assert graph["graph_revision"] >= 53
    assert compass["source_graph_revision"] == graph["graph_revision"]
    assert compass["map_revision"] >= 40
    assert node["status"] == "accepted"
    assert node["kind"] == "synthesis"
    assert {
        opening["boundary"] for opening in node["authority"]["authorized_openings"]
    } == {"container-runtime", "model-runtime", "provider-call"}
    assert any(
        "UI node remains deterministic" in note
        for note in node["authority"]["notes"]
    )

    journey = {step["node_id"]: step for step in compass["journey"]}
    assert node["id"] in journey
    current = _node(graph, compass["current_position"]["node_id"])
    assert current["status"] == "accepted"
    assert current["id"] in journey
    assert not any(
        item["id"] == "reception-one-visual-synthesis"
        for item in compass["decision_horizon"]
    )


def test_cell_requests_are_exact_fictional_and_credential_free() -> None:
    for name in (
        "dry-run-cell-request.json",
        "dry-run-002-cell-request.json",
        "dry-run-003-cell-request.json",
        "occupied-cell-request.json",
    ):
        request = _json(contracts.ARTIFACT_ROOT / name)
        assert contracts.validate_cell_request(request) == []
        serialized = json.dumps(request, sort_keys=True).casefold()
        for forbidden in (
            "service_account",
            "oauth",
            "credential",
            "aiplatform",
            "googleapis",
            "gemini-2.5-flash",
            "bernie-emr4-dev",
            "patient",
        ):
            assert forbidden not in serialized


def test_vertex_design_request_is_typed_toolless_and_officially_parseable() -> None:
    request = contracts.build_vertex_request(
        _json(contracts.CELL_REQUEST_PATH)
    )
    assert set(request) == {
        "systemInstruction",
        "contents",
        "generationConfig",
    }
    config = request["generationConfig"]
    assert config["temperature"] == 0
    assert config["maxOutputTokens"] == 1024
    assert config["responseMimeType"] == "application/json"
    assert config["thinkingConfig"] == {"thinkingBudget": 0}
    assert "tools" not in request
    assert "toolConfig" not in request
    assert "cachedContent" not in request
    assert config["responseSchema"] == contracts.provider_response_schema()
    ParseDict(
        {
            "model": (
                "projects/bernie-emr4-dev/locations/australia-southeast1/"
                "publishers/google/models/gemini-2.5-flash"
            ),
            **request,
        },
        aiplatform_v1.types.GenerateContentRequest.pb()(),
    )


def test_design_proofreader_repairs_only_mechanical_ordering() -> None:
    fixture_packet = contracts.provider_free_fixture_response()
    draft = contracts.extract_provider_draft(fixture_packet)
    proof = contracts.proofread(draft)

    assert proof["disposition"] == "released"
    assert proof["human_gate"] is True
    assert proof["findings"] == []
    assert proof["safe_repairs"] == [
        "evidence_ids_deterministically_ordered",
        "risk_ids_deterministically_ordered",
    ]
    assert proof["release"]["authority_class"] == "design_candidate_only"
    assert proof["release"]["evidence_ids"] == sorted(contracts.EVIDENCE)
    assert set(proof["released_field_manifest"]) == set(
        contracts.RELEASE_FIELDS
    )


def test_design_proofreader_rejects_authority_or_ungrounded_evidence() -> None:
    draft = contracts.extract_provider_draft(
        contracts.provider_free_fixture_response()
    )
    draft["authority_class"] = "implementation_authority"
    draft["evidence_ids"][-1] = "invented"
    proof = contracts.proofread(draft)

    assert proof["disposition"] == "edge_aborted"
    assert proof["release"] is None
    assert "authority_class_invalid" in proof["findings"]
    assert "evidence_ids_invalid" in proof["findings"]


def test_provider_free_candidate_matches_release_schema() -> None:
    jsonschema = __import__("jsonschema")
    draft = contracts.extract_provider_draft(
        contracts.provider_free_fixture_response()
    )
    release = contracts.proofread(draft)["release"]
    jsonschema.validate(
        release,
        _json(contracts.RELEASE_SCHEMA_PATH),
    )


def test_visual_launcher_is_unique_exact_and_credential_free_for_cell() -> None:
    for source in launcher.ALLOWED_REQUEST_SOURCES:
        plan = launcher.build_plan(source)
        assert launcher.validate_plan(plan) == []
        assert plan["build_context"]["files"][3] == {
            "source": source,
            "target": "cell-request.json",
        }
        assert plan["cell_boundary"]["credential_material"] is False
        assert plan["cell_boundary"]["provider_or_service_account_details"] is False
        assert plan["cell_boundary"]["environment"] == []
        assert plan["cell_boundary"]["mounts"] == []
        assert plan["broker_process"]["api_key_environment_forwarded"] is False
        assert (
            plan["broker_process"]["google_application_credentials_forwarded"]
            is False
        )
    assert launcher.NETWORK != "ariadne-vertex-sydney-gemini-25-internal"


def test_occupied_candidate_failed_closed_without_retry_or_release() -> None:
    audit = _json(OCCUPIED_AUDIT)

    assert audit["result"] == "revision_required"
    assert audit["provider_observation"]["http_status"] == 200
    assert audit["proofreader"]["disposition"] == "edge_aborted"
    assert audit["proofreader"]["findings"] == ["priority_order_invalid"]
    assert audit["proofreader"]["released_field_manifest"] == []
    assert audit["proofreader"]["released_values"] == {}
    assert audit["retry_decision"]["retry_performed"] is False
    assert audit["ledger"]["provider_calls_consumed"] == 1
    assert audit["ledger"]["status"] == "consumed"
    assert audit["explicit_exclusions"]["raw_provider_response_recorded"] is False
    assert audit["explicit_exclusions"]["provider_or_regional_fallback_performed"] is False


def test_deterministic_ui_keeps_model_out_and_projects_distinct_candidates() -> None:
    source = (DIARY / "meta-grid.js").read_text(encoding="utf-8")
    html = (DIARY / "diary.html").read_text(encoding="utf-8")
    css = (DIARY / "meta-grid.css").read_text(encoding="utf-8")

    for required in (
        'intentTokens: document.getElementById("meta-grid-intent-tokens")',
        'const increment = 15;',
        'const span = 1;',
        '["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]',
        "appointment_write_authority: false",
        'replace(/(?: · [^·]+ selected)+$/, "")',
        r"/^(\d{1,2}):(\d{2})(?::\d{2})?$/",
    ):
        assert required in source
    for forbidden in (
        "fetch(",
        "XMLHttpRequest",
        "new WebSocket",
        "generativelanguage.googleapis.com",
        "aiplatform.googleapis.com",
        "gemini-2.5-flash",
    ):
        assert forbidden not in source
    for required in (
        'id="meta-grid-intent-tokens"',
        'id="meta-grid-conversation-request"',
        'aria-label="Keyboard shortcuts"',
    ):
        assert required in html
    for required in (
        ".meta-grid-schedule-layout",
        ".meta-grid-selection-panel",
        ".meta-grid-keyboard-hints",
        "@media (max-width: 620px)",
    ):
        assert required in css


def test_exact_raster_browser_evidence_is_hashed_responsive_and_read_only() -> None:
    evidence = _json(BROWSER_EVIDENCE)

    assert evidence["result"] == "browser_pass"
    assert (
        evidence["evidence_mode"]
        == "authenticated_local_authored_synthetic_fixture_browser"
    )
    assert evidence["route_interception"] is False
    assert evidence["api_interception"] is False
    assert evidence["authority"] == {
        "appointment_write_authority": False,
        "confirmation_control_activated": False,
        "operational_receipt_produced": False,
        "proposal_handoff_activated": False,
        "provider_runtime_in_ui": False,
    }
    assert evidence["browser_console_unexpected_warnings_or_errors"] == []
    assert evidence["browser_page_errors"] == []
    assert evidence["network"]["unexpected_http_responses"] == []
    assert evidence["network"]["forbidden_external_hosts"] == []
    assert (
        evidence["network"]["expected_default_off_committed_event_feed_404_count"]
        == 4
    )
    assert all(evidence["keyboard"].values())

    assert [row["id"] for row in evidence["viewports"]] == [
        "desktop_landscape",
        "tablet_landscape",
        "tablet_portrait",
        "phone_portrait",
    ]
    for row in evidence["viewports"]:
        assert row["page_horizontal_overflow_px"] == 0
        assert row["host_horizontal_overflow_px"] == 0
        assert row["enabled_controls_below_44px"] == []
        assert row["slot_count"] == row["distinct_card_tops"] == 8
        assert row["selected_count"] == 1
        assert row["selection_panel_visible"] is True
        assert row["appointment_write_authority"] is True

    screenshot_root = BROWSER_EVIDENCE.parent
    for record in evidence["screenshots"]:
        screenshot = screenshot_root / record["file"]
        payload = screenshot.read_bytes()
        assert hashlib.sha256(payload).hexdigest() == record["sha256"]
        assert int.from_bytes(payload[16:20], "big") == record["width"]
        assert int.from_bytes(payload[20:24], "big") == record["height"]
