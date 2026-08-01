from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-cloud-run-api-runtime-identity-enablement"
)


def test_exact_api_and_zero_role_identity_result_is_recorded() -> None:
    evidence = json.loads((CONTINUITY / "evidence.json").read_text(encoding="utf-8"))

    assert evidence["result"] == "raisa_cloud_run_api_runtime_identity_enablement_pass"
    assert evidence["mutations"]["apis_enabled"] == [
        "run.googleapis.com",
        "artifactregistry.googleapis.com",
    ]
    assert evidence["mutations"]["runtime_service_accounts_created"] == [
        "raisa-office-web-runtime@bernie-emr4-dev.iam.gserviceaccount.com"
    ]
    assert evidence["mutations"]["runtime_project_roles_granted"] == []
    assert evidence["mutations"]["service_account_keys_created"] == 0
    verification = evidence["post_mutation_verification"]
    assert verification["cloud_run_admin_api_enabled"] is True
    assert verification["artifact_registry_api_enabled"] is True
    assert verification["runtime_service_account_project_role_count"] == 0
    assert verification["runtime_service_account_user_managed_key_count"] == 0
    assert verification["artifact_registry_repository"]["exists"] is False
    assert verification["cloud_run_service"]["exists"] is False


def test_external_creation_and_deployment_remain_closed() -> None:
    evidence = json.loads((CONTINUITY / "evidence.json").read_text(encoding="utf-8"))
    mutations = evidence["mutations"]

    assert mutations["artifact_registry_repositories_created"] == 0
    assert mutations["cloud_run_services_created"] == 0
    assert mutations["public_invoker_bindings_created"] == 0
    assert mutations["images_built_or_pushed"] == 0
    assert mutations["deployments"] == 0
    assert mutations["billing_changes"] == 0


def test_continuity_and_compass_bind_the_new_control_plane_result() -> None:
    graph = json.loads(
        (
            ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
        ).read_text(encoding="utf-8")
    )
    compass = json.loads(
        (
            ROOT / "orchestration" / "continuity" / "emr4-compass.json"
        ).read_text(encoding="utf-8")
    )

    assert graph["graph_revision"] == 180
    assert compass["map_revision"] == 161
    assert compass["source_graph_revision"] == 180
    node = next(
        item
        for item in graph["nodes"]
        if item["id"] == "raisa-cloud-run-api-runtime-identity-enablement"
    )
    assert node["status"] == "accepted"
    assert node["relationships"] == [
        {
            "node_id": "raisa-cloud-run-public-https-dev-host-readiness",
            "relation": "builds_on",
        }
    ]
    assert any(item["node_id"] == node["id"] for item in compass["journey"])
