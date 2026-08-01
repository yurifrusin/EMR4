"""Read-only programme navigation over the local Ariadne continuity graph.

The Compass renders a human and machine-readable account of strategic position.
It cannot choose a tranche, grant authority, spawn an agent, execute a workflow,
alter Git state, call a provider, or issue an EMR command.
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any, Iterable

try:
    from scripts import ariadne_continuity as continuity
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    import ariadne_continuity as continuity  # type: ignore[no-redef]


SCHEMA_VERSION = "ariadne.compass.v1"
REPORT_VERSION = "ariadne.compass_report.v1"
HORIZON_STATUSES = {"active", "candidate", "deferred", "blocked"}


class CompassError(ValueError):
    """Raised for a fail-closed Compass input or command error."""


def default_compass_path(repo_root: Path) -> Path:
    return repo_root / "orchestration" / "continuity" / "emr4-compass.json"


def _load_object(path: Path, *, label: str) -> dict[str, Any]:
    payload = continuity.load_json(path, label=label)
    if not isinstance(payload, dict):
        raise CompassError(f"{label}_must_be_object")
    return payload


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_array(value: Any, *, allow_empty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(_nonempty_string(item) for item in value)
    )


def _sensitive_key_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text.casefold() in continuity.FORBIDDEN_CONTENT_KEYS:
                errors.append(f"sensitive_field_forbidden:{path}.{key_text}")
            errors.extend(_sensitive_key_errors(child, f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_sensitive_key_errors(child, f"{path}[{index}]"))
    return errors


def _evidence_groups(compass: dict[str, Any]) -> Iterable[tuple[str, Any]]:
    for key in ("north_star", "programme", "current_position"):
        item = compass.get(key)
        if isinstance(item, dict):
            yield key, item.get("evidence")
    for key in ("journey", "decision_horizon", "programme_support_horizon"):
        items = compass.get(key)
        if isinstance(items, list):
            for index, item in enumerate(items):
                if isinstance(item, dict):
                    yield f"{key}:{index}", item.get("evidence")
    decisions = compass.get("user_owned_decisions")
    if isinstance(decisions, list):
        for index, item in enumerate(decisions):
            if isinstance(item, dict):
                yield f"user_owned_decisions:{index}", item.get("evidence")


def _evidence_errors(
    compass: dict[str, Any], *, repo_root: Path, require_evidence_files: bool
) -> list[str]:
    errors: list[str] = []
    for label, values in _evidence_groups(compass):
        if not _string_array(values):
            errors.append(f"compass_evidence_required:{label}")
            continue
        if len(values) != len(set(values)):
            errors.append(f"compass_evidence_duplicate:{label}")
        for value in values:
            if not continuity.is_safe_repo_reference(value):
                errors.append(f"unsafe_repo_reference:compass:{label}:{value}")
            elif require_evidence_files and not (repo_root / value).is_file():
                errors.append(f"evidence_not_found:compass:{label}:{value}")
    return errors


def _has_inheriting_parent(
    node: dict[str, Any], parent_id: str
) -> bool:
    return any(
        relationship.get("node_id") == parent_id
        and relationship.get("relation") in continuity.CONTRACT_INHERITING_RELATIONS
        for relationship in node.get("relationships", [])
        if isinstance(relationship, dict)
    )


def _validate_horizon(
    items: Any,
    *,
    label: str,
    known_boundaries: set[str],
    seen_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(items, list) or (label == "decision_horizon" and not items):
        return [f"{label}_array_required"]
    for index, item in enumerate(items):
        prefix = f"{label}:{index}"
        if not isinstance(item, dict):
            errors.append(f"horizon_item_object_required:{prefix}")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not continuity.ID_PATTERN.fullmatch(item_id):
            errors.append(f"horizon_id_invalid:{prefix}:{item_id}")
        elif item_id in seen_ids:
            errors.append(f"horizon_id_duplicate:{item_id}")
        else:
            seen_ids.add(item_id)
        if item.get("status") not in HORIZON_STATUSES:
            errors.append(f"horizon_status_invalid:{item_id}:{item.get('status')}")
        for key in ("title", "strategic_question", "why_it_matters"):
            if not _nonempty_string(item.get(key)):
                errors.append(f"horizon_{key}_required:{item_id}")
        if not _string_array(item.get("prerequisites")):
            errors.append(f"horizon_prerequisites_required:{item_id}")
        boundary_changes = item.get("boundary_changes")
        if not _string_array(boundary_changes, allow_empty=True):
            errors.append(f"horizon_boundary_changes_array_required:{item_id}")
            continue
        if len(boundary_changes) != len(set(boundary_changes)):
            errors.append(f"horizon_boundary_change_duplicate:{item_id}")
        for boundary in boundary_changes:
            if boundary not in known_boundaries:
                errors.append(f"horizon_boundary_unknown:{item_id}:{boundary}")
    return errors


def validate_compass(
    compass: dict[str, Any],
    graph: dict[str, Any],
    *,
    repo_root: Path,
    require_evidence_files: bool = True,
) -> list[str]:
    """Return deterministic structural, provenance and continuity errors."""

    errors = _sensitive_key_errors(compass)
    graph_errors = continuity.validate_graph(
        graph, repo_root=repo_root, require_evidence_files=require_evidence_files
    )
    errors.extend(f"source_graph:{reason}" for reason in graph_errors)

    if compass.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"compass_schema_version_invalid:{compass.get('schema_version')}")
    if compass.get("project_id") != graph.get("project_id"):
        errors.append(
            f"compass_project_mismatch:{compass.get('project_id')}:{graph.get('project_id')}"
        )
    if not isinstance(compass.get("map_revision"), int) or compass.get("map_revision", 0) < 1:
        errors.append("compass_map_revision_invalid")
    if compass.get("source_graph_revision") != graph.get("graph_revision"):
        errors.append(
            "compass_graph_revision_mismatch:"
            f"{compass.get('source_graph_revision')}:{graph.get('graph_revision')}"
        )
    if not _nonempty_string(compass.get("updated_at")):
        errors.append("compass_updated_at_required")
    if not _nonempty_string(compass.get("orientation_statement")):
        errors.append("compass_orientation_statement_required")

    for key in ("north_star", "programme"):
        item = compass.get(key)
        if not isinstance(item, dict):
            errors.append(f"compass_{key}_object_required")
            continue
        required = ("title", "summary") if key == "north_star" else (
            "id",
            "title",
            "master_plan_phase",
            "summary",
        )
        for field in required:
            if not _nonempty_string(item.get(field)):
                errors.append(f"compass_{key}_{field}_required")

    errors.extend(
        _evidence_errors(
            compass,
            repo_root=repo_root,
            require_evidence_files=require_evidence_files,
        )
    )

    nodes = continuity._node_index(graph)
    journey = compass.get("journey")
    journey_ids: list[str] = []
    if not isinstance(journey, list) or not journey:
        errors.append("compass_journey_array_required")
    else:
        for index, step in enumerate(journey):
            if not isinstance(step, dict):
                errors.append(f"journey_step_object_required:{index}")
                continue
            node_id = step.get("node_id")
            if not isinstance(node_id, str) or node_id not in nodes:
                errors.append(f"journey_node_unknown:{index}:{node_id}")
                continue
            if node_id in journey_ids:
                errors.append(f"journey_node_duplicate:{node_id}")
            node = nodes[node_id]
            if node.get("status") != "accepted":
                errors.append(f"journey_node_not_accepted:{node_id}:{node.get('status')}")
            lineage_parent = step.get("lineage_parent")
            if index == 0:
                if lineage_parent is not None:
                    errors.append(f"journey_root_parent_forbidden:{node_id}:{lineage_parent}")
            elif not isinstance(lineage_parent, str) or lineage_parent not in journey_ids:
                errors.append(f"journey_parent_not_earlier:{node_id}:{lineage_parent}")
            elif not _has_inheriting_parent(node, lineage_parent):
                errors.append(f"journey_lineage_not_in_graph:{node_id}:{lineage_parent}")
            for key in ("strategic_role", "outcome"):
                if not _nonempty_string(step.get(key)):
                    errors.append(f"journey_{key}_required:{node_id}")
            journey_ids.append(node_id)

    current = compass.get("current_position")
    if not isinstance(current, dict):
        errors.append("current_position_object_required")
    else:
        current_id = current.get("node_id")
        if not isinstance(current_id, str) or current_id not in nodes:
            errors.append(f"current_position_node_unknown:{current_id}")
        else:
            current_node = nodes[current_id]
            if current_node.get("status") != "accepted":
                errors.append(
                    f"current_position_not_accepted:{current_id}:{current_node.get('status')}"
                )
            if not journey_ids or journey_ids[-1] != current_id:
                errors.append(f"current_position_not_journey_terminal:{current_id}")
            if not graph_errors:
                current_audit = continuity.audit_graph(
                    graph, repo_root=repo_root, node_id=current_id
                )
                for reason in current_audit.get("reasons", []):
                    errors.append(f"current_position_continuity:{reason}")
        for key in ("strategic_role", "why_now", "outcome"):
            if not _nonempty_string(current.get(key)):
                errors.append(f"current_position_{key}_required")
        for key in ("unlocks", "does_not_solve"):
            if not _string_array(current.get(key)):
                errors.append(f"current_position_{key}_required")

    governance = graph.get("governance", {})
    known_boundaries = set(governance.get("closed_boundaries", []))
    seen_horizon_ids: set[str] = set()
    errors.extend(
        _validate_horizon(
            compass.get("decision_horizon"),
            label="decision_horizon",
            known_boundaries=known_boundaries,
            seen_ids=seen_horizon_ids,
        )
    )
    errors.extend(
        _validate_horizon(
            compass.get("programme_support_horizon"),
            label="programme_support_horizon",
            known_boundaries=known_boundaries,
            seen_ids=seen_horizon_ids,
        )
    )

    user_decisions = compass.get("user_owned_decisions")
    seen_decision_ids: set[str] = set()
    if not isinstance(user_decisions, list) or not user_decisions:
        errors.append("user_owned_decisions_array_required")
    else:
        for index, decision in enumerate(user_decisions):
            if not isinstance(decision, dict):
                errors.append(f"user_decision_object_required:{index}")
                continue
            decision_id = decision.get("id")
            if not isinstance(decision_id, str) or not continuity.ID_PATTERN.fullmatch(decision_id):
                errors.append(f"user_decision_id_invalid:{index}:{decision_id}")
            elif decision_id in seen_decision_ids:
                errors.append(f"user_decision_id_duplicate:{decision_id}")
            else:
                seen_decision_ids.add(decision_id)
            for key in ("question", "required_before"):
                if not _nonempty_string(decision.get(key)):
                    errors.append(f"user_decision_{key}_required:{decision_id}")

    if not _string_array(compass.get("map_limits")):
        errors.append("compass_map_limits_required")
    return sorted(set(errors))


def build_compass_report(
    compass: dict[str, Any], graph: dict[str, Any], *, repo_root: Path
) -> dict[str, Any]:
    """Build a deterministic read-only programme-position report."""

    errors = validate_compass(compass, graph, repo_root=repo_root)
    if errors:
        return {
            "schema_version": REPORT_VERSION,
            "status": "revision_required",
            "reasons": errors,
            "map_revision": compass.get("map_revision"),
            "graph_revision": graph.get("graph_revision"),
        }

    nodes = continuity._node_index(graph)
    current_id = compass["current_position"]["node_id"]
    current_audit = continuity.audit_graph(
        graph, repo_root=repo_root, node_id=current_id
    )["nodes"][0]
    journey = []
    for step in compass["journey"]:
        node = nodes[step["node_id"]]
        journey.append(
            {
                **copy.deepcopy(step),
                "title": node["title"],
                "kind": node["kind"],
                "status": node["status"],
            }
        )
    current_position = copy.deepcopy(compass["current_position"])
    current_position["title"] = nodes[current_id]["title"]
    return {
        "schema_version": REPORT_VERSION,
        "status": "passed",
        "reasons": [],
        "project_id": compass["project_id"],
        "map_revision": compass["map_revision"],
        "graph_revision": graph["graph_revision"],
        "updated_at": compass["updated_at"],
        "orientation_statement": compass["orientation_statement"],
        "north_star": copy.deepcopy(compass["north_star"]),
        "programme": copy.deepcopy(compass["programme"]),
        "journey": journey,
        "current_position": current_position,
        "continuity": {
            "status": current_audit["status"],
            "required_contracts": copy.deepcopy(current_audit["required_contracts"]),
            "authorized_openings": copy.deepcopy(current_audit["authorized_openings"]),
            "inherited_closed_boundaries": list(
                current_audit["inherited_closed_boundaries"]
            ),
        },
        "decision_horizon": copy.deepcopy(compass["decision_horizon"]),
        "programme_support_horizon": copy.deepcopy(
            compass["programme_support_horizon"]
        ),
        "user_owned_decisions": copy.deepcopy(compass["user_owned_decisions"]),
        "map_limits": list(compass["map_limits"]),
    }


def _markdown_bullets(items: Iterable[str]) -> list[str]:
    return [f"- {item}" for item in items]


def render_markdown(report: dict[str, Any]) -> str:
    """Render a passed Compass report for a human reader."""

    if report.get("status") != "passed":
        reasons = report.get("reasons", [])
        lines = ["# Ariadne Compass — revision required", ""]
        lines.extend(_markdown_bullets(reasons))
        return "\n".join(lines) + "\n"

    lines = [
        "# Ariadne Compass — EMR4",
        "",
        f"> {report['orientation_statement']}",
        "",
        "## North star",
        "",
        f"**{report['north_star']['title']}**",
        "",
        report["north_star"]["summary"],
        "",
        "## Programme position",
        "",
        f"**{report['programme']['title']}** — {report['programme']['master_plan_phase']}",
        "",
        report["programme"]["summary"],
        "",
        "## Journey so far",
        "",
    ]
    for index, step in enumerate(report["journey"], start=1):
        branch_note = (
            "This is the journey foundation"
            if step["lineage_parent"] is None
            else f"Lineage parent: `{step['lineage_parent']}`"
        )
        lines.extend(
            [
                f"{index}. **{step['strategic_role']} — {step['title']}**",
                f"   {step['outcome']} {branch_note}.",
            ]
        )

    current = report["current_position"]
    lines.extend(
        [
            "",
            "## Current position",
            "",
            f"**{current['strategic_role']} — {current['title']}**",
            "",
            f"**Why this proof came next:** {current['why_now']}",
            "",
            current["outcome"],
            "",
            "### What this unlocks",
            "",
            *_markdown_bullets(current["unlocks"]),
            "",
            "### What it does not solve",
            "",
            *_markdown_bullets(current["does_not_solve"]),
            "",
            "## Continuity and authority",
            "",
            f"- Current-node audit: **{report['continuity']['status']}**",
        ]
    )
    for contract in report["continuity"]["required_contracts"]:
        lines.append(f"- Contract `{contract['contract_id']}`: **{contract['status']}**")
    if report["continuity"]["authorized_openings"]:
        for opening in report["continuity"]["authorized_openings"]:
            lines.append(
                f"- Bounded opening `{opening['boundary']}`: {opening.get('scope', 'See source evidence.')}"
            )
    opened_boundaries = {
        opening["boundary"] for opening in report["continuity"]["authorized_openings"]
    }
    remaining_boundaries = [
        item
        for item in report["continuity"]["inherited_closed_boundaries"]
        if item not in opened_boundaries
    ]
    lines.append(
        "- All other named boundaries remain closed: "
        + ", ".join(f"`{item}`" for item in remaining_boundaries)
        + "."
    )

    lines.extend(["", "## Product decision horizon", ""])
    for item in report["decision_horizon"]:
        lines.extend(
            [
                f"### {item['title']} — {item['status']}",
                "",
                item["strategic_question"],
                "",
                item["why_it_matters"],
                "",
                "Prerequisites:",
                "",
                *_markdown_bullets(item["prerequisites"]),
                "",
            ]
        )

    if report["programme_support_horizon"]:
        lines.extend(["## Programme-support horizon", ""])
        for item in report["programme_support_horizon"]:
            lines.extend(
                [
                    f"### {item['title']} — {item['status']}",
                    "",
                    item["strategic_question"],
                    "",
                    item["why_it_matters"],
                    "",
                    "Prerequisites:",
                    "",
                    *_markdown_bullets(item["prerequisites"]),
                    "",
                ]
            )

    lines.extend(["## Decisions that remain Yuri's", ""])
    for decision in report["user_owned_decisions"]:
        lines.extend(
            [
                f"- **{decision['question']}**",
                f"  Required before: {decision['required_before']}",
            ]
        )

    lines.extend(["", "## Map limits", ""])
    lines.extend(_markdown_bullets(report["map_limits"]))
    evidence = sorted(
        {
            value
            for _, values in _evidence_groups(report)
            if isinstance(values, list)
            for value in values
        }
    )
    lines.extend(["", "## Evidence index", ""])
    lines.extend(f"- `{value}`" for value in evidence)
    lines.extend(
        [
            "",
            f"_Compass map revision {report['map_revision']}; continuity graph revision {report['graph_revision']}._",
        ]
    )
    return "\n".join(lines) + "\n"


def validation_report(
    compass: dict[str, Any], graph: dict[str, Any], *, repo_root: Path
) -> dict[str, Any]:
    errors = validate_compass(compass, graph, repo_root=repo_root)
    return {
        "schema_version": "ariadne.compass_validation.v1",
        "status": "passed" if not errors else "revision_required",
        "reasons": errors,
        "map_revision": compass.get("map_revision"),
        "graph_revision": graph.get("graph_revision"),
        "journey_count": len(compass.get("journey", []))
        if isinstance(compass.get("journey"), list)
        else 0,
        "decision_count": len(compass.get("decision_horizon", []))
        if isinstance(compass.get("decision_horizon"), list)
        else 0,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect the read-only Ariadne Compass.")
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--graph", type=Path)
    parser.add_argument("--compass", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate", help="Validate map, evidence, lineage and current continuity.")
    show = subparsers.add_parser("show", help="Show the current programme position.")
    show.add_argument("--format", choices=["json", "markdown"], default="markdown")
    return parser


def _emit_json(payload: Any) -> None:
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        repo_root = continuity.resolve_repo_root(args.repo_root)
        graph_path = continuity.resolve_repo_path(
            args.graph if args.graph else continuity.default_graph_path(repo_root),
            repo_root,
            label="graph",
        )
        compass_path = continuity.resolve_repo_path(
            args.compass if args.compass else default_compass_path(repo_root),
            repo_root,
            label="compass",
        )
        graph = _load_object(graph_path, label="graph")
        compass = _load_object(compass_path, label="compass")
        if args.command == "validate":
            result = validation_report(compass, graph, repo_root=repo_root)
            _emit_json(result)
            return 0 if result["status"] == "passed" else 2
        if args.command == "show":
            result = build_compass_report(compass, graph, repo_root=repo_root)
            if args.format == "json":
                _emit_json(result)
            else:
                sys.stdout.write(render_markdown(result))
            return 0 if result["status"] == "passed" else 2
        raise CompassError(f"unsupported_command:{args.command}")
    except (CompassError, continuity.ContinuityError, OSError) as error:
        _emit_json(
            {
                "schema_version": "ariadne.compass_command.v1",
                "status": "revision_required",
                "reasons": [str(error)],
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
