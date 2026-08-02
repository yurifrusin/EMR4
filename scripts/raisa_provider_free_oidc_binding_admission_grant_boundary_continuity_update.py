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
UPDATED_AT = "2026-08-02T12:00:00Z"
BRANCH = "codex/raisa-provider-free-oidc-binding-admission-grant-boundary"
SOURCE_HEAD = "9a562c97b1761e61aa7614517d7ef4de5384703b"
PARENT = "raisa-provider-free-oidc-start-callback-transport-boundary"
NODE = "raisa-provider-free-oidc-binding-admission-grant-boundary"

ARTIFACTS = {
    "plan": "docs/raisa-provider-free-oidc-binding-admission-grant-boundary-plan.md",
    "design": "docs/raisa-provider-free-oidc-binding-admission-grant-boundary-design.md",
    "threat": "docs/security/raisa-provider-free-oidc-binding-admission-grant-boundary-threat-model-delta.md",
    "model": "app/models/application_identity_federation.py",
    "migration": "alembic/versions/s8t9u0v1w2x3_add_federation_admission_grants.py",
    "role": "app/services/application_identity_oidc_binding_database_role.py",
    "operational": "app/services/application_identity_oidc_binding_operational.py",
    "service": "app/services/application_identity_oidc_admission_grant.py",
    "transport": "app/services/application_identity_oidc_transport.py",
    "openapi": "docs/api-spine/openapi/application-identity-federation-session-bridge.yaml",
    "evidence": "orchestration/continuity/raisa-provider-free-oidc-binding-admission-grant-boundary/live-local-http-backend-postgres-evidence.json",
    "closeout": "docs/raisa-provider-free-oidc-binding-admission-grant-boundary-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-binding-admission-grant-boundary-sol-acceptance.md",
    "runtime_state": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-binding-admission-grant-boundary-rehydration-runtime-state.json",
    "rehydration": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-binding-admission-grant-boundary-rehydration-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-binding-admission-grant-boundary-preacceptance-receipt.json",
    "prepush": "orchestration/agent_inbox/codex/raisa-provider-free-oidc-binding-admission-grant-boundary-prepush-receipt.json",
    "runner": "scripts/raisa_provider_free_oidc_binding_admission_grant_boundary_acceptance.py",
    "tests": "tests/test_raisa_provider_free_oidc_binding_admission_grant_boundary.py",
    "continuity_runner": "scripts/raisa_provider_free_oidc_binding_admission_grant_boundary_continuity_update.py",
    "continuity_tests": "tests/test_raisa_provider_free_oidc_binding_admission_grant_boundary_continuity.py",
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
            ARTIFACTS["model"],
            ARTIFACTS["migration"],
            ARTIFACTS["role"],
            ARTIFACTS["operational"],
            ARTIFACTS["service"],
            ARTIFACTS["transport"],
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
    if graph["graph_revision"] == 198:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 198 has an unexpected terminal node.")
        graph["nodes"][-1]["authority"]["authorized_openings"][0][
            "boundary"
        ] = "api-change"
        graph["nodes"][-1]["evidence"] = _evidence()
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 197 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected binding admission predecessor.")
    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa Provider-Free OIDC Binding and Admission-Grant Boundary",
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
                        "scope": "Resolve one provider-free authored-synthetic Microsoft principal through exact HMAC-only PostgreSQL authority and issue one exact-origin 60-second admission grant without a session or product read.",
                    }
                ],
                "notes": [
                    "Yuri preauthorised this descendant and the following atomic redemption descendant unless a material directional choice arises.",
                    "No live Microsoft call, real identity, application session, cookie, product read, deployment, production or release occurred.",
                    "The user-owned docs/branding directory remained untracked, unstaged and excluded.",
                ],
            },
            "decisions": [
                {
                    "id": "split-binding-resolver-and-grant-issuer-198",
                    "source": ARTIFACTS["role"],
                    "status": "accepted",
                    "summary": "Separate resolver-call and grant-issuer capabilities behind one finite NOINHERIT login while keeping the security-definer owner ungranted and NOLOGIN.",
                },
                {
                    "id": "require-hmac-only-exact-subject-binding-198",
                    "source": ARTIFACTS["migration"],
                    "status": "accepted",
                    "summary": "Resolve issuer, tenant, object and subject HMACs under forced RLS and append resolved or rejected audit before returning any internal references.",
                },
                {
                    "id": "release-60-second-audited-grant-only-198",
                    "source": ARTIFACTS["service"],
                    "status": "accepted",
                    "summary": "Store only a separately keyed grant HMAC, force issued audit through a database trigger, and release the raw 256-bit bearer once through the exact-origin bridge.",
                },
            ],
            "claim_scope": [
                "Real loopback HTTP and disposable PostgreSQL prove exact HMAC binding resolution, a 60-second authored-synthetic grant, required audit and complete six-role/database/server cleanup.",
                "Direct login, resolver-call, grant-issuer and resolver-owner privilege probes deny every out-of-scope table edge under forced RLS.",
                "Provider calls, real identities, application sessions, cookies and product reads remain zero.",
            ],
            "contract_evidence": [],
            "evidence": _evidence(),
            "unresolved_gates": [
                "The preauthorised atomic admission-grant redemption bridge requires a fresh five-source tranche rehydration.",
                "Redemption must re-resolve binding version and load fresh internal principal truth before atomic grant consumption and session commit.",
                "Live Microsoft, real identity and product reads remain closed.",
                "Production secret custody, hosted connectivity, distributed abuse resistance and monitoring remain closed.",
                "Cloud/IAM, deployment, protected integration, production, release and GitHub Pages remain separately closed.",
            ],
        }
    )
    graph["graph_revision"] = 198
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 179
        and compass["source_graph_revision"] == 198
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 178
        or compass["source_graph_revision"] != 197
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected binding admission Compass predecessor.")
    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["migration"],
        ARTIFACTS["role"],
        ARTIFACTS["service"],
        ARTIFACTS["transport"],
        ARTIFACTS["openapi"],
        ARTIFACTS["evidence"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": "Bridge verified external identity to a tightly bounded, non-session internal admission artifact",
            "outcome": "Exact HMAC-only binding resolution now issues one audited 60-second exact-origin grant while session and product authority remain closed.",
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Provider-free HMAC binding and admission-grant boundary",
        "why_now": "The accepted callback transport deliberately stopped before binding and session authority; Yuri preauthorised the exact HMAC-only intermediate boundary.",
        "outcome": "Real loopback HTTP and disposable PostgreSQL prove exact four-component HMAC resolution, required audit, least-authority role separation and one 60-second exact-origin grant with complete cleanup.",
        "unlocks": [
            "Review the binding/grant result on its stacked draft pull request.",
            "Freshly rehydrate the preauthorised atomic admission-grant redemption descendant.",
        ],
        "does_not_solve": [
            "Live Microsoft/provider calls or real identities.",
            "Grant redemption, fresh internal principal truth, application sessions, cookies or product access.",
            "Production secret custody, hosted connectivity, distributed abuse resistance, monitoring, deployment, production or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions[
        "authorize-provider-free-oidc-binding-admission-grant-boundary"
    ]
    completed["required_before"] = (
        "Satisfied on 2026-08-02 only for provider-free authored-synthetic HMAC binding resolution and one 60-second admission grant. Redemption, session, cookie and product authority remain closed."
    )
    completed["evidence"] = evidence
    next_id = "authorize-provider-free-oidc-admission-grant-redemption-bridge"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should EMR4 atomically redeem the provider-free admission grant into the accepted application-session runtime?",
                "required_before": "Preauthorised by Yuri on 2026-08-02, but requires a fresh five-source tranche rehydration, exact binding-version recheck and fresh internal principal truth before any session or cookie.",
                "evidence": evidence,
            }
        )
    compass["map_limits"].insert(
        0,
        "The HMAC binding/admission result is provider-free and authored-synthetic: its 60-second bearer is not an application session and grants no cookie, product, deployment or production authority.",
    )
    compass["orientation_statement"] = (
        "EMR4 now has a provider-free HMAC-only binding resolver and audited 60-second exact-origin admission grant behind the default-off OIDC callback. Continuity 198 / Compass 179 bind four-component HMAC resolution, least-authority PostgreSQL roles, inseparable audit and zero session/product authority. Live Microsoft, real identity, redemption/session/cookies, product access, cloud/IAM, deployment, production and release remain closed."
    )
    compass["map_revision"] = 179
    compass["source_graph_revision"] = 198
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
