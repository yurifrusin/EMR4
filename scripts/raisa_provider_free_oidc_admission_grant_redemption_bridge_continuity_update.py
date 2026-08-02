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
UPDATED_AT = "2026-08-02T13:00:00Z"
BRANCH = "codex/raisa-provider-free-oidc-admission-grant-redemption-bridge"
SOURCE_HEAD = "511fe57965c9f59d233fd521477bc1236f57d046"
PARENT = "raisa-provider-free-oidc-binding-admission-grant-boundary"
NODE = "raisa-provider-free-oidc-admission-grant-redemption-bridge"

ARTIFACTS = {
    "plan": "docs/raisa-provider-free-oidc-admission-grant-redemption-bridge-plan.md",
    "design": "docs/raisa-provider-free-oidc-admission-grant-redemption-bridge-design.md",
    "threat": "docs/security/raisa-provider-free-oidc-admission-grant-redemption-bridge-threat-model-delta.md",
    "auth_model": "app/models/application_auth.py",
    "federation_model": "app/models/application_identity_federation.py",
    "migration": "alembic/versions/t9u0v1w2x3y4_add_oidc_grant_redemption_bridge.py",
    "role": "app/services/application_identity_oidc_redemption_database_role.py",
    "operational": "app/services/application_identity_oidc_redemption_operational.py",
    "service": "app/services/application_identity_oidc_redemption.py",
    "persistence": "app/services/application_auth_persistence.py",
    "runtime": "app/services/application_auth_role_runtime.py",
    "router": "app/routers/application_auth.py",
    "openapi": "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml",
    "evidence": "orchestration/continuity/raisa-provider-free-oidc-admission-grant-redemption-bridge/live-local-http-backend-postgres-redemption-evidence.json",
    "closeout": "docs/raisa-provider-free-oidc-admission-grant-redemption-bridge-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-admission-grant-redemption-bridge-sol-acceptance.md",
    "runtime_state": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-admission-grant-redemption-bridge-rehydration-runtime-state.json",
    "rehydration": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-admission-grant-redemption-bridge-rehydration-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-admission-grant-redemption-bridge-preacceptance-receipt.json",
    "prepush": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-admission-grant-redemption-bridge-prepush-receipt.json",
    "runner": "scripts/raisa_provider_free_oidc_admission_grant_redemption_bridge_acceptance.py",
    "tests": "tests/test_raisa_provider_free_oidc_admission_grant_redemption_bridge.py",
    "continuity_runner": "scripts/raisa_provider_free_oidc_admission_grant_redemption_bridge_continuity_update.py",
    "continuity_tests": "tests/test_raisa_provider_free_oidc_admission_grant_redemption_bridge_continuity.py",
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
            ARTIFACTS["auth_model"],
            ARTIFACTS["federation_model"],
            ARTIFACTS["migration"],
            ARTIFACTS["role"],
            ARTIFACTS["operational"],
            ARTIFACTS["service"],
            ARTIFACTS["persistence"],
            ARTIFACTS["runtime"],
            ARTIFACTS["router"],
            ARTIFACTS["openapi"],
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
    if graph["graph_revision"] == 199:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 199 has an unexpected terminal node.")
        graph["nodes"][-1]["evidence"] = _evidence()
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 198 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected redemption predecessor.")
    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa Provider-Free OIDC Admission-Grant Redemption Bridge",
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
                        "scope": "Atomically redeem one provider-free authored-synthetic admission grant into the accepted application-session runtime after exact binding/version and fresh internal security-principal checks.",
                    }
                ],
                "notes": [
                    "Yuri preauthorised this final provider-free descendant unless a material direction choice arose.",
                    "No live Microsoft call, real identity, product read, deployment, production or release occurred.",
                    "The user-owned docs/branding directory remained untracked, unstaged and excluded.",
                ],
            },
            "decisions": [
                {
                    "id": "reuse-one-session-policy-transaction-199",
                    "source": ARTIFACTS["persistence"],
                    "status": "accepted",
                    "summary": "Reuse ApplicationAuthRuntime inside the grant transaction so consumption, required audits and hash-only session state commit once without a second policy engine.",
                },
                {
                    "id": "lock-current-binding-and-principal-truth-199",
                    "source": ARTIFACTS["migration"],
                    "status": "accepted",
                    "summary": "Lock the grant, reselect its immutable active binding/version and lock exact authored-synthetic user/practice/role/practitioner-link truth before session creation.",
                },
                {
                    "id": "cookie-after-known-commit-only-199",
                    "source": ARTIFACTS["router"],
                    "status": "accepted",
                    "summary": "Return the surface bearer only after known commit and then set the accepted session and CSRF cookies under no-store exact-origin transport.",
                },
            ],
            "claim_scope": [
                "Real loopback HTTP and disposable PostgreSQL prove one-use atomic authored-synthetic redemption, exact cookies, binding/principal freshness, audit rollback and complete seven-role/database/server cleanup.",
                "Two independent sessions racing one grant admit exactly one session and one generic conflict.",
                "Provider calls, real identities and product reads remain zero.",
            ],
            "contract_evidence": [],
            "evidence": _evidence(),
            "unresolved_gates": [
                "Live Microsoft interoperability and real identity/principal truth remain closed.",
                "Real binding administration/recovery and product authorization/read paths remain closed.",
                "Production secret custody, hosted connectivity, distributed abuse resistance and monitoring remain closed.",
                "Cloud/IAM, deployment, protected integration, production, release and GitHub Pages remain separately closed.",
                "The next product/security direction is a material Yuri-owned choice.",
            ],
        }
    )
    graph["graph_revision"] = 199
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 180
        and compass["source_graph_revision"] == 199
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 179
        or compass["source_graph_revision"] != 198
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected redemption Compass predecessor.")
    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["migration"],
        ARTIFACTS["role"],
        ARTIFACTS["service"],
        ARTIFACTS["router"],
        ARTIFACTS["openapi"],
        ARTIFACTS["evidence"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": "Close the provider-free external-authentication bridge at an atomic backend-owned application session",
            "outcome": "One-use grant redemption now rechecks binding and current synthetic principal truth and commits the accepted session/cookies without product authority.",
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Provider-free atomic admission-grant redemption bridge",
        "why_now": "The accepted callback deliberately stopped at a 60-second non-session artifact; Yuri preauthorised the final atomic bridge descendant.",
        "outcome": "Real loopback HTTP and disposable PostgreSQL prove one-use grant consumption, binding/version and fresh authored-synthetic principal checks, accepted session policy reuse, exact post-commit cookies and complete cleanup.",
        "unlocks": [
            "Review the completed three-descendant provider-free bridge sequence on its stacked draft pull requests.",
            "Choose the next product/security direction before opening real identity, product authorization or live-provider work.",
        ],
        "does_not_solve": [
            "Live Microsoft/provider interoperability or real identities.",
            "Real binding administration, real principal truth or product authorization/reads.",
            "Production secret custody, hosted connectivity, distributed abuse resistance, monitoring, deployment, production or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions[
        "authorize-provider-free-oidc-admission-grant-redemption-bridge"
    ]
    completed["required_before"] = (
        "Satisfied on 2026-08-02 only for provider-free authored-synthetic atomic grant redemption and session cookies. Live identity and product authority remain closed."
    )
    completed["evidence"] = evidence
    next_id = "choose-post-redemption-identity-or-product-direction"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should the next tranche pursue live-provider interoperability, real internal principal mapping, or a separately bounded product-authorization path?",
                "required_before": "This is a material direction choice after the three authorised provider-free bridge descendants; no option is implied by the current acceptance.",
                "evidence": evidence,
            }
        )
    compass["map_limits"].insert(
        0,
        "The atomic redemption result remains provider-free and authored-synthetic: its session cookies prove the backend transaction shape, not real identity or product authorization.",
    )
    compass["orientation_statement"] = (
        "EMR4 now closes the provider-free OIDC bridge at one backend-owned authored-synthetic application session. Continuity 199 / Compass 180 bind atomic grant consumption, active binding/version and fresh principal-truth checks, accepted session-policy reuse, exact post-commit cookies and zero provider/product authority. The next live-identity or product direction is a material Yuri-owned choice; cloud/IAM, deployment, production and release remain closed."
    )
    compass["map_revision"] = 180
    compass["source_graph_revision"] = 199
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
