"""Advance Continuity and Compass for delete-confirm physical design."""

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
NODE_ID = "raisa-provider-free-unmounted-delete-confirm-physical-design-architecture"
PARENT = (
    "raisa-provider-free-read-only-unmounted-delete-confirm-"
    "physical-representability-review"
)
SOURCE_HEAD = "3fd22ba69f96c0378538ea27c6bea444fcb81936"
UPDATED_AT = "2026-08-15T06:35:48Z"
PLAN = "docs/raisa-provider-free-unmounted-delete-confirm-physical-design-architecture-plan.md"
THREAT = (
    "docs/security/raisa-provider-free-unmounted-delete-confirm-"
    "physical-design-architecture-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-delete-confirm-"
    "physical-design-architecture-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-"
    "physical-design-architecture/"
)
CONTRACT = BASE + "physical-design-contract.json"
SCHEMA = BASE + "physical-design-contract.schema.json"
EVIDENCE = BASE + "provider-free-physical-design-evidence.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-"
    "physical-design-architecture-sol-acceptance.md"
)
POSTCHANGE = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-design-"
    "gemini37-postchange-receipt.json"
)
PREDISPATCH = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-design-"
    "gemini37-veto-predispatch-receipt.json"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-design-"
    "gemini37-preacceptance-receipt.json"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-delete-confirm-"
    "physical-design-gemini37-review-receipt.json"
)
ALLOCATION = "docs/ariadne-antigravity-gemini-37-high-verifier-allocation.md"
INCIDENT = "docs/ariadne-agent-error-correction-register-revision-290.md"
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-15--delete-confirm-physical-design-architecture.md"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_delete_confirm_"
    "physical_design_architecture.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_delete_confirm_"
    "physical_design_architecture_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_delete_confirm_"
    "physical_design_architecture_continuity_update.py"
)


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def _evidence() -> list[str]:
    return [
        PLAN,
        THREAT,
        CONTRACT,
        SCHEMA,
        EVIDENCE,
        CLOSEOUT,
        ACCEPTANCE,
        POSTCHANGE,
        PREDISPATCH,
        PREACCEPTANCE,
        REVIEW,
        ALLOCATION,
        INCIDENT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": (
            "Provider-free unmounted delete-confirm physical-design architecture"
        ),
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
                "The accepted design is authored-synthetic, provider-free and unmounted; implementation_authorized remains false.",
                "It selects a product authority generation and normalized grants, versioned private delete receipt, attributable audit, exact canonical bytes, ordered transaction and separate readback without executing them.",
                "Yuri requested a product-development pause after closeout; the next scaffold candidate is planned but not opened.",
                "Application/migration/route implementation, database execution, product providers/data/commands and protected integration remain closed.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-physical-design-architecture",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the exact additive authority, receipt, audit, "
                    "transaction and readback design; retain the unmounted "
                    "scaffold as the next planned candidate but pause before "
                    "opening it."
                ),
            }
        ],
        "claim_scope": [
            "The users row is a database-owned monotonic authority fence and normalized exact cancellation/read grants default deny without automatic backfill.",
            "Existing appointment state advances n to n+1 under one exact structured cancellation reason and optional bounded text.",
            "A family-qualified private receipt and attributable delete audit bind authority, session, request and pre/post state while delivery uses one integrity-checked six-field byte buffer.",
            "One READ COMMITTED transaction locks authority, appointment and idempotency in order with two authority checks and one cumulative 2000 ms wait budget; readback is separately authorised after commit.",
            "Twenty hashes, 166 hostile mutations, the canonical 196-test fast profile and one fresh Gemini 3.7 Flash/high exact-candidate veto pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, EVIDENCE, ALLOCATION, INCIDENT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [POSTCHANGE, PREDISPATCH, PREACCEPTANCE, REVIEW],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [UPDATER],
        },
        "unresolved_gates": [
            "No ORM model, migration, service helper or route embodies the accepted physical design.",
            "Executable DDL, PostgreSQL catalogue/trigger/lock behavior, capability provisioning and mounted-route parity remain unproved.",
            "The current full delete-confirm response has not transitioned to the accepted minimized receipt contract.",
            "Product/patient data, product providers, credentials, watchers/events, commands, deployment, Pages and protected refs remain closed.",
            "The next scaffold candidate remains paused until Yuri resumes product development after the Prime Agent assessment.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 297 and graph["nodes"][-1]["id"] == PARENT:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 298
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 298 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected delete-confirm physical-design predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": (
            "Freeze the cancellation authority and atomic transaction boundary "
            "before any runtime edit"
        ),
        "outcome": (
            "One exact additive authority, receipt, audit, ordered transaction "
            "and separate-readback design passes; implementation remains "
            "unmounted and the next product tranche is paused."
        ),
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 279
        and compass["source_graph_revision"] == 297
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 280
        and compass["source_graph_revision"] == 298
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected delete-confirm physical-design Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, conditional-command and delete-confirm representability lineage.",
                "When Yuri resumes product development, freeze the exact provider-free unmounted delete-confirm physical schema-and-transaction scaffold before implementation.",
                "Keep database execution, mounted routes, providers, product data, commands and protected integration separately gated.",
            ]
            for item in journey["evidence"]:
                if item not in horizon["evidence"]:
                    horizon["evidence"].append(item)
            break
    else:
        raise SystemExit("Practice Context Fabric horizon item missing")

    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "The cancellation safety kernel has one exact physical design and "
            "is paused before runtime embodiment"
        ),
        "why_now": (
            "The exact-file representability review proved additive feasibility, "
            "allowing authority, receipt, audit, transaction and readback "
            "decisions to be frozen before code or database execution."
        ),
        "outcome": (
            "The unmounted architecture passes deterministic and fresh Gemini "
            "3.7 veto evidence; Yuri requested a pause before the planned scaffold."
        ),
        "unlocks": [
            "After Yuri resumes, implement a provider-free unmounted delete-confirm physical schema-and-transaction scaffold.",
            "Lower only the exact product authority fence, normalized grants, receipt, audit and unmounted helper contract under deterministic static tests.",
            "Keep database and route execution behind later evidence gates.",
        ],
        "does_not_solve": [
            "Executable Alembic lowering, ORM/service correctness, capability provisioning or mounted-route behavior.",
            "PostgreSQL catalogue, trigger, lock-wait, rollback, restart or unknown-commit behavior.",
            "The explicit API response/route compatibility transition.",
            "Provider/credential activity, patient/product data, watchers/events, product commands, deployment, production, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 298 / Compass 280. The unmounted delete-confirm "
        "physical-design architecture passes with database-owned current "
        "authority, an exact private receipt and audit, one ordered transaction "
        "and separate readback. The next scaffold is planned but product "
        "development is paused at Yuri's request."
    )
    limit = (
        "The accepted delete-confirm physical design proves a closed architecture, "
        "not executable DDL, PostgreSQL behavior, ORM/service wiring, capability "
        "provisioning, response transition or a mounted route."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 298
    compass["map_revision"] = 280
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
