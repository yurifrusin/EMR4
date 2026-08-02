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
UPDATED_AT = "2026-08-02T07:00:00Z"
BRANCH = "codex/raisa-postgresql-oidc-authorization-attempt-store"
SOURCE_HEAD = "e3a0cb7b8259250dd021924df05c70d9f9ab576c"
PARENT = "raisa-two-component-oidc-runtime-adapter"
NODE = "raisa-postgresql-oidc-authorization-attempt-store"

ARTIFACTS = {
    "plan": "docs/raisa-postgresql-oidc-authorization-attempt-store-plan.md",
    "design": "docs/raisa-postgresql-oidc-authorization-attempt-store-design.md",
    "threat": "docs/security/raisa-postgresql-oidc-authorization-attempt-store-threat-model-delta.md",
    "adapter": "app/services/application_identity_oidc_adapter.py",
    "model": "app/models/application_identity_oidc_attempt.py",
    "migration": "alembic/versions/r7s8t9u0v1w2_add_oidc_authorization_attempt_store.py",
    "role": "app/services/application_identity_oidc_attempt_database_role.py",
    "store": "app/services/application_identity_oidc_attempt_store.py",
    "evidence": "orchestration/continuity/raisa-postgresql-oidc-authorization-attempt-store/live-local-backend-postgres-evidence.json",
    "closeout": "docs/raisa-postgresql-oidc-authorization-attempt-store-closeout.md",
    "acceptance": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-authorization-attempt-store-sol-acceptance.md",
    "rehydration": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-authorization-attempt-store-rehydration-receipt.json",
    "preacceptance": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-authorization-attempt-store-preacceptance-receipt.json",
    "prepush": "orchestration/agent_inbox/codex/raisa-postgresql-oidc-authorization-attempt-store-prepush-receipt.json",
    "runner": "scripts/raisa_postgresql_oidc_authorization_attempt_store_acceptance.py",
    "tests": "tests/test_raisa_postgresql_oidc_authorization_attempt_store.py",
    "continuity_runner": "scripts/raisa_postgresql_oidc_authorization_attempt_store_continuity_update.py",
    "continuity_tests": "tests/test_raisa_postgresql_oidc_authorization_attempt_store_continuity.py",
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
            ARTIFACTS["adapter"],
            ARTIFACTS["model"],
            ARTIFACTS["migration"],
            ARTIFACTS["role"],
            ARTIFACTS["store"],
            ARTIFACTS["evidence"],
        ],
        "closeouts": [ARTIFACTS["closeout"]],
        "acceptances": [ARTIFACTS["acceptance"]],
        "receipts": [
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
    if graph["graph_revision"] == 195:
        if graph["nodes"][-1]["id"] != NODE:
            raise SystemExit("Revision 195 has an unexpected terminal node.")
        return
    if graph["graph_revision"] != 194 or graph["nodes"][-1]["id"] != PARENT:
        raise SystemExit("Unexpected PostgreSQL OIDC attempt-store predecessor.")
    graph["nodes"].append(
        {
            "id": NODE,
            "title": "Raisa PostgreSQL OIDC Authorization-Attempt Store",
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
                        "scope": "Implement provider-free durable encrypted authorization attempts with exact atomic consume, bounded expiry/capacity and least-privilege role/RLS.",
                    }
                ],
                "notes": [
                    "Yuri explicitly authorised the next tranche as described after the route-free adapter passed.",
                    "No route, provider call, real identity, binding, application session, product read, deployment, production or release occurred.",
                    "The user-owned docs/branding directory remained untracked, unstaged and excluded.",
                ],
            },
            "decisions": [
                {
                    "id": "persist-encrypted-oidc-attempts-195",
                    "source": ARTIFACTS["store"],
                    "status": "accepted",
                    "summary": "Persist only state/nonce HMAC references plus a versioned authenticated-encryption envelope and exact five-minute metadata.",
                },
                {
                    "id": "consume-before-exchange-with-delete-returning-195",
                    "source": ARTIFACTS["design"],
                    "status": "accepted",
                    "summary": "Commit one DELETE RETURNING before expiry/decrypt checks or provider exchange so replay, corruption and concurrency are terminal.",
                },
                {
                    "id": "bound-attempt-capability-with-role-and-rls-195",
                    "source": ARTIFACTS["role"],
                    "status": "accepted",
                    "summary": "Give an exact NOLOGIN capability role only select/insert/delete on the forced-RLS attempt table; grant no update or product access.",
                },
                {
                    "id": "keep-routes-identity-session-product-closed-195",
                    "source": ARTIFACTS["closeout"],
                    "status": "accepted",
                    "summary": "Durable authored-synthetic attempts add no route, live identity, binding, session or product authority.",
                },
            ],
            "claim_scope": [
                "Disposable loopback PostgreSQL proves migration reversibility, exact grants, forced RLS and complete database/role cleanup.",
                "Two concurrent callbacks produce one deletion, one synthetic exchange, one verification and one bounded principal release.",
                "Rotation, expiry, capacity, collision, audit cleanup and tamper cases pass with no raw flow/key residue in an active row.",
            ],
            "contract_evidence": [],
            "evidence": _evidence(),
            "unresolved_gates": [
                "A finite deployment LOGIN, exact pool SET ROLE and runtime key-provider/configuration seam require fresh authority.",
                "Any start/callback route, CSRF/origin edge, callback page or admission-grant bridge requires later separate authority.",
                "Live Microsoft and real identity require later separate authority.",
                "Binding resolution, application sessions, product reads, monitoring, deployment, production and release remain closed.",
                "Protected integration and GitHub Pages remain separately closed.",
            ],
        }
    )
    graph["graph_revision"] = 195
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 176
        and compass["source_graph_revision"] == 195
        and compass["current_position"]["node_id"] == NODE
    ):
        return
    if (
        compass["map_revision"] != 175
        or compass["source_graph_revision"] != 194
        or compass["current_position"]["node_id"] != PARENT
    ):
        raise SystemExit("Unexpected PostgreSQL OIDC attempt-store Compass predecessor.")
    evidence = [
        ARTIFACTS["plan"],
        ARTIFACTS["design"],
        ARTIFACTS["threat"],
        ARTIFACTS["model"],
        ARTIFACTS["migration"],
        ARTIFACTS["role"],
        ARTIFACTS["store"],
        ARTIFACTS["evidence"],
        ARTIFACTS["closeout"],
    ]
    compass["journey"].append(
        {
            "node_id": NODE,
            "lineage_parent": PARENT,
            "strategic_role": "Make one-use OIDC attempts durable across processes without opening a route or identity authority",
            "outcome": "A synthetic-only forced-RLS PostgreSQL store now preserves encrypted flow material and exact cross-session consume-before-exchange semantics.",
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE,
        "strategic_role": "Provider-free durable Microsoft OIDC authorization-attempt foundation",
        "why_now": "The route-free adapter exposed a frozen persistence port and Yuri authorised its durable PostgreSQL descendant.",
        "outcome": "One encrypted authored-synthetic attempt table, versioned keyrings, bounded capacity/expiry and exact NOLOGIN role/RLS pass disposable local PostgreSQL acceptance.",
        "unlocks": [
            "Review the durable attempt-store result on its stacked draft pull request.",
            "Seek fresh authority for a provider-free finite LOGIN/pool and runtime key-provider configuration boundary.",
        ],
        "does_not_solve": [
            "Deployment credentials/pool, mounted callback routes, CSRF/origin edge or browser handoff.",
            "Live Microsoft behavior, real tenant/identity, binding or application session issuance.",
            "Product authorization/read access, distributed abuse resistance, monitoring, deployment, production or release.",
        ],
        "evidence": evidence,
    }
    decisions = {item["id"]: item for item in compass["user_owned_decisions"]}
    completed = decisions["authorize-provider-free-postgresql-authorization-attempt-store"]
    completed["required_before"] = (
        "Satisfied on 2026-08-02 only for the provider-free authored-synthetic PostgreSQL attempt store. "
        "Operational LOGIN/pool, routes, live Microsoft, real identity, bindings, sessions and product reads remain closed."
    )
    completed["evidence"] = evidence
    next_id = "authorize-postgresql-oidc-attempt-store-operational-connection-boundary"
    if next_id not in decisions:
        compass["user_owned_decisions"].append(
            {
                "id": next_id,
                "question": "Should EMR4 add the provider-free finite LOGIN/pool and runtime key-provider configuration boundary for the accepted PostgreSQL OIDC attempt store?",
                "required_before": "Any durable attempt-store deployment connection or runtime key configuration. Routes, live Microsoft, real identity, bindings, sessions and product reads remain separately closed.",
                "evidence": evidence,
            }
        )
    compass["map_limits"].insert(
        0,
        "The PostgreSQL OIDC attempt-store result is provider-free and authored-synthetic only; it has no deployment LOGIN/pool, runtime key custody, route or live identity authority.",
    )
    compass["orientation_statement"] = (
        "EMR4 now has a dormant durable Microsoft OIDC attempt foundation: one forced-RLS PostgreSQL table stores only versioned state/nonce HMAC references and an authenticated-encryption envelope, and DELETE RETURNING commits exact one-use consumption before exchange. Continuity 195 / Compass 176 bind the provider-free result. Operational credentials/pool, routes, live identity, bindings, sessions, product access, deployment, production and release remain closed."
    )
    compass["map_revision"] = 176
    compass["source_graph_revision"] = 195
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
