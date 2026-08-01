from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-word-online-authenticated-companion-verification"
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_word_online_companion_passes_with_exact_zero_authority_service() -> None:
    evidence = load_json(CONTINUITY / "browser-word-online-evidence.json")

    assert evidence["result"] == "pass"
    assert evidence["scope"] == {
        "project": "bernie-emr4-dev",
        "region": "australia-southeast1",
        "service": "raisa-office-web-dev",
        "hostname": "raisa-office-web-dev-nnbntbx5yq-ts.a.run.app",
        "word_host_class": "signed_in_personal_word_online_session",
        "data_class": "authored_synthetic",
    }
    repair = evidence["service_repair"]
    assert repair["post_repair_revision"] == "raisa-office-web-dev-00006-xf9"
    assert repair["post_repair_image_digest"] == (
        "sha256:8e06f07e4efd393f38275348d8bd7b136e664c2797c399a89207b66116839324"
    )
    assert repair["traffic_percent_to_post_repair_revision"] == 100
    assert repair["runtime_identity_project_role_count"] == 0
    assert repair["runtime_identity_user_managed_key_count"] == 0
    assert repair["invoker_iam_check_disabled"] is True
    assert repair["all_users_iam_binding_count"] == 0
    assert repair["iam_or_organisation_policy_changes"] == 0


def test_first_attempt_failed_closed_and_repair_released_only_generic_count() -> None:
    evidence = load_json(CONTINUITY / "browser-word-online-evidence.json")

    assert evidence["attempts"][0] == {
        "attempt": "pre_repair",
        "disposition": "fail_closed",
        "office_dialog_opened": True,
        "typed_request_admitted": False,
        "generic_summary_released": False,
        "reason_code": "hosted_diary_capability_mismatch",
    }
    admitted = evidence["attempts"][1]
    assert admitted["disposition"] == "pass"
    assert admitted["native_diary_result_count"] == 3
    assert admitted["generic_summary_result_count"] == 3
    assert admitted["word_summary_retained_after_close"] is True

    detail = evidence["detail_isolation"]
    assert detail["synthetic_patient_detail_visible_in_native_diary"] is True
    assert detail["synthetic_patient_detail_visible_in_word_summary"] is False
    assert detail["request_text_visible_in_word_summary"] is False
    assert detail["document_body_read"] is False
    assert detail["document_body_written"] is False


def test_no_backend_provider_command_or_credential_path_ran() -> None:
    evidence = load_json(CONTINUITY / "browser-word-online-evidence.json")

    assert all(value == 0 for value in evidence["network_observation"].values())
    authority = evidence["authority_and_privacy"]
    for field in (
        "provider_calls",
        "backend_calls",
        "database_reads",
        "database_writes",
        "appointment_commands",
        "confirmations",
        "microphone_access",
    ):
        assert authority[field] == 0
    for field in (
        "account_identifier_persisted",
        "tenant_identifier_persisted",
        "document_identifier_persisted",
        "document_filename_persisted",
    ):
        assert authority[field] is False


def test_cleanup_and_revision_binding_are_terminal() -> None:
    residue = load_json(CONTINUITY / "final-residue-evidence.json")
    graph = load_json(
        ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
    )
    compass = load_json(
        ROOT / "orchestration" / "continuity" / "emr4-compass.json"
    )

    assert all(value == 0 for value in residue["local_residue"].values())
    cleanup = residue["word_document_cleanup"]
    assert cleanup["task_created_blank_documents"] == 2
    assert cleanup["documents_with_authored_content"] == 0
    assert cleanup["moved_to_onedrive_recycle_bin"] == 2
    assert cleanup["recoverable"] is True
    assert cleanup["active_storage_residue"] == 0

    assert graph["graph_revision"] >= 180
    assert compass["map_revision"] >= 161
    assert compass["source_graph_revision"] == graph["graph_revision"]
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-word-online-authenticated-companion-verification"
    )
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "raisa-cloud-run-public-access-word-online-verification",
            "relation": "builds_on",
        }
    ]
    journey = {item["node_id"]: item for item in compass["journey"]}
    architecture_id = "raisa-shared-application-auth-clinician-role-boundary"
    runtime_id = "raisa-shared-application-auth-runtime-foundation"
    persistence_id = "raisa-shared-application-auth-postgresql-persistence"
    transport_id = "raisa-shared-application-auth-runtime-role-secure-transport"
    operational_id = "raisa-shared-application-auth-operational-hardening"
    governance_id = "security-finding-governance"
    assert journey[architecture_id]["lineage_parent"] == node["id"]
    assert journey[runtime_id]["lineage_parent"] == architecture_id
    assert journey[persistence_id]["lineage_parent"] == runtime_id
    assert journey[transport_id]["lineage_parent"] == persistence_id
    assert journey[operational_id]["lineage_parent"] == transport_id
    assert journey[governance_id]["lineage_parent"] == operational_id
    assert compass["current_position"]["node_id"] == governance_id
