from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-cloud-run-public-access-word-online-verification"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_public_access_evidence_is_exact_service_only() -> None:
    evidence = load_json(CONTINUITY / "public-access-and-route-evidence.json")

    assert evidence["result"] == "pass"
    assert evidence["scope"] == {
        "project": "bernie-emr4-dev",
        "region": "australia-southeast1",
        "service": "raisa-office-web-dev",
        "hostname": "raisa-office-web-dev-nnbntbx5yq-ts.a.run.app",
    }
    control = evidence["cloud_run_control"]
    assert control["invoker_iam_check_disabled"] is True
    assert control["all_users_iam_binding_count"] == 0
    assert control["latest_ready_revision"] == "raisa-office-web-dev-00005-w82"
    assert control["traffic_percent_to_latest_revision"] == 100
    assert len(evidence["route_matrix"]) == 11
    assert all(
        item.get("observed_status", item.get("final_observed_status"))
        == item.get("expected_status", item.get("final_expected_status"))
        for item in evidence["route_matrix"]
    )


def test_word_online_gate_stopped_before_manifest_transmission() -> None:
    evidence = load_json(CONTINUITY / "browser-word-online-evidence.json")

    assert evidence["public_browser_gate"]["result"] == "pass"
    word = evidence["word_online_gate"]
    assert word["result"] == "blocked_before_manifest_transmission"
    assert word["blocker_code"] == "chrome_extension_file_url_access_required"
    for field in (
        "task_specific_manifest_selected",
        "manifest_uploaded",
        "add_in_loaded",
        "synthetic_request_submitted",
        "office_dialog_opened",
        "generic_summary_released",
    ):
        assert word[field] is False

    boundary = evidence["privacy_and_authority"]
    assert all(value is False for value in (
        boundary["document_body_read"],
        boundary["document_body_written"],
        boundary["raw_synthetic_request_persisted"],
        boundary["account_identifier_persisted"],
        boundary["tenant_identifier_persisted"],
        boundary["document_identifier_persisted"],
    ))
    assert all(
        boundary[field] == 0
        for field in (
            "provider_calls",
            "backend_calls",
            "database_reads",
            "database_writes",
            "commands_or_confirmations",
        )
    )


def test_manifest_is_public_https_read_document_only() -> None:
    manifest = (
        CONTINUITY / "manifest.xml"
    ).read_text(encoding="utf-8")

    origin = "https://raisa-office-web-dev-nnbntbx5yq-ts.a.run.app"
    assert f"<AppDomain>{origin}</AppDomain>" in manifest
    assert (
        f"{origin}/taskpane.html?reception_one_companion_demo=true"
        in manifest
    )
    assert "<Permissions>ReadDocument</Permissions>" in manifest
    assert "ReadWriteDocument" not in manifest
    assert "localhost" not in manifest


def test_continuity_preserves_public_gate_and_binds_terminal_word_descendant() -> None:
    graph = load_json(
        ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
    )
    compass = load_json(
        ROOT / "orchestration" / "continuity" / "emr4-compass.json"
    )

    assert graph["graph_revision"] == 180
    assert compass["map_revision"] == 161
    assert compass["source_graph_revision"] == 180
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-cloud-run-public-access-word-online-verification"
    )
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "raisa-cloud-run-public-https-dev-host-deployment",
            "relation": "builds_on",
        }
    ]
    assert any(
        "file URLs" in gate
        for gate in node["unresolved_gates"]
    )
    descendant = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-word-online-authenticated-companion-verification"
    )
    assert descendant["status"] == "accepted"
    assert descendant["relationships"] == [
        {
            "node_id": node["id"],
            "relation": "builds_on",
        }
    ]
    assert compass["journey"][-1]["node_id"] == descendant["id"]
    assert compass["current_position"]["node_id"] == descendant["id"]
