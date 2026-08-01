from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-cloud-run-public-https-dev-host-deployment"
)
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
EXPECTED_DIGEST = (
    "sha256:6696b3c97682ba8d02d3b18bab3d5d3d131f8c56c613c1adfca32400f94b3f5d"
)
EXPECTED_URL = "https://raisa-office-web-dev-nnbntbx5yq-ts.a.run.app"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_private_deployment_is_exact_and_public_gate_failed_closed() -> None:
    evidence = load_json(CONTINUITY / "partial-deployment-evidence.json")

    assert evidence["result"] == "blocked_organization_policy_public_invocation"
    repository = evidence["artifact_registry"]
    assert repository["repository"] == "raisa-office-web-dev"
    assert repository["location"] == "australia-southeast1"
    assert repository["format"] == "DOCKER"
    assert repository["mode"] == "STANDARD_REPOSITORY"
    assert repository["created"] is True
    assert repository["digest"] == EXPECTED_DIGEST
    assert len(repository["tags"]) == 2

    service = evidence["cloud_run"]
    assert service["service"] == "raisa-office-web-dev"
    assert service["location"] == "australia-southeast1"
    assert service["url"] == EXPECTED_URL
    assert service["latest_ready_revision"] == "raisa-office-web-dev-00003-9vg"
    assert service["traffic_to_latest_revision_percent"] == 100
    assert service["image_reference"].endswith(f"@{EXPECTED_DIGEST}")
    assert service["runtime_service_account"] == (
        "raisa-office-web-runtime@bernie-emr4-dev.iam.gserviceaccount.com"
    )
    assert service["runtime_service_account_project_role_count"] == 0
    assert service["runtime_service_account_user_managed_key_count"] == 0
    assert service["ready"] is True
    assert service["private"] is True

    configuration = service["configuration"]
    assert configuration == {
        "service_min_instances": 0,
        "service_max_instances": 1,
        "revision_min_instances": 0,
        "revision_max_instances": 1,
        "cpu": "1",
        "memory": "256Mi",
        "concurrency": 20,
        "timeout_seconds": 60,
        "cpu_throttling": True,
        "startup_cpu_boost": False,
        "ingress": "all",
        "session_affinity": False,
        "protocol": "http1",
        "hosting_mode": "public_https_development",
        "expected_public_origin_matches_url": True,
        "secret_reference_count": 0,
        "volume_count": 0,
        "vpc_configuration_present": False,
        "cloud_sql_configuration_present": False,
    }

    gate = evidence["public_invocation_gate"]
    assert gate["attempted_member"] == "allUsers"
    assert gate["attempted_role"] == "roles/run.invoker"
    assert gate["provider_status"] == "FAILED_PRECONDITION"
    assert gate["classification"] == "domain_restricted_sharing_organization_policy"
    assert gate["binding_created"] is False
    assert gate["all_users_binding_count_after_attempt"] == 0
    assert gate["service_remains_private"] is True
    assert gate["alternative"] == "disable_cloud_run_invoker_iam_check"
    assert gate["alternative_executed"] is False


def test_local_residue_is_clean_and_authorized_cloud_resources_are_retained() -> None:
    residue = load_json(CONTINUITY / "final-local-residue-evidence.json")

    assert residue["result"] == "pass_with_authorized_cloud_resources_retained"
    assert residue["local_task_containers"] == 0
    assert residue["local_task_networks"] == 0
    assert residue["local_task_image_tags"] == 0
    assert residue["local_task_temporary_contexts"] == 0
    assert residue["local_task_docker_credential_directories"] == 0
    assert residue["local_raw_error_files"] == 0
    assert residue["credentials_or_tokens_persisted"] == 0
    assert len(residue["cloud_resources_intentionally_retained"]) == 4


def test_continuity_preserves_deployment_and_advances_to_word_terminal_gate() -> None:
    graph = load_json(GRAPH)
    compass = load_json(COMPASS)

    assert graph["graph_revision"] == 180
    assert compass["map_revision"] == 161
    assert compass["source_graph_revision"] == 180

    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-cloud-run-public-https-dev-host-deployment"
    )
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "raisa-cloud-run-api-runtime-identity-enablement",
            "relation": "builds_on",
        }
    ]
    assert compass["journey"][-3]["node_id"] == node["id"]
    assert compass["journey"][-2]["node_id"] == (
        "raisa-cloud-run-public-access-word-online-verification"
    )
    assert compass["journey"][-1]["node_id"] == (
        "raisa-word-online-authenticated-companion-verification"
    )
    assert compass["current_position"]["node_id"] == (
        "raisa-word-online-authenticated-companion-verification"
    )
    assert not any(
        item["id"] == "resume-raisa-word-online-manifest-upload"
        for item in compass["decision_horizon"]
    )
    assert not any(
        item["id"] == "enable-chatgpt-chrome-file-url-access"
        for item in compass["user_owned_decisions"]
    )
