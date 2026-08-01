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
UPDATED_AT = "2026-08-01T06:00:00Z"
BRANCH = "codex/raisa-real-identity-microsoft-federation"

OFFICE_PARENT = "raisa-shared-application-auth-postgresql-office-host-compatibility"
ARCH_NODE = "raisa-real-identity-microsoft-federation-boundary"
RUNTIME_NODE = "raisa-microsoft-federation-admission-runtime"
PERSISTENCE_NODE = "raisa-microsoft-federation-postgresql-persistence"

RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-real-identity-microsoft-federation-three-tranche-"
    "rehydration-receipt.json"
)

ARCH = {
    "plan": "docs/raisa-real-identity-microsoft-federation-boundary-plan.md",
    "design": "docs/raisa-real-identity-microsoft-federation-boundary-design.md",
    "threat": (
        "docs/security/raisa-real-identity-microsoft-federation-boundary-"
        "threat-model-delta.md"
    ),
    "policy": (
        "orchestration/continuity/raisa-real-identity-microsoft-federation-"
        "boundary/federation-policy.json"
    ),
    "evidence": (
        "orchestration/continuity/raisa-real-identity-microsoft-federation-"
        "boundary/provider-free-acceptance-evidence.json"
    ),
    "closeout": (
        "docs/raisa-real-identity-microsoft-federation-boundary-closeout.md"
    ),
    "acceptance": (
        "orchestration/agent_inbox/codex/raisa-real-identity-microsoft-"
        "federation-boundary-sol-acceptance.md"
    ),
    "runner": (
        "scripts/raisa_real_identity_microsoft_federation_boundary_acceptance.py"
    ),
    "tests": (
        "tests/test_raisa_real_identity_microsoft_federation_boundary.py"
    ),
}
RUNTIME = {
    "plan": "docs/raisa-microsoft-federation-admission-runtime-plan.md",
    "threat": (
        "docs/security/raisa-microsoft-federation-admission-runtime-"
        "threat-model-delta.md"
    ),
    "service": "app/services/application_identity_federation.py",
    "evidence": (
        "orchestration/continuity/raisa-microsoft-federation-admission-"
        "runtime/provider-free-acceptance-evidence.json"
    ),
    "closeout": "docs/raisa-microsoft-federation-admission-runtime-closeout.md",
    "acceptance": (
        "orchestration/agent_inbox/codex/raisa-microsoft-federation-"
        "admission-runtime-sol-acceptance.md"
    ),
    "runner": (
        "scripts/raisa_microsoft_federation_admission_runtime_acceptance.py"
    ),
    "tests": "tests/test_raisa_microsoft_federation_admission_runtime.py",
}
PERSISTENCE = {
    "plan": "docs/raisa-microsoft-federation-postgresql-persistence-plan.md",
    "threat": (
        "docs/security/raisa-microsoft-federation-postgresql-persistence-"
        "threat-model-delta.md"
    ),
    "model": "app/models/application_identity_federation.py",
    "migration": (
        "alembic/versions/q6r7s8t9u0v1_add_application_identity_federation_"
        "persistence.py"
    ),
    "service": (
        "app/services/application_identity_federation_persistence.py"
    ),
    "evidence": (
        "orchestration/continuity/raisa-microsoft-federation-postgresql-"
        "persistence/live-local-backend-postgres-evidence.json"
    ),
    "closeout": (
        "docs/raisa-microsoft-federation-postgresql-persistence-closeout.md"
    ),
    "acceptance": (
        "orchestration/agent_inbox/codex/raisa-microsoft-federation-"
        "postgresql-persistence-sol-acceptance.md"
    ),
    "runner": (
        "scripts/raisa_microsoft_federation_postgresql_persistence_"
        "acceptance.py"
    ),
    "tests": (
        "tests/test_raisa_microsoft_federation_postgresql_persistence.py"
    ),
}


def _write(path: Path, value: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _node(
    *,
    node_id: str,
    title: str,
    parent_id: str,
    source_head: str,
    plan: str,
    claim_scope: list[str],
    decisions: list[dict[str, str]],
    evidence: dict[str, list[str]],
    unresolved_gates: list[str],
    authority_scope: str,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "title": title,
        "kind": "foundation",
        "status": "accepted",
        "created_at": UPDATED_AT,
        "updated_at": UPDATED_AT,
        "coordinates": {
            "git_ref": BRANCH,
            "source_head": source_head,
            "thread_id": None,
            "worktree_role": "task",
        },
        "relationships": [{"node_id": parent_id, "relation": "builds_on"}],
        "authority": {
            "authorized_openings": [
                {
                    "boundary": "api-change",
                    "source": plan,
                    "scope": authority_scope,
                }
            ],
            "notes": [
                (
                    "Yuri explicitly authorised the architecture-only real-"
                    "identity/Microsoft-federation boundary and its next two "
                    "logical descendants."
                ),
                (
                    "Live Microsoft/provider calls, public routes, real identity "
                    "data, application sessions and product reads remained closed."
                ),
                (
                    "The user-owned docs/branding/raisa directory remained "
                    "untracked, unstaged and excluded."
                ),
            ],
        },
        "decisions": decisions,
        "claim_scope": claim_scope,
        "contract_evidence": [],
        "evidence": evidence,
        "unresolved_gates": unresolved_gates,
    }


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 191:
        if graph["nodes"][-1]["id"] != PERSISTENCE_NODE:
            raise SystemExit("Revision 191 has an unexpected terminal node.")
        return
    if (
        graph["graph_revision"] != 188
        or graph["nodes"][-1]["id"] != OFFICE_PARENT
    ):
        raise SystemExit("Unexpected federation architecture predecessor.")

    graph["nodes"].append(
        _node(
            node_id=ARCH_NODE,
            title="Raisa Real Identity and Microsoft Federation Boundary",
            parent_id=OFFICE_PARENT,
            source_head="ed45c098b9e11fcd1000afb58d6d66c5c369a7e4",
            plan=ARCH["plan"],
            authority_scope=(
                "Architecture-only tenant-specific Microsoft Entra boundary, "
                "typed policy and deterministic authored-synthetic acceptance."
            ),
            decisions=[
                {
                    "id": "accept-tenant-specific-prebound-federation-189",
                    "source": ARCH["policy"],
                    "status": "accepted",
                    "summary": (
                        "Accept one organisational tenant, code plus OIDC/S256 "
                        "PKCE, exact claims and immutable tid-plus-oid prebinding."
                    ),
                },
                {
                    "id": "keep-authentication-separate-from-authority-189",
                    "source": ARCH["design"],
                    "status": "accepted",
                    "summary": (
                        "Keep Microsoft authentication separate from EMR4 identity, "
                        "role, clinician, session and product authorization truth."
                    ),
                },
                {
                    "id": "keep-live-federation-and-product-closed-189",
                    "source": ARCH["closeout"],
                    "status": "accepted",
                    "summary": (
                        "Keep live Microsoft wiring, real identity, routes, product "
                        "reads, deployment, production and release outside the pass."
                    ),
                },
            ],
            claim_scope=[
                "One schema-validated tenant-specific Microsoft Entra architecture passes 22 exact authored-synthetic cases.",
                "Only an exact active pre-provisioned immutable subject binding can release a principal candidate after required audit.",
                "Email, domain, display name and Office signed-in state confer no EMR4 identity or authority.",
            ],
            evidence={
                "plans": [ARCH["plan"], ARCH["design"], ARCH["threat"]],
                "findings": [ARCH["policy"], ARCH["evidence"]],
                "closeouts": [ARCH["closeout"]],
                "acceptances": [ARCH["acceptance"]],
                "receipts": [RECEIPT],
                "tests": [ARCH["runner"], ARCH["tests"]],
            },
            unresolved_gates=[
                "No live Microsoft Entra app registration, redirect, discovery, token exchange or cryptographic verification exists.",
                "No real identity binding, session bridge, product read, deployment, production or release is authorised.",
                "Protected integration remains separately gated by the GitHub Pages deployment side effect.",
            ],
        )
    )
    graph["nodes"].append(
        _node(
            node_id=RUNTIME_NODE,
            title="Raisa Microsoft Federation Synthetic Admission Runtime",
            parent_id=ARCH_NODE,
            source_head="e201435a7ff7949c654c3bb5e9b43784659f78ca",
            plan=RUNTIME["plan"],
            authority_scope=(
                "Default-off route-free provider-free in-memory authored-"
                "synthetic admission, exact binding and required audit only."
            ),
            decisions=[
                {
                    "id": "accept-route-free-synthetic-admission-runtime-190",
                    "source": RUNTIME["service"],
                    "status": "accepted",
                    "summary": (
                        "Accept a default-off route-free policy runtime consuming "
                        "only explicitly synthetic verifier evidence."
                    ),
                },
                {
                    "id": "accept-audit-before-bounded-candidate-190",
                    "source": RUNTIME["evidence"],
                    "status": "accepted",
                    "summary": (
                        "Accept exact binding and keyed-reference audit before a "
                        "role-free, session-free principal candidate is returned."
                    ),
                },
                {
                    "id": "keep-verifier-session-and-product-closed-190",
                    "source": RUNTIME["closeout"],
                    "status": "accepted",
                    "summary": (
                        "Keep real token verification, routes, sessions, product "
                        "reads and deployment outside the runtime pass."
                    ),
                },
            ],
            claim_scope=[
                "The default-off in-memory runtime matches all 22 frozen architecture cases with one exact admission.",
                "Required audit failure overrides admission and no tested raw external identity value enters audit.",
                "No router, provider, database, session or product path imports or invokes the runtime.",
            ],
            evidence={
                "plans": [RUNTIME["plan"], RUNTIME["threat"]],
                "findings": [RUNTIME["service"], RUNTIME["evidence"]],
                "closeouts": [RUNTIME["closeout"]],
                "acceptances": [RUNTIME["acceptance"]],
                "receipts": [RECEIPT],
                "tests": [RUNTIME["runner"], RUNTIME["tests"]],
            },
            unresolved_gates=[
                "Synthetic verifier flags prove no real OIDC cryptography or Microsoft interoperability.",
                "Durable uniqueness, real principal reload, session creation and product authorization remain closed at this node.",
                "Deployment, production and release remain separately closed.",
            ],
        )
    )
    graph["nodes"].append(
        _node(
            node_id=PERSISTENCE_NODE,
            title="Raisa Microsoft Federation PostgreSQL Persistence",
            parent_id=RUNTIME_NODE,
            source_head="4f4e6105e4f36fd1a541a5232b254da617572de6",
            plan=PERSISTENCE["plan"],
            authority_scope=(
                "Two authored-synthetic keyed-reference binding/audit tables, "
                "one reversible migration and disposable local PostgreSQL proof."
            ),
            decisions=[
                {
                    "id": "accept-keyed-reference-federation-persistence-191",
                    "source": PERSISTENCE["migration"],
                    "status": "accepted",
                    "summary": (
                        "Accept exactly two detached authored-synthetic tables "
                        "containing HMAC-only external identity references."
                    ),
                },
                {
                    "id": "accept-unique-terminal-audited-binding-191",
                    "source": PERSISTENCE["evidence"],
                    "status": "accepted",
                    "summary": (
                        "Accept database uniqueness, terminal revocation, same-"
                        "transaction audit, append-only guards and exact RLS proof."
                    ),
                },
                {
                    "id": "accept-disposable-cleanup-191",
                    "source": PERSISTENCE["closeout"],
                    "status": "accepted",
                    "summary": (
                        "Accept verified removal of the only task-created database "
                        "with no existing environment migration."
                    ),
                },
                {
                    "id": "keep-live-bootstrap-session-and-product-closed-191",
                    "source": PERSISTENCE["threat"],
                    "status": "accepted",
                    "summary": (
                        "Keep live verifier/bootstrap roles, real identities, routes, "
                        "sessions, product reads and deployment outside this pass."
                    ),
                },
            ],
            claim_scope=[
                "A reversible single-head migration and matching ORM add exactly two keyed-reference authored-synthetic tables.",
                "Concurrent duplicate binding admits exactly one row; revocation is terminal and required-audit failure rolls back state.",
                "Forced practice RLS, append-only audit, raw-value non-leakage and complete disposable database cleanup pass.",
            ],
            evidence={
                "plans": [PERSISTENCE["plan"], PERSISTENCE["threat"]],
                "findings": [
                    PERSISTENCE["model"],
                    PERSISTENCE["migration"],
                    PERSISTENCE["service"],
                    PERSISTENCE["evidence"],
                ],
                "closeouts": [PERSISTENCE["closeout"]],
                "acceptances": [PERSISTENCE["acceptance"]],
                "receipts": [RECEIPT],
                "tests": [PERSISTENCE["runner"], PERSISTENCE["tests"]],
            },
            unresolved_gates=[
                "No maintained live OIDC verifier, least-privilege provider bootstrap or session bridge exists.",
                "Production HMAC key custody, rotation, retention, recovery, rate limiting and SIEM remain unresolved.",
                "No real identity, product data, deployment, production or release authority is established.",
                "Protected integration remains separately gated by the GitHub Pages deployment side effect.",
            ],
        )
    )
    graph["graph_revision"] = 191
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 172
        and compass["source_graph_revision"] == 191
        and compass["current_position"]["node_id"] == PERSISTENCE_NODE
    ):
        return
    if (
        compass["map_revision"] != 169
        or compass["source_graph_revision"] != 188
        or compass["current_position"]["node_id"] != OFFICE_PARENT
    ):
        raise SystemExit("Unexpected federation Compass predecessor.")

    arch_evidence = [
        ARCH["plan"],
        ARCH["design"],
        ARCH["threat"],
        ARCH["evidence"],
        ARCH["closeout"],
    ]
    runtime_evidence = [
        RUNTIME["plan"],
        RUNTIME["threat"],
        RUNTIME["service"],
        RUNTIME["evidence"],
        RUNTIME["closeout"],
    ]
    persistence_evidence = [
        PERSISTENCE["plan"],
        PERSISTENCE["threat"],
        PERSISTENCE["migration"],
        PERSISTENCE["service"],
        PERSISTENCE["evidence"],
        PERSISTENCE["closeout"],
    ]
    compass["journey"].extend(
        [
            {
                "node_id": ARCH_NODE,
                "lineage_parent": OFFICE_PARENT,
                "strategic_role": "Real-identity and Microsoft-federation trust-boundary architecture",
                "outcome": (
                    "One tenant-specific organisational Entra, code/OIDC/S256 "
                    "PKCE and exact prebinding architecture passes 22 provider-free "
                    "cases while Microsoft remains authentication input only."
                ),
                "evidence": arch_evidence,
            },
            {
                "node_id": RUNTIME_NODE,
                "lineage_parent": ARCH_NODE,
                "strategic_role": "Default-off synthetic federation admission runtime",
                "outcome": (
                    "A route-free in-memory runtime matches all 22 frozen cases, "
                    "records keyed-reference audit before a role-free/session-free "
                    "candidate and has zero external or product side effects."
                ),
                "evidence": runtime_evidence,
            },
            {
                "node_id": PERSISTENCE_NODE,
                "lineage_parent": RUNTIME_NODE,
                "strategic_role": "Durable keyed-reference federation binding and audit boundary",
                "outcome": (
                    "A reversible two-table authored-synthetic PostgreSQL boundary "
                    "proves unique binding, terminal revocation, transaction-bound "
                    "append-only audit, exact RLS, raw-value non-leakage and cleanup."
                ),
                "evidence": persistence_evidence,
            },
        ]
    )
    outcome = (
        "The three authorised federation descendants pass: tenant-specific "
        "architecture, default-off route-free synthetic admission, and disposable "
        "PostgreSQL keyed-reference binding/audit persistence. Live Microsoft, real "
        "identity, routes, sessions, product reads, deployment and release remain closed."
    )
    compass["current_position"] = {
        "node_id": PERSISTENCE_NODE,
        "strategic_role": "Durable keyed-reference federation binding and audit boundary",
        "why_now": (
            "The accepted Office-host session stack left real identity and Microsoft "
            "federation as the next security boundary; Yuri authorised the architecture "
            "and its two smallest provider-free implementation descendants."
        ),
        "outcome": outcome,
        "unlocks": [
            "Publish the task branch for review without moving protected refs or triggering GitHub Pages.",
            "Seek fresh authority for an architecture-only maintained OIDC verifier and least-privilege bootstrap/session-bridge design.",
            "Separately ask whether protected integration and its GitHub Pages deployment are authorised.",
            "Keep Dependabot alert 17 as a separate explicit native-disposition decision.",
        ],
        "does_not_solve": [
            "Live Microsoft Entra registration, redirect, discovery, token exchange or key rollover.",
            "Real identity binding administration, recovery or production key custody.",
            "Application-session issuance, current internal role reload or product-data authorization.",
            "Distributed abuse resistance, incident paging/SIEM, deployment, production or release.",
            "The native disposition or removal of Dependabot alert 17.",
        ],
        "evidence": persistence_evidence,
    }

    decisions = {
        item["id"]: item for item in compass["user_owned_decisions"]
    }
    identity = decisions["authorize-real-identity-federation-architecture"]
    identity["required_before"] = (
        "Satisfied on 2026-08-01 for the architecture-only boundary and its two "
        "route-free provider-free authored-synthetic descendants. Live Microsoft, "
        "real identity, sessions, product reads and deployment remain closed."
    )
    identity["evidence"] = arch_evidence + runtime_evidence + persistence_evidence
    for item in (
        {
            "id": "authorize-microsoft-federation-synthetic-admission-runtime",
            "question": (
                "Should EMR4 implement the frozen federation admission policy as a "
                "default-off route-free authored-synthetic runtime?"
            ),
            "required_before": (
                "Satisfied on 2026-08-01 for the provider-free in-memory runtime. "
                "Live verification, routes, sessions and product reads remain closed."
            ),
            "evidence": runtime_evidence,
        },
        {
            "id": "authorize-microsoft-federation-postgresql-persistence",
            "question": (
                "Should EMR4 persist authored-synthetic external bindings and audit "
                "with keyed references in a disposable local PostgreSQL database?"
            ),
            "required_before": (
                "Satisfied on 2026-08-01 for one reversible two-table migration and "
                "disposable local proof. No existing database or live identity was used."
            ),
            "evidence": persistence_evidence,
        },
        {
            "id": "authorize-maintained-oidc-verifier-session-bridge-architecture",
            "question": (
                "Should EMR4 next freeze an architecture-only maintained OIDC verifier, "
                "least-privilege provider bootstrap and application-session bridge?"
            ),
            "required_before": (
                "Any live Microsoft discovery/token verification, real external binding, "
                "provider bootstrap role, session issuance or product identity reload."
            ),
            "evidence": persistence_evidence,
        },
    ):
        if item["id"] not in decisions:
            compass["user_owned_decisions"].append(item)

    compass["map_limits"].insert(
        0,
        (
            "The federation sequence proves architecture and authored-synthetic "
            "route-free runtime/persistence only. It does not establish live Microsoft "
            "interoperability, real identity, session issuance, product data, "
            "deployment, production or release."
        ),
    )
    compass["orientation_statement"] = (
        "EMR4 now has an accepted tenant-specific real-identity/Microsoft-federation "
        "architecture plus default-off synthetic admission and keyed-reference "
        "PostgreSQL binding/audit foundations. Continuity 191 / Compass 172 bind the "
        "three provider-free results. Protected integration remains paused because "
        "it would trigger public GitHub Pages deployment. Live Microsoft, real "
        "identity, application sessions, product data, production and release remain closed."
    )
    compass["map_revision"] = 172
    compass["source_graph_revision"] = 191
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
