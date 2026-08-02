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
UPDATED_AT = "2026-08-02T08:00:00Z"
BRANCH = "codex/raisa-postgresql-oidc-operational-connection-boundary"
SOURCE_HEAD = "559ef5de02355effa48676736681ac03323fb8fe"
PARENT = "raisa-postgresql-oidc-authorization-attempt-store"
NODE = "raisa-postgresql-oidc-operational-connection-boundary"

ARTIFACTS = {
    "plan": "docs/raisa-postgresql-oidc-operational-connection-boundary-plan.md",
    "design": "docs/raisa-postgresql-oidc-operational-connection-boundary-design.md",
    "threat": "docs/security/raisa-postgresql-oidc-operational-connection-boundary-threat-model-delta.md",
    "role": "app/services/application_identity_oidc_attempt_database_role.py",
    "runtime": "app/services/application_identity_oidc_attempt_operational.py",
    "evidence": "orchestration/continuity/raisa-postgresql-oidc-operational-connection-boundary/live-local-backend-postgres-operational-evidence.json",
    "closeout": "docs/raisa-postgresql-oidc-operational-connection-boundary-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-operational-connection-boundary-sol-acceptance.md",
    "runtime_state": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-operational-connection-boundary-rehydration-runtime-state.json",
    "rehydration": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-operational-connection-boundary-rehydration-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-operational-connection-boundary-preacceptance-receipt.json",
    "prepush": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-operational-connection-boundary-prepush-receipt.json",
    "runner": "scripts/raisa_postgresql_oidc_operational_connection_boundary_acceptance.py",
    "tests": "tests/test_raisa_postgresql_oidc_operational_connection_boundary.py",
    "continuity_runner": "scripts/raisa_postgresql_oidc_operational_connection_boundary_continuity_update.py",
    "continuity_tests": "tests/test_raisa_postgresql_oidc_operational_connection_boundary_continuity.py",
}


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _evidence() -> dict[str, list[str]]:
    return {
        "plans": [ARTIFACTS["plan"], ARTIFACTS["design"], ARTIFACTS["threat"]],
        "findings": [ARTIFACTS["role"], ARTIFACTS["runtime"], ARTIFACTS["evidence"]],
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
    if graph["graph_revision"] == 196:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 196 has an unexpected terminal node.")
        return
    if graph["graph_revision"] != 195 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected OIDC operational-boundary predecessor.")
    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa PostgreSQL OIDC Operational Connection Boundary",
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
                        "scope": "Implement the provider-free finite LOGIN, exact bounded pool role/reset lifecycle and credential-free runtime key-provider/configuration seam for the accepted dormant PostgreSQL attempt store.",
                    }
                ],
                "notes": [
                    "Yuri explicitly authorised the next candidate tranche.",
                    "No persistent credential, hosted connection, route, provider call, real identity, binding, application session, product read, deployment, production or release occurred.",
                    "The user-owned docs/branding directory remained untracked, unstaged and excluded.",
                ],
            },
            "decisions": [
                {
                    "id": "separate-login-from-attempt-capability-196",
                    "source": ARTIFACTS["role"],
                    "status": "accepted",
                    "summary": "Use one finite PASSWORD NULL NOINHERIT LOGIN with membership only in the exact NOLOGIN attempt-table capability.",
                },
                {
                    "id": "verify-pool-checkout-and-return-hygiene-196",
                    "source": ARTIFACTS["runtime"],
                    "status": "accepted",
                    "summary": "Verify capability and timeout setup on checkout, then rollback and verify RESET ROLE/ALL to the LOGIN before physical-connection reuse.",
                },
                {
                    "id": "resolve-bounded-keys-by-reference-196",
                    "source": ARTIFACTS["runtime"],
                    "status": "accepted",
                    "summary": "Keep raw keys outside configuration and resolve one active plus bounded retained cipher/digest references through one exact provider port without fallback or cross-use.",
                },
                {
                    "id": "keep-oidc-transport-and-identity-closed-196",
                    "source": ARTIFACTS["closeout"],
                    "status": "accepted",
                    "summary": "Operational construction remains dormant and adds no mounted route, live provider, real identity, binding, session or product authority.",
                },
            ],
            "claim_scope": [
                "Disposable loopback PostgreSQL proves exact LOGIN/capability separation, direct-LOGIN denial and complete database/two-role cleanup.",
                "One deliberately contaminated physical connection resets to the LOGIN and restores exact capability/timeouts on reuse; pool exhaustion is bounded.",
                "A fresh rotated runtime consumes an old encrypted attempt with zero raw flow/key/password/reference residue.",
            ],
            "contract_evidence": [],
            "evidence": _evidence(),
            "unresolved_gates": [
                "A default-off provider-free mounted OIDC start/callback transport boundary requires fresh authority.",
                "Live Microsoft and real identity require later separate authority.",
                "Binding resolution, admission-grant/session redeem and product reads remain closed.",
                "Production credential/key custody, managed pooler/TLS, distributed abuse resistance and monitoring remain closed.",
                "Cloud/IAM, deployment, protected integration, production, release and GitHub Pages remain separately closed.",
            ],
        }
    )
    graph["graph_revision"] = 196
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 177
        and compass["source_graph_revision"] == 196
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 176
        or compass["source_graph_revision"] != 195
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected OIDC operational-boundary Compass predecessor.")
    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["role"],
        ARTIFACTS["runtime"],
        ARTIFACTS["evidence"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": "Make the durable attempt store operationally constructible without mounting identity transport",
            "outcome": "A finite LOGIN, verified pool-role lifecycle and bounded key-reference provider now assemble the dormant provider-free store.",
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Provider-free operational connection and key-configuration boundary",
        "why_now": "The accepted durable store still lacked an authenticating principal, reusable pool hygiene and a credential-free key startup seam; Yuri authorised that exact gap.",
        "outcome": "Disposable PostgreSQL proves membership-only LOGIN isolation, contaminated-session reset, bounded exhaustion, exact capability restoration and fresh-runtime key rotation with complete cleanup.",
        "unlocks": [
            "Review the operational connection result on its stacked draft pull request.",
            "Seek fresh authority for a default-off provider-free mounted OIDC start/callback transport boundary.",
        ],
        "does_not_solve": [
            "Persistent production password/key custody, hosted database connectivity, managed pooler/TLS or monitoring.",
            "Mounted start/callback routes, CSRF/origin edge, bridge page, live Microsoft or real identity.",
            "Binding, admission-grant/session redeem, product access, distributed abuse resistance, deployment, production or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions[
        "authorize-postgresql-oidc-attempt-store-operational-connection-boundary"
    ]
    completed["required_before"] = (
        "Satisfied on 2026-08-02 only for the provider-free dormant finite LOGIN/pool and key-reference configuration seam. Mounted routes, live Microsoft, real identity, bindings, sessions and product reads remain closed."
    )
    completed["evidence"] = evidence
    next_id = "authorize-provider-free-oidc-start-callback-transport-boundary"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should EMR4 add a default-off provider-free mounted OIDC start/callback transport boundary with exact origin/CSRF, bounded form_post and a restrictive no-store bridge page?",
                "required_before": "Any mounted OIDC start/callback route or browser bridge page. Live Microsoft, real identity, binding, session redeem and product reads remain separately closed.",
                "evidence": evidence,
            }
        )
    obsolete_limits = {
        "The PostgreSQL OIDC attempt-store result is provider-free and authored-synthetic only; it has no deployment LOGIN/pool, runtime key custody, route or live identity authority.",
        "The OIDC runtime-adapter result is default-off, route-free and provider-free; its encrypted attempt store is process-local and not deployable distributed persistence.",
    }
    compass["map_limits"] = [
        item for item in compass["map_limits"] if item not in obsolete_limits
    ]
    compass["map_limits"].insert(
        0,
        "The PostgreSQL OIDC operational result is provider-free and dormant: its PASSWORD NULL LOGIN contract and key-reference seam prove no persistent credential, secret-manager custody, mounted route, live identity, deployment or production readiness.",
    )
    compass["orientation_statement"] = (
        "EMR4 now has a dormant provider-free Microsoft OIDC operational foundation: the durable encrypted attempt store sits behind a finite membership-only LOGIN, verified pool checkout/reset lifecycle and bounded credential-free key-reference seam. Continuity 196 / Compass 177 bind the local authored-synthetic result. Mounted transport, live Microsoft, real identity, binding/session/product access, cloud/IAM, deployment, production and release remain closed."
    )
    compass["map_revision"] = 177
    compass["source_graph_revision"] = 196
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
