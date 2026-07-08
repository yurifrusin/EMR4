"""Build a safe aggregate status for external read-model readiness."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.external_read_model_gap_status import (
    DEFAULT_INVENTORY_PATH,
    REQUIRED_CLOSED_GATE_PHRASES,
    build_gap_status,
    load_gap_inventory,
    parse_gap_rows,
)
DEFAULT_DAG_PATH = (
    REPO_ROOT / "docs" / "api-spine" / "external-read-model-readiness-dag.json"
)
DEFAULT_ROOT_INVENTORY_PATH = (
    REPO_ROOT / "docs" / "api-spine" / "external-router-read-root-inventory.md"
)
DEFAULT_COMBINED_REVIEW_PATH = (
    REPO_ROOT
    / "docs"
    / "api-spine"
    / "external-read-model-combined-readiness-review.md"
)
DEFAULT_APPROVED_GATE_PATH = (
    REPO_ROOT / "docs" / "api-spine" / "practitioner-directory-approved-gate.json"
)

STATUS_SCHEMA_VERSION = "api_spine.external_read_model_readiness_check.v1"
GAP_STATUS_SCHEMA_VERSION = "api_spine.external_read_model_gap_status.v1"

EXPECTED_DAG_SCHEMA_VERSION = "api_spine.external_read_model_readiness_dag.v1"
EXPECTED_COMPLETED_NODE_COUNT = 9
EXPECTED_BLOCKED_RUNTIME_GATE_COUNT = 3
EXPECTED_READY_FLAGS = {
    "external_read_model_runtime_ready": False,
    "graphql_resolver_ready": False,
    "rest_route_ready": False,
    "provider_or_directory_runtime_ready": False,
    "runtime_or_memory_ready": False,
    "write_authority_ready": False,
    "raw_compat_mode_change_ready": False,
}
EXPECTED_APPROVAL_DECISION = "approved_for_rest_route_first_slice"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"External readiness DAG does not exist: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _root_inventory_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise ValueError(f"External read-root inventory does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    section = text.split("## External Read Route Bridge", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(
            {
                "surface": cells[0].strip("`"),
                "source": cells[1].strip("`"),
                "coverage": cells[3].strip("`"),
                "posture": cells[4].strip("`"),
            }
        )
    return rows


def _assert_directory_root_gap_disjunction(
    root_inventory_path: Path,
    gap_inventory_path: Path = DEFAULT_INVENTORY_PATH,
) -> dict[str, int | bool]:
    root_rows = _root_inventory_rows(root_inventory_path)
    gap_rows_all = parse_gap_rows(load_gap_inventory(gap_inventory_path))
    root_gap_surfaces = {
        row["surface"] for row in root_rows if row["posture"] == "read_model_gap"
    }
    selected_gap_surfaces = {row["surface"] for row in gap_rows_all}
    assert selected_gap_surfaces < root_gap_surfaces

    rows = [row for row in root_rows if row["surface"].startswith("Query.directorySearch")]
    local_route_rows = [
        row
        for row in rows
        if row["source"].startswith("GET ") and row["posture"] == "read_only_route"
    ]
    gap_rows = [
        row
        for row in rows
        if row["source"] == "none"
        and row["coverage"] == "gap"
        and row["posture"] == "read_model_gap"
    ]

    assert len(local_route_rows) == 2
    assert len(gap_rows) == 2
    assert {row["surface"] for row in local_route_rows}.isdisjoint(
        {row["surface"] for row in gap_rows}
    )

    return {
        "root_surface_count": len(root_rows),
        "root_full_count": sum(row["coverage"] == "full" for row in root_rows),
        "root_partial_count": sum(row["coverage"] == "partial" for row in root_rows),
        "root_gap_count": sum(row["posture"] == "read_model_gap" for row in root_rows),
        "root_gap_disjunction_matched": True,
        "selected_gap_surface_count": len(selected_gap_surfaces),
        "selected_gap_surfaces_are_root_gaps": True,
        "unselected_root_gap_count": len(root_gap_surfaces - selected_gap_surfaces),
        "directory_local_read_route_count": len(local_route_rows),
        "directory_unimplemented_source_count": len(gap_rows),
        "directory_local_and_unimplemented_sources_disjoint": True,
    }


def _combined_review_closed_gate_count(text: str) -> int:
    section = text.split("## Closed Gates", 1)[1].split("\n## ", 1)[0]
    return sum(1 for line in section.splitlines() if line.startswith("- "))


def _assert_combined_review(path: Path) -> dict[str, object]:
    if not path.exists():
        raise ValueError(f"Combined external read-model review does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    compact = " ".join(text.split())
    assert "Overall decision: `blocked`" in text
    assert "Sprint engine state: `continuing`" in text
    assert "Pause required: `false`" in text
    assert "does not authorize" in text
    assert "does not prove runtime GraphQL resolver implementation" in compact
    for flag in EXPECTED_READY_FLAGS:
        assert f"| `{flag}` | `false` |" in text
    return {
        "combined_review_decision": "blocked",
        "combined_review_false_count": len(EXPECTED_READY_FLAGS),
        "combined_review_closed_gate_count": _combined_review_closed_gate_count(text),
    }


def build_readiness_status(
    *,
    dag_path: Path = DEFAULT_DAG_PATH,
    root_inventory_path: Path = DEFAULT_ROOT_INVENTORY_PATH,
    combined_review_path: Path = DEFAULT_COMBINED_REVIEW_PATH,
    approved_gate_path: Path = DEFAULT_APPROVED_GATE_PATH,
) -> dict[str, object]:
    dag = _load_json(dag_path)
    gap_status = build_gap_status()
    root_disjunction = _assert_directory_root_gap_disjunction(root_inventory_path)
    combined_review_status = _assert_combined_review(combined_review_path)
    approved_gate = _load_json(approved_gate_path)

    assert dag["schema_version"] == EXPECTED_DAG_SCHEMA_VERSION
    assert dag["decision"] == "blocked"
    assert dag["readiness"] == EXPECTED_READY_FLAGS
    assert approved_gate["decision"] == EXPECTED_APPROVAL_DECISION
    assert approved_gate["approval"]["reviewer"] == "yuri"
    assert approved_gate["approval"]["go_no_go_acknowledged"] is True
    assert approved_gate["permitted_scope"]["rest_route_first_slice_only"] is True
    for blocked_scope in [
        "sdl_changes_allowed",
        "graphql_resolver_allowed",
        "graphql_runtime_dependency_allowed",
        "provider_or_memory_trove_allowed",
        "write_authority_allowed",
        "readiness_flag_changes_allowed",
        "deployment_or_production_readiness_allowed",
    ]:
        assert approved_gate["permitted_scope"][blocked_scope] is False
    assert approved_gate["readiness_posture"] == EXPECTED_READY_FLAGS
    assert all(node["runtime_authority"] is False for node in dag["nodes"])

    completed_nodes = [
        node
        for node in dag["nodes"]
        if node["status"] in {"static_complete", "design_complete_no_runtime"}
    ]
    runtime_gate_nodes = [
        node for node in dag["nodes"] if node["kind"] == "runtime_gate"
    ]
    combined_nodes = [
        node for node in dag["nodes"] if node["id"] == "combined_readiness_review"
    ]
    approval_gate_nodes = [
        node for node in dag["nodes"] if node["id"] == "practitioner_directory_approval_gate"
    ]

    assert len(completed_nodes) == EXPECTED_COMPLETED_NODE_COUNT
    assert len(runtime_gate_nodes) == EXPECTED_BLOCKED_RUNTIME_GATE_COUNT
    assert len(combined_nodes) == 1
    assert len(approval_gate_nodes) == 1
    assert combined_nodes[0]["status"] == "static_complete"
    assert combined_nodes[0]["artifact"] == str(
        combined_review_path.relative_to(REPO_ROOT)
    ).replace("\\", "/")
    assert approval_gate_nodes[0]["kind"] == "approval_gate"
    assert approval_gate_nodes[0]["status"] == "static_complete"
    assert approval_gate_nodes[0]["artifact"] == (
        "docs/api-spine/practitioner-directory-approved-gate.json"
    )
    assert approval_gate_nodes[0]["runtime_authority"] is False
    assert all(node["status"] == "blocked" for node in runtime_gate_nodes)
    assert gap_status["closed_gate_count"] == len(REQUIRED_CLOSED_GATE_PHRASES)
    assert combined_review_status["combined_review_closed_gate_count"] >= gap_status[
        "closed_gate_count"
    ]

    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "gap_status_schema_version": GAP_STATUS_SCHEMA_VERSION,
        "dag_schema_version": dag["schema_version"],
        "dag_decision": dag["decision"],
        "dag_sprint": dag["sprint"],
        "completed_static_or_design_node_count": len(completed_nodes),
        "blocked_runtime_gate_count": len(runtime_gate_nodes),
        "combined_readiness_review_status": combined_nodes[0]["status"],
        "combined_readiness_review_artifact_present": True,
        "approval_gate_node_count": len(approval_gate_nodes),
        "approval_gate_decision": approved_gate["decision"],
        "approval_gate_artifact_present": True,
        "approval_gate_runtime_authority": approval_gate_nodes[0]["runtime_authority"],
        **combined_review_status,
        "dag_all_readiness_false": all(value is False for value in dag["readiness"].values()),
        "dag_static_node_count": len(completed_nodes),
        "dag_blocked_node_count": len(runtime_gate_nodes),
        "gap_surface_count": gap_status["surface_count"],
        "model_only_gap_count": gap_status["model_only_gap_count"],
        "no_source_gap_count": gap_status["no_source_gap_count"],
        "missing_route_count": gap_status["missing_route_count"],
        "route_gap_count": gap_status["route_gap_count"],
        "route_and_shape_gap_count": gap_status["route_and_shape_gap_count"],
        "source_and_licensing_gap_count": gap_status[
            "source_and_licensing_gap_count"
        ],
        **root_disjunction,
        **EXPECTED_READY_FLAGS,
        "runtime_authority_node_count": 0,
        "closed_gate_count": len(dag["closed_gates"]),
        "closed_gate_consistency": True,
        "sprint_engine_state": "continuing",
        "pause_required": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a safe aggregate external read-model readiness status."
    )
    parser.add_argument("--dag", type=Path, default=DEFAULT_DAG_PATH)
    parser.add_argument(
        "--root-inventory", type=Path, default=DEFAULT_ROOT_INVENTORY_PATH
    )
    parser.add_argument(
        "--combined-review", type=Path, default=DEFAULT_COMBINED_REVIEW_PATH
    )
    args = parser.parse_args()
    print(
        json.dumps(
            build_readiness_status(
                dag_path=args.dag,
                root_inventory_path=args.root_inventory,
                combined_review_path=args.combined_review,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
