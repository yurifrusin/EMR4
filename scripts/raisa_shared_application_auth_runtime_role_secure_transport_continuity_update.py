from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
NODE_ID = "raisa-shared-application-auth-runtime-role-secure-transport"
PARENT_ID = "raisa-shared-application-auth-postgresql-persistence"
UPDATED_AT = "2026-08-01T00:25:13Z"
SOURCE_HEAD = "2ae8f2173276147e59be361e0182f6cb4b7453fa"

PLAN = "docs/raisa-shared-application-auth-runtime-role-secure-transport-plan.md"
THREAT_MODEL = (
    "docs/security/"
    "raisa-shared-application-auth-runtime-role-secure-transport-threat-model-delta.md"
)
HANDOFF = (
    "docs/raisa-shared-application-auth-runtime-role-secure-transport-"
    "cross-pc-handoff.md"
)
OPENAPI = "docs/api-spine/openapi/application-auth-synthetic-transport.yaml"
MIGRATION = (
    "alembic/versions/"
    "p5q6r7s8t9u0_add_application_auth_runtime_bootstrap.py"
)
ROLE_CONTRACT = "app/services/application_auth_database_role.py"
ROLE_RUNTIME = "app/services/application_auth_role_runtime.py"
SCHEMAS = "app/schemas/application_auth_transport.py"
TRANSPORT = "app/services/application_auth_transport.py"
ROUTER = "app/routers/application_auth.py"
EVIDENCE = (
    "orchestration/continuity/"
    "raisa-shared-application-auth-runtime-role-secure-transport/"
    "live-local-backend-postgres-transport-evidence.json"
)
CLOSEOUT = (
    "docs/raisa-shared-application-auth-runtime-role-secure-transport-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-runtime-role-secure-transport-sol-acceptance.md"
)
RESUME_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-runtime-role-secure-transport-"
    "cross-pc-resume-receipt.json"
)
PREACCEPTANCE_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-runtime-role-secure-transport-"
    "preacceptance-receipt.json"
)
ACCEPTANCE_SCRIPT = (
    "scripts/raisa_shared_application_auth_runtime_role_secure_transport_acceptance.py"
)
TESTS = [
    "tests/test_raisa_shared_application_auth_transport.py",
    "tests/test_raisa_shared_application_auth_runtime_role_secure_transport.py",
]


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 184:
        if not any(node["id"] == NODE_ID for node in graph["nodes"]):
            raise SystemExit("Revision 184 is missing the transport node.")
        return
    if graph["graph_revision"] != 183:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity transport node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": (
                "Raisa Shared Application Authentication Runtime Role and "
                "Secure Synthetic Transport"
            ),
            "kind": "foundation",
            "status": "accepted",
            "created_at": UPDATED_AT,
            "updated_at": UPDATED_AT,
            "coordinates": {
                "git_ref": "codex/ariadne-terra-gemini-comparative-rehearsal",
                "source_head": SOURCE_HEAD,
                "thread_id": None,
                "worktree_role": "integration",
            },
            "relationships": [{"node_id": PARENT_ID, "relation": "builds_on"}],
            "authority": {
                "authorized_openings": [
                    {
                        "boundary": "api-change",
                        "source": PLAN,
                        "scope": (
                            "One database-scoped hash resolver, parameterised "
                            "NOLOGIN capability-role contract and default-off "
                            "authored-synthetic session transport exercised only "
                            "against a uniquely named disposable local database."
                        ),
                    }
                ],
                "notes": [
                    (
                        "Yuri explicitly authorised the exact Compass 164 runtime-"
                        "role and secure synthetic transport candidate."
                    ),
                    (
                        "The mounted FastAPI surface remains unavailable unless an "
                        "authored-synthetic transport dependency is explicitly "
                        "injected; no environment switch enables it."
                    ),
                    (
                        "External identity, Microsoft/Office federation, product "
                        "reads, clinical authority, deployment, production and "
                        "release remained closed."
                    ),
                    "No worker, subagent, provider or external control plane ran.",
                ],
            },
            "decisions": [
                {
                    "id": "accept-least-privilege-auth-capability-role-184",
                    "source": ROLE_CONTRACT,
                    "status": "accepted",
                    "summary": (
                        "Accept the exact NOLOGIN, non-owner capability-role grant "
                        "matrix over only five auth tables, one audit sequence and "
                        "one bounded token-reference resolver."
                    ),
                },
                {
                    "id": "accept-default-off-cookie-csrf-transport-184",
                    "source": ROUTER,
                    "status": "accepted",
                    "summary": (
                        "Accept seven default-off POST routes with exact-origin and "
                        "CSRF gates, generic external failures and partitioned "
                        "Secure HttpOnly __Host- cookies."
                    ),
                },
                {
                    "id": "accept-disposable-role-transport-proof-184",
                    "source": EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept the live-local disposable PostgreSQL role, resolver, "
                        "session lifecycle, audit rollback and residue proof."
                    ),
                },
                {
                    "id": "keep-real-identity-product-and-release-closed-184",
                    "source": CLOSEOUT,
                    "status": "accepted",
                    "summary": (
                        "Keep real identity mapping, federation, product data, "
                        "commands, deployment, production and release outside this "
                        "pass."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "A narrow SECURITY DEFINER hash resolver and parameterised "
                    "capability role bootstrap authored-synthetic principals without "
                    "broad pre-context table reads or product privileges."
                ),
                (
                    "Seven mounted routes remain closed by default and expose only "
                    "bounded generic 401, 403, 404 and 503 classes."
                ),
                (
                    "Exact-origin, double-submit CSRF and partitioned Secure "
                    "HttpOnly __Host- cookies protect login, validate, rotation, "
                    "Word-to-Diary exchange and logout in the local protocol proof."
                ),
                (
                    "The disposable acceptance proves old-token revocation, one-use "
                    "bootstrap and exchange, required-audit rollback, practice RLS, "
                    "zero product privileges, zero raw-secret matches and exact "
                    "database/role cleanup."
                ),
                (
                    "Focused, expanded no-conftest and serial legacy database gates "
                    "pass with every recorded external and product side effect zero."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [PLAN, ROUTER, EVIDENCE],
                    "note": (
                        "The transport exposes no product read, proposal, confirmation "
                        "or command path."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [THREAT_MODEL, EVIDENCE, CLOSEOUT],
                    "note": (
                        "Only task-created authored-synthetic auth state ran; no Diary "
                        "truth, committed event or product table was accessed."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, THREAT_MODEL, HANDOFF, OPENAPI],
                "findings": [
                    MIGRATION,
                    ROLE_CONTRACT,
                    ROLE_RUNTIME,
                    SCHEMAS,
                    TRANSPORT,
                    ROUTER,
                    EVIDENCE,
                ],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [RESUME_RECEIPT, PREACCEPTANCE_RECEIPT],
                "tests": [ACCEPTANCE_SCRIPT, *TESTS],
            },
            "unresolved_gates": [
                (
                    "No real EMR4 identity-to-practice mapping, external identity "
                    "provider or Microsoft/Office federation exists."
                ),
                (
                    "Deployment login credential isolation, pooler behavior, proxy "
                    "trust, rate limiting and retained unauthenticated audit remain "
                    "unproved operational architecture."
                ),
                (
                    "Real Word desktop/Online third-party-cookie compatibility and "
                    "browser supply-chain controls remain untested."
                ),
                (
                    "Product-derived, patient, health, clinical and historical reads "
                    "remain closed."
                ),
                (
                    "Appointment or arrival commands, microphone capture, document "
                    "mutation, organisational deployment, production and release "
                    "remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 184
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 165
        and compass["source_graph_revision"] == 184
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        return
    if (
        compass["map_revision"] != 164
        or compass["source_graph_revision"] != 183
    ):
        raise SystemExit("Unexpected Compass predecessor revision.")

    evidence = [
        PLAN,
        THREAT_MODEL,
        OPENAPI,
        ROLE_CONTRACT,
        ROLE_RUNTIME,
        ROUTER,
        EVIDENCE,
        CLOSEOUT,
    ]
    strategic_role = (
        "Default-off least-privilege authored-synthetic application-auth transport"
    )
    outcome = (
        "The accepted PostgreSQL shared-auth boundary now has one exact NOLOGIN "
        "capability-role contract, a bounded hash resolver and seven default-off "
        "FastAPI routes. Exact-origin and CSRF controls, partitioned Secure HttpOnly "
        "cookies, rotation, logout and one-use Word-to-Diary exchange pass through "
        "the single backend policy engine in a completely removed disposable "
        "database and role. Real identity and every product read remain closed."
    )
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": strategic_role,
            "outcome": outcome,
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": strategic_role,
        "why_now": (
            "The durable parent had no safe bootstrap, runtime role or browser "
            "transport. Yuri authorised the exact repository-local provider-free "
            "authored-synthetic descendant and its disposable PostgreSQL proof."
        ),
        "outcome": outcome,
        "unlocks": [
            (
                "Review a separately authorised repository-local operational "
                "hardening design for deployment-role isolation, proxy trust, rate "
                "limits, retained denial audit and pool/time-out behavior."
            ),
            (
                "Plan a separately authorised supervised authored-synthetic Office "
                "cookie-compatibility check without real identity or product data."
            ),
            (
                "Preserve one backend-owned authorization and PostgreSQL transaction "
                "path for any later identity integration."
            ),
        ],
        "does_not_solve": [
            "Real EMR4 identity verification or user/practice mapping.",
            "External identity-provider or Microsoft/Office federation.",
            (
                "Production database-login isolation, proxy/rate-limit posture, "
                "retention, backup or multi-region behavior."
            ),
            (
                "Safety or authority for product-derived, patient, health, clinical "
                "or historical data."
            ),
            (
                "Appointment commands, microphone capture, document mutation, "
                "deployment, production or release."
            ),
        ],
        "evidence": evidence,
    }

    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"] != "shared-application-auth-runtime-role-secure-transport"
    ]
    hardening_question = (
        "Should EMR4 define a repository-local provider-free operational hardening "
        "architecture for the synthetic auth transport covering deployment-role "
        "isolation, proxy trust, rate limiting, retained denial audit and bounded "
        "pool behavior while real identity and product reads remain closed?"
    )
    compass["decision_horizon"].insert(
        0,
        {
            "id": "shared-application-auth-operational-hardening",
            "title": "Shared auth operational hardening architecture",
            "status": "candidate",
            "strategic_question": hardening_question,
            "why_it_matters": (
                "The local protocol and capability-role proof now pass, but deployed "
                "credential separation, abuse resistance, proxy semantics and "
                "operational audit behavior remain intentionally unproved."
            ),
            "prerequisites": [
                "Fresh Yuri authority for the exact repository-local design scope.",
                "Authored-synthetic identities only; no product or patient data.",
                "No external identity provider, Office federation, deployment, production or release.",
                "Preserve the accepted default-off router, policy engine and PostgreSQL transaction boundary.",
            ],
            "boundary_changes": ["api-change"],
            "evidence": [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT],
        },
    )

    for decision in compass["user_owned_decisions"]:
        if (
            decision["id"]
            == "authorize-shared-application-auth-runtime-role-secure-transport"
        ):
            decision["required_before"] = (
                "Satisfied on 2026-08-01 for the exact default-off, provider-free, "
                "authored-synthetic runtime-role and transport tranche only. Real "
                "identity, product reads, deployment, production and release remain "
                "new authority decisions."
            )
            decision["evidence"] = [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT]
            break
    else:
        raise SystemExit("Missing current transport authority decision.")

    if not any(
        item["id"] == "authorize-shared-application-auth-operational-hardening"
        for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].append(
            {
                "id": "authorize-shared-application-auth-operational-hardening",
                "question": hardening_question,
                "required_before": (
                    "Any new deployment-role, proxy-trust, rate-limit, retained "
                    "unauthenticated-audit or pool-management design or implementation."
                ),
                "evidence": [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT],
            }
        )

    compass["map_limits"].insert(
        0,
        (
            "The accepted shared-auth runtime-role/transport descendant proves one "
            "local authored-synthetic capability-role and hash-resolver boundary, "
            "seven default-off routes, exact-origin/CSRF enforcement, partitioned "
            "Secure HttpOnly cookie carriage, atomic rotation/logout, database one-"
            "use and exact disposable cleanup. It does not prove real identity, "
            "Office cookie compatibility, abuse resistance, product-data safety, "
            "deployment, production or release."
        ),
    )
    compass["orientation_statement"] = (
        "Raisa now has an accepted default-off, provider-free authored-synthetic "
        "application-auth transport above its shared PostgreSQL policy boundary. "
        "One exact NOLOGIN capability-role contract and narrow hash resolver expose "
        "no product privilege; seven mounted routes remain unavailable without "
        "explicit injection and use generic failures, exact origins, CSRF and "
        "partitioned Secure HttpOnly __Host- cookies. Login, validation, atomic "
        "rotation, one-use Word-to-Diary exchange, logout, required-audit rollback "
        "and exact disposable database/role cleanup pass with zero external or "
        "product side effects. Continuity 184 / Compass 165 bind the result. Real "
        "identity, federation, product data, deployment, production and release "
        "remain closed."
    )
    compass["map_revision"] = 165
    compass["source_graph_revision"] = 184
    compass["updated_at"] = UPDATED_AT
    _write(COMPASS, compass)


def render_report() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    report = ariadne_compass.build_compass_report(
        compass,
        graph,
        repo_root=ROOT,
    )
    if report["status"] != "passed":
        raise SystemExit(
            "Compass validation failed: " + ", ".join(report["reasons"])
        )
    REPORT.write_text(
        ariadne_compass.render_markdown(report),
        encoding="utf-8",
    )


def main() -> int:
    update_graph()
    update_compass()
    render_report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
