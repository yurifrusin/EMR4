from __future__ import annotations

import json
from pathlib import Path

from scripts import ariadne_compass


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
NODE_ID = "raisa-shared-application-auth-runtime-foundation"
PARENT_ID = "raisa-shared-application-auth-clinician-role-boundary"
UPDATED_AT = "2026-07-31T13:45:00Z"
SOURCE_HEAD = "8fa732592fbee4f57c322b13d9d8ff89fcc7fa33"

PLAN = "docs/raisa-shared-application-auth-runtime-foundation-plan.md"
THREAT_MODEL = (
    "docs/security/"
    "raisa-shared-application-auth-runtime-foundation-threat-model-delta.md"
)
RUNTIME = "app/services/application_auth_runtime.py"
EVIDENCE = (
    "orchestration/continuity/"
    "raisa-shared-application-auth-runtime-foundation/"
    "provider-free-acceptance-evidence.json"
)
CLOSEOUT = "docs/raisa-shared-application-auth-runtime-foundation-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-runtime-foundation-sol-acceptance.md"
)
REHYDRATION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-runtime-foundation-rehydration-receipt.json"
)
PREACCEPTANCE_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-runtime-foundation-preacceptance-receipt.json"
)
ACCEPTANCE_SCRIPT = (
    "scripts/raisa_shared_application_auth_runtime_foundation_acceptance.py"
)
TEST = "tests/test_raisa_shared_application_auth_runtime_foundation.py"
PARENT_DESIGN = (
    "docs/raisa-shared-application-auth-clinician-role-boundary-design.md"
)
PARENT_POLICY = (
    "orchestration/continuity/"
    "raisa-shared-application-auth-clinician-role-boundary/"
    "auth-boundary-policy.json"
)


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 182:
        existing = next(
            (node for node in graph["nodes"] if node["id"] == NODE_ID),
            None,
        )
        if existing is None:
            raise SystemExit("Revision 182 is missing the runtime node.")
        for path in (PLAN, THREAT_MODEL, PARENT_DESIGN):
            if path not in existing["evidence"]["plans"]:
                existing["evidence"]["plans"].append(path)
        for path in (RUNTIME, EVIDENCE, PARENT_POLICY):
            if path not in existing["evidence"]["findings"]:
                existing["evidence"]["findings"].append(path)
        _write(GRAPH, graph)
        return
    if graph["graph_revision"] != 181:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "Raisa Shared Application Authentication Runtime Foundation",
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
                "authorized_openings": [],
                "notes": [
                    (
                        "Yuri explicitly authorized the repository-local "
                        "runtime-foundation candidate defined in " + PLAN + "."
                    ),
                    (
                        "The implementation was limited to an unmounted "
                        "service and authored-synthetic in-memory state."
                    ),
                    (
                        "FastAPI/GraphQL routes, cookies, databases, external "
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
                    "id": "accept-hash-only-bounded-sessions-182",
                    "source": RUNTIME,
                    "status": "accepted",
                    "summary": (
                        "Accept explicit authored-synthetic opaque parent and "
                        "surface sessions with hash-only state, bounded expiry "
                        "and centralized principal-generation revocation."
                    ),
                },
                {
                    "id": "accept-atomic-single-use-exchange-182",
                    "source": EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept the route-free Word-to-Diary single-use "
                        "exchange after exact binding, concurrency and replay "
                        "acceptance passed."
                    ),
                },
                {
                    "id": "accept-audit-before-mutation-182",
                    "source": THREAT_MODEL,
                    "status": "accepted",
                    "summary": (
                        "Accept required metadata audit admission before each "
                        "successful in-memory mutation, with tested no-change "
                        "failure closure."
                    ),
                },
                {
                    "id": "keep-auth-persistence-routes-and-product-closed-182",
                    "source": CLOSEOUT,
                    "status": "accepted",
                    "summary": (
                        "Keep database persistence, routes, cookies, external "
                        "identity, product reads, deployment, production and "
                        "release outside this pass."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "All three surfaces can validate a bounded opaque "
                    "authored-synthetic parent/surface session whose server "
                    "state contains only hash references."
                ),
                (
                    "Explicit and generation revocation, idle/absolute expiry "
                    "and exact surface/origin/audience checks fail closed."
                ),
                (
                    "Word desktop and Word Online each create one native-Diary "
                    "binding through the exact single-use exchange contract."
                ),
                (
                    "A two-thread redemption admits exactly one consumer and "
                    "audit failure leaves create, redeem and revoke state "
                    "unchanged."
                ),
                (
                    "Thirty-two focused and 145 corrected expanded no-conftest "
                    "cases pass with every external and product side-effect "
                    "count zero."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [PARENT_POLICY, RUNTIME, EVIDENCE],
                    "note": (
                        "The runtime creates no product read, proposal, "
                        "confirmation or command authority."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [PARENT_DESIGN, EVIDENCE, CLOSEOUT],
                    "note": (
                        "No database, committed event or Diary truth path ran "
                        "or changed."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, THREAT_MODEL, PARENT_DESIGN],
                "findings": [RUNTIME, EVIDENCE, PARENT_POLICY],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [REHYDRATION_RECEIPT, PREACCEPTANCE_RECEIPT],
                "tests": [ACCEPTANCE_SCRIPT, TEST],
            },
            "unresolved_gates": [
                (
                    "No FastAPI/GraphQL login or exchange route, secure cookie "
                    "or same-origin BFF transport has been implemented."
                ),
                (
                    "No database-backed or distributed session, generation, "
                    "single-use exchange or audit transaction exists."
                ),
                (
                    "External identity-provider and Microsoft or Office "
                    "federation remain unselected and unauthorized."
                ),
                (
                    "Product-derived, patient, health, clinical and historical "
                    "reads remain closed."
                ),
                (
                    "Database changes, appointment commands, microphone "
                    "capture, document mutation, organisational Office "
                    "deployment, production and release remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 182
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 163
        and compass["source_graph_revision"] == 182
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        return
    if (
        compass["map_revision"] != 162
        or compass["source_graph_revision"] != 181
    ):
        raise SystemExit("Unexpected Compass predecessor revision.")

    evidence = [PLAN, THREAT_MODEL, RUNTIME, EVIDENCE, CLOSEOUT]
    strategic_role = (
        "Route-free authored-synthetic shared authentication runtime foundation"
    )
    outcome = (
        "The frozen backend-owned session architecture now has one explicit "
        "unmounted in-memory implementation: hash-only parent and surface "
        "sessions, bounded expiry, generation revocation, atomic single-use "
        "Word-to-Diary exchange and audit-before-mutation all pass against "
        "authored-synthetic metadata. Routes, cookies, persistence, external "
        "identity and product reads remain closed."
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
            "The accepted architecture left all runtime primitives unproved. "
            "Yuri authorised its exact repository-local runtime candidate "
            "before any persistence, route, cookie or product-derived read."
        ),
        "outcome": outcome,
        "unlocks": [
            (
                "Review a separately authorised PostgreSQL transaction and "
                "migration design for durable session, revocation, exchange "
                "and metadata-audit state using disposable synthetic fixtures."
            ),
            (
                "Reuse the service's hash-only records and typed denial "
                "semantics as the persistence adapter contract."
            ),
            (
                "Evaluate route and Secure HttpOnly cookie or same-origin BFF "
                "transport only after durable atomicity passes."
            ),
        ],
        "does_not_solve": [
            "Live EMR4 login, routes, cookies or browser transport.",
            "Durable, database-backed, crash-consistent or distributed revocation.",
            "External identity-provider or Microsoft/Office federation.",
            (
                "Safety or authority for product-derived, patient, health, "
                "clinical or historical data."
            ),
            (
                "Database changes, appointment commands, microphone capture, "
                "document mutation, deployment, production or release."
            ),
        ],
        "evidence": evidence,
    }

    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"] != "shared-application-auth-runtime-foundation"
    ]
    persistence_question = (
        "Should EMR4 implement a PostgreSQL-backed transaction and migration "
        "for parent/surface sessions, principal generation, single-use exchange "
        "and metadata-only audit using disposable authored-synthetic fixtures "
        "while routes, cookies and product reads remain closed?"
    )
    compass["decision_horizon"].insert(
        0,
        {
            "id": "shared-application-auth-postgresql-persistence",
            "title": "Shared application-authentication PostgreSQL persistence",
            "status": "candidate",
            "strategic_question": persistence_question,
            "why_it_matters": (
                "The in-memory proof does not survive process loss or establish "
                "database-level single-use and audit atomicity required before "
                "a live transport can be considered."
            ),
            "prerequisites": [
                "Fresh Yuri authority for the exact schema, migration and disposable test-write scope.",
                "Authored-synthetic identities only; no product or patient data.",
                "One database transaction or transactional-outbox boundary for every admitted mutation.",
                "No login route, cookie, external identity, product read, deployment or production change.",
            ],
            "boundary_changes": ["api-change"],
            "evidence": [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT],
        },
    )

    for decision in compass["user_owned_decisions"]:
        if decision["id"] == "authorize-shared-application-auth-runtime-foundation":
            decision["required_before"] = (
                "Satisfied on 2026-07-31 for the unmounted authored-synthetic "
                "in-memory foundation only. Database persistence, routes, "
                "cookies, external identity, product-derived reads, deployment, "
                "production and release remain new authority decisions."
            )
            decision["evidence"] = [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT]
            break

    persistence_decision = {
        "id": "authorize-shared-application-auth-postgresql-persistence",
        "question": persistence_question,
        "required_before": (
            "Any authentication schema/migration, database-backed session or "
            "revocation state, durable single-use exchange, required-audit "
            "write or disposable database acceptance run."
        ),
        "evidence": [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT],
    }
    if not any(
        item["id"] == persistence_decision["id"]
        for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].append(persistence_decision)

    compass["map_limits"].insert(
        0,
        (
            "The accepted shared-auth runtime foundation proves one unmounted "
            "authored-synthetic in-memory implementation with hash-only state, "
            "bounded expiry, generation revocation, one-use exchange and "
            "audit-before-mutation. It does not prove live routes or cookies, "
            "durable/database/distributed atomicity, external identity, product "
            "data safety, deployment, production or release."
        ),
    )
    compass["orientation_statement"] = (
        "Raisa now has an accepted route-free authored-synthetic implementation "
        "of the frozen shared application-authentication primitives across "
        "desktop Word, Word Online and the native Diary. Hash-only parent and "
        "surface sessions, bounded expiry, centralized generation revocation, "
        "single-use exact-bound Word-to-Diary exchange and required audit-before-"
        "mutation pass, including concurrent redemption and audit-outage closure. "
        "Thirty-two focused and 145 corrected expanded tests pass with zero "
        "external or product side effects. Continuity 182 / Compass 163 bind the "
        "result. Routes, cookies, persistence, external identity, product data, "
        "deployment, production and release remain closed."
    )
    compass["map_revision"] = 163
    compass["source_graph_revision"] = 182
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
