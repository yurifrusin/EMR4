"""Build a route-scoped practitioner-directory REST readiness status."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_APPROVAL_PATH = (
    REPO_ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-rest-route-readiness-approval.json"
)
DEFAULT_SPRINT258_PATH = (
    REPO_ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-sprint258-blocker-closure.json"
)
DEFAULT_GLOBAL_SNAPSHOT_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)

STATUS_SCHEMA_VERSION = "api_spine.practitioner_directory_route_readiness_status.v1"
TARGET_ROUTE = "GET /api/v1/practice/practitioners"
APPROVAL_DECISION = "approved_for_practitioner_directory_rest_route_ready_true"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Readiness artifact does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_practitioner_directory_route_readiness_status(
    *,
    approval_path: Path = DEFAULT_APPROVAL_PATH,
    sprint258_path: Path = DEFAULT_SPRINT258_PATH,
    global_snapshot_path: Path = DEFAULT_GLOBAL_SNAPSHOT_PATH,
    today: date | None = None,
) -> dict[str, object]:
    approval = _load_json(approval_path)
    sprint258 = _load_json(sprint258_path)
    global_snapshot = _load_json(global_snapshot_path)
    today = today or date.today()

    _require(approval["decision"] == APPROVAL_DECISION, "approval decision is not route-ready")
    _require(approval["target_route"] == TARGET_ROUTE, "approval target route drifted")
    _require(
        approval["target_readiness_flag"] == "rest_route_ready",
        "approval target readiness flag drifted",
    )
    _require(approval["approved_value"] is True, "route readiness approval is not true")
    _require(
        approval["approved_scope"]["rest_route_ready_route_scoped_only"] is True,
        "approval is no longer route scoped only",
    )
    _require(
        approval["approved_scope"]["client_scope"] == "authenticated_internal_staff_only",
        "approval client scope drifted",
    )
    _require(
        approval["readiness_fixture_change"]["performed_in_this_payload"] is False,
        "approval payload unexpectedly changes readiness fixture",
    )
    _require(
        all(value is False for value in approval["must_remain_false"].values()),
        "one or more adjacent approval gates no longer remain false",
    )
    _require(
        approval["must_remain_false"] == approval["non_rest_scope_fields"],
        "non-REST scope field list drifted from closed gate list",
    )
    _require(
        date.fromisoformat(approval["approval_expires_on"]) >= today,
        "route readiness approval has expired",
    )

    _require(sprint258["target_route"] == TARGET_ROUTE, "Sprint 258 target route drifted")
    _require(
        sprint258["criteria_status_after_sprint258"][
            "separate_yuri_approval_payload_exists"
        ]
        == "missing_requires_explicit_yuri_approval",
        "Sprint 258 approval-payload prerequisite drifted",
    )
    _require(
        sprint258["criteria_status_after_sprint258"][
            "runtime_test_matrix_passes_in_isolated_run"
        ]
        == "closed",
        "Sprint 258 runtime test matrix prerequisite is not closed",
    )
    _require(
        sprint258["criteria_status_after_sprint258"][
            "external_client_exposure_decision_recorded"
        ]
        == "closed_internal_staff_only",
        "Sprint 258 external-client prerequisite drifted",
    )

    # The global external-readiness status remains an all-false runtime posture.
    # This helper exposes the narrower route-specific approval layer separately.
    _require(global_snapshot["rest_route_ready"] is False, "global rest route readiness flipped")
    _require(
        global_snapshot["external_read_model_runtime_ready"] is False,
        "global external read-model runtime readiness flipped",
    )
    _require(
        global_snapshot["graphql_resolver_ready"] is False,
        "global GraphQL resolver readiness flipped",
    )
    _require(
        global_snapshot["write_authority_ready"] is False,
        "global write authority readiness flipped",
    )

    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "target_route": TARGET_ROUTE,
        "route_readiness_approval_decision": approval["decision"],
        "rest_route_ready": True,
        "route_ready_for_authenticated_internal_staff_read_use": True,
        "approval_expires_on": approval["approval_expires_on"],
        "global_readiness_snapshot_updated": False,
        "global_snapshot_rest_route_ready": global_snapshot["rest_route_ready"],
        "global_external_read_model_runtime_ready": global_snapshot[
            "external_read_model_runtime_ready"
        ],
        "global_graphql_resolver_ready": global_snapshot["graphql_resolver_ready"],
        "global_write_authority_ready": global_snapshot["write_authority_ready"],
        "global_provider_or_directory_runtime_ready": global_snapshot[
            "provider_or_directory_runtime_ready"
        ],
        "adjacent_gate_false_count": len(approval["must_remain_false"]),
        "deployment_ready": approval["must_remain_false"]["deployment_ready"],
        "production_ready": approval["must_remain_false"]["production_ready"],
        "external_patient_client_ready": approval["must_remain_false"][
            "external_patient_client_ready"
        ],
        "rate_limit_posture": approval["residual_risks_accepted_for_this_route_only"][
            "route_specific_rate_limit"
        ],
        "rls_posture": approval["residual_risks_accepted_for_this_route_only"][
            "postgresql_rls"
        ],
        "field_encryption_posture": approval[
            "residual_risks_accepted_for_this_route_only"
        ]["field_level_encryption"],
        "next_migration_step": (
            "keep route-scoped status separate unless a later sprint deliberately "
            "migrates the global external-readiness DAG and snapshot semantics"
        ),
        "sprint_engine_state": "continuing",
        "pause_required": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build route-scoped practitioner-directory REST readiness status."
    )
    parser.add_argument("--approval", type=Path, default=DEFAULT_APPROVAL_PATH)
    parser.add_argument("--sprint258", type=Path, default=DEFAULT_SPRINT258_PATH)
    parser.add_argument("--global-snapshot", type=Path, default=DEFAULT_GLOBAL_SNAPSHOT_PATH)
    args = parser.parse_args()
    print(
        json.dumps(
            build_practitioner_directory_route_readiness_status(
                approval_path=args.approval,
                sprint258_path=args.sprint258,
                global_snapshot_path=args.global_snapshot,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
