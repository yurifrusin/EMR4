from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from scripts import ariadne_compass
except ModuleNotFoundError:  # Direct execution from scripts/.
    import ariadne_compass  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
UPDATED_AT = "2026-08-02T00:30:00Z"
BRANCH = "codex/raisa-oidc-verifier-session-bridge-architecture"
SOURCE_HEAD = "2e34bdad732fdab32fbf778280b3d3c70d66d602"
PARENT = "raisa-microsoft-federation-postgresql-persistence"
NODE = "raisa-maintained-oidc-verifier-session-bridge-architecture"

ARTIFACTS = {
    "plan": "docs/raisa-maintained-oidc-verifier-session-bridge-architecture-plan.md",
    "design": "docs/raisa-maintained-oidc-verifier-session-bridge-architecture-design.md",
    "threat": (
        "docs/security/raisa-maintained-oidc-verifier-session-bridge-"
        "threat-model-delta.md"
    ),
    "openapi": (
        "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml"
    ),
    "policy_schema": (
        "orchestration/continuity/raisa-maintained-oidc-verifier-session-bridge-"
        "architecture/architecture-policy.schema.json"
    ),
    "policy": (
        "orchestration/continuity/raisa-maintained-oidc-verifier-session-bridge-"
        "architecture/architecture-policy.json"
    ),
    "decision_schema": (
        "orchestration/continuity/raisa-maintained-oidc-verifier-session-bridge-"
        "architecture/architecture-decision.schema.json"
    ),
    "cases": (
        "orchestration/continuity/raisa-maintained-oidc-verifier-session-bridge-"
        "architecture/acceptance-cases.json"
    ),
    "evidence": (
        "orchestration/continuity/raisa-maintained-oidc-verifier-session-bridge-"
        "architecture/provider-free-acceptance-evidence.json"
    ),
    "closeout": (
        "docs/raisa-maintained-oidc-verifier-session-bridge-architecture-"
        "closeout.md"
    ),
    "acceptance": (
        "orchestration/agent_inbox/codex/raisa-maintained-oidc-verifier-"
        "session-bridge-architecture-sol-acceptance.md"
    ),
    "rehydration": (
        "orchestration/agent_inbox/codex/raisa-oidc-verifier-session-bridge-"
        "architecture-rehydration-receipt.json"
    ),
    "postcompaction": (
        "orchestration/agent_inbox/codex/raisa-oidc-verifier-session-bridge-"
        "architecture-postcompaction-receipt.json"
    ),
    "preacceptance": (
        "orchestration/agent_inbox/codex/raisa-oidc-verifier-session-bridge-"
        "architecture-preacceptance-receipt.json"
    ),
    "runner": (
        "scripts/raisa_maintained_oidc_verifier_session_bridge_architecture_"
        "acceptance.py"
    ),
    "tests": (
        "tests/test_raisa_maintained_oidc_verifier_session_bridge_architecture.py"
    ),
    "continuity_runner": (
        "scripts/raisa_maintained_oidc_verifier_session_bridge_continuity_update.py"
    ),
    "continuity_tests": (
        "tests/test_raisa_maintained_oidc_verifier_session_bridge_continuity.py"
    ),
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
            ARTIFACTS["openapi"],
            ARTIFACTS["policy_schema"],
            ARTIFACTS["policy"],
            ARTIFACTS["decision_schema"],
            ARTIFACTS["cases"],
            ARTIFACTS["evidence"],
        ],
        "closeouts": [ARTIFACTS["closeout"]],
        "acceptances": [ARTIFACTS["acceptance"]],
        "receipts": [
            ARTIFACTS["rehydration"],
            ARTIFACTS["postcompaction"],
            ARTIFACTS["preacceptance"],
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
    if graph["graph_revision"] == 192:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 192 has an unexpected terminal node.")
        return
    if graph["graph_revision"] != 191 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected OIDC bridge architecture predecessor.")

    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa Maintained OIDC Verifier and Session Bridge Architecture",
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
                        "scope": (
                            "Architecture-only maintained OIDC verifier, least-"
                            "privilege provider-to-practice bootstrap and partition-"
                            "safe application-session bridge design."
                        ),
                    }
                ],
                "notes": [
                    (
                        "Yuri explicitly authorised this architecture-only successor "
                        "and its task-branch tests, commits, push and draft PR."
                    ),
                    (
                        "No dependency, provider request, real identity, route, "
                        "database role/function, application session, product read, "
                        "deployment, protected integration or Pages rebuild occurred."
                    ),
                    (
                        "The user-owned docs/branding/raisa directory remained "
                        "untracked, unstaged and excluded."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-msal-only-oidc-boundary-192",
                    "source": ARTIFACTS["design"],
                    "status": "accepted",
                    "summary": (
                        "Freeze MSAL Python as the sole future tenant-specific "
                        "confidential-client OIDC/code-flow verifier boundary."
                    ),
                },
                {
                    "id": "accept-execute-only-hmac-bootstrap-192",
                    "source": ARTIFACTS["threat"],
                    "status": "accepted",
                    "summary": (
                        "Replace table-owner bootstrap with one execute-only, forced-"
                        "RLS, HMAC-only resolver that audits before returning."
                    ),
                },
                {
                    "id": "accept-partition-safe-one-use-session-bridge-192",
                    "source": ARTIFACTS["openapi"],
                    "status": "accepted",
                    "summary": (
                        "Use a callback-cookie-free one-use grant and atomic original-"
                        "partition redemption across native Diary and both Word hosts."
                    ),
                },
                {
                    "id": "keep-live-identity-session-product-closed-192",
                    "source": ARTIFACTS["closeout"],
                    "status": "accepted",
                    "summary": (
                        "Keep dependencies, live Microsoft, real identity, database "
                        "objects, routes, sessions, product reads and deployment closed."
                    ),
                },
            ],
            "claim_scope": [
                "One schema-validated provider-free architecture matches all 33 authored-synthetic acceptance cases.",
                "MSAL-only verification, execute-only HMAC bootstrap and callback-cookie-free one-use grant redemption are frozen.",
                "Native Diary, installed Word and Word Online converge on one atomic backend-owned session path with fresh internal authority reload.",
            ],
            "contract_evidence": [],
            "evidence": _evidence(),
            "unresolved_gates": [
                "MSAL dependency, licence/SBOM/security admission and offline adapter implementation require fresh authority.",
                "Database resolver/grant roles, functions, RLS and concurrency require a later disposable-PostgreSQL implementation gate.",
                "Live Microsoft, real identity, routes, product reads, organisational deployment, production and release remain closed.",
                "Protected integration and any further GitHub Pages rebuild remain separately closed.",
            ],
        }
    )
    graph["graph_revision"] = 192
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 173
        and compass["source_graph_revision"] == 192
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 172
        or compass["source_graph_revision"] != 191
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected OIDC bridge Compass predecessor.")

    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["openapi"],
        ARTIFACTS["policy"],
        ARTIFACTS["evidence"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": (
                "Maintained Microsoft OIDC, least-privilege identity bootstrap "
                "and partition-safe application-session architecture"
            ),
            "outcome": (
                "A 33-case provider-free architecture freezes MSAL-only tenant-"
                "specific verification, execute-only HMAC bootstrap and one-use "
                "original-partition session redemption with fresh internal truth."
            ),
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": (
            "Maintained Microsoft OIDC, least-privilege identity bootstrap and "
            "partition-safe application-session architecture"
        ),
        "why_now": (
            "The protected-integrated federation persistence parent deliberately "
            "left maintained cryptographic verification, table-owner-free bootstrap "
            "and cross-Office session handoff as the next security boundary."
        ),
        "outcome": (
            "The architecture passes 33 exact provider-free cases and freezes one "
            "backend-owned path without adding a dependency, provider call, route, "
            "database object, session, product read or deployment."
        ),
        "unlocks": [
            "Review the architecture in its draft task-branch pull request without moving protected refs.",
            "Seek fresh authority for MSAL dependency review/pinning and a provider-free offline adapter-admission implementation.",
            "Later seek separate authority for disposable-PostgreSQL resolver/grant capability implementation.",
            "Keep Dependabot alert 17 as a separate explicit native-disposition decision.",
        ],
        "does_not_solve": [
            "Live Microsoft Entra registration, discovery, token exchange, key rollover or real identity.",
            "Database resolver/grant privilege and concurrency correctness.",
            "A live callback, application session, product read or endpoint authorization.",
            "Distributed abuse resistance, key custody, incident paging/SIEM, deployment, production or release.",
            "Protected integration, another GitHub Pages rebuild or Dependabot alert 17 disposition.",
        ],
        "evidence": evidence,
    }

    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions[
        "authorize-maintained-oidc-verifier-session-bridge-architecture"
    ]
    completed["required_before"] = (
        "Satisfied on 2026-08-02 for architecture-only MSAL verifier, execute-only "
        "HMAC bootstrap and partition-safe application-session bridge design. "
        "Dependencies, live Microsoft, real identity, database objects, routes, "
        "sessions, product reads and deployment remain closed."
    )
    completed["evidence"] = evidence

    next_id = "authorize-msal-offline-adapter-dependency-tranche"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": (
                    "Should EMR4 review and pin MSAL Python, then implement its "
                    "provider adapter behind provider-free offline fault fixtures?"
                ),
                "required_before": (
                    "Any package/dependency addition or maintained-verifier adapter "
                    "implementation. Live network, real identity, routes, database "
                    "changes and product reads would remain separately closed."
                ),
                "evidence": evidence,
            }
        )

    compass["map_limits"].insert(
        0,
        (
            "The maintained OIDC/bootstrap/session-bridge result is architecture-only. "
            "It proves no dependency installation, live provider behavior, real "
            "identity, database capability, session, product access or deployment."
        ),
    )
    compass["orientation_statement"] = (
        "EMR4 now has an accepted architecture for MSAL-only tenant-specific OIDC, "
        "execute-only HMAC identity bootstrap and one-use original-partition session "
        "redemption. Continuity 192 / Compass 173 bind the provider-free result. "
        "Dependency admission, live Microsoft, real identity, database capability, "
        "application sessions, product reads, protected integration, production and "
        "release remain closed."
    )
    compass["map_revision"] = 173
    compass["source_graph_revision"] = 192
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
