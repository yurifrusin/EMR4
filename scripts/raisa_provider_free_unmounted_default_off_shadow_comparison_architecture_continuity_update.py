"""Advance Continuity and Compass for default-off shadow architecture."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_compass


GRAPH = ROOT / "orchestration/continuity/emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration/continuity/emr4-compass.json"
REPORT = ROOT / "docs/ariadne-compass-current.md"
NODE_ID = "raisa-provider-free-unmounted-default-off-shadow-comparison-architecture"
PARENT = "raisa-provider-free-unmounted-pure-route-adapter-differential-rehearsal"
SOURCE_HEAD = "e1dca1c6dc5d3f3e241548f80a226e5bb776417f"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-plan.md"
DESIGN = "docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture.md"
THREAT = "docs/security/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-threat-model-delta.md"
PACKET_DIR = "orchestration/continuity/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture/"
CONTRACT = PACKET_DIR + "contract.json"
SCHEMA = PACKET_DIR + "contract.schema.json"
CLOSEOUT = "docs/raisa-provider-free-unmounted-default-off-shadow-comparison-architecture-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-default-off-shadow-comparison-architecture-sol-acceptance.md"
PREPLANNING_RECEIPT = "orchestration/agent_inbox/codex/raisa-default-off-shadow-comparison-architecture-preplanning-receipt.json"
PRECOMMIT_RECEIPT = "orchestration/agent_inbox/codex/raisa-default-off-shadow-comparison-architecture-candidate-precommit-receipt.json"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--default-off-shadow-comparison-architecture.md"
TEST = "tests/test_raisa_provider_free_unmounted_default_off_shadow_comparison_architecture_continuity.py"
UPDATER = "scripts/raisa_provider_free_unmounted_default_off_shadow_comparison_architecture_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _evidence() -> list[str]:
    return [PLAN, DESIGN, THREAT, CONTRACT, SCHEMA, CLOSEOUT, ACCEPTANCE, PREPLANNING_RECEIPT, PRECOMMIT_RECEIPT, MAILBOX]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free unmounted default-off shadow-comparison architecture",
        "kind": "foundation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {"git_ref": "codex/ariadne-bernie-davida-parallel-seam", "source_head": SOURCE_HEAD, "thread_id": None, "worktree_role": "task"},
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "This is a provider-free unmounted static shadow architecture.",
                "It imports or changes no application route and creates no observer runtime.",
                "Shadow evidence is diagnostic, lossy and never command or audit authority.",
            ],
        },
        "decisions": [{"id": "accept-default-off-shadow-comparison-architecture", "source": CLOSEOUT, "status": "accepted", "summary": "Accept the four-way default-deny, post-result, one-way diagnostic boundary without runtime wiring."}],
        "claim_scope": [
            "Exactly four raw route adapters are in scope; confirm and proposal routes are excluded.",
            "A current immutable generation, global flag, practice flag and exact route allowlist must intersect.",
            "A 24-field digest projection may produce only a 15-field lossy diagnostic record.",
            "All twelve feedback edges and every observer capability are forbidden.",
            "All forty-six hostile mutations fail closed.",
        ],
        "contract_evidence": [],
        "evidence": {"plans": [PLAN], "findings": [DESIGN, THREAT], "closeouts": [CLOSEOUT, MAILBOX], "acceptances": [ACCEPTANCE], "receipts": [PREPLANNING_RECEIPT, PRECOMMIT_RECEIPT], "tests": ["tests/test_raisa_provider_free_unmounted_default_off_shadow_comparison_architecture.py", TEST], "artifacts": [CONTRACT, SCHEMA, UPDATER]},
        "unresolved_gates": [
            "No application hook, observer, feature flag, queue, sink, persistence, retention or aggregation is implemented.",
            "No product hashing, latency/concurrency isolation, operational monitoring or rollback is proved.",
            "Database/source/watcher/event access, patient/product data, provider, commands, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 248 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 249
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 249 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected shadow architecture Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {"node_id": NODE_ID, "lineage_parent": PARENT, "strategic_role": "Freeze a diagnostic-only shadow boundary beside raw appointment routes", "outcome": "Static default-off architecture passes; authored-synthetic shadow behavior rehearsal is next.", "evidence": _evidence()}
    if compass["map_revision"] == 230 and compass["source_graph_revision"] == 248 and compass["current_position"]["node_id"] == PARENT:
        compass["journey"].append(journey)
    elif compass["map_revision"] == 231 and compass["source_graph_revision"] == 249 and compass["current_position"]["node_id"] == NODE_ID:
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected shadow architecture Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Rehearse the default-off shadow boundary with authored-synthetic disabled, expected-gap, divergence, failure, timeout and overflow cases.",
                "Keep all application route/runtime wiring closed until that pure behavior evidence passes.",
                "Then separately review default-off runtime instrumentation before client proposal/confirm parity.",
                "Select and prove a database-owned create schedule fence before create convergence.",
                "Retain Durable Event and Cue Delivery as a later observability-first extension.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Default-off shadow boundary frozen; pure failure-isolation rehearsal next",
        "why_now": "The pure route adapters pass, so a diagnostic observer can now be rehearsed without granting it any command or response influence.",
        "outcome": "Four-way default denial, post-result placement, digest minimization and twelve no-feedback edges pass all 46 hostile mutations.",
        "unlocks": [
            "Exercise disabled, admitted, exact-gap, divergence, timeout, overflow and observer/sink failure scenarios with authored-synthetic inputs.",
            "Prove every scenario leaves the sealed primary result byte-for-byte unchanged and emits at most one minimized diagnostic record.",
        ],
        "does_not_solve": [
            "Application hook or route wiring, production hashing, queue/sink persistence, latency isolation, client migration or database fencing.",
            "Durable cue delivery, CF-D2, patient/product data, providers, commands, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 249 / Compass 231. The provider-free unmounted "
        "default-off shadow architecture freezes four-way denial, post-result "
        "one-way placement, digest minimization and twelve no-feedback edges; all "
        "46 hostile mutations pass. The next safe tranche is its authored-synthetic "
        "shadow-comparison rehearsal."
    )
    limit = "The shadow result is static architecture only; no route hook, observer, queue, sink, persistence or runtime exists."
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 249
    compass["map_revision"] = 231
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
