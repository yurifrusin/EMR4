"""Build a safe aggregate status for external read-model gaps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY_PATH = (
    REPO_ROOT / "docs" / "api-spine" / "external-router-read-model-gap-inventory.md"
)

INVENTORY_SCHEMA_VERSION = "api_spine.external_read_model_gap_inventory.v1"
STATUS_SCHEMA_VERSION = "api_spine.external_read_model_gap_status.v1"

EXPECTED_SURFACES = {
    "Query.practice.practitioners",
    "Query.patient.reminders",
    "Query.patient.messages",
    "Query.directorySearch.RACGP_GUIDELINES",
    "Query.directorySearch.COCHRANE_LIBRARY",
}

EXPECTED_COVERAGE_COUNTS = {
    "model_only": 3,
    "none": 2,
}

EXPECTED_GAP_POSTURE_COUNTS = {
    "route_gap": 1,
    "route_and_shape_gap": 2,
    "source_and_licensing_gap": 2,
}

REQUIRED_CLOSED_GATE_PHRASES = {
    "adding GraphQL resolvers or GraphQL mutations",
    "adding new REST routes",
    "provider calls or live provider gates",
    "provider dry-run wiring",
    "runtime FGA clients",
    "external patient clients",
    "H15/H-series runtime imports",
    "memory/RAG/GraphRAG runtime wiring",
    "broad historical diary trove mining",
    "Access AI invocation wiring",
    "reminder, message, SMS, practitioner, or directory write authority",
    "model-to-database writes outside REST command handlers",
    "raw compatibility deprecation mode changes",
}


def load_gap_inventory(path: Path = DEFAULT_INVENTORY_PATH) -> str:
    if not path.exists():
        raise ValueError(f"External read-model gap inventory does not exist: {path}")
    return path.read_text(encoding="utf-8")


def parse_gap_rows(text: str) -> list[dict[str, str]]:
    section = text.split("## Gap Inventory", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows.append(
            {
                "surface": cells[0].strip("`"),
                "route_source": cells[2].strip("`"),
                "coverage": cells[3].strip("`"),
                "gap_posture": cells[5].strip("`"),
            }
        )
    return rows


def _counts(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def assert_gap_inventory_static_and_blocked(text: str) -> None:
    rows = parse_gap_rows(text)
    assert len(rows) == 5
    assert {row["surface"] for row in rows} == EXPECTED_SURFACES
    assert all(row["route_source"] == "none" for row in rows)
    assert _counts([row["coverage"] for row in rows]) == EXPECTED_COVERAGE_COUNTS
    assert _counts([row["gap_posture"] for row in rows]) == EXPECTED_GAP_POSTURE_COUNTS

    assert "does not create GraphQL resolvers" in text
    assert "does not authorize" in text
    assert "does not prove runtime GraphQL resolver implementation" in " ".join(
        text.split()
    )
    for phrase in REQUIRED_CLOSED_GATE_PHRASES:
        assert phrase in text


def build_gap_status(path: Path = DEFAULT_INVENTORY_PATH) -> dict[str, object]:
    text = load_gap_inventory(path)
    assert_gap_inventory_static_and_blocked(text)
    rows = parse_gap_rows(text)
    coverage_counts = _counts([row["coverage"] for row in rows])
    posture_counts = _counts([row["gap_posture"] for row in rows])
    missing_route_count = sum(1 for row in rows if row["route_source"] == "none")

    return {
        "schema_version": STATUS_SCHEMA_VERSION,
        "inventory_schema_version": INVENTORY_SCHEMA_VERSION,
        "surface_count": len(rows),
        "coverage_kind_count": len(coverage_counts),
        "gap_posture_kind_count": len(posture_counts),
        "model_only_gap_count": coverage_counts["model_only"],
        "no_source_gap_count": coverage_counts["none"],
        "missing_route_count": missing_route_count,
        "route_gap_count": posture_counts["route_gap"],
        "route_and_shape_gap_count": posture_counts["route_and_shape_gap"],
        "source_and_licensing_gap_count": posture_counts["source_and_licensing_gap"],
        "closed_gate_count": len(REQUIRED_CLOSED_GATE_PHRASES),
        "graphql_resolver_ready": False,
        "rest_route_ready": False,
        "provider_or_directory_runtime_ready": False,
        "runtime_or_memory_ready": False,
        "write_authority_ready": False,
        "raw_compat_mode_change_ready": False,
        "sprint_engine_state": "continuing",
        "pause_required": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a safe aggregate external read-model gap status."
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=DEFAULT_INVENTORY_PATH,
        help="Path to the external read-model gap inventory markdown file.",
    )
    args = parser.parse_args()
    print(json.dumps(build_gap_status(args.inventory), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
