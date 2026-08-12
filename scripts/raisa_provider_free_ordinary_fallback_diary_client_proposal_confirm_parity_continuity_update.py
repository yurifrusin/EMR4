"""Advance Continuity and Compass for native Diary proposal-confirm parity."""

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
NODE_ID = "raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity"
PARENT = "raisa-provider-free-globally-disabled-runtime-instrumentation-scaffold"
SOURCE_HEAD = "78cbcca756476fddfd0fda4b4d1241f195b21ab6"
UPDATED_AT = "2026-08-12T00:00:00Z"
PLAN = "docs/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-plan.md"
DESIGN = "docs/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-design.md"
THREAT = "docs/security/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-threat-model-delta.md"
CLOSEOUT = "docs/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity-closeout.md"
ACCEPTANCE = "orchestration/agent_inbox/codex/raisa-ordinary-fallback-diary-client-proposal-confirm-parity-sol-acceptance.md"
PREPLANNING_RECEIPT = "orchestration/agent_inbox/codex/raisa-provider-free-ordinary-fallback-client-proposal-confirm-parity-preplanning-receipt.json"
PRECOMMIT_RECEIPT = "orchestration/agent_inbox/codex/raisa-provider-free-ordinary-fallback-client-proposal-confirm-parity-precommit-receipt.json"
MAILBOX = "orchestration/human_inbox/yuri/2026-08-12--ordinary-fallback-diary-client-proposal-confirm-parity.md"
INVENTORY = "orchestration/continuity/raisa-provider-free-ordinary-fallback-diary-client-proposal-confirm-parity/native-diary-raw-call-site-inventory.json"
TEST = "tests/test_raisa_provider_free_ordinary_fallback_diary_client_proposal_confirm_parity_continuity.py"
UPDATER = "scripts/raisa_provider_free_ordinary_fallback_diary_client_proposal_confirm_parity_continuity_update.py"


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        DESIGN,
        THREAT,
        INVENTORY,
        CLOSEOUT,
        ACCEPTANCE,
        PREPLANNING_RECEIPT,
        PRECOMMIT_RECEIPT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": "Provider-free ordinary/fallback Diary client proposal-confirm parity",
        "kind": "foundation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": "codex/ariadne-bernie-davida-parallel-seam",
            "source_head": SOURCE_HEAD,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [],
            "notes": [
                "This is provider-free native-client proposal-confirm parity.",
                "The four backend raw compatibility routes remain mounted and unchanged.",
                "No external-consumer, kernel-convergence or route-retirement authority is granted.",
            ],
        },
        "decisions": [
            {
                "id": "accept-ordinary-fallback-diary-client-proposal-confirm-parity",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": "Accept zero native raw appointment mutations with fail-closed proposal plus signed-confirm behavior.",
            }
        ],
        "claim_scope": [
            "Exactly seven source-bound native raw call sites are inventoried and zero remain in the Diary client.",
            "Every native proposal family sends an idempotency header and missing signed evidence fails closed.",
            "Fresh blocks override earlier warning review and changed warning codes require renewed review.",
            "Create/update follow-up status and delete-404 fallback use signed status confirmation.",
            "Eight tranche, 142 Diary browser, 242 focused backend/API and canonical 191 fast-profile tests pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [DESIGN, THREAT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [PREPLANNING_RECEIPT, PRECOMMIT_RECEIPT],
            "tests": [
                "tests/test_raisa_provider_free_ordinary_fallback_diary_client_proposal_confirm_parity.py",
                "review/test_diary_smoke.py",
                TEST,
            ],
            "artifacts": [
                "docs/diary/diary.js",
                "docs/api-spine/raw-compat-consumer-signal-readiness.md",
                "docs/api-spine/legacy-compatibility-write-deprecation-map.md",
                INVENTORY,
                UPDATER,
            ],
        },
        "unresolved_gates": [
            "External, import, recovery and migration consumers of compatibility routes remain unidentified.",
            "Create/update plus status remains two distinct committed commands with explicit partial-outcome reporting.",
            "Compatibility-route retirement, raw-route kernel convergence and create schedule fencing remain closed.",
            "Shadow enablement, product data, provider calls, deployment, Pages and protected refs remain closed.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 252 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 253
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 253 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected Diary client parity Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": "Remove native raw fallbacks before compatibility-route convergence",
        "outcome": "Seven native raw call sites are closed; compatibility-consumer and kernel-convergence admission review is next.",
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 234
        and compass["source_graph_revision"] == 252
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 235
        and compass["source_graph_revision"] == 253
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected Diary client parity Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Inventory every remaining repository/system compatibility-route consumer and import/recovery obligation.",
                "Freeze exact behavior-preservation and observability requirements before any route implementation changes.",
                "Select the narrowest status, delete or update kernel-convergence slice before create.",
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
        "strategic_role": "Native proposal-confirm parity proved; compatibility-consumer admission next",
        "why_now": "The native Diary no longer selects raw appointment mutations, so remaining compatibility obligations can be examined without conflating them with ordinary product behavior.",
        "outcome": "Seven raw client paths are replaced by fail-closed proposal plus signed-confirm flows while all backend compatibility routes remain mounted.",
        "unlocks": [
            "Inventory remaining repository/system, import, recovery and migration consumers.",
            "Freeze the exact first raw-route kernel-convergence implementation boundary without changing a route.",
        ],
        "does_not_solve": [
            "External-consumer readiness, compatibility-route retirement or raw-route kernel convergence.",
            "Create schedule fencing, shadow enablement, product data, deployment, Pages or protected refs.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 253 / Compass 235. Provider-free native Diary "
        "proposal-confirm parity passes with seven raw appointment mutation call "
        "sites reduced to zero, all 142 Diary browser tests and exact backend-route "
        "preservation. Compatibility-consumer and kernel-convergence admission review is next."
    )
    limit = (
        "Native-client parity does not identify external compatibility consumers or authorize route retirement or kernel convergence."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 253
    compass["map_revision"] = 235
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
