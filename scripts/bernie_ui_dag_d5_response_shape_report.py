"""Safe aggregate response-shape report for Bernie UI DAG D5 delivery."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT_SCHEMA_VERSION = "bernie.ui_dag.d5_response_shape_report.v1"
DEFAULT_REVIEW_PATH = (
    REPO_ROOT / "docs" / "bernie-ui-derived-state-dag-d5-post-implementation-review.json"
)
DEFAULT_SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "bernie_ui_dag_d5"
    / "response_shape_report.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Required response-shape source does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_response_shape_report(review_path: Path = DEFAULT_REVIEW_PATH) -> dict[str, object]:
    review = _load_json(review_path)
    implemented_scope = review["implemented_scope"]
    closed_scope = review["closed_scope"]
    evidence = review["evidence"]

    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "source": "committed_d5_post_implementation_review",
        "implemented_commit": review["implemented_commit"],
        "approval_decision": review["approval_decision"],
        "single_response_assembly_point": implemented_scope[
            "single_response_assembly_point"
        ],
        "response_field_present_when_snapshot_exists": implemented_scope[
            "source_snapshot_required"
        ],
        "response_field_null_without_snapshot": implemented_scope[
            "no_server_session_field_null"
        ],
        "display_model_schema_version": "bernie.ui_view_model.v1",
        "client_confirmation_request_state_default": implemented_scope[
            "client_confirmation_request_state_default"
        ],
        "command_payload_unchanged": implemented_scope["confirm_payload_unchanged"],
        "appointment_write_behavior_unchanged": implemented_scope[
            "appointment_write_behavior_unchanged"
        ],
        "frontend_javascript_unchanged": implemented_scope["frontend_javascript_unchanged"],
        "backend_delivery_test_count": 2,
        "guard_evidence_count": len(evidence),
        "closed_scope_count": sum(value is False for value in closed_scope.values()),
        "closed_scope_total": len(closed_scope),
        "provider_or_live_provider_wiring_ready": False,
        "memory_or_rag_wiring_ready": False,
        "graphql_delivery_ready": False,
        "write_authority_ready": False,
        "external_patient_client_ready": False,
        "additional_route_delivery_ready": False,
        "evidence_label": "backend_response_shape_synthetic_or_fake_provider",
        "next_required_decision": "separate_review_for_any_scope_expansion",
    }
    assert_response_shape_report_safety(report)
    return report


def assert_response_shape_report_safety(report: dict[str, object]) -> None:
    assert report["schema_version"] == REPORT_SCHEMA_VERSION
    assert report["source"] == "committed_d5_post_implementation_review"
    assert report["approval_decision"] == "approved_for_backend_response_delivery_first_slice"
    assert report["single_response_assembly_point"] is True
    assert report["response_field_present_when_snapshot_exists"] is True
    assert report["response_field_null_without_snapshot"] is True
    assert report["display_model_schema_version"] == "bernie.ui_view_model.v1"
    assert report["client_confirmation_request_state_default"] == "idle"
    assert report["command_payload_unchanged"] is True
    assert report["appointment_write_behavior_unchanged"] is True
    assert report["frontend_javascript_unchanged"] is True
    assert report["backend_delivery_test_count"] == 2
    assert report["guard_evidence_count"] >= 6
    assert report["closed_scope_count"] == report["closed_scope_total"]
    assert report["closed_scope_total"] >= 12
    assert report["provider_or_live_provider_wiring_ready"] is False
    assert report["memory_or_rag_wiring_ready"] is False
    assert report["graphql_delivery_ready"] is False
    assert report["write_authority_ready"] is False
    assert report["external_patient_client_ready"] is False
    assert report["additional_route_delivery_ready"] is False
    assert report["evidence_label"] == "backend_response_shape_synthetic_or_fake_provider"
    assert report["next_required_decision"] == "separate_review_for_any_scope_expansion"

    serialized = json.dumps(report, sort_keys=True).casefold()
    for forbidden in [
        "/api/",
        "supervised-booking",
        "confirm_payload",
        "appointment_id",
        "patient_id",
        "practitioner_id",
        "local_data",
        "raw diary",
    ]:
        assert forbidden not in serialized


def load_committed_response_shape_report(
    snapshot_path: Path = DEFAULT_SNAPSHOT_PATH,
) -> dict[str, object]:
    return _load_json(snapshot_path)


def assert_matches_committed_response_shape_report(
    report: dict[str, object],
    snapshot_path: Path = DEFAULT_SNAPSHOT_PATH,
) -> None:
    assert report == load_committed_response_shape_report(snapshot_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a safe aggregate Bernie UI D5 response-shape report."
    )
    parser.add_argument("--review", type=Path, default=DEFAULT_REVIEW_PATH)
    parser.add_argument("--snapshot", type=Path, default=DEFAULT_SNAPSHOT_PATH)
    args = parser.parse_args()
    report = build_response_shape_report(args.review)
    assert_matches_committed_response_shape_report(report, args.snapshot)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
