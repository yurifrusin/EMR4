from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
NODE_ID = "raisa-shared-application-auth-postgresql-persistence"
PARENT_ID = "raisa-shared-application-auth-runtime-foundation"
UPDATED_AT = "2026-07-31T21:58:00Z"
SOURCE_HEAD = "8fa732592fbee4f57c322b13d9d8ff89fcc7fa33"

PLAN = "docs/raisa-shared-application-auth-postgresql-persistence-plan.md"
THREAT_MODEL = (
    "docs/security/"
    "raisa-shared-application-auth-postgresql-persistence-threat-model-delta.md"
)
MODEL = "app/models/application_auth.py"
MIGRATION = (
    "alembic/versions/"
    "o4p5q6r7s8t9_add_application_auth_persistence.py"
)
PERSISTENCE = "app/services/application_auth_persistence.py"
EVIDENCE = (
    "orchestration/continuity/"
    "raisa-shared-application-auth-postgresql-persistence/"
    "live-local-backend-postgres-evidence.json"
)
CLOSEOUT = "docs/raisa-shared-application-auth-postgresql-persistence-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-postgresql-persistence-sol-acceptance.md"
)
REHYDRATION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-postgresql-persistence-rehydration-receipt.json"
)
POSTCOMPACTION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-postgresql-persistence-postcompaction-receipt.json"
)
PREACCEPTANCE_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-postgresql-persistence-preacceptance-receipt.json"
)
ACCEPTANCE_SCRIPT = (
    "scripts/raisa_shared_application_auth_postgresql_persistence_acceptance.py"
)
TEST = "tests/test_raisa_shared_application_auth_postgresql_persistence.py"
PARENT_RUNTIME = "app/services/application_auth_runtime.py"


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 183:
        existing = next(
            (node for node in graph["nodes"] if node["id"] == NODE_ID),
            None,
        )
        if existing is None:
            raise SystemExit("Revision 183 is missing the persistence node.")
        existing["authority"]["authorized_openings"] = [
            {
                "boundary": "api-change",
                "source": PLAN,
                "scope": (
                    "Five authored-synthetic auth tables, one reversible local "
                    "migration and uniquely named disposable test writes only."
                ),
            }
        ]
        if PARENT_RUNTIME not in existing["evidence"]["findings"]:
            existing["evidence"]["findings"].append(PARENT_RUNTIME)
        existing["claim_scope"][-1] = (
            "Sixty focused, 156 corrected expanded no-conftest and 12 serial "
            "legacy database cases pass with zero external or product side effects."
        )
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 182:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity persistence node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": (
                "Raisa Shared Application Authentication PostgreSQL Persistence"
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
            "relationships": [
                {
                    "node_id": PARENT_ID,
                    "relation": "builds_on",
                }
            ],
            "authority": {
                "authorized_openings": [
                    {
                        "boundary": "api-change",
                        "source": PLAN,
                        "scope": (
                            "Five authored-synthetic auth tables, one reversible "
                            "local migration and uniquely named disposable test "
                            "writes only."
                        ),
                    }
                ],
                "notes": [
                    (
                        "Yuri explicitly authorised the exact PostgreSQL "
                        "persistence/migration candidate defined in " + PLAN + "."
                    ),
                    (
                        "The implementation remained route-free and accepted "
                        "only authored-synthetic identity metadata."
                    ),
                    (
                        "Routes, cookies, runtime database roles, external "
                        "identity, product reads and deployment remained closed."
                    ),
                    (
                        "No worker, subagent, provider or external control "
                        "plane was selected."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-normalized-hash-only-auth-persistence-183",
                    "source": MIGRATION,
                    "status": "accepted",
                    "summary": (
                        "Accept five normalized authored-synthetic tables with "
                        "hash-only opaque references and no product-table link."
                    ),
                },
                {
                    "id": "accept-principal-lock-and-audit-transaction-183",
                    "source": PERSISTENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept one principal-generation row lock and one "
                        "transaction for required metadata audit plus state."
                    ),
                },
                {
                    "id": "accept-database-single-use-and-rls-183",
                    "source": EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept database-level one-use exchange, exact-practice "
                        "RLS and immutable guard behavior after live-local proof."
                    ),
                },
                {
                    "id": "keep-auth-transport-identity-and-product-closed-183",
                    "source": CLOSEOUT,
                    "status": "accepted",
                    "summary": (
                        "Keep routes, cookies, runtime roles, external identity, "
                        "product reads, deployment, production and release outside "
                        "this pass."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "A reversible migration and matching ORM define exactly five "
                    "normalized authored-synthetic application-auth tables."
                ),
                (
                    "Parent/surface state, principal generation and exchange "
                    "consumption survive fresh SQLAlchemy sessions without raw "
                    "opaque value persistence."
                ),
                (
                    "Two independent transactions admit exactly one exchange "
                    "consumer, while required-audit failure rolls back all state."
                ),
                (
                    "Forced practice RLS, append-only audit, monotonic generation "
                    "and terminal exchange-consumption guards pass."
                ),
                (
                    "Sixty focused, 156 corrected expanded no-conftest and "
                    "12 serial legacy database cases pass with zero external or "
                    "product side effects."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [PARENT_RUNTIME, PERSISTENCE, EVIDENCE],
                    "note": (
                        "The persistence layer creates no product read, proposal, "
                        "confirmation or command authority."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [PLAN, EVIDENCE, CLOSEOUT],
                    "note": (
                        "Only task-created authored-synthetic auth rows existed; "
                        "no Diary truth, committed event or product table ran."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, THREAT_MODEL],
                "findings": [
                    MODEL,
                    MIGRATION,
                    PERSISTENCE,
                    EVIDENCE,
                    PARENT_RUNTIME,
                ],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [
                    REHYDRATION_RECEIPT,
                    POSTCOMPACTION_RECEIPT,
                    PREACCEPTANCE_RECEIPT,
                ],
                "tests": [ACCEPTANCE_SCRIPT, TEST],
            },
            "unresolved_gates": [
                (
                    "No least-privilege runtime database role or token-to-practice "
                    "bootstrap boundary has been implemented."
                ),
                (
                    "No FastAPI/GraphQL login or exchange route, Secure HttpOnly "
                    "cookie, CSRF control or same-origin BFF transport exists."
                ),
                (
                    "External identity-provider and Microsoft or Office federation "
                    "remain unselected and unauthorized."
                ),
                (
                    "Product-derived, patient, health, clinical and historical "
                    "reads remain closed."
                ),
                (
                    "Appointment or arrival commands, microphone capture, document "
                    "mutation, organisational deployment, production and release "
                    "remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 183
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 164
        and compass["source_graph_revision"] == 183
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        compass["orientation_statement"] = compass[
            "orientation_statement"
        ].replace("Fifty-nine focused", "Sixty focused")
        _write(COMPASS, compass)
        return
    if (
        compass["map_revision"] != 163
        or compass["source_graph_revision"] != 182
    ):
        raise SystemExit("Unexpected Compass predecessor revision.")

    evidence = [PLAN, THREAT_MODEL, MODEL, MIGRATION, PERSISTENCE, EVIDENCE, CLOSEOUT]
    strategic_role = (
        "Route-free authored-synthetic shared-auth PostgreSQL transaction boundary"
    )
    outcome = (
        "The accepted session foundation now has one reversible PostgreSQL "
        "schema and route-free coordinator. Principal-row locking, hash-only "
        "state, durable one-use Word-to-Diary exchange, same-transaction required "
        "audit, forced practice RLS and database guards pass in a disposable "
        "live-local database. Routes, cookies, runtime roles, external identity "
        "and product reads remain closed."
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
            "The accepted in-memory runtime could not prove restart durability, "
            "cross-process single-use or audit crash consistency. Yuri authorised "
            "the exact synthetic-only migration and transaction descendant."
        ),
        "outcome": outcome,
        "unlocks": [
            (
                "Review a separately authorised least-privilege runtime database "
                "role and token-to-practice bootstrap architecture."
            ),
            (
                "Design provider-free synthetic login and exchange routes with "
                "non-enumerating errors, CSRF and opaque Secure HttpOnly cookie or "
                "same-origin BFF transport."
            ),
            (
                "Keep the same backend-owned policy engine and PostgreSQL unit of "
                "work when a later transport is authorised."
            ),
        ],
        "does_not_solve": [
            "Live EMR4 identity establishment, routes, cookies or browser transport.",
            (
                "A least-privilege runtime database role, token-to-practice "
                "bootstrap or operational retention/backup policy."
            ),
            "External identity-provider or Microsoft/Office federation.",
            (
                "Safety or authority for product-derived, patient, health, "
                "clinical or historical data."
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
        if item["id"] != "shared-application-auth-postgresql-persistence"
    ]
    transport_question = (
        "Should EMR4 define the least-privilege runtime database role and secure "
        "provider-free synthetic session transport, including token-to-practice "
        "bootstrap, non-enumerating routes, CSRF and opaque Secure HttpOnly cookie "
        "or same-origin BFF handling, while product reads remain closed?"
    )
    compass["decision_horizon"].insert(
        0,
        {
            "id": "shared-application-auth-runtime-role-secure-transport",
            "title": "Shared auth runtime role and secure synthetic transport",
            "status": "candidate",
            "strategic_question": transport_question,
            "why_it_matters": (
                "Durable state is now proven locally, but a live transport cannot "
                "safely use a table owner or expose detailed internal denials."
            ),
            "prerequisites": [
                "Fresh Yuri authority for the exact runtime-role and route/cookie architecture scope.",
                "Authored-synthetic identities only; no product or patient data.",
                "One backend-owned authorization policy and the accepted PostgreSQL unit of work.",
                "No external identity provider, Microsoft/Office authority, product read, deployment or production change.",
            ],
            "boundary_changes": ["api-change"],
            "evidence": [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT],
        },
    )

    persistence_question = (
        "Should EMR4 implement a PostgreSQL-backed transaction and migration "
        "for parent/surface sessions, principal generation, single-use exchange "
        "and metadata-only audit using disposable authored-synthetic fixtures "
        "while routes, cookies and product reads remain closed?"
    )
    for decision in compass["user_owned_decisions"]:
        if decision["id"] == "authorize-shared-application-auth-postgresql-persistence":
            decision["required_before"] = (
                "Satisfied on 2026-08-01 for the reversible authored-synthetic "
                "PostgreSQL schema, route-free coordinator and disposable local "
                "acceptance only. Runtime roles, routes, cookies, external "
                "identity, product reads, deployment, production and release "
                "remain new authority decisions."
            )
            decision["evidence"] = [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT]
            break
    else:
        compass["user_owned_decisions"].append(
            {
                "id": "authorize-shared-application-auth-postgresql-persistence",
                "question": persistence_question,
                "required_before": (
                    "Satisfied on 2026-08-01 for the exact bounded persistence "
                    "tranche; all broader auth and product gates remain closed."
                ),
                "evidence": [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT],
            }
        )

    transport_decision = {
        "id": "authorize-shared-application-auth-runtime-role-secure-transport",
        "question": transport_question,
        "required_before": (
            "Any runtime database privilege grant, token lookup bootstrap, login "
            "or exchange route, cookie/BFF transport, CSRF behavior or browser "
            "session wiring."
        ),
        "evidence": [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT],
    }
    if not any(
        item["id"] == transport_decision["id"]
        for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].append(transport_decision)

    compass["map_limits"].insert(
        0,
        (
            "The accepted PostgreSQL shared-auth descendant proves reversible "
            "local schema creation, hash-only authored-synthetic persistence, "
            "principal-row serialization, database single-use exchange, same-"
            "transaction metadata audit, forced practice RLS and complete cleanup. "
            "It does not prove live identity, routes, cookies, a runtime database "
            "role, product-data safety, deployment, production or release."
        ),
    )
    compass["orientation_statement"] = (
        "Raisa now has an accepted route-free authored-synthetic PostgreSQL "
        "transaction boundary beneath its shared application-authentication "
        "runtime. Five normalized hash-only tables, a reversible migration, "
        "principal-row locking, durable one-use Word-to-Diary exchange, same-"
        "transaction required audit, forced practice RLS and immutable database "
        "guards pass in a completely removed disposable database. Sixty "
        "focused, 156 corrected expanded and 12 serial legacy database cases "
        "pass with zero external or product side effects. Continuity 183 / "
        "Compass 164 bind the result. Routes, cookies, runtime roles, external "
        "identity, product data, deployment, production and release remain closed."
    )
    compass["map_revision"] = 164
    compass["source_graph_revision"] = 183
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
