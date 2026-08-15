"""Advance Continuity and Compass for the delete-confirm physical scaffold."""

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
NODE_ID = (
    "raisa-provider-free-unmounted-delete-confirm-physical-schema-transaction-scaffold"
)
PARENT = "raisa-provider-free-unmounted-delete-confirm-physical-design-architecture"
GRAPH_PREDECESSOR = (
    "ariadne-provider-free-continuity-journal-and-refinement-promotion-safeguards"
)
SOURCE_HEAD = "843769b415597f4545663d78044eaaad303c7692"
UPDATED_AT = "2026-08-15T14:24:19Z"
PLAN = (
    "docs/raisa-provider-free-unmounted-delete-confirm-physical-schema-"
    "transaction-scaffold-plan.md"
)
THREAT = (
    "docs/security/raisa-provider-free-unmounted-delete-confirm-physical-schema-"
    "transaction-scaffold-threat-model-delta.md"
)
CLOSEOUT = (
    "docs/raisa-provider-free-unmounted-delete-confirm-physical-schema-"
    "transaction-scaffold-closeout.md"
)
BASE = (
    "orchestration/continuity/raisa-provider-free-unmounted-delete-confirm-"
    "physical-schema-transaction-scaffold/"
)
CONTRACT = BASE + "scaffold-contract.json"
SCHEMA = BASE + "scaffold-contract.schema.json"
EVIDENCE = BASE + "provider-free-scaffold-evidence.json"
JOURNAL = BASE + "operation-journal.json"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-schema-"
    "transaction-scaffold-sol-acceptance.md"
)
REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-delete-confirm-physical-"
    "scaffold-gemini37-retry-review-receipt.json"
)
FAILED_REVIEW = (
    "orchestration/agent_inbox/antigravity/raisa-delete-confirm-physical-"
    "scaffold-gemini37-review-receipt.json"
)
POSTCOMPACTION = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-"
    "scaffold-postcompaction-receipt.json"
)
PREVERIFIER = (
    "orchestration/agent_inbox/codex/raisa-delete-confirm-physical-"
    "scaffold-retry-pre-verifier-acceptance-receipt.json"
)
INCIDENT = "docs/ariadne-agent-error-correction-register-revision-302.md"
MAILBOX = (
    "orchestration/human_inbox/yuri/"
    "2026-08-16--delete-confirm-physical-schema-transaction-scaffold.md"
)
MODEL_FILES = ["app/models/tenancy.py", "app/models/appointments.py"]
MIGRATION = "alembic/versions/x3y4z5a6b7c8_add_delete_confirm_physical_scaffold.py"
SERVICE = "app/services/appointment_delete_physical.py"
VALIDATOR = (
    "scripts/raisa_provider_free_unmounted_delete_confirm_physical_schema_"
    "transaction_scaffold.py"
)
TEST = (
    "tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_"
    "transaction_scaffold.py"
)
CONTINUITY_TEST = (
    "tests/test_raisa_provider_free_unmounted_delete_confirm_physical_schema_"
    "transaction_scaffold_continuity.py"
)
UPDATER = (
    "scripts/raisa_provider_free_unmounted_delete_confirm_physical_schema_"
    "transaction_scaffold_continuity_update.py"
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
        JOURNAL,
        *MODEL_FILES,
        MIGRATION,
        SERVICE,
        VALIDATOR,
        TEST,
        CLOSEOUT,
        ACCEPTANCE,
        FAILED_REVIEW,
        REVIEW,
        POSTCOMPACTION,
        PREVERIFIER,
        INCIDENT,
        MAILBOX,
    ]


def _node() -> dict[str, Any]:
    return {
        "id": NODE_ID,
        "title": (
            "Provider-free unmounted delete-confirm physical schema-and-"
            "transaction scaffold"
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
                "The accepted source is authored-synthetic, provider-free and unmounted; runtime authority remains false.",
                "It maps database-owned current authority, normalized default-deny grants, a private delete receipt, attributable audit, inert migration and an unmounted ordered transaction seam.",
                "No migration or SQL ran, no database or route opened and no capability was provisioned.",
                "Yuri requested a pause after closeout before the disposable PostgreSQL parse/catalogue rehearsal.",
            ],
        },
        "decisions": [
            {
                "id": "accept-delete-confirm-physical-schema-transaction-scaffold",
                "source": CLOSEOUT,
                "status": "accepted",
                "summary": (
                    "Accept the exact unmounted mapping, inert migration, pure "
                    "receipt helpers and authority-first transaction seam, then "
                    "pause before database parse/catalogue proof."
                ),
            }
        ],
        "claim_scope": [
            "PostgreSQL-owned positive authority generation and exact normalized grants default deny without automatic provisioning.",
            "One inert migration lowers exact receipt and attributable audit additions while preserving the status family.",
            "Pure helpers bind six-field canonical bytes, domain-separated session HMAC and constant-time replay integrity.",
            "The unmounted seam uses one cumulative 2000 ms budget, exact lock order, two full current-authority checks and a complete atomic write-set barrier.",
            "Twenty bindings, 117 hostile mutations, 57 focused tests, 36 API Spine tests, the canonical 196-test fast profile and one corrected clean Gemini 3.7 Flash/high veto pass.",
        ],
        "contract_evidence": [],
        "evidence": {
            "plans": [PLAN],
            "findings": [THREAT, CONTRACT, SCHEMA, EVIDENCE, JOURNAL, INCIDENT],
            "closeouts": [CLOSEOUT, MAILBOX],
            "acceptances": [ACCEPTANCE],
            "receipts": [FAILED_REVIEW, REVIEW, POSTCOMPACTION, PREVERIFIER],
            "tests": [TEST, CONTINUITY_TEST],
            "artifacts": [*MODEL_FILES, MIGRATION, SERVICE, VALIDATOR, UPDATER],
        },
        "unresolved_gates": [
            "PostgreSQL has not parsed or installed the migration; exact catalogues and trigger bodies remain unproved.",
            "No real lock, transaction, rollback, RLS, concurrency, restart, unknown-commit or route behavior has run.",
            "Capability provisioning and the public response/route compatibility transition remain closed.",
            "Product/patient data, providers, credentials, watchers/events, commands, deployment, Pages and protected refs remain closed.",
            "The next parse/catalogue tranche is paused pending Yuri's requested workflow-efficiency review.",
        ],
    }


def main() -> int:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 299 and graph["nodes"][-1]["id"] == GRAPH_PREDECESSOR:
        graph["nodes"].append(_node())
        graph["graph_revision"] = 300
        graph["updated_at"] = UPDATED_AT
    elif graph["graph_revision"] == 300 and graph["nodes"][-1]["id"] == NODE_ID:
        graph["nodes"][-1] = _node()
    else:
        raise SystemExit("Unexpected delete-confirm scaffold Continuity predecessor")
    _write(GRAPH, graph)

    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    journey = {
        "node_id": NODE_ID,
        "lineage_parent": PARENT,
        "strategic_role": (
            "Embody the cancellation authority and atomic transaction design "
            "without opening a database or route"
        ),
        "outcome": (
            "Exact mappings, inert migration, canonical receipt helpers and the "
            "ordered transaction seam pass as an unmounted scaffold."
        ),
        "evidence": _evidence(),
    }
    if (
        compass["map_revision"] == 281
        and compass["source_graph_revision"] == 299
        and compass["current_position"]["node_id"] == PARENT
    ):
        compass["journey"].append(journey)
    elif (
        compass["map_revision"] == 282
        and compass["source_graph_revision"] == 300
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["journey"][-1] = journey
    else:
        raise SystemExit("Unexpected delete-confirm scaffold Compass predecessor")

    for horizon in compass["programme_support_horizon"]:
        if horizon["id"] == "raisa-practice-context-fabric":
            horizon["status"] = "active"
            horizon["prerequisites"] = [
                "Preserve the accepted source-owned-truth, conditional-command and delete-confirm design/scaffold lineage.",
                "After Yuri resumes, prove only this exact migration in a provider-free disposable PostgreSQL parse/catalogue rehearsal.",
                "Keep behavior, provisioning, routes, product data, providers and protected integration separately gated.",
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
            "The cancellation safety kernel has an unmounted physical source "
            "scaffold and is paused before database embodiment"
        ),
        "why_now": (
            "The physical design passed and has now been lowered into exact "
            "source without executing a migration, database transaction or route."
        ),
        "outcome": (
            "Database-owned authority mapping, inert DDL, canonical receipt "
            "helpers and the authority-first lock seam pass deterministic and "
            "fresh independent review evidence."
        ),
        "unlocks": [
            "After Yuri resumes, run a provider-free disposable PostgreSQL delete-confirm scaffold parse/catalogue rehearsal.",
            "Verify only empty-instance installation plus exact columns, constraints, functions and triggers.",
            "Keep behavior and route execution behind later evidence gates.",
        ],
        "does_not_solve": [
            "PostgreSQL installation, catalogue, trigger, RLS, real lock, rollback or timing behavior.",
            "Capability provisioning, mounted-route behavior or the public response compatibility transition.",
            "Provider/credential activity, patient/product data, watchers/events, product commands, deployment, release, Pages or protected-ref movement.",
        ],
        "evidence": journey["evidence"],
    }
    compass["orientation_statement"] = (
        "EMR4 is at Continuity 300 / Compass 282. The unmounted delete-confirm "
        "physical schema-and-transaction scaffold passes with database-owned "
        "current authority, normalized default-deny grants, inert DDL, exact "
        "private receipt/audit mappings and an ordered transaction seam. Work "
        "is paused before the disposable PostgreSQL parse/catalogue rehearsal."
    )
    limit = (
        "The accepted delete-confirm physical scaffold proves source lowering "
        "only, not PostgreSQL installation, real locks, capability provisioning, "
        "route behavior or product command safety."
    )
    if limit not in compass["map_limits"]:
        compass["map_limits"].insert(0, limit)
    compass["source_graph_revision"] = 300
    compass["map_revision"] = 282
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)

    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
