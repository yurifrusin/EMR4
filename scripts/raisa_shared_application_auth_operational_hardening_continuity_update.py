from __future__ import annotations

import json
from pathlib import Path

try:
    from scripts import ariadne_compass
except ModuleNotFoundError:  # Direct execution from the scripts directory.
    import ariadne_compass  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
NODE_ID = "raisa-shared-application-auth-operational-hardening"
PARENT_ID = "raisa-shared-application-auth-runtime-role-secure-transport"
UPDATED_AT = "2026-08-01T04:40:00Z"
SOURCE_HEAD = "2ae8f2173276147e59be361e0182f6cb4b7453fa"

PLAN = "docs/raisa-shared-application-auth-operational-hardening-plan.md"
THREAT_MODEL = (
    "docs/security/"
    "raisa-shared-application-auth-operational-hardening-threat-model-delta.md"
)
TRACKING_REVIEW = "docs/security/security-finding-tracking-review-2026-08-01.md"
BANDIT_REVIEW = "docs/security/bandit-candidate-validation-2026-08-01.md"
BANDIT_LEDGER = "docs/security/bandit-candidate-validation-ledger.jsonl"
ROLE_CONTRACT = "app/services/application_auth_database_role.py"
POOL = "app/services/application_auth_operational_database.py"
HARDENING = "app/services/application_auth_operational_hardening.py"
ROUTER = "app/routers/application_auth.py"
OPENAPI = "docs/api-spine/openapi/application-auth-synthetic-transport.yaml"
EVIDENCE = (
    "orchestration/continuity/"
    "raisa-shared-application-auth-operational-hardening/"
    "live-local-backend-postgres-operational-evidence.json"
)
CLOSEOUT = "docs/raisa-shared-application-auth-operational-hardening-closeout.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-operational-hardening-sol-acceptance.md"
)
REHYDRATION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-operational-hardening-rehydration-receipt.json"
)
POSTCOMPACTION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-operational-hardening-postcompaction-receipt.json"
)
PREACCEPTANCE_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-operational-hardening-preacceptance-receipt.json"
)
ACCEPTANCE_SCRIPT = (
    "scripts/raisa_shared_application_auth_operational_hardening_acceptance.py"
)
TESTS = "tests/test_raisa_shared_application_auth_operational_hardening.py"


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 185:
        if not any(node["id"] == NODE_ID for node in graph["nodes"]):
            raise SystemExit("Revision 185 is missing the operational node.")
        return
    if graph["graph_revision"] != 184:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity operational-hardening node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": (
                "Raisa Shared Application Authentication Operational Hardening"
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
                            "Repository-local provider-free authored-synthetic "
                            "deployment-login isolation, strict proxy trust, "
                            "bounded rate limiting, retained denial audit and "
                            "finite SQLAlchemy pool behavior only."
                        ),
                    }
                ],
                "notes": [
                    (
                        "Yuri explicitly authorised the Compass 165 shared-auth "
                        "operational-hardening candidate."
                    ),
                    (
                        "The operational guard may deny only and remains an "
                        "explicit dependency beside the default-off transport."
                    ),
                    (
                        "Real identity, Office federation, product reads, cloud/IAM "
                        "mutation, deployment, production and release remained closed."
                    ),
                    "No worker, subagent, provider or external control plane ran.",
                ],
            },
            "decisions": [
                {
                    "id": "accept-deployment-login-capability-isolation-185",
                    "source": POOL,
                    "status": "accepted",
                    "summary": (
                        "Accept an exact NOINHERIT login with no direct table grants, "
                        "finite connection limit and exact pool SET ROLE to the "
                        "NOLOGIN capability role."
                    ),
                },
                {
                    "id": "accept-proxy-rate-and-denial-audit-185",
                    "source": HARDENING,
                    "status": "accepted",
                    "summary": (
                        "Accept strict one-hop trusted-proxy resolution, bounded "
                        "per-process rate admission and required HMAC-only retained "
                        "denial audit."
                    ),
                },
                {
                    "id": "accept-disposable-operational-proof-185",
                    "source": EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept live-local role separation, finite pool timeout, "
                        "RLS/append-only denial rows, zero raw matches and exact "
                        "database plus two-role cleanup."
                    ),
                },
                {
                    "id": "record-security-tracking-gap-without-disposition-185",
                    "source": TRACKING_REVIEW,
                    "status": "accepted",
                    "summary": (
                        "Record laptop-independent GitHub detection and the missing "
                        "durable owner/SLA/disposition lifecycle without changing any "
                        "GitHub alert or setting."
                    ),
                },
                {
                    "id": "keep-real-identity-product-and-release-closed-185",
                    "source": CLOSEOUT,
                    "status": "accepted",
                    "summary": (
                        "Keep real identity, federation, product data, distributed "
                        "abuse controls, deployment, production and release outside "
                        "this pass."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "One exact deployment login authenticates without direct auth-"
                    "table grants, then enters the existing NOLOGIN capability role "
                    "on every new bounded-pool connection."
                ),
                (
                    "One-hop trusted-proxy parsing rejects spoofing, duplicate or "
                    "chained fields, incomplete pairs and non-HTTPS forwarding; its "
                    "HMAC result is abuse-control identity only."
                ),
                (
                    "All seven routes have bounded fixed-window admission, first-"
                    "block audit coalescing and generic 429/503 failure behavior."
                ),
                (
                    "Required denial audit retains fixed metadata and an HMAC client "
                    "reference under forced RLS and append-only guards with no raw "
                    "network or authentication material."
                ),
                (
                    "The disposable proof, focused/expanded/serial tests and security "
                    "gates pass with zero raw matches, zero external/product side "
                    "effects and exact database plus role cleanup."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [PLAN, ROUTER, EVIDENCE],
                    "note": (
                        "The guard can deny auth transport only and exposes no "
                        "product read, proposal, confirmation or command path."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [THREAT_MODEL, EVIDENCE, CLOSEOUT],
                    "note": (
                        "Only task-created authored-synthetic auth and denial-audit "
                        "state ran; no Diary truth, event or product table was read."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, THREAT_MODEL, OPENAPI],
                "findings": [
                    ROLE_CONTRACT,
                    POOL,
                    HARDENING,
                    ROUTER,
                    EVIDENCE,
                    TRACKING_REVIEW,
                    BANDIT_REVIEW,
                    BANDIT_LEDGER,
                ],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [
                    REHYDRATION_RECEIPT,
                    POSTCOMPACTION_RECEIPT,
                    PREACCEPTANCE_RECEIPT,
                ],
                "tests": [ACCEPTANCE_SCRIPT, TESTS],
            },
            "unresolved_gates": [
                (
                    "No real identity-to-practice mapping, external identity "
                    "provider or Microsoft/Office federation exists."
                ),
                (
                    "The limiter is per-process; production ingress, distributed "
                    "rate limiting, credential lifecycle and operational retention "
                    "or SIEM remain unproved."
                ),
                (
                    "Security findings lack one durable owner/SLA/native-disposition "
                    "lifecycle; Python and Node security workflows remain unscheduled."
                ),
                (
                    "Real Word desktop/Online third-party-cookie compatibility and "
                    "browser supply-chain controls remain untested."
                ),
                (
                    "Product-derived, patient, health, clinical and historical reads, "
                    "commands, deployment, production and release remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 185
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def _security_candidate() -> dict:
    return {
        "id": "security-finding-governance",
        "title": "Durable security-finding governance",
        "status": "candidate",
        "strategic_question": (
            "Should EMR4 make security finding tracking independent of the laptop "
            "by joining native GitHub alert IDs to a durable owner/SLA register and "
            "scheduling Python and Node security workflows in GitHub?"
        ),
        "why_it_matters": (
            "GitHub already supplies laptop-independent CodeQL and Dependabot "
            "detection, but scanner outputs, repository validation and native alert "
            "disposition are not governed as one owned lifecycle."
        ),
        "prerequisites": [
            "Fresh Yuri authority for repository workflow and governance changes.",
            "Exact review of alerts 8-15 without force overrides.",
            "An explicit SECURITY.md diff approval before policy text changes.",
            "Separate authority before dismissing or mutating any native GitHub alert.",
        ],
        "boundary_changes": [],
        "evidence": [TRACKING_REVIEW, BANDIT_REVIEW, BANDIT_LEDGER, CLOSEOUT],
    }


def _office_candidate() -> dict:
    return {
        "id": "shared-application-auth-office-cookie-compatibility",
        "title": "Supervised Office cookie compatibility",
        "status": "candidate",
        "strategic_question": (
            "Can the accepted default-off authored-synthetic session-cookie "
            "transport operate across supervised Word desktop and Word Online host "
            "constraints without opening real identity or product data?"
        ),
        "why_it_matters": (
            "The local HTTP contract passes, but real Office host partitioning and "
            "third-party-cookie behavior remain intentionally unproved."
        ),
        "prerequisites": [
            "Fresh Yuri authority for an exact supervised authored-synthetic exercise.",
            "Real identity and all product-derived data remain closed.",
            "No deployment, production or release claim.",
        ],
        "boundary_changes": [],
        "evidence": [PLAN, OPENAPI, EVIDENCE, CLOSEOUT],
    }


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 166
        and compass["source_graph_revision"] == 185
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        return
    if compass["map_revision"] != 165 or compass["source_graph_revision"] != 184:
        raise SystemExit("Unexpected Compass predecessor revision.")

    evidence = [PLAN, THREAT_MODEL, POOL, HARDENING, ROUTER, EVIDENCE, CLOSEOUT]
    strategic_role = "Bounded local shared-auth operational posture"
    outcome = (
        "The accepted default-off shared-auth transport now separates an exact "
        "deployment LOGIN from its NOLOGIN capability role, enters that role through "
        "a finite pool, rejects ambiguous proxy identity, rate-limits all seven "
        "routes and retains HMAC-only denial audit. Disposable PostgreSQL proof "
        "passes with zero raw matches, zero external/product side effects and exact "
        "database plus two-role cleanup. Real identity and product data remain closed."
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
            "The local transport proof deliberately left deployment-login, proxy, "
            "abuse-control, denial-audit and pool behavior unresolved. Yuri "
            "authorised exactly that repository-local authored-synthetic hardening."
        ),
        "outcome": outcome,
        "unlocks": [
            (
                "Review a separately authorised durable security-finding governance "
                "tranche with scheduled GitHub checks, ownership and SLA rules."
            ),
            (
                "Plan a separately authorised supervised authored-synthetic Office "
                "cookie-compatibility check without real identity or product data."
            ),
            (
                "Preserve one backend-owned authorization and bounded PostgreSQL "
                "path for any later identity integration."
            ),
        ],
        "does_not_solve": [
            "Real EMR4 identity verification or user/practice mapping.",
            "External identity-provider or Microsoft/Office federation.",
            (
                "Production ingress, credential rotation, distributed rate limiting, "
                "retention, SIEM, backup or multi-region behavior."
            ),
            (
                "A complete owned GitHub security-alert lifecycle or disposition of "
                "the nine open Dependabot and three open validated CodeQL highs."
            ),
            (
                "Product-derived data, commands, Office cookie compatibility, "
                "deployment, production or release."
            ),
        ],
        "evidence": evidence,
    }

    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"] != "shared-application-auth-operational-hardening"
    ]
    existing = {item["id"] for item in compass["decision_horizon"]}
    additions = []
    if "security-finding-governance" not in existing:
        additions.append(_security_candidate())
    if "shared-application-auth-office-cookie-compatibility" not in existing:
        additions.append(_office_candidate())
    compass["decision_horizon"] = additions + compass["decision_horizon"]

    for decision in compass["user_owned_decisions"]:
        if decision["id"] == "authorize-shared-application-auth-operational-hardening":
            decision["required_before"] = (
                "Satisfied on 2026-08-01 for the exact repository-local provider-free "
                "authored-synthetic operational-hardening descendant only. Real "
                "identity, product reads, deployment, production and release remain "
                "fresh authority decisions."
            )
            decision["evidence"] = [PLAN, THREAT_MODEL, EVIDENCE, CLOSEOUT]
            break
    else:
        raise SystemExit("Missing operational-hardening authority decision.")

    decision_ids = {item["id"] for item in compass["user_owned_decisions"]}
    if "authorize-security-finding-governance" not in decision_ids:
        candidate = _security_candidate()
        compass["user_owned_decisions"].append(
            {
                "id": "authorize-security-finding-governance",
                "question": candidate["strategic_question"],
                "required_before": (
                    "Any workflow schedule, durable register, SECURITY.md policy or "
                    "native GitHub alert-disposition change."
                ),
                "evidence": candidate["evidence"],
            }
        )

    compass["map_limits"].insert(
        0,
        (
            "The accepted shared-auth operational-hardening descendant proves one "
            "local authored-synthetic deployment-login/capability split, strict "
            "one-hop proxy contract, bounded per-process limiter, HMAC-only denial "
            "audit and finite SQLAlchemy pool with exact cleanup. It does not prove "
            "real identity, distributed abuse resistance, production ingress, "
            "credential lifecycle, monitoring/retention, product-data safety, "
            "deployment, production or release."
        ),
    )
    compass["orientation_statement"] = (
        "Raisa now has an accepted repository-local provider-free operational "
        "posture for its default-off authored-synthetic shared-auth transport. An "
        "exact deployment LOGIN enters the existing NOLOGIN capability role through "
        "a finite pool; strict one-hop proxy handling, bounded per-process rate "
        "admission and HMAC-only retained denial audit guard all seven routes. "
        "Disposable PostgreSQL evidence proves role separation, finite exhaustion, "
        "RLS/append-only audit, zero raw matches and complete database plus role "
        "cleanup. Continuity 185 / Compass 166 bind the result. Real identity, "
        "federation, product data, deployment, production and release remain closed."
    )
    compass["map_revision"] = 166
    compass["source_graph_revision"] = 185
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
