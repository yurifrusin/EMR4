"""Apply the accepted status-confirm readiness re-review continuity update."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS_PATH = ROOT / "orchestration/continuity/emr4-compass.json"
COMPASS_DOC_PATH = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview"
SOURCE_HEAD = "b2107060facb701208d034cba3bc8ef29f22a7f9"
UPDATED_AT = "2026-08-12T23:52:23Z"

EVIDENCE = [
    "docs/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview-plan.md",
    "docs/security/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview-threat-model-delta.md",
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview/route-mounting-readiness-rereview-contract.json",
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview/route-mounting-readiness-rereview-evidence.json",
    "orchestration/continuity/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview/route-mounting-readiness-rereview-report.md",
    "scripts/raisa_provider_free_read_only_status_confirm_route_mounting_readiness_rereview.py",
    "tests/test_raisa_provider_free_read_only_status_confirm_route_mounting_readiness_rereview.py",
    "docs/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview-closeout.md",
    "orchestration/agent_inbox/codex/raisa-status-confirm-route-mounting-readiness-rereview-sol-acceptance.md",
    "orchestration/human_inbox/yuri/2026-08-13--status-confirm-route-mounting-readiness-rereview.md",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update(graph: dict[str, Any], compass: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    if graph["graph_revision"] != 269 or compass["map_revision"] != 251:
        raise ValueError("unexpected continuity baseline")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise ValueError("readiness re-review node already exists")
    graph["graph_revision"] = 270
    graph["updated_at"] = UPDATED_AT
    graph["nodes"].append({
        "id": NODE_ID,
        "title": "Provider-free read-only status-confirm route-mounting readiness re-review",
        "kind": "review",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {"git_ref": "codex/ariadne-bernie-davida-parallel-seam", "source_head": SOURCE_HEAD, "thread_id": None, "worktree_role": "task"},
        "relationships": [{"node_id": "raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal", "relation": "builds_on"}],
        "authority": {"authorized_openings": [], "notes": ["Text-only exact-file review; no application import, route, database, provider, product data or command authority.", "Route mounting remains blocked until four application-owned adapters pass off-route."]},
        "decisions": [{"id": "accept-readiness-rereview", "source": "docs/raisa-provider-free-read-only-status-confirm-route-mounting-readiness-rereview-closeout.md", "status": "accepted", "summary": "Accept four satisfied, two partial and four blocking dimensions; continue only to an unmounted product-adapter rehearsal."}],
        "claim_scope": ["Four satisfied, two partial and four blocking dimensions.", "All fourteen frozen source hashes and 69 hostile mutations pass.", "The accepted physical PostgreSQL proof is consumed without reopening concurrency, restart or unknown commit."],
        "contract_evidence": [],
        "evidence": {"plans": EVIDENCE[:2], "findings": [], "closeouts": [EVIDENCE[7], EVIDENCE[9]], "acceptances": [EVIDENCE[8]], "receipts": [], "tests": [EVIDENCE[6]], "artifacts": EVIDENCE[2:6]},
        "unresolved_gates": ["Application-owned server session/current authority, status-only admission, locked-state policy and atomic effect/audit adapters remain absent.", "Canonical alias policy and stored-byte HTTP delivery remain later route decisions."]
    })

    compass["map_revision"] = 252
    compass["source_graph_revision"] = 270
    compass["updated_at"] = UPDATED_AT
    compass["orientation_statement"] = "EMR4 is at Continuity 270 / Compass 252. The status-confirm readiness re-review passes with four remaining product-adapter blockers; route mounting and product execution remain closed."
    compass["journey"].append({
        "node_id": NODE_ID,
        "lineage_parent": "raisa-provider-free-unmounted-status-confirm-route-convergence-composition-rehearsal",
        "strategic_role": "Separate completed off-route composition from the still-missing application-owned product adapter",
        "outcome": "The route is not ready to mount; four coupled adapter responsibilities are the narrow next tranche.",
        "evidence": EVIDENCE,
    })
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Route readiness is now reduced to one bounded application-owned adapter seam",
        "why_now": "The accepted composition closed three former blockers and reduced stored delivery to a later transport partial.",
        "outcome": "Four satisfied, two partial and four blocking dimensions are accepted; route mounting remains closed.",
        "unlocks": ["Freeze one provider-free unmounted status-confirm product-adapter rehearsal covering the four coupled blockers."],
        "does_not_solve": ["Route mounting/calling or database execution.", "Canonical alias policy or exact HTTP stored-byte delivery.", "Concurrency, restart, crash, unknown commit, provider, product data, deployment or release."],
        "evidence": EVIDENCE,
    }
    for item in compass["programme_support_horizon"]:
        if item["id"] == "raisa-practice-context-fabric":
            item["prerequisites"] = [
                "Preserve the accepted physical PostgreSQL and unmounted composition proofs.",
                "Rehearse the four coupled status-confirm product adapters off-route and provider-free.",
                "Keep route transport, product execution, providers and protected integration separately gated.",
            ]
            for path in EVIDENCE:
                if path not in item["evidence"]:
                    item["evidence"].append(path)
            break
    else:
        raise ValueError("Context Fabric horizon missing")
    compass["map_limits"].append("The accepted readiness re-review does not mount or authorise the status-confirm route; four product-adapter blockers remain.")
    return graph, compass


def main() -> int:
    graph, compass = update(read_json(GRAPH_PATH), read_json(COMPASS_PATH))
    write_json(GRAPH_PATH, graph)
    write_json(COMPASS_PATH, compass)
    old = "> EMR4 is at Continuity 269 / Compass 251. The post-compaction active-operation latch passes and the provider-free read-only status-confirm route-mounting readiness re-review is in progress. Mounted execution and product authority remain closed."
    new = "> EMR4 is at Continuity 270 / Compass 252. The status-confirm readiness re-review passes with four remaining product-adapter blockers. Route mounting and product execution remain closed."
    text = COMPASS_DOC_PATH.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError("Compass current orientation baseline missing")
    COMPASS_DOC_PATH.write_text(text.replace(old, new, 1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from orchestration_harness.governance_writer_guard import refuse_retired_legacy_writer
    refuse_retired_legacy_writer(ROOT)
    raise SystemExit(main())
