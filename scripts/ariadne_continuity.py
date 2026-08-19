"""Local, metadata-only continuity graph for EMR4 task lineage.

The graph is advisory.  It records provenance, inherited obligations and
candidate knowledge; it cannot grant authority, accept product work, spawn an
agent, alter Git refs or execute a product command.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


SCHEMA_VERSION = "ariadne.continuity_graph.v1"
ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEAD_PATTERN = re.compile(r"^[0-9a-f]{40}$")

NODE_KINDS = {
    "foundation",
    "concept",
    "implementation",
    "integration",
    "review",
    "tooling",
    "exploration",
    "synthesis",
    "maintenance",
}
NODE_STATUSES = {"planned", "active", "accepted", "rejected", "superseded", "closed"}
RELATIONS = {
    "builds_on",
    "implements",
    "validates",
    "forked_from",
    "synthesizes",
    "supersedes",
    "protects",
}
CONTRACT_INHERITING_RELATIONS = {
    "builds_on",
    "implements",
    "validates",
    "forked_from",
    "synthesizes",
}
CONTRACT_STATES = {"satisfied", "waived", "gap"}
DECISION_STATES = {"candidate", "accepted", "rejected"}
HARVEST_STATES = {"candidate", "promoted", "rejected"}
EVIDENCE_CATEGORIES = {
    "plans",
    "acceptances",
    "receipts",
    "tests",
    "closeouts",
    "findings",
}
FORBIDDEN_CONTENT_KEYS = {
    "password",
    "secret",
    "token",
    "access_token",
    "bearer_token",
    "credential",
    "credentials",
    "raw_transcript",
    "transcript",
    "prompt",
    "model_reasoning",
    "pii",
}


class ContinuityError(ValueError):
    """Raised for a fail-closed graph or command error."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def emit(payload: Any) -> None:
    sys.stdout.write(canonical_json(payload))


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() and (candidate / "AGENTS.md").is_file():
            return candidate
    raise ContinuityError("repository_root_not_found")


def resolve_repo_root(explicit: Path | None) -> Path:
    """Resolve a genuine EMR4 repository root, including explicit input."""

    root = explicit.resolve() if explicit else find_repo_root(Path.cwd())
    if not (root / ".git").exists() or not (root / "AGENTS.md").is_file():
        raise ContinuityError(f"repository_markers_missing:{root}")
    return root


def ensure_inside_repo(path: Path, repo_root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as error:
        raise ContinuityError(f"{label}_outside_repository:{resolved}") from error
    return resolved


def resolve_repo_path(raw: str | Path, repo_root: Path, *, label: str) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    return ensure_inside_repo(candidate, repo_root, label=label)


def default_graph_path(repo_root: Path) -> Path:
    return repo_root / "orchestration" / "continuity" / "emr4-continuity-graph.json"


def load_json(path: Path, *, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ContinuityError(f"{label}_not_found:{path}") from error
    except json.JSONDecodeError as error:
        raise ContinuityError(f"{label}_invalid_json:{error.msg}") from error


def load_graph(path: Path) -> dict[str, Any]:
    payload = load_json(path, label="graph")
    if not isinstance(payload, dict):
        raise ContinuityError("graph_must_be_object")
    return payload


def is_safe_repo_reference(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or "://" in value:
        return False
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        return False
    if ":" in pure.parts[0]:
        return False
    return True


def is_acceptance_reference(value: Any) -> bool:
    if not is_safe_repo_reference(value):
        return False
    path = PurePosixPath(str(value))
    return (
        path.parts[:3] == ("orchestration", "agent_inbox", "codex")
        and path.name.endswith("-acceptance.md")
    )


def _sensitive_key_errors(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text.casefold() in FORBIDDEN_CONTENT_KEYS:
                errors.append(f"sensitive_field_forbidden:{path}.{key_text}")
            errors.extend(_sensitive_key_errors(child, f"{path}.{key_text}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_sensitive_key_errors(child, f"{path}[{index}]"))
    return errors


def _string_list(value: Any, *, reason: str) -> tuple[list[str], list[str]]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        return [], [reason]
    return list(value), []


def _reference_errors(
    values: Iterable[Any], *, prefix: str, repo_root: Path, require_exists: bool
) -> list[str]:
    errors: list[str] = []
    for value in values:
        if not is_safe_repo_reference(value):
            errors.append(f"unsafe_repo_reference:{prefix}:{value}")
            continue
        if require_exists and not (repo_root / str(value)).is_file():
            errors.append(f"evidence_not_found:{prefix}:{value}")
    return errors


def _node_index(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    nodes = graph.get("nodes", [])
    if not isinstance(nodes, list):
        return {}
    return {
        node["id"]: node
        for node in nodes
        if isinstance(node, dict) and isinstance(node.get("id"), str)
    }


def _contract_index(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    contracts = graph.get("contracts", [])
    if not isinstance(contracts, list):
        return {}
    return {
        contract["id"]: contract
        for contract in contracts
        if isinstance(contract, dict) and isinstance(contract.get("id"), str)
    }


def _cycle_errors(nodes: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str, trail: tuple[str, ...]) -> None:
        if node_id in visiting:
            cycle = "->".join((*trail, node_id))
            errors.append(f"graph_cycle:{cycle}")
            return
        if node_id in visited:
            return
        visiting.add(node_id)
        node = nodes[node_id]
        relationships = node.get("relationships", [])
        if isinstance(relationships, list):
            for relationship in relationships:
                if not isinstance(relationship, dict):
                    continue
                parent_id = relationship.get("node_id")
                if isinstance(parent_id, str) and parent_id in nodes:
                    visit(parent_id, (*trail, node_id))
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(nodes):
        visit(node_id, ())
    return sorted(set(errors))


def validate_graph(
    graph: dict[str, Any], *, repo_root: Path, require_evidence_files: bool = True
) -> list[str]:
    """Return deterministic fail-closed structural and safety errors."""

    errors = _sensitive_key_errors(graph)
    if graph.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version_invalid:{graph.get('schema_version')}")
    if not isinstance(graph.get("project_id"), str) or not graph.get("project_id"):
        errors.append("project_id_required")
    if not isinstance(graph.get("graph_revision"), int) or graph.get("graph_revision", 0) < 1:
        errors.append("graph_revision_invalid")
    if not isinstance(graph.get("updated_at"), str) or not graph.get("updated_at"):
        errors.append("updated_at_required")

    governance = graph.get("governance")
    if not isinstance(governance, dict):
        errors.append("governance_object_required")
        governance = {}
    if governance.get("advisory_only") is not True:
        errors.append("governance_advisory_only_required")
    boundaries, boundary_errors = _string_list(
        governance.get("closed_boundaries"), reason="closed_boundaries_string_array_required"
    )
    errors.extend(boundary_errors)
    if len(boundaries) != len(set(boundaries)):
        errors.append("closed_boundary_duplicate")
    for boundary in boundaries:
        if not ID_PATTERN.fullmatch(boundary):
            errors.append(f"closed_boundary_id_invalid:{boundary}")

    raw_nodes = graph.get("nodes")
    if not isinstance(raw_nodes, list):
        errors.append("nodes_array_required")
        raw_nodes = []
    nodes = _node_index(graph)
    if len(nodes) != len(raw_nodes):
        errors.append("node_id_missing_or_duplicate")
    known_contract_ids = set(_contract_index(graph))

    for node_id, node in sorted(nodes.items()):
        prefix = f"node:{node_id}"
        if not ID_PATTERN.fullmatch(node_id):
            errors.append(f"node_id_invalid:{node_id}")
        if not isinstance(node.get("title"), str) or not node.get("title"):
            errors.append(f"node_title_required:{node_id}")
        if node.get("kind") not in NODE_KINDS:
            errors.append(f"node_kind_invalid:{node_id}:{node.get('kind')}")
        if node.get("status") not in NODE_STATUSES:
            errors.append(f"node_status_invalid:{node_id}:{node.get('status')}")
        for timestamp_key in ("created_at", "updated_at"):
            if not isinstance(node.get(timestamp_key), str) or not node.get(timestamp_key):
                errors.append(f"node_{timestamp_key}_required:{node_id}")

        coordinates = node.get("coordinates")
        if not isinstance(coordinates, dict):
            errors.append(f"node_coordinates_required:{node_id}")
            coordinates = {}
        thread_id = coordinates.get("thread_id")
        if thread_id is not None and (not isinstance(thread_id, str) or not thread_id):
            errors.append(f"thread_id_invalid:{node_id}")
        if not isinstance(coordinates.get("git_ref"), str) or not coordinates.get("git_ref"):
            errors.append(f"git_ref_required:{node_id}")
        if not HEAD_PATTERN.fullmatch(str(coordinates.get("source_head", ""))):
            errors.append(f"source_head_invalid:{node_id}")
        if coordinates.get("worktree_role") not in {"integration", "task", "historical", "none"}:
            errors.append(f"worktree_role_invalid:{node_id}")

        relationships = node.get("relationships")
        if not isinstance(relationships, list):
            errors.append(f"relationships_array_required:{node_id}")
            relationships = []
        seen_relationships: set[tuple[str, str]] = set()
        for relationship in relationships:
            if not isinstance(relationship, dict):
                errors.append(f"relationship_object_required:{node_id}")
                continue
            parent_id = relationship.get("node_id")
            relation = relationship.get("relation")
            if not isinstance(parent_id, str) or parent_id not in nodes:
                errors.append(f"relationship_parent_missing:{node_id}:{parent_id}")
            if relation not in RELATIONS:
                errors.append(f"relationship_type_invalid:{node_id}:{relation}")
            key = (str(parent_id), str(relation))
            if key in seen_relationships:
                errors.append(f"relationship_duplicate:{node_id}:{parent_id}:{relation}")
            seen_relationships.add(key)

        evidence = node.get("evidence")
        if not isinstance(evidence, dict):
            errors.append(f"evidence_object_required:{node_id}")
            evidence = {}
        evidence_paths: list[str] = []
        for category in sorted(EVIDENCE_CATEGORIES):
            values, value_errors = _string_list(
                evidence.get(category), reason=f"evidence_array_required:{node_id}:{category}"
            )
            errors.extend(value_errors)
            evidence_paths.extend(values)
            errors.extend(
                _reference_errors(
                    values,
                    prefix=f"{prefix}:{category}",
                    repo_root=repo_root,
                    require_exists=require_evidence_files,
                )
            )

        if node.get("status") == "accepted":
            if not evidence.get("acceptances"):
                errors.append(f"accepted_node_missing_acceptance:{node_id}")
            for acceptance in evidence.get("acceptances", []):
                if not is_acceptance_reference(acceptance):
                    errors.append(f"accepted_node_acceptance_invalid:{node_id}:{acceptance}")

        authority = node.get("authority")
        if not isinstance(authority, dict):
            errors.append(f"authority_object_required:{node_id}")
            authority = {}
        openings = authority.get("authorized_openings")
        if not isinstance(openings, list):
            errors.append(f"authorized_openings_array_required:{node_id}")
            openings = []
        for opening in openings:
            if not isinstance(opening, dict):
                errors.append(f"authorized_opening_object_required:{node_id}")
                continue
            boundary = opening.get("boundary")
            source = opening.get("source")
            if boundary not in boundaries:
                errors.append(f"authorized_opening_boundary_unknown:{node_id}:{boundary}")
            errors.extend(
                _reference_errors(
                    [source],
                    prefix=f"{prefix}:authorized-opening",
                    repo_root=repo_root,
                    require_exists=require_evidence_files,
                )
            )
            if source not in evidence_paths:
                errors.append(f"authorized_opening_source_not_evidence:{node_id}:{boundary}")

        contract_evidence = node.get("contract_evidence")
        if not isinstance(contract_evidence, list):
            errors.append(f"contract_evidence_array_required:{node_id}")
            contract_evidence = []
        seen_contracts: set[str] = set()
        for record in contract_evidence:
            if not isinstance(record, dict):
                errors.append(f"contract_evidence_object_required:{node_id}")
                continue
            contract_id = record.get("contract_id")
            if not isinstance(contract_id, str):
                errors.append(f"contract_evidence_id_required:{node_id}")
                continue
            if contract_id in seen_contracts:
                errors.append(f"contract_evidence_duplicate:{node_id}:{contract_id}")
            seen_contracts.add(contract_id)
            if contract_id not in known_contract_ids:
                errors.append(f"contract_evidence_contract_unknown:{node_id}:{contract_id}")
            if record.get("status") not in CONTRACT_STATES:
                errors.append(f"contract_evidence_status_invalid:{node_id}:{contract_id}")
            record_paths, record_errors = _string_list(
                record.get("evidence"),
                reason=f"contract_evidence_paths_required:{node_id}:{contract_id}",
            )
            errors.extend(record_errors)
            errors.extend(
                _reference_errors(
                    record_paths,
                    prefix=f"{prefix}:contract:{contract_id}",
                    repo_root=repo_root,
                    require_exists=require_evidence_files,
                )
            )
            for record_path in record_paths:
                if record_path not in evidence_paths:
                    errors.append(
                        f"contract_evidence_path_not_node_evidence:{node_id}:"
                        f"{contract_id}:{record_path}"
                    )
            waiver_source = record.get("waiver_source")
            if record.get("status") == "waived":
                errors.extend(
                    _reference_errors(
                        [waiver_source],
                        prefix=f"{prefix}:waiver:{contract_id}",
                        repo_root=repo_root,
                        require_exists=require_evidence_files,
                    )
                )
                if not is_acceptance_reference(waiver_source):
                    errors.append(
                        f"contract_waiver_acceptance_invalid:{node_id}:{contract_id}:"
                        f"{waiver_source}"
                    )
                if waiver_source not in evidence_paths:
                    errors.append(
                        f"contract_waiver_not_node_evidence:{node_id}:{contract_id}:"
                        f"{waiver_source}"
                    )

        decisions = node.get("decisions")
        if not isinstance(decisions, list):
            errors.append(f"decisions_array_required:{node_id}")
            decisions = []
        decision_ids: set[str] = set()
        for decision in decisions:
            if not isinstance(decision, dict):
                errors.append(f"decision_object_required:{node_id}")
                continue
            decision_id = decision.get("id")
            if not isinstance(decision_id, str) or not ID_PATTERN.fullmatch(decision_id):
                errors.append(f"decision_id_invalid:{node_id}:{decision_id}")
            elif decision_id in decision_ids:
                errors.append(f"decision_id_duplicate:{node_id}:{decision_id}")
            else:
                decision_ids.add(decision_id)
            if decision.get("status") not in DECISION_STATES:
                errors.append(f"decision_status_invalid:{node_id}:{decision_id}")
            if not isinstance(decision.get("summary"), str) or not decision.get("summary"):
                errors.append(f"decision_summary_required:{node_id}:{decision_id}")
            errors.extend(
                _reference_errors(
                    [decision.get("source")],
                    prefix=f"{prefix}:decision:{decision_id}",
                    repo_root=repo_root,
                    require_exists=require_evidence_files,
                )
            )

        gates, gate_errors = _string_list(
            node.get("unresolved_gates"), reason=f"unresolved_gates_array_required:{node_id}"
        )
        errors.extend(gate_errors)
        if any(not gate for gate in gates):
            errors.append(f"unresolved_gate_empty:{node_id}")

        claim_scope, claim_errors = _string_list(
            node.get("claim_scope"), reason=f"claim_scope_array_required:{node_id}"
        )
        errors.extend(claim_errors)
        if any(not item for item in claim_scope):
            errors.append(f"claim_scope_empty:{node_id}")

        authority_notes, authority_note_errors = _string_list(
            authority.get("notes"), reason=f"authority_notes_array_required:{node_id}"
        )
        errors.extend(authority_note_errors)
        if any(not note for note in authority_notes):
            errors.append(f"authority_note_empty:{node_id}")

    raw_contracts = graph.get("contracts")
    if not isinstance(raw_contracts, list):
        errors.append("contracts_array_required")
        raw_contracts = []
    contracts = _contract_index(graph)
    if len(contracts) != len(raw_contracts):
        errors.append("contract_id_missing_or_duplicate")
    for contract_id, contract in sorted(contracts.items()):
        if not ID_PATTERN.fullmatch(contract_id):
            errors.append(f"contract_id_invalid:{contract_id}")
        if not isinstance(contract.get("title"), str) or not contract.get("title"):
            errors.append(f"contract_title_required:{contract_id}")
        if not isinstance(contract.get("description"), str) or not contract.get("description"):
            errors.append(f"contract_description_required:{contract_id}")
        if contract.get("source_node") not in nodes:
            errors.append(f"contract_source_node_missing:{contract_id}:{contract.get('source_node')}")
        kinds, kind_errors = _string_list(
            contract.get("applies_to_kinds"),
            reason=f"contract_applies_to_kinds_required:{contract_id}",
        )
        errors.extend(kind_errors)
        for kind in kinds:
            if kind not in NODE_KINDS:
                errors.append(f"contract_kind_invalid:{contract_id}:{kind}")
        required_types, type_errors = _string_list(
            contract.get("required_evidence_types"),
            reason=f"contract_required_evidence_types_required:{contract_id}",
        )
        errors.extend(type_errors)
        for category in required_types:
            if category not in EVIDENCE_CATEGORIES:
                errors.append(f"contract_evidence_type_invalid:{contract_id}:{category}")
        contract_paths, path_errors = _string_list(
            contract.get("evidence"), reason=f"contract_evidence_required:{contract_id}"
        )
        errors.extend(path_errors)
        errors.extend(
            _reference_errors(
                contract_paths,
                prefix=f"contract:{contract_id}",
                repo_root=repo_root,
                require_exists=require_evidence_files,
            )
        )

    raw_harvests = graph.get("harvests")
    if not isinstance(raw_harvests, list):
        errors.append("harvests_array_required")
        raw_harvests = []
    harvest_ids: set[str] = set()
    for harvest in raw_harvests:
        if not isinstance(harvest, dict):
            errors.append("harvest_object_required")
            continue
        harvest_id = harvest.get("id")
        if not isinstance(harvest_id, str) or not ID_PATTERN.fullmatch(harvest_id):
            errors.append(f"harvest_id_invalid:{harvest_id}")
        elif harvest_id in harvest_ids:
            errors.append(f"harvest_id_duplicate:{harvest_id}")
        else:
            harvest_ids.add(harvest_id)
        sources, source_errors = _string_list(
            harvest.get("source_nodes"), reason=f"harvest_sources_required:{harvest_id}"
        )
        errors.extend(source_errors)
        if not sources:
            errors.append(f"harvest_source_empty:{harvest_id}")
        for source in sources:
            if source not in nodes:
                errors.append(f"harvest_source_missing:{harvest_id}:{source}")
        target = harvest.get("target_node")
        if target not in nodes:
            errors.append(f"harvest_target_missing:{harvest_id}:{target}")
        if harvest.get("status") not in HARVEST_STATES:
            errors.append(f"harvest_status_invalid:{harvest_id}:{harvest.get('status')}")
        if not isinstance(harvest.get("created_at"), str) or not harvest.get("created_at"):
            errors.append(f"harvest_created_at_required:{harvest_id}")
        if not isinstance(harvest.get("summary"), str) or not harvest.get("summary"):
            errors.append(f"harvest_summary_required:{harvest_id}")
        harvest_decisions, harvest_decision_errors = _string_list(
            harvest.get("decisions"), reason=f"harvest_decisions_required:{harvest_id}"
        )
        errors.extend(harvest_decision_errors)
        if any(not decision for decision in harvest_decisions):
            errors.append(f"harvest_decision_empty:{harvest_id}")
        harvest_evidence, harvest_evidence_errors = _string_list(
            harvest.get("evidence"), reason=f"harvest_evidence_required:{harvest_id}"
        )
        errors.extend(harvest_evidence_errors)
        errors.extend(
            _reference_errors(
                harvest_evidence,
                prefix=f"harvest:{harvest_id}",
                repo_root=repo_root,
                require_exists=require_evidence_files,
            )
        )

    errors.extend(_cycle_errors(nodes))
    return sorted(set(errors))


def _ancestor_ids(graph: dict[str, Any], node_id: str) -> set[str]:
    nodes = _node_index(graph)
    ancestors: set[str] = set()
    pending = [node_id]
    while pending:
        current = pending.pop()
        node = nodes[current]
        for relationship in node.get("relationships", []):
            if relationship.get("relation") not in CONTRACT_INHERITING_RELATIONS:
                continue
            parent_id = relationship["node_id"]
            if parent_id not in ancestors:
                ancestors.add(parent_id)
                pending.append(parent_id)
    return ancestors


def required_contracts(graph: dict[str, Any], node_id: str) -> list[dict[str, Any]]:
    node = _node_index(graph)[node_id]
    ancestors = _ancestor_ids(graph, node_id)
    contracts = []
    for contract in graph["contracts"]:
        if (
            contract["source_node"] in ancestors
            and node["kind"] in contract["applies_to_kinds"]
        ):
            contracts.append(contract)
    return sorted(contracts, key=lambda item: item["id"])


def audit_graph(
    graph: dict[str, Any],
    *,
    repo_root: Path,
    node_id: str | None = None,
    require_evidence_files: bool = True,
) -> dict[str, Any]:
    structural_errors = validate_graph(
        graph,
        repo_root=repo_root,
        require_evidence_files=require_evidence_files,
    )
    if structural_errors:
        return {
            "schema_version": "ariadne.continuity_audit.v1",
            "status": "revision_required",
            "reasons": structural_errors,
            "nodes": [],
        }
    nodes = _node_index(graph)
    if node_id is not None and node_id not in nodes:
        raise ContinuityError(f"node_not_found:{node_id}")
    targets = [node_id] if node_id else sorted(nodes)
    graph_boundaries = sorted(graph["governance"]["closed_boundaries"])
    reports: list[dict[str, Any]] = []
    reasons: list[str] = []
    for target in targets:
        node = nodes[target]
        node_reasons: list[str] = []
        records = {record["contract_id"]: record for record in node["contract_evidence"]}
        contract_reports: list[dict[str, Any]] = []
        for contract in required_contracts(graph, target):
            contract_id = contract["id"]
            record = records.get(contract_id)
            if record is None:
                state = "missing"
                reason = f"contract_evidence_missing:{target}:{contract_id}"
                reasons.append(reason)
                node_reasons.append(reason)
                contract_reports.append({"contract_id": contract_id, "status": state, "reasons": [reason]})
                continue
            record_reasons: list[str] = []
            state = record["status"]
            if state == "gap":
                record_reasons.append(f"contract_gap_open:{target}:{contract_id}")
            elif state == "satisfied":
                if not record["evidence"]:
                    record_reasons.append(f"contract_satisfaction_evidence_missing:{target}:{contract_id}")
                for category in contract["required_evidence_types"]:
                    if not node["evidence"][category]:
                        record_reasons.append(
                            f"contract_evidence_type_missing:{target}:{contract_id}:{category}"
                        )
                    elif not set(record["evidence"]).intersection(node["evidence"][category]):
                        record_reasons.append(
                            f"contract_evidence_type_unlinked:{target}:{contract_id}:{category}"
                        )
            elif state == "waived" and not record.get("waiver_source"):
                record_reasons.append(f"contract_waiver_source_missing:{target}:{contract_id}")
            reasons.extend(record_reasons)
            node_reasons.extend(record_reasons)
            contract_reports.append(
                {"contract_id": contract_id, "status": state, "reasons": sorted(record_reasons)}
            )

        boundary_reasons: list[str] = []
        for opening in node["authority"]["authorized_openings"]:
            source = opening.get("source")
            if not source:
                boundary_reasons.append(
                    f"boundary_authorization_missing:{target}:{opening.get('boundary')}"
                )
        reasons.extend(boundary_reasons)
        node_reasons.extend(boundary_reasons)
        node_reasons = sorted(set(node_reasons))
        reports.append(
            {
                "node_id": target,
                "status": "passed" if not node_reasons else "revision_required",
                "required_contracts": contract_reports,
                "inherited_closed_boundaries": graph_boundaries,
                "authorized_openings": copy.deepcopy(node["authority"]["authorized_openings"]),
                "reasons": node_reasons,
            }
        )
    return {
        "schema_version": "ariadne.continuity_audit.v1",
        "status": "passed" if not reasons else "revision_required",
        "reasons": sorted(set(reasons)),
        "nodes": reports,
    }


def validation_report(graph: dict[str, Any], *, repo_root: Path) -> dict[str, Any]:
    errors = validate_graph(graph, repo_root=repo_root)
    return {
        "schema_version": "ariadne.continuity_validation.v1",
        "status": "passed" if not errors else "revision_required",
        "reasons": errors,
        "graph_revision": graph.get("graph_revision"),
        "node_count": len(graph.get("nodes", [])) if isinstance(graph.get("nodes"), list) else 0,
        "contract_count": len(graph.get("contracts", []))
        if isinstance(graph.get("contracts"), list)
        else 0,
        "harvest_count": len(graph.get("harvests", []))
        if isinstance(graph.get("harvests"), list)
        else 0,
    }


def write_graph(path: Path, graph: dict[str, Any], *, repo_root: Path, at: str) -> None:
    ensure_inside_repo(path, repo_root, label="graph")
    graph["graph_revision"] += 1
    graph["updated_at"] = at
    errors = validate_graph(graph, repo_root=repo_root)
    if errors:
        raise ContinuityError("graph_write_rejected:" + "|".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = canonical_json(graph).encode("utf-8")
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(file_descriptor, "wb") as handle:
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _mutation_result(command: str, graph: dict[str, Any], **details: Any) -> dict[str, Any]:
    return {
        "schema_version": "ariadne.continuity_command.v1",
        "status": "passed",
        "command": command,
        "graph_revision": graph["graph_revision"],
        **details,
    }


def checkpoint_node(
    graph: dict[str, Any], node: dict[str, Any], *, update: bool
) -> dict[str, Any]:
    nodes = _node_index(graph)
    node_id = node.get("id")
    if not isinstance(node_id, str):
        raise ContinuityError("checkpoint_node_id_required")
    if node_id in nodes and not update:
        raise ContinuityError(f"checkpoint_node_exists:{node_id}")
    if node_id in nodes:
        graph["nodes"] = [node if item["id"] == node_id else item for item in graph["nodes"]]
    else:
        graph["nodes"].append(node)
    graph["nodes"] = sorted(graph["nodes"], key=lambda item: item["id"])
    return graph


def fork_node(
    graph: dict[str, Any], *, parent: str, node_id: str, title: str, kind: str,
    relation: str, git_ref: str, source_head: str, thread_id: str | None,
    worktree_role: str, at: str,
) -> dict[str, Any]:
    nodes = _node_index(graph)
    if parent not in nodes:
        raise ContinuityError(f"fork_parent_not_found:{parent}")
    if node_id in nodes:
        raise ContinuityError(f"fork_node_exists:{node_id}")
    if relation not in RELATIONS:
        raise ContinuityError(f"fork_relation_invalid:{relation}")
    graph["nodes"].append(
        {
            "id": node_id,
            "title": title,
            "kind": kind,
            "status": "planned",
            "created_at": at,
            "updated_at": at,
            "relationships": [{"node_id": parent, "relation": relation}],
            "coordinates": {
                "thread_id": thread_id,
                "git_ref": git_ref,
                "source_head": source_head,
                "worktree_role": worktree_role,
            },
            "evidence": {category: [] for category in sorted(EVIDENCE_CATEGORIES)},
            "authority": {"authorized_openings": [], "notes": []},
            "contract_evidence": [],
            "decisions": [],
            "unresolved_gates": [],
            "claim_scope": [],
        }
    )
    graph["nodes"] = sorted(graph["nodes"], key=lambda item: item["id"])
    return graph


def add_harvest(
    graph: dict[str, Any], *, harvest_id: str, sources: list[str], target: str,
    summary: str, decisions: list[str], evidence: list[str], at: str,
) -> dict[str, Any]:
    nodes = _node_index(graph)
    if harvest_id in {item.get("id") for item in graph["harvests"]}:
        raise ContinuityError(f"harvest_exists:{harvest_id}")
    missing = sorted(source for source in sources if source not in nodes)
    if missing:
        raise ContinuityError("harvest_sources_missing:" + ",".join(missing))
    if target not in nodes:
        raise ContinuityError(f"harvest_target_missing:{target}")
    graph["harvests"].append(
        {
            "id": harvest_id,
            "source_nodes": sorted(set(sources)),
            "target_node": target,
            "created_at": at,
            "status": "candidate",
            "summary": summary,
            "decisions": decisions,
            "evidence": evidence,
        }
    )
    graph["harvests"] = sorted(graph["harvests"], key=lambda item: item["id"])
    return graph


def close_node(
    graph: dict[str, Any], *, node_id: str, status: str, decision: str,
    source: str, acceptance: str | None, at: str,
) -> dict[str, Any]:
    nodes = _node_index(graph)
    if node_id not in nodes:
        raise ContinuityError(f"close_node_not_found:{node_id}")
    if status not in {"accepted", "rejected", "superseded", "closed"}:
        raise ContinuityError(f"close_status_invalid:{status}")
    if status == "accepted" and not acceptance:
        raise ContinuityError(f"close_acceptance_required:{node_id}")
    if status == "accepted" and not is_acceptance_reference(acceptance):
        raise ContinuityError(f"close_acceptance_invalid:{node_id}:{acceptance}")
    node = nodes[node_id]
    node["status"] = status
    node["updated_at"] = at
    if acceptance and acceptance not in node["evidence"]["acceptances"]:
        node["evidence"]["acceptances"].append(acceptance)
        node["evidence"]["acceptances"].sort()
    decision_status = "accepted" if status in {"accepted", "closed"} else "rejected"
    node["decisions"].append(
        {
            "id": f"{node_id}-close-{graph['graph_revision'] + 1}",
            "status": decision_status,
            "summary": decision,
            "source": source,
        }
    )
    return graph


def compare_nodes(graph: dict[str, Any], node_ids: list[str]) -> dict[str, Any]:
    nodes = _node_index(graph)
    missing = sorted(node_id for node_id in node_ids if node_id not in nodes)
    if missing:
        raise ContinuityError("compare_nodes_missing:" + ",".join(missing))
    snapshots = []
    for node_id in node_ids:
        node = nodes[node_id]
        snapshots.append(
            {
                "node_id": node_id,
                "kind": node["kind"],
                "status": node["status"],
                "parents": copy.deepcopy(node["relationships"]),
                "required_contracts": [item["id"] for item in required_contracts(graph, node_id)],
                "contract_evidence": copy.deepcopy(node["contract_evidence"]),
                "authorized_openings": copy.deepcopy(node["authority"]["authorized_openings"]),
                "decisions": copy.deepcopy(node["decisions"]),
                "unresolved_gates": list(node["unresolved_gates"]),
                "claim_scope": list(node["claim_scope"]),
            }
        )
    return {
        "schema_version": "ariadne.continuity_comparison.v1",
        "status": "passed",
        "nodes": snapshots,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Operate the local Ariadne continuity graph.")
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--graph", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate", help="Validate structure, safety, references and DAG integrity.")
    audit = subparsers.add_parser("audit", help="Audit inherited contracts and closed boundaries.")
    audit.add_argument("--node")

    show = subparsers.add_parser("show", help="Show one node or a compact graph index.")
    show.add_argument("--node")

    checkpoint = subparsers.add_parser("checkpoint", help="Add or explicitly update a node file.")
    checkpoint.add_argument("--node-file", type=Path, required=True)
    checkpoint.add_argument("--update", action="store_true")
    checkpoint.add_argument("--at", default=None)

    fork = subparsers.add_parser("fork", help="Record a child branch without spawning it.")
    fork.add_argument("--parent", required=True)
    fork.add_argument("--id", required=True)
    fork.add_argument("--title", required=True)
    fork.add_argument("--kind", choices=sorted(NODE_KINDS), required=True)
    fork.add_argument("--relation", choices=sorted(RELATIONS), default="forked_from")
    fork.add_argument("--git-ref", required=True)
    fork.add_argument("--source-head", required=True)
    fork.add_argument("--thread-id")
    fork.add_argument(
        "--worktree-role", choices=["integration", "task", "historical", "none"], default="task"
    )
    fork.add_argument("--at", default=None)

    harvest = subparsers.add_parser("harvest", help="Record candidate cross-branch knowledge.")
    harvest.add_argument("--id", required=True)
    harvest.add_argument("--source", action="append", required=True)
    harvest.add_argument("--target", required=True)
    harvest.add_argument("--summary", required=True)
    harvest.add_argument("--decision", action="append", default=[])
    harvest.add_argument("--evidence", action="append", default=[])
    harvest.add_argument("--at", default=None)

    compare = subparsers.add_parser("compare", help="Compare two or more nodes without writing.")
    compare.add_argument("--node", action="append", required=True)

    close = subparsers.add_parser("close", help="Record an evidence-backed branch disposition.")
    close.add_argument("--node", required=True)
    close.add_argument("--status", choices=["accepted", "rejected", "superseded", "closed"], required=True)
    close.add_argument("--decision", required=True)
    close.add_argument("--source", required=True)
    close.add_argument("--acceptance")
    close.add_argument("--at", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        repo_root = resolve_repo_root(args.repo_root)
        graph_path = resolve_repo_path(
            args.graph if args.graph else default_graph_path(repo_root), repo_root, label="graph"
        )
        graph = load_graph(graph_path)

        if args.command == "validate":
            result = validation_report(graph, repo_root=repo_root)
            emit(result)
            return 0 if result["status"] == "passed" else 2
        if args.command == "audit":
            result = audit_graph(graph, repo_root=repo_root, node_id=args.node)
            emit(result)
            return 0 if result["status"] == "passed" else 2

        structural_errors = validate_graph(graph, repo_root=repo_root)
        if structural_errors:
            emit(
                {
                    "schema_version": "ariadne.continuity_command.v1",
                    "status": "revision_required",
                    "reasons": structural_errors,
                }
            )
            return 2
        if args.command == "show":
            nodes = _node_index(graph)
            if args.node:
                if args.node not in nodes:
                    raise ContinuityError(f"node_not_found:{args.node}")
                result = {
                    "schema_version": "ariadne.continuity_view.v1",
                    "status": "passed",
                    "node": nodes[args.node],
                    "required_contracts": [
                        contract["id"] for contract in required_contracts(graph, args.node)
                    ],
                }
            else:
                result = {
                    "schema_version": "ariadne.continuity_view.v1",
                    "status": "passed",
                    "graph_revision": graph["graph_revision"],
                    "nodes": [
                        {"id": node["id"], "title": node["title"], "kind": node["kind"], "status": node["status"]}
                        for node in sorted(graph["nodes"], key=lambda item: item["id"])
                    ],
                }
            emit(result)
            return 0

        at = getattr(args, "at", None) or utc_now()
        if args.command == "checkpoint":
            node_file = resolve_repo_path(args.node_file, repo_root, label="node_file")
            node = load_json(node_file, label="node_file")
            if not isinstance(node, dict):
                raise ContinuityError("checkpoint_node_must_be_object")
            checkpoint_node(graph, node, update=args.update)
            detail = {"node_id": node.get("id"), "updated": args.update}
        elif args.command == "fork":
            fork_node(
                graph,
                parent=args.parent,
                node_id=args.id,
                title=args.title,
                kind=args.kind,
                relation=args.relation,
                git_ref=args.git_ref,
                source_head=args.source_head,
                thread_id=args.thread_id,
                worktree_role=args.worktree_role,
                at=at,
            )
            detail = {"node_id": args.id, "parent": args.parent, "relation": args.relation}
        elif args.command == "harvest":
            add_harvest(
                graph,
                harvest_id=args.id,
                sources=args.source,
                target=args.target,
                summary=args.summary,
                decisions=args.decision,
                evidence=args.evidence,
                at=at,
            )
            detail = {"harvest_id": args.id, "target_node": args.target, "status": "candidate"}
        elif args.command == "compare":
            if len(args.node) < 2:
                raise ContinuityError("compare_requires_two_nodes")
            emit(compare_nodes(graph, args.node))
            return 0
        elif args.command == "close":
            close_node(
                graph,
                node_id=args.node,
                status=args.status,
                decision=args.decision,
                source=args.source,
                acceptance=args.acceptance,
                at=at,
            )
            detail = {"node_id": args.node, "status": args.status}
        else:  # pragma: no cover - argparse guarantees a known command
            raise ContinuityError(f"unsupported_command:{args.command}")

        write_graph(graph_path, graph, repo_root=repo_root, at=at)
        emit(_mutation_result(args.command, graph, **detail))
        return 0
    except (ContinuityError, OSError) as error:
        emit(
            {
                "schema_version": "ariadne.continuity_command.v1",
                "status": "revision_required",
                "reasons": [str(error)],
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
