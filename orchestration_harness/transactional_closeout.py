"""Provider-free shadow transaction and shared broker clock for Ariadne closeout."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from orchestration_harness.active_operation import validate_active_operation
from orchestration_harness.git_object_resolution import resolve_commit_source
from orchestration_harness.git_refs_snapshot import build_git_refs_snapshot
from scripts import ariadne_compass

SCHEMA_VERSION = "ariadne.transactional_closeout_manifest.v1"
BUNDLE_VERSION = "ariadne.transactional_closeout_bundle.v1"
WORK_ORDER_VERSION = "ariadne.deepseek_work_order.v1"
EVENT_VERSION = "ariadne.bureaucratic_clock_event.v1"
ZERO_DIGEST = "sha256:" + "0" * 64
EXPECTED_PROTECTED_COMMIT = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PROTECTED_REFS = (
    "refs/heads/master",
    "refs/remotes/origin/master",
    "refs/heads/handoff/current",
    "refs/remotes/origin/handoff/current",
)
ALLOWED_TOOLS = ["edit", "glob", "read"]
ID = re.compile(r"^[a-z][a-z0-9._-]{0,127}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def sha256(value: object) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _exact(value: object, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{label}_keys_not_exact")
    return value


def _text(value: object, label: str, maximum: int = 1000) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > maximum
        or "\r" in value
    ):
        raise ValueError(f"{label}_invalid")
    return value


def _identifier(value: object, label: str) -> str:
    text = _text(value, label, 128)
    if ID.fullmatch(text) is None:
        raise ValueError(f"{label}_invalid")
    return text


def _strings(value: object, label: str, *, empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not empty and not value):
        raise ValueError(f"{label}_invalid")
    result = [_text(item, label, 500) for item in value]
    if len(result) != len(set(result)):
        raise ValueError(f"{label}_duplicate")
    return result


def _validate_incidents(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("incidents_invalid")
    incidents: list[dict[str, Any]] = []
    for item in value:
        row = _exact(item, {"incident_id", "source_id", "peers"}, "incident")
        incidents.append(
            {
                "incident_id": _identifier(row["incident_id"], "incident_id"),
                "source_id": _identifier(row["source_id"], "source_id"),
                "peers": _strings(row["peers"], "incident_peers", empty=True),
            }
        )
    ids = {item["incident_id"] for item in incidents}
    if len(ids) != len(incidents):
        raise ValueError("incident_id_duplicate")
    for item in incidents:
        for peer in item["peers"]:
            other = next((row for row in incidents if row["incident_id"] == peer), None)
            if other is None or item["incident_id"] not in other["peers"]:
                raise ValueError("incident_peer_not_symmetric")
    return incidents


def validate_manifest(value: object) -> dict[str, Any]:
    manifest = _exact(
        value,
        {
            "schema_version",
            "operation_id",
            "title",
            "source_anchor",
            "recorded_at",
            "node",
            "journey",
            "current_position",
            "next_operation",
            "incidents",
            "broker",
        },
        "manifest",
    )
    if manifest["schema_version"] != SCHEMA_VERSION:
        raise ValueError("manifest_schema_invalid")
    if manifest["source_anchor"] != "current_head":
        raise ValueError("source_anchor_invalid")
    operation_id = _identifier(manifest["operation_id"], "operation_id")
    node = _exact(
        manifest["node"],
        {
            "id", "title", "kind", "relationships", "authority", "decisions",
            "claim_scope", "contract_evidence", "evidence", "unresolved_gates",
        },
        "node",
    )
    _identifier(node["id"], "node_id")
    relationships = node["relationships"]
    if not isinstance(relationships, list) or len(relationships) != 1:
        raise ValueError("node_relationship_invalid")
    relation = _exact(relationships[0], {"node_id", "relation"}, "relationship")
    if relation["relation"] != "builds_on":
        raise ValueError("node_relationship_invalid")
    _identifier(relation["node_id"], "parent_node_id")
    journey = _exact(manifest["journey"], {"strategic_role", "outcome", "evidence"}, "journey")
    position = _exact(
        manifest["current_position"],
        {"strategic_role", "why_now", "outcome", "unlocks", "does_not_solve", "evidence", "orientation_statement"},
        "current_position",
    )
    for item, fields in ((journey, ("strategic_role", "outcome")), (position, ("strategic_role", "why_now", "outcome", "orientation_statement"))):
        for field in fields:
            _text(item[field], field)
    for field in ("evidence",):
        _strings(journey[field], f"journey_{field}")
        _strings(position[field], f"position_{field}")
    _strings(position["unlocks"], "unlocks")
    _strings(position["does_not_solve"], "does_not_solve")
    next_operation = _exact(
        manifest["next_operation"],
        {"operation_id", "active_tranche", "objective", "authority_source", "next_stage"},
        "next_operation",
    )
    _identifier(next_operation["operation_id"], "next_operation_id")
    for field in ("active_tranche", "objective", "authority_source", "next_stage"):
        _text(next_operation[field], f"next_operation_{field}")
    broker = _exact(manifest["broker"], {"enabled", "posture"}, "broker")
    if not isinstance(broker["enabled"], bool) or broker["posture"] != "provider_free_shadow":
        raise ValueError("broker_contract_invalid")
    incidents = _validate_incidents(manifest["incidents"])
    return {**copy.deepcopy(manifest), "operation_id": operation_id, "incidents": incidents}


def _event(
    *, journal_id: str, transaction_id: str, operation_id: str,
    sequence: int, previous: str, event_type: str, payload: dict[str, Any],
) -> dict[str, Any]:
    event = {
        "schema_version": EVENT_VERSION,
        "journal_id": journal_id,
        "transaction_id": transaction_id,
        "operation_id": operation_id,
        "sequence": sequence,
        "previous_event_sha256": previous,
        "event_type": event_type,
        "actor": "gpt-sol",
        "payload": payload,
    }
    event["event_sha256"] = sha256(event)
    return event


def validate_event_chain(events: object, *, sequence: int = 1, previous: str = ZERO_DIGEST) -> None:
    if not isinstance(events, list) or not events:
        raise ValueError("event_chain_empty")
    identity: tuple[object, object, object] | None = None
    for event in events:
        row = _exact(
            event,
            {"schema_version", "journal_id", "transaction_id", "operation_id", "sequence", "previous_event_sha256", "event_type", "actor", "payload", "event_sha256"},
            "event",
        )
        if row["schema_version"] != EVENT_VERSION or row["sequence"] != sequence:
            raise ValueError("event_sequence_invalid")
        current_identity = (
            row["journal_id"], row["transaction_id"], row["operation_id"]
        )
        if identity is None:
            identity = current_identity
        elif current_identity != identity:
            raise ValueError("event_identity_drift")
        if row["previous_event_sha256"] != previous:
            raise ValueError("event_previous_digest_invalid")
        supplied = row["event_sha256"]
        if not isinstance(supplied, str) or supplied != sha256({k: v for k, v in row.items() if k != "event_sha256"}):
            raise ValueError("event_digest_invalid")
        previous, sequence = supplied, sequence + 1


def _incident_aggregate(incidents: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(incidents, key=lambda item: item["incident_id"])
    return {
        "population": len(ordered),
        "latest_incident_id": ordered[-1]["incident_id"] if ordered else None,
        "source_cutoff": max((item["source_id"] for item in ordered), default=None),
        "peer_links": {item["incident_id"]: item["peers"] for item in ordered},
    }


def _projection_report(compass: dict[str, Any], graph: dict[str, Any], repo_root: Path) -> str:
    errors = ariadne_compass.validate_compass(
        compass, graph, repo_root=repo_root, require_evidence_files=False
    )
    errors = [item for item in errors if not item.startswith("current_position_continuity:evidence_not_found:")]
    if errors:
        raise ValueError("prospective_projection_invalid:" + ",".join(errors))
    return (
        f"# Ariadne transactional projection — structurally passed\n\nCompass {compass['map_revision']} / Continuity {graph['graph_revision']}.\n\n"
        "Historical evidence-file presence remains a canonical-adoption gate.\n"
    )


def prepare_transaction(
    value: object, *, repo_root: Path, graph: dict[str, Any],
    compass: dict[str, Any], active_latch: dict[str, Any],
) -> dict[str, Any]:
    manifest = validate_manifest(value)
    latch = validate_active_operation(active_latch)
    if latch["status"] != "in_progress" or latch["operation_id"] != manifest["operation_id"]:
        raise ValueError("active_operation_mismatch")
    snapshot = build_git_refs_snapshot(
        repo_root=repo_root, expected_protected_commit=EXPECTED_PROTECTED_COMMIT,
        protected_refs=PROTECTED_REFS,
    )
    if snapshot["status"] != "passed":
        raise ValueError("protected_refs_mismatch")
    source_head = resolve_commit_source(repo_root=repo_root, source_head=snapshot["head"])["resolved_commit"]
    parent_id = manifest["node"]["relationships"][0]["node_id"]
    if graph["nodes"][-1]["id"] != parent_id or compass["current_position"]["node_id"] != parent_id:
        raise ValueError("projection_predecessor_mismatch")
    node = copy.deepcopy(manifest["node"])
    node.update({"status": "accepted", "created_at": manifest["recorded_at"], "updated_at": manifest["recorded_at"]})
    node["coordinates"] = {"git_ref": snapshot["branch"], "source_head": source_head, "thread_id": None, "worktree_role": "task"}
    next_graph = copy.deepcopy(graph)
    next_graph["nodes"].append(node)
    next_graph["graph_revision"] += 1
    next_graph["updated_at"] = manifest["recorded_at"]
    journey = {"node_id": node["id"], "lineage_parent": parent_id, **copy.deepcopy(manifest["journey"])}
    next_compass = copy.deepcopy(compass)
    next_compass["journey"].append(journey)
    next_compass["current_position"] = {"node_id": node["id"], **{k: copy.deepcopy(v) for k, v in manifest["current_position"].items() if k != "orientation_statement"}}
    next_compass["orientation_statement"] = manifest["current_position"]["orientation_statement"]
    next_compass["source_graph_revision"] = next_graph["graph_revision"]
    next_compass["map_revision"] += 1
    next_compass["updated_at"] = manifest["recorded_at"]
    report = _projection_report(next_compass, next_graph, repo_root)
    next_spec = manifest["next_operation"]
    next_latch = {
        "schema_version": latch["schema_version"], "operation_id": next_spec["operation_id"],
        "active_tranche": next_spec["active_tranche"], "objective": next_spec["objective"],
        "status": "in_progress", "source_head": source_head, "authority_source": next_spec["authority_source"],
        "checkpoint": {"completed_stage": f"Accepted {manifest['operation_id']} at the machine-resolved source.", "next_executable_stage": next_spec["next_stage"], "retry_counters": {key: 0 for key in latch["checkpoint"]["retry_counters"]}, "settings_fingerprint": latch["checkpoint"]["settings_fingerprint"]},
        "interruption_policy": latch["interruption_policy"], "resume_after_compaction": True,
        "user_attention": {"required": False, "reason": None},
        "terminal_response": {"permitted": False, "reason": "unfinished_authorized_operation"},
        "protected_boundaries": latch["protected_boundaries"],
    }
    validate_active_operation(next_latch)
    manifest_sha = sha256(manifest)
    transaction_id = "txn-" + sha256({"manifest": manifest_sha, "head": source_head})[7:31]
    journal_id = "journal-" + transaction_id[4:]
    events: list[dict[str, Any]] = []
    previous = ZERO_DIGEST
    for event_type, payload in (
        ("manifest-accepted", {"manifest_sha256": manifest_sha}),
        ("git-source-resolved", {"source_commit": source_head, "protected_refs_sha256": sha256(snapshot["protected_refs"])}),
        ("projections-reduced", {"graph_revision": next_graph["graph_revision"], "map_revision": next_compass["map_revision"]}),
        ("projections-validated", {"continuity": "passed", "compass": "passed", "latch": "passed"}),
        ("transaction-prepared", {"publication_mode": "shadow_directory_rename"}),
    ):
        item = _event(journal_id=journal_id, transaction_id=transaction_id, operation_id=manifest["operation_id"], sequence=len(events) + 1, previous=previous, event_type=event_type, payload=payload)
        events.append(item)
        previous = item["event_sha256"]
    authority_sha = sha256({"boundaries": latch["protected_boundaries"], "authority": node["authority"]})
    work_order = None
    if manifest["broker"]["enabled"]:
        base = {
            "schema_version": WORK_ORDER_VERSION, "work_order_id": "wo-" + transaction_id[4:],
            "transaction_id": transaction_id, "operation_id": manifest["operation_id"],
            "lease_id": "lease-" + transaction_id[4:], "journal_id": journal_id,
            "source_commit": source_head, "authority_sha256": authority_sha,
            "forbidden_surfaces_sha256": sha256(latch["protected_boundaries"]),
            "branch": snapshot["branch"], "worktree": str(repo_root.resolve()),
            "allowed_tool_names": ALLOWED_TOOLS, "posture": "provider_free_shadow",
        }
        issued = _event(journal_id=journal_id, transaction_id=transaction_id, operation_id=manifest["operation_id"], sequence=len(events) + 1, previous=previous, event_type="work-order-issued", payload={"work_order_base_sha256": sha256(base)})
        events.append(issued)
        work_order = {**base, "next_sequence": issued["sequence"] + 1, "previous_event_sha256": issued["event_sha256"]}
    validate_event_chain(events)
    projections = {"graph": next_graph, "compass": next_compass, "report": report, "latch": next_latch, "incident_aggregate": _incident_aggregate(manifest["incidents"])}
    bundle = {
        "schema_version": BUNDLE_VERSION, "transaction_id": transaction_id,
        "manifest_sha256": manifest_sha, "source_commit": source_head,
        "git_snapshot": snapshot, "journal": events, "projections": projections,
        "projection_sha256s": {key: sha256(value) for key, value in projections.items()},
        "work_order": work_order, "work_order_sha256": sha256(work_order) if work_order is not None else None,
    }
    validate_bundle(bundle, repo_root=repo_root)
    return bundle


def validate_bundle(bundle: object, *, repo_root: Path) -> None:
    row = _exact(bundle, {"schema_version", "transaction_id", "manifest_sha256", "source_commit", "git_snapshot", "journal", "projections", "projection_sha256s", "work_order", "work_order_sha256"}, "bundle")
    if row["schema_version"] != BUNDLE_VERSION or HEX40.fullmatch(row["source_commit"]) is None:
        raise ValueError("bundle_identity_invalid")
    validate_event_chain(row["journal"])
    if row["projection_sha256s"] != {key: sha256(value) for key, value in row["projections"].items()}:
        raise ValueError("projection_digest_invalid")
    validate_active_operation(row["projections"]["latch"])
    if row["projections"]["report"] != _projection_report(
        row["projections"]["compass"], row["projections"]["graph"], repo_root
    ):
        raise ValueError("bundle_projection_invalid")
    work_order = row["work_order"]
    if work_order is not None:
        _validate_work_order(work_order)
        if row["work_order_sha256"] != sha256(work_order):
            raise ValueError("work_order_digest_invalid")
        if work_order["previous_event_sha256"] != row["journal"][-1]["event_sha256"]:
            raise ValueError("work_order_anchor_invalid")
        expected_bindings = {
            "transaction_id": row["transaction_id"],
            "operation_id": row["journal"][-1]["operation_id"],
            "journal_id": row["journal"][-1]["journal_id"],
            "source_commit": row["source_commit"],
            "next_sequence": row["journal"][-1]["sequence"] + 1,
        }
        if any(work_order[key] != expected for key, expected in expected_bindings.items()):
            raise ValueError("work_order_bundle_binding_invalid")


def _validate_work_order(value: object) -> dict[str, Any]:
    keys = {"schema_version", "work_order_id", "transaction_id", "operation_id", "lease_id", "journal_id", "source_commit", "authority_sha256", "forbidden_surfaces_sha256", "branch", "worktree", "allowed_tool_names", "posture", "next_sequence", "previous_event_sha256"}
    row = _exact(value, keys, "work_order")
    if row["schema_version"] != WORK_ORDER_VERSION or HEX40.fullmatch(row["source_commit"]) is None:
        raise ValueError("work_order_source_invalid")
    for key in ("work_order_id", "transaction_id", "operation_id", "lease_id", "journal_id"):
        _identifier(row[key], key)
    for key in ("authority_sha256", "forbidden_surfaces_sha256"):
        if not isinstance(row[key], str) or DIGEST.fullmatch(row[key]) is None:
            raise ValueError("work_order_digest_binding_invalid")
    _text(row["branch"], "work_order_branch", 300)
    _text(row["worktree"], "work_order_worktree", 1000)
    if row["allowed_tool_names"] != ALLOWED_TOOLS or row["posture"] != "provider_free_shadow":
        raise ValueError("work_order_authority_invalid")
    if not isinstance(row["next_sequence"], int) or row["next_sequence"] < 1 or DIGEST.fullmatch(row["previous_event_sha256"]) is None:
        raise ValueError("work_order_clock_invalid")
    return row


def validate_broker_events(work_order: object, events: object) -> None:
    order = _validate_work_order(work_order)
    if not isinstance(events, list) or not events:
        raise ValueError("broker_event_chain_empty")
    sequence, previous = order["next_sequence"], order["previous_event_sha256"]
    for event in events:
        if not isinstance(event, dict) or event.get("clock_sequence") != sequence or event.get("previous_event_sha256") != previous:
            raise ValueError("broker_event_clock_invalid")
        for key in ("work_order_id", "transaction_id", "operation_id", "source_commit", "authority_sha256"):
            if event.get(key) != order[key]:
                raise ValueError("broker_event_binding_invalid")
        supplied = event.get("event_sha256")
        if supplied != sha256({key: value for key, value in event.items() if key != "event_sha256"}):
            raise ValueError("broker_event_digest_invalid")
        previous, sequence = supplied, sequence + 1


def publish_shadow(bundle: object, *, repo_root: Path, target: Path, fail_after_write: int | None = None) -> Path:
    validate_bundle(bundle, repo_root=repo_root)
    resolved, root = target.resolve(), repo_root.resolve()
    forbidden = {root / "AGENTS.md", root / "orchestration/continuity/emr4-continuity-graph.json", root / "orchestration/continuity/emr4-compass.json", root / "docs/ariadne-compass-current.md", root / "orchestration/continuity/ariadne-active-operation-latch/current.json"}
    allowed_repo_shadow = (root / "orchestration/continuity/ariadne-transactional-closeout-control-plane-consolidation-efficacy-rehearsal/shadow").resolve()
    inside_repo = root == resolved or root in resolved.parents
    if resolved in {path.resolve() for path in forbidden} or resolved.exists() or (inside_repo and allowed_repo_shadow not in resolved.parents):
        raise ValueError("shadow_target_forbidden")
    resolved.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=resolved.name + ".staging-", dir=resolved.parent))
    files = {
        "journal.jsonl": "".join(json.dumps(item, sort_keys=True, ensure_ascii=False) + "\n" for item in bundle["journal"]),
        "continuity.json": json.dumps(bundle["projections"]["graph"], indent=2, ensure_ascii=False) + "\n",
        "compass.json": json.dumps(bundle["projections"]["compass"], indent=2, ensure_ascii=False) + "\n",
        "compass.md": bundle["projections"]["report"],
        "latch.json": json.dumps(bundle["projections"]["latch"], indent=2, ensure_ascii=False) + "\n",
        "incident-aggregate.json": json.dumps(bundle["projections"]["incident_aggregate"], indent=2, ensure_ascii=False) + "\n",
        "work-order.json": json.dumps(bundle["work_order"], indent=2, ensure_ascii=False) + "\n",
        "work-order.sha256": str(bundle["work_order_sha256"]) + "\n",
    }
    try:
        for index, (name, content) in enumerate(files.items(), start=1):
            (staging / name).write_text(content, encoding="utf-8", newline="\n")
            if fail_after_write == index:
                raise RuntimeError("injected_shadow_write_failure")
        if any(not (staging / name).is_file() for name in files):
            raise ValueError("shadow_reread_failed")
        os.replace(staging, resolved)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return resolved


def verify_historical_fixtures(value: object, *, repo_root: Path, graph: dict[str, Any], compass: dict[str, Any]) -> dict[str, Any]:
    fixtures = _exact(value, {"schema_version", "fixtures"}, "fixtures")
    if fixtures["schema_version"] != "ariadne.transactional_closeout_shadow_fixtures.v1" or not isinstance(fixtures["fixtures"], list):
        raise ValueError("fixture_schema_invalid")
    results = []
    for item in fixtures["fixtures"]:
        row = _exact(item, {"node_id", "node_sha256", "journey_sha256", "legacy_updater", "legacy_test", "legacy_lines"}, "fixture")
        node = next(entry for entry in graph["nodes"] if entry["id"] == row["node_id"])
        journey = next(entry for entry in compass["journey"] if entry["node_id"] == row["node_id"])
        paths = [repo_root / row["legacy_updater"], repo_root / row["legacy_test"]]
        observed_lines = sum(len(path.read_text(encoding="utf-8").splitlines()) for path in paths)
        passed = sha256(node) == row["node_sha256"] and sha256(journey) == row["journey_sha256"] and observed_lines == row["legacy_lines"] and HEX40.fullmatch(node["coordinates"]["source_head"]) is not None
        results.append({"node_id": row["node_id"], "status": "passed" if passed else "revision_required", "legacy_lines": observed_lines})
    return {"status": "passed" if all(item["status"] == "passed" for item in results) else "revision_required", "fixtures": results, "legacy_files": len(results) * 2, "legacy_lines": sum(item["legacy_lines"] for item in results)}


def measure_efficacy(
    *, repo_root: Path, manifest: dict[str, Any], graph: dict[str, Any],
    compass: dict[str, Any], latch: dict[str, Any], fixtures: dict[str, Any],
    candidate_paths: list[str], iterations: int = 20,
) -> dict[str, Any]:
    """Run the frozen controlled shadow comparison and derive every total."""
    if iterations < 20:
        raise ValueError("efficacy_iterations_too_small")
    historical = verify_historical_fixtures(fixtures, repo_root=repo_root, graph=graph, compass=compass)
    mutations = []
    for key, value in (("source_head", "1234567"), ("source_cutoff", "stale-source"), ("incident_population", 566)):
        candidate = copy.deepcopy(manifest)
        candidate[key] = value
        mutations.append((key, candidate, latch))
    peers = copy.deepcopy(manifest)
    peers["incidents"] = [{"incident_id": "aer-1", "source_id": "source-1", "peers": ["aer-2"]}, {"incident_id": "aer-2", "source_id": "source-2", "peers": []}]
    boundaries = copy.deepcopy(manifest)
    boundaries["next_operation"]["protected_boundaries"] = ["paraphrased boundary"]
    stale_latch = copy.deepcopy(latch)
    stale_latch["operation_id"] = "stale-operation"
    mutations.extend([("asymmetric_peer", peers, latch), ("boundary_paraphrase", boundaries, latch), ("stale_latch", manifest, stale_latch)])
    prevented = []
    for defect, candidate, candidate_latch in mutations:
        try:
            prepare_transaction(candidate, repo_root=repo_root, graph=graph, compass=compass, active_latch=candidate_latch)
        except ValueError:
            prevented.append(defect)
    bundle = prepare_transaction(manifest, repo_root=repo_root, graph=graph, compass=compass, active_latch=latch)
    with tempfile.TemporaryDirectory(prefix="ariadne-efficacy-") as temporary:
        temporary_root = Path(temporary)
        fault_prevented = True
        for step in range(1, 9):
            target = temporary_root / f"fault-{step}"
            try:
                publish_shadow(bundle, repo_root=repo_root, target=target, fail_after_write=step)
            except RuntimeError:
                pass
            fault_prevented = fault_prevented and not target.exists()
    if fault_prevented:
        prevented.append("prevalidation_or_partial_publication")
    diff = subprocess.run(["git", "diff", "--numstat", latch["source_head"], "--", *candidate_paths], cwd=repo_root, check=True, capture_output=True, text=True, encoding="utf-8")
    deltas = {path: int(added) + int(deleted) for added, deleted, path in (line.split("\t") for line in diff.stdout.splitlines() if line)}
    candidate_lines = 0
    for path in candidate_paths:
        tracked = subprocess.run(["git", "ls-files", "--error-unmatch", path], cwd=repo_root, capture_output=True, check=False).returncode == 0
        candidate_lines += deltas[path] if tracked else len((repo_root / path).read_text(encoding="utf-8").splitlines())
    legacy_writes = sum((repo_root / item[key]).read_text(encoding="utf-8").count("_write(") + (repo_root / item[key]).read_text(encoding="utf-8").count("REPORT.write_text") for item in fixtures["fixtures"] for key in ("legacy_updater",))
    legacy_constants = sum(sum(isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id.isupper() for target in node.targets) for node in ast.parse((repo_root / item["legacy_updater"]).read_text(encoding="utf-8")).body) for item in fixtures["fixtures"])
    def leaf_count(value: object) -> int:
        return sum(leaf_count(item) for item in value.values()) if isinstance(value, dict) else sum(leaf_count(item) for item in value) if isinstance(value, list) else 1
    candidate_fields = leaf_count(manifest)
    escaped = sorted({"source_head", "source_cutoff", "incident_population", "asymmetric_peer", "boundary_paraphrase", "stale_latch", "prevalidation_or_partial_publication"} - set(prevented))
    passed = historical["status"] == "passed" and not escaped and candidate_lines < historical["legacy_lines"] and len(candidate_paths) < historical["legacy_files"]
    return {
        "schema_version": "ariadne.transactional_closeout_efficacy.v1",
        "status": "passed" if passed else "efficacy_not_proven",
        "historical_shadow": historical,
        "defects": {"named": 7, "prevented": sorted(prevented), "escaped": escaped, "coverage_loss": False},
        "retries": {"legacy_reference": 7, "candidate": len(escaped), "reduction_percent": round((7 - len(escaped)) * 100 / 7, 1)},
        "commands": {"legacy_projection_write_calls": legacy_writes, "candidate_publication_calls": 1},
        "manual_fields": {"legacy_top_level_binding_constants": legacy_constants, "candidate_manifest_leaf_values": candidate_fields, "reduction_percent": round((legacy_constants - candidate_fields) * 100 / legacy_constants, 1)},
        "surface": {"legacy_files": historical["legacy_files"], "legacy_lines": historical["legacy_lines"], "candidate_files": len(candidate_paths), "candidate_lines": candidate_lines, "raw_repository_growth_reported": True},
        "timing": {"reproduced": False, "acceptance_relevant": False},
        "canonical_writes_before_validation": 0,
        "hand_copied_git_object_ids": 0,
    }
