"""Static release check for practitioner-directory route-scoped readiness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.practitioner_directory_route_readiness_status import (
    TARGET_ROUTE,
    build_practitioner_directory_route_readiness_status,
)


CONSUMER_BOUNDARY_PATH = (
    REPO_ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-route-readiness-consumer-boundary.json"
)
RELEASE_CHECK_SCHEMA_VERSION = (
    "api_spine.practitioner_directory_route_readiness_release_check.v1"
)
ALLOWED_DECISION = "route_scoped_readiness_status_may_feed_static_release_checks_only"
ALLOWED_NEXT_STEP = "add static release-check consumption only, if useful, without runtime wiring"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Release-check artifact does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def build_practitioner_directory_route_readiness_release_check(
    *,
    consumer_boundary_path: Path = CONSUMER_BOUNDARY_PATH,
) -> dict[str, object]:
    boundary = _load_json(consumer_boundary_path)
    status = build_practitioner_directory_route_readiness_status()

    _require(boundary["decision"] == ALLOWED_DECISION, "consumer boundary decision drifted")
    _require(boundary["target_route"] == TARGET_ROUTE, "consumer boundary target route drifted")
    _require(
        boundary["next_allowed_step"] == ALLOWED_NEXT_STEP,
        "consumer boundary no longer allows only static release-check consumption",
    )
    _require(
        "static CI or pytest release-gate checks that emit aggregate readiness status"
        in boundary["allowed_consumers"],
        "static CI/pytest release-gate checks are not an allowed consumer",
    )

    forbidden_consumers = set(boundary["forbidden_consumers"])
    for forbidden in (
        "production app routers or services",
        "deployment or production configuration",
        "external patient-client enablement",
        "global external-readiness DAG or blocked_readiness_status mutation",
        "appointment or practitioner write authority",
    ):
        _require(forbidden in forbidden_consumers, f"missing forbidden consumer: {forbidden}")

    _require(status["target_route"] == TARGET_ROUTE, "status target route drifted")
    _require(status["rest_route_ready"] is True, "route-scoped readiness is not true")
    _require(
        status["route_ready_for_authenticated_internal_staff_read_use"] is True,
        "internal-staff read-use readiness is not true",
    )
    _require(
        status["global_readiness_snapshot_updated"] is False,
        "global readiness snapshot was updated",
    )
    for key in (
        "global_snapshot_rest_route_ready",
        "global_external_read_model_runtime_ready",
        "global_graphql_resolver_ready",
        "global_write_authority_ready",
        "global_provider_or_directory_runtime_ready",
        "deployment_ready",
        "production_ready",
        "external_patient_client_ready",
    ):
        _require(status[key] is False, f"{key} unexpectedly became ready")
    _require(status["adjacent_gate_false_count"] == 8, "adjacent gate count drifted")
    _require(status["pause_required"] is False, "release check unexpectedly requires pause")
    _require(
        status["sprint_engine_state"] == "continuing",
        "sprint engine state is no longer continuing",
    )

    return {
        "schema_version": RELEASE_CHECK_SCHEMA_VERSION,
        "target_route": TARGET_ROUTE,
        "source_status_schema_version": status["schema_version"],
        "consumer_boundary_schema_version": boundary["schema_version"],
        "static_release_check_ready": True,
        "allowed_consumer": "static CI or pytest release-gate checks that emit aggregate readiness status",
        "runtime_consumers_allowed": False,
        "global_readiness_snapshot_updated": status["global_readiness_snapshot_updated"],
        "rest_route_ready": status["rest_route_ready"],
        "deployment_ready": status["deployment_ready"],
        "production_ready": status["production_ready"],
        "external_patient_client_ready": status["external_patient_client_ready"],
        "global_graphql_resolver_ready": status["global_graphql_resolver_ready"],
        "global_provider_or_directory_runtime_ready": status[
            "global_provider_or_directory_runtime_ready"
        ],
        "global_write_authority_ready": status["global_write_authority_ready"],
        "adjacent_gate_false_count": status["adjacent_gate_false_count"],
        "pause_required": status["pause_required"],
        "sprint_engine_state": status["sprint_engine_state"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the static practitioner-directory route readiness release check."
    )
    parser.add_argument("--consumer-boundary", type=Path, default=CONSUMER_BOUNDARY_PATH)
    args = parser.parse_args()
    print(
        json.dumps(
            build_practitioner_directory_route_readiness_release_check(
                consumer_boundary_path=args.consumer_boundary,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
