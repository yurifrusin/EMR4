"""Run predefined safe reports over a neutral historical diary graph."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.historical_diary_output_safety import (
    load_json,
    validate_historical_diary_output,
)


DEFAULT_OUTPUT = Path(
    "local_data/historical-diary-trove/inventory/neutral_graph_report_h20.json"
)
NOTABLE_EVENT_CLASSES = ("large_unexplained_delta", "time_grid_delta")


def build_neutral_graph_report(graph_payload: dict[str, Any]) -> dict[str, Any]:
    validate_historical_diary_output(graph_payload)

    nodes_by_id = {node["node_id"]: node for node in graph_payload.get("nodes", [])}
    roots_by_id = {
        node["node_id"]: node
        for node in graph_payload.get("nodes", [])
        if node["node_kind"] == "root"
    }
    queries = [
        *_event_class_queries(graph_payload.get("edges", []), nodes_by_id, roots_by_id),
        *_delta_bucket_queries(graph_payload.get("edges", []), nodes_by_id, roots_by_id),
    ]
    output = {
        "classifier": {
            "output_class": "neutral_graph_query_report",
            "version": 1,
            "sample_only": True,
        },
        "privacy": {
            "emits_document_text": False,
            "emits_filenames": False,
            "emits_raw_paths": False,
            "emits_exact_document_timestamps": False,
            "emits_patient_or_staff_labels": False,
        },
        "generated_at_utc": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "graph": {
            "version": 1,
            "sample_only": True,
            "output_class": "neutral_graph_query_report",
            "root_count": graph_payload["graph"]["root_count"],
            "node_count": graph_payload["graph"]["node_count"],
            "edge_count": graph_payload["graph"]["edge_count"],
            "transition_count": graph_payload["graph"]["transition_count"],
        },
        "queries": queries,
    }
    validate_historical_diary_output(output)
    return output


def _event_class_queries(
    edges: list[dict[str, Any]],
    nodes_by_id: dict[str, dict[str, Any]],
    roots_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    queries = []
    for event_class in NOTABLE_EVENT_CLASSES:
        roots = []
        target_node_id = f"event_class:{event_class}"
        for edge in edges:
            if (
                edge["edge_kind"] == "has_event_class_count"
                and edge["target_node_id"] == target_node_id
            ):
                roots.append(
                    {
                        "root_label": roots_by_id[edge["source_node_id"]]["root_label"],
                        "event_class": nodes_by_id[edge["target_node_id"]][
                            "event_class"
                        ],
                        "count": int(edge["count"]),
                    }
                )
        queries.append(
            {
                "query_id": "roots_by_notable_event_class",
                "event_class": event_class,
                "result_count": len(roots),
                "roots": sorted(roots, key=lambda root: root["root_label"]),
            }
        )
    return queries


def _delta_bucket_queries(
    edges: list[dict[str, Any]],
    nodes_by_id: dict[str, dict[str, Any]],
    roots_by_id: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    values = sorted(
        node["value"]
        for node in nodes_by_id.values()
        if node["node_kind"] == "delta_bucket"
    )
    queries = []
    for value in values:
        roots = []
        target_node_id = f"delta_bucket:{value}"
        for edge in edges:
            if (
                edge["edge_kind"] == "has_delta_bucket"
                and edge["target_node_id"] == target_node_id
            ):
                roots.append(
                    {
                        "root_label": roots_by_id[edge["source_node_id"]]["root_label"],
                        "value": nodes_by_id[edge["target_node_id"]]["value"],
                        "min": int(edge["min"]),
                        "max": int(edge["max"]),
                    }
                )
        queries.append(
            {
                "query_id": "roots_by_delta_bucket",
                "value": value,
                "result_count": len(roots),
                "roots": sorted(roots, key=lambda root: root["root_label"]),
            }
        )
    return queries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("neutral_graph_json", type=Path)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = build_neutral_graph_report(load_json(args.neutral_graph_json))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"wrote safe neutral graph report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
