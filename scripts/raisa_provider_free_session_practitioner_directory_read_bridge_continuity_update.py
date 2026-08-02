from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from scripts import ariadne_compass
except ModuleNotFoundError:
    import ariadne_compass  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
UPDATED_AT = "2026-08-02T11:51:32Z"
BRANCH = "codex/raisa-provider-free-session-practitioner-directory-read-bridge"
SOURCE_HEAD = "9fdfaaf0cdae4c54b81e04a010fb2df4cc779da6"
PARENT = "raisa-provider-free-oidc-admission-grant-redemption-bridge"
NODE = "raisa-provider-free-session-practitioner-directory-read-bridge"

ARTIFACTS = {
    "plan": "docs/raisa-provider-free-session-practitioner-directory-read-bridge-plan.md",
    "design": "docs/raisa-provider-free-session-practitioner-directory-read-bridge-design.md",
    "threat": "docs/security/raisa-provider-free-session-practitioner-directory-read-bridge-threat-model-delta.md",
    "migration": "alembic/versions/u0v1w2x3y4z5_extend_auth_audit_for_directory_read.py",
    "auth_model": "app/models/application_auth.py",
    "auth_runtime": "app/services/application_auth_runtime.py",
    "auth_persistence": "app/services/application_auth_persistence.py",
    "role_runtime": "app/services/application_auth_role_runtime.py",
    "product_bridge": "app/services/application_auth_product_read.py",
    "product_role": "app/services/application_auth_product_read_database_role.py",
    "product_pool": "app/services/application_auth_product_read_operational.py",
    "graphql_adapter": "app/graphql/application_auth_product.py",
    "graphql_schema": "app/graphql/schema.py",
    "directory_service": "app/services/practice/practitioner_directory_read.py",
    "evidence": "orchestration/continuity/raisa-provider-free-session-practitioner-directory-read-bridge/live-local-http-backend-postgres-directory-evidence.json",
    "closeout": "docs/raisa-provider-free-session-practitioner-directory-read-bridge-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-provider-free-session-practitioner-directory-read-bridge-sol-acceptance.md",
    "runtime_state": "orchestration/agent_inbox/codex/raisa-provider-free-session-practitioner-directory-read-bridge-rehydration-runtime-state.json",
    "rehydration": "orchestration/agent_inbox/codex/raisa-provider-free-session-practitioner-directory-read-bridge-rehydration-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-provider-free-session-practitioner-directory-read-bridge-preacceptance-receipt.json",
    "prepush": "orchestration/agent_inbox/codex/raisa-provider-free-session-practitioner-directory-read-bridge-prepush-receipt.json",
    "runner": "scripts/raisa_provider_free_session_practitioner_directory_read_bridge_acceptance.py",
    "tests": "tests/test_raisa_provider_free_session_practitioner_directory_read_bridge.py",
    "continuity_runner": "scripts/raisa_provider_free_session_practitioner_directory_read_bridge_continuity_update.py",
    "continuity_tests": "tests/test_raisa_provider_free_session_practitioner_directory_read_bridge_continuity.py",
}


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _evidence() -> dict[str, list[str]]:
    return {
        "plans": [ARTIFACTS["plan"], ARTIFACTS["design"], ARTIFACTS["threat"]],
        "findings": [
            ARTIFACTS["migration"],
            ARTIFACTS["auth_model"],
            ARTIFACTS["auth_runtime"],
            ARTIFACTS["auth_persistence"],
            ARTIFACTS["role_runtime"],
            ARTIFACTS["product_bridge"],
            ARTIFACTS["product_role"],
            ARTIFACTS["product_pool"],
            ARTIFACTS["graphql_adapter"],
            ARTIFACTS["graphql_schema"],
            ARTIFACTS["directory_service"],
            ARTIFACTS["evidence"],
        ],
        "closeouts": [ARTIFACTS["closeout"]],
        "acceptances": [ARTIFACTS["acceptance"]],
        "receipts": [
            ARTIFACTS["runtime_state"],
            ARTIFACTS["rehydration"],
            ARTIFACTS["preacceptance"],
            ARTIFACTS["prepush"],
        ],
        "tests": [
            ARTIFACTS["runner"],
            ARTIFACTS["tests"],
            ARTIFACTS["continuity_runner"],
            ARTIFACTS["continuity_tests"],
        ],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 200:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 200 has an unexpected terminal node.")
        graph["nodes"][-1]["evidence"] = _evidence()
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 199 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected product-read predecessor.")
    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa Provider-Free Session Practitioner-Directory Read Bridge",
            "kind": "foundation",
            "status": "accepted",
            "created_at": UPDATED_AT,
            "updated_at": UPDATED_AT,
            "coordinates": {
                "git_ref": BRANCH,
                "source_head": SOURCE_HEAD,
                "thread_id": None,
                "worktree_role": "task",
            },
            "relationships": [{"node_id": PARENT, "relation": "builds_on"}],
            "authority": {
                "authorized_openings": [
                    {
                        "boundary": "api-change",
                        "source": ARTIFACTS["plan"],
                        "scope": "Authorize one default-off provider-free authored-synthetic application-session active-practitioner-directory read with exact product columns and required audit.",
                    }
                ],
                "notes": [
                    "Yuri selected the recommended bounded product-authorization direction.",
                    "No patient/clinical data, live identity/provider, product mutation, deployment, production or release occurred.",
                    "The user-owned docs/branding directory remained untracked, unstaged and excluded.",
                ],
            },
            "decisions": [
                {
                    "id": "reuse-api-spine-practitioner-directory-200",
                    "source": ARTIFACTS["graphql_schema"],
                    "status": "accepted",
                    "summary": "Keep the existing GraphQL field and shared read service; inject one endpoint-owned authorization callback before the query.",
                },
                {
                    "id": "exact-column-product-role-200",
                    "source": ARTIFACTS["product_role"],
                    "status": "accepted",
                    "summary": "Use a separate finite NOINHERIT product login/capability with exact display-source SELECT columns and no auth-state or write access.",
                },
                {
                    "id": "unattributed-session-generic-denial-200",
                    "source": ARTIFACTS["role_runtime"],
                    "status": "accepted",
                    "summary": "Classify an unresolvable session with a boolean resolver recheck so it returns generic 401 without fabricating practice-scoped forced-RLS audit data; identifiable audit failures remain 503.",
                },
            ],
            "claim_scope": [
                "Real loopback HTTP and disposable PostgreSQL prove one exact active-practitioner-directory projection, required allow/deny audit and complete server/database/four-role cleanup.",
                "Six direct least-privilege probes deny product-write, sensitive-column, auth-table and cross-role access with PostgreSQL 42501.",
                "Provider calls, real identities, patient/clinical reads and product writes remain zero.",
            ],
            "contract_evidence": [],
            "evidence": _evidence(),
            "unresolved_gates": [
                "Real identity mapping and live Microsoft/provider interoperability remain closed.",
                "Patient/clinical reads, other product resources and every command/write remain closed.",
                "The GraphQL factory is unmounted and no Office UI consumer is established.",
                "Production secret custody, product-table RLS, distributed abuse resistance and monitoring remain closed.",
                "Cloud/IAM, deployment, protected integration, production, release and GitHub Pages remain separately closed.",
            ],
        }
    )
    graph["graph_revision"] = 200
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 181
        and compass["source_graph_revision"] == 200
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 180
        or compass["source_graph_revision"] != 199
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected product-read Compass predecessor.")
    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["migration"],
        ARTIFACTS["product_bridge"],
        ARTIFACTS["product_role"],
        ARTIFACTS["graphql_adapter"],
        ARTIFACTS["evidence"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": "Open the least-sensitive provider-free product read behind the accepted application session",
            "outcome": "One unmounted endpoint factory now authorizes and audits an active authored-synthetic practitioner-directory read through exact product columns.",
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Provider-free active-practitioner-directory authorization bridge",
        "why_now": "Yuri chose the product-authorization direction after the provider-free OIDC bridge closed at an application session.",
        "outcome": "Real loopback HTTP and disposable PostgreSQL prove exact current-principal checks, required authorization audit, display-safe projection, least-privilege product access and complete cleanup.",
        "unlocks": [
            "Review the result on its stacked draft pull request.",
            "A later bounded tranche may connect a supervised authored-synthetic Office consumer to this still-unmounted factory.",
        ],
        "does_not_solve": [
            "Real identity, live Microsoft/provider interoperability or real principal mapping.",
            "Patient/clinical reads, other product resources, commands or writes.",
            "General endpoint mounting, Office UI consumption, production security, deployment or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions["choose-post-redemption-identity-or-product-direction"]
    completed["required_before"] = (
        "Satisfied on 2026-08-02: Yuri selected the bounded provider-free product-authorization path; live identity and broader product authority remain closed."
    )
    completed["evidence"] = evidence
    next_id = "authorize-provider-free-office-directory-consumer"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should a supervised authored-synthetic Office consumer be connected to the default-off practitioner-directory factory?",
                "required_before": "Required before adding a taskpane consumer or task-specific mount; real identity, patient/clinical data and production remain separately closed.",
                "evidence": evidence,
            }
        )
    compass["map_limits"].insert(
        0,
        "The practitioner-directory result is provider-free, authored-synthetic, active-only and unmounted; it proves neither real identity nor patient/clinical product access.",
    )
    compass["orientation_statement"] = (
        "EMR4 now extends its provider-free application session to one unmounted, active-only authored-synthetic practitioner-directory read. Continuity 200 / Compass 181 bind exact current-principal checks, required authorization audit, display-safe product columns and zero patient/clinical/provider/write authority. Real identity, broader product access, deployment, production and release remain closed."
    )
    compass["map_revision"] = 181
    compass["source_graph_revision"] = 200
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)


def render_report() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    report = ariadne_compass.build_compass_report(compass, graph, repo_root=ROOT)
    if report["status"] != "passed":
        raise SystemExit("Compass validation failed: " + ", ".join(report["reasons"]))
    REPORT.write_text(ariadne_compass.render_markdown(report), encoding="utf-8")


def main() -> int:
    update_graph()
    update_compass()
    render_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
