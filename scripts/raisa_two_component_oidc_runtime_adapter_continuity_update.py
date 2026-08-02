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
UPDATED_AT = "2026-08-02T05:00:00Z"
BRANCH = "codex/raisa-two-component-oidc-runtime-adapter"
SOURCE_HEAD = "d136a8c19be657f6adc5f40cb9d8415d3a9ce2b5"
PARENT = "raisa-two-component-oidc-verifier-architecture-revision"
NODE = "raisa-two-component-oidc-runtime-adapter"

ARTIFACTS = {
    "plan": "docs/raisa-two-component-oidc-runtime-adapter-plan.md",
    "design": "docs/raisa-two-component-oidc-runtime-adapter-design.md",
    "threat": "docs/security/raisa-two-component-oidc-runtime-adapter-threat-model-delta.md",
    "module": "app/services/application_identity_oidc_adapter.py",
    "openapi": "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml",
    "cases": "orchestration/continuity/raisa-two-component-oidc-runtime-adapter/acceptance-cases.json",
    "evidence": "orchestration/continuity/raisa-two-component-oidc-runtime-adapter/provider-free-acceptance-evidence.json",
    "closeout": "docs/raisa-two-component-oidc-runtime-adapter-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-two-component-oidc-runtime-adapter-sol-acceptance.md",
    "rehydration": "orchestration/agent_inbox/codex/raisa-two-component-oidc-runtime-adapter-rehydration-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-two-component-oidc-runtime-adapter-preacceptance-receipt.json",
    "runner": "scripts/raisa_two_component_oidc_runtime_adapter_acceptance.py",
    "tests": "tests/test_raisa_two_component_oidc_runtime_adapter.py",
    "continuity_runner": "scripts/raisa_two_component_oidc_runtime_adapter_continuity_update.py",
    "continuity_tests": "tests/test_raisa_two_component_oidc_runtime_adapter_continuity.py",
}


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _evidence() -> dict[str, list[str]]:
    return {
        "plans": [ARTIFACTS["plan"], ARTIFACTS["design"], ARTIFACTS["threat"]],
        "findings": [ARTIFACTS["module"], ARTIFACTS["openapi"], ARTIFACTS["cases"], ARTIFACTS["evidence"]],
        "closeouts": [ARTIFACTS["closeout"]],
        "acceptances": [ARTIFACTS["acceptance"]],
        "receipts": [ARTIFACTS["rehydration"], ARTIFACTS["preacceptance"]],
        "tests": [ARTIFACTS["runner"], ARTIFACTS["tests"], ARTIFACTS["continuity_runner"], ARTIFACTS["continuity_tests"]],
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 194:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 194 has an unexpected terminal node.")
        return
    if graph["graph_revision"] != 193 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected OIDC runtime-adapter predecessor.")
    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa Two-Component OIDC Runtime Adapter",
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
                        "scope": "Implement the provider-free default-off MSAL/Authlib adapter behind the frozen ports and fault matrix.",
                    }
                ],
                "notes": [
                    "Yuri explicitly authorised the next candidate after the two-component architecture revision.",
                    "No route, external network, real identity, database truth, binding, role, session, product read, deployment, production or release occurred.",
                    "The user-owned docs/branding directory remained untracked, unstaged and excluded.",
                ],
            },
            "decisions": [
                {
                    "id": "implement-route-free-msal-authlib-adapter-194",
                    "source": ARTIFACTS["module"],
                    "status": "accepted",
                    "summary": "Add a default-off application service in which MSAL owns code-flow mechanics and Authlib/JOSE RFC independently owns raw ID-token admission.",
                },
                {
                    "id": "encrypt-provider-free-authorization-attempt-194",
                    "source": ARTIFACTS["design"],
                    "status": "accepted",
                    "summary": "Keep the five-minute MSAL flow in a bounded process-local authenticated-encryption envelope keyed by state HMAC and atomically consume it before exchange.",
                },
                {
                    "id": "reconcile-msal-state-contract-194",
                    "source": ARTIFACTS["openapi"],
                    "status": "accepted",
                    "summary": "Accept the selected MSAL version's 22-character state while preserving exact HMAC correlation and a bounded 16-256-character schema.",
                },
                {
                    "id": "keep-identity-session-product-closed-194",
                    "source": ARTIFACTS["closeout"],
                    "status": "accepted",
                    "summary": "A verified external principal grants no binding, role, application session or product authority.",
                },
            ],
            "claim_scope": [
                "Twenty-five provider-free authored-synthetic cases pass, including the MSAL-claims bypass, encryption residue, one-use concurrency and Authlib token/JWKS fault matrix.",
                "MSAL start and one rejected redemption are exercised only over intercepted in-memory HTTP; outbound network and Microsoft provider calls are zero.",
                "The adapter is default-off and route-free, and releases only verified tid/oid/sub with explicit false authorization/session flags.",
            ],
            "contract_evidence": [],
            "evidence": _evidence(),
            "unresolved_gates": [
                "A provider-free durable PostgreSQL authorization-attempt store requires fresh authority.",
                "Any route, callback page, CSRF/origin edge or admission-grant bridge requires later separate authority.",
                "Live Microsoft registration/traffic and real identity require later separate authority.",
                "Binding resolution, application sessions, product reads, deployment, production and release remain closed.",
                "Protected integration and GitHub Pages remain separately closed.",
            ],
        }
    )
    graph["graph_revision"] = 194
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 175
        and compass["source_graph_revision"] == 194
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 174
        or compass["source_graph_revision"] != 193
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected OIDC runtime-adapter Compass predecessor.")
    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["module"],
        ARTIFACTS["openapi"],
        ARTIFACTS["evidence"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": "Implement the dormant two-component identity-verification seam without opening identity authority",
            "outcome": "The default-off route-free adapter now enforces encrypted one-use MSAL flow handling and independent Authlib verification across twenty-five provider-free cases.",
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Provider-free Microsoft OIDC protocol and verification runtime foundation",
        "why_now": "The corrected component ownership and reviewed dependencies were accepted and Yuri authorised their next implementation candidate.",
        "outcome": "A dormant application service now proves the exact MSAL/Authlib seam, one-use encrypted process-local attempts and normalized failure/audit behavior without a route or provider call.",
        "unlocks": [
            "Review the route-free runtime adapter on its stacked draft pull request.",
            "Seek fresh authority for a provider-free durable PostgreSQL authorization-attempt store behind the same port.",
        ],
        "does_not_solve": [
            "Distributed/durable attempt atomicity, callback routes, CSRF/origin edge or browser handoff.",
            "Live Microsoft behavior, tenant configuration, credential custody or real identity.",
            "Identity bindings, application sessions, product authorization, deployment, production or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions["authorize-two-component-oidc-runtime-adapter"]
    completed["required_before"] = (
        "Satisfied on 2026-08-02 only for the default-off route-free provider-free adapter. "
        "Routes, live Microsoft, real identity, database changes, sessions and product reads remain closed."
    )
    completed["evidence"] = evidence
    next_id = "authorize-provider-free-postgresql-authorization-attempt-store"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should EMR4 implement a provider-free PostgreSQL authorization-attempt store behind the accepted OIDC adapter port?",
                "required_before": "Any database migration, role/function/grant or durable attempt write. Routes, live Microsoft, real identity, bindings, sessions and product reads remain separately closed.",
                "evidence": evidence,
            }
        )
    compass["map_limits"].insert(
        0,
        "The OIDC runtime-adapter result is default-off, route-free and provider-free; its encrypted attempt store is process-local and not deployable distributed persistence.",
    )
    compass["orientation_statement"] = (
        "EMR4 now has a dormant two-component Microsoft OIDC runtime foundation: "
        "MSAL owns one-use code-flow mechanics and Authlib/JOSE RFC independently owns signed-token admission. "
        "Continuity 194 / Compass 175 bind twenty-five provider-free cases. Durable persistence, routes, live identity, bindings, sessions, product access, deployment, production and release remain closed."
    )
    compass["map_revision"] = 175
    compass["source_graph_revision"] = 194
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
