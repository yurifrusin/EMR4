from __future__ import annotations

import json
from pathlib import Path

try:
    from scripts import ariadne_compass
except ModuleNotFoundError:  # Direct execution from scripts/.
    import ariadne_compass  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
REPORT = ROOT / "docs" / "ariadne-compass-current.md"
NODE_ID = "raisa-shared-application-auth-postgresql-office-host-compatibility"
PARENT_ID = "raisa-shared-application-auth-office-cookie-compatibility"
UPDATED_AT = "2026-08-01T11:05:00Z"
SOURCE_HEAD = "4d8f855aa8194b2c9bae396a4ef9f516829c3c8a"

PLAN = "docs/raisa-shared-application-auth-postgresql-office-host-compatibility-plan.md"
THREAT = (
    "docs/security/"
    "raisa-shared-application-auth-postgresql-office-host-compatibility-"
    "threat-model-delta.md"
)
LIVE = (
    "orchestration/continuity/"
    "shared-application-auth-postgresql-office-host-compatibility/"
    "live-office-backend-postgres-evidence.json"
)
RESIDUE = (
    "orchestration/continuity/"
    "shared-application-auth-postgresql-office-host-compatibility/"
    "final-residue-evidence.json"
)
EVIDENCE = (
    "orchestration/continuity/"
    "shared-application-auth-postgresql-office-host-compatibility/"
    "acceptance-evidence.json"
)
CLOSEOUT = (
    "docs/raisa-shared-application-auth-postgresql-office-host-"
    "compatibility-closeout.md"
)
REHYDRATION = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-postgresql-office-host-compatibility-"
    "rehydration-receipt.json"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-postgresql-office-host-compatibility-"
    "preacceptance-receipt.json"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-postgresql-office-host-compatibility-"
    "sol-acceptance.md"
)
HARNESS = (
    "scripts/raisa_shared_application_auth_postgresql_office_host_"
    "compatibility.py"
)
TESTS = (
    "tests/test_raisa_shared_application_auth_postgresql_office_host_"
    "compatibility.py"
)
DESKTOP_MANIFEST = (
    "orchestration/continuity/"
    "shared-application-auth-postgresql-office-host-compatibility/"
    "word-desktop-manifest.xml"
)
ONLINE_MANIFEST = (
    "orchestration/continuity/"
    "shared-application-auth-postgresql-office-host-compatibility/"
    "word-online-manifest.xml"
)


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 188:
        if graph["nodes"][-1]["id"] != NODE_ID:
            raise SystemExit("Revision 188 has an unexpected terminal node.")
        return
    if graph["graph_revision"] != 187 or graph["nodes"][-1]["id"] != PARENT_ID:
        raise SystemExit("Unexpected PostgreSQL Office compatibility predecessor.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": (
                "Raisa Shared Application-Auth PostgreSQL Office-Host "
                "Compatibility"
            ),
            "kind": "integration",
            "status": "accepted",
            "created_at": UPDATED_AT,
            "updated_at": UPDATED_AT,
            "coordinates": {
                "git_ref": (
                    "codex/shared-auth-postgresql-office-host-compatibility"
                ),
                "source_head": SOURCE_HEAD,
                "thread_id": None,
                "worktree_role": "integration",
            },
            "relationships": [
                {"node_id": PARENT_ID, "relation": "builds_on"},
                {
                    "node_id": (
                        "raisa-shared-application-auth-operational-hardening"
                    ),
                    "relation": "validates",
                },
                {
                    "node_id": (
                        "raisa-shared-application-auth-runtime-role-secure-"
                        "transport"
                    ),
                    "relation": "validates",
                },
            ],
            "authority": {
                "authorized_openings": [
                    {
                        "boundary": "api-change",
                        "source": PLAN,
                        "scope": (
                            "One provider-free authored-synthetic installed-Word "
                            "and Word Online session lifecycle through the accepted "
                            "disposable local PostgreSQL, separate LOGIN role and "
                            "exact NOLOGIN capability role."
                        ),
                    }
                ],
                "notes": [
                    (
                        "Yuri authorised the exact Compass 168 PostgreSQL-backed "
                        "Office-host descendant and supplied the two supervised "
                        "host observations."
                    ),
                    (
                        "PR 70 integration remained paused because master docs "
                        "changes automatically trigger public GitHub Pages "
                        "deployment, which remains separately closed."
                    ),
                    (
                        "The concurrent user-owned Raisa branding directory was "
                        "preserved, unstaged and excluded."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-postgresql-office-host-lifecycle-188",
                    "source": LIVE,
                    "status": "accepted",
                    "summary": (
                        "Accept two independent real-Office create, validate, "
                        "rotate, revalidate, logout and post-logout denial results "
                        "through the exact PostgreSQL capability-role path."
                    ),
                },
                {
                    "id": "accept-exact-durable-auth-readback-188",
                    "source": EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept two principals, two parents, four revoked surface "
                        "rows, fourteen lifecycle audits, two denial audits, exact "
                        "RLS scope and zero raw-value matches."
                    ),
                },
                {
                    "id": "accept-complete-owned-cleanup-188",
                    "source": RESIDUE,
                    "status": "accepted",
                    "summary": (
                        "Accept verified absence of the database, both roles, "
                        "task processes, listeners and desktop registration."
                    ),
                },
                {
                    "id": "keep-deployment-and-real-identity-closed-188",
                    "source": THREAT,
                    "status": "accepted",
                    "summary": (
                        "Keep GitHub Pages deployment, real identity, Microsoft "
                        "federation, product data, production and release outside "
                        "this pass."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "Installed Word and Word Online each completed one independent "
                    "authored-synthetic secure-cookie lifecycle through the exact "
                    "local PostgreSQL LOGIN-to-capability-role path."
                ),
                (
                    "Fresh readback proved exact practice RLS shapes, hash-only "
                    "references, fourteen lifecycle audits, two retained denials "
                    "and four revoked surface sessions."
                ),
                (
                    "No raw secret or task target entered PostgreSQL or durable "
                    "evidence, and all owned database/role/process/listener residue "
                    "was removed."
                ),
                (
                    "No identity provider, Microsoft federation, product or "
                    "document read, provider, cloud mutation, deployment, "
                    "production or protected-ref action occurred."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": (
                        "combined-patient-practitioner-time-duration-intent"
                    ),
                    "status": "satisfied",
                    "evidence": [PLAN, THREAT, LIVE, TESTS],
                    "note": (
                        "The seven-route harness contains no product context, "
                        "appointment proposal or command path."
                    ),
                },
                {
                    "contract_id": (
                        "committed-reschedule-availability-reconciliation"
                    ),
                    "status": "satisfied",
                    "evidence": [LIVE, RESIDUE, CLOSEOUT, TESTS],
                    "note": (
                        "Only authored-synthetic application-auth rows were "
                        "created; no Diary, event, availability or appointment "
                        "state was read or changed."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, THREAT],
                "findings": [LIVE, RESIDUE, EVIDENCE],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [REHYDRATION, PREACCEPTANCE],
                "tests": [HARNESS, TESTS, DESKTOP_MANIFEST, ONLINE_MANIFEST],
            },
            "unresolved_gates": [
                (
                    "The proof covers one Windows Office installation, one signed-"
                    "in Word Online environment and one exact development origin, "
                    "not every browser, WebView, tenant or Office policy."
                ),
                (
                    "Real identity mapping, Microsoft federation and product-data "
                    "authorization remain separately closed."
                ),
                (
                    "The limiter remains per process and proves no distributed "
                    "or production abuse resistance."
                ),
                (
                    "Protected integration would trigger public GitHub Pages "
                    "deployment and requires Yuri's explicit deployment decision."
                ),
                (
                    "Dependabot alert 17 remains native-open/needs_review pending "
                    "its separate explicit disposition decision."
                ),
            ],
        }
    )
    graph["graph_revision"] = 188
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 169
        and compass["source_graph_revision"] == 188
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        return
    if (
        compass["map_revision"] != 168
        or compass["source_graph_revision"] != 187
        or compass["current_position"]["node_id"] != PARENT_ID
    ):
        raise SystemExit("Unexpected PostgreSQL Office Compass predecessor.")

    evidence = [PLAN, THREAT, LIVE, RESIDUE, EVIDENCE, CLOSEOUT]
    outcome = (
        "Installed Word and Word Online each passed one independent authored-"
        "synthetic secure-cookie lifecycle through the accepted disposable local "
        "PostgreSQL, separate finite LOGIN role, exact NOLOGIN capability role, "
        "forced-RLS and retained-audit path. Exact database readback and complete "
        "owned cleanup pass with no raw-value match, product/identity/provider "
        "path, deployment or protected-ref move."
    )
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": (
                "Real Office-host PostgreSQL capability-role compatibility proof"
            ),
            "outcome": outcome,
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Real Office-host PostgreSQL capability-role compatibility proof"
        ),
        "why_now": (
            "The process-local Office cookie proof passed, leaving the already "
            "accepted durable role-scoped persistence path as the next smallest "
            "application-auth uncertainty."
        ),
        "outcome": outcome,
        "unlocks": [
            (
                "Publish and review the task branch without moving protected refs "
                "or triggering deployment."
            ),
            (
                "Ask Yuri whether the public GitHub Pages rebuild caused by "
                "protected integration is authorised."
            ),
            (
                "Separately seek fresh authority for an architecture-only real-"
                "identity and Microsoft-federation boundary design with no live "
                "wiring or product reads."
            ),
            (
                "Make the separate explicit native disposition decision for "
                "Dependabot alert 17."
            ),
        ],
        "does_not_solve": [
            "Every Office/WebView/browser/tenant cookie policy.",
            "Real identity, Microsoft federation or product-data authorization.",
            "Distributed or production abuse resistance.",
            "Organisational deployment, production or release.",
            "The native disposition or removal of Dependabot alert 17.",
        ],
        "evidence": evidence,
    }
    decision_id = (
        "authorize-shared-application-auth-postgresql-office-host-compatibility"
    )
    if not any(
        item["id"] == decision_id for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].append(
            {
                "id": decision_id,
                "question": (
                    "Should EMR4 exercise the accepted session transport through "
                    "local PostgreSQL and the exact capability role in both real "
                    "Office hosts?"
                ),
                "required_before": (
                    "Satisfied on 2026-08-01 for one provider-free authored-"
                    "synthetic installed-Word and Word Online exercise. Real "
                    "identity, product data and deployment remain closed."
                ),
                "evidence": evidence,
            }
        )
    pages_decision = "authorize-protected-integration-pages-deployment"
    if not any(
        item["id"] == pages_decision for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].append(
            {
                "id": pages_decision,
                "question": (
                    "May the accepted Office authentication branches be protected-"
                    "integrated when that master docs push will rebuild and publish "
                    "GitHub Pages?"
                ),
                "required_before": (
                    "Marking the affected PR ready or merging it to master. No "
                    "deployment or protected-ref movement is currently authorised."
                ),
                "evidence": [CLOSEOUT, ".github/workflows/pages.yml"],
            }
        )
    identity_decision = "authorize-real-identity-federation-architecture"
    if not any(
        item["id"] == identity_decision
        for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].append(
            {
                "id": identity_decision,
                "question": (
                    "Should EMR4 freeze an architecture-only real-identity and "
                    "Microsoft-federation boundary next?"
                ),
                "required_before": (
                    "Any identity adapter, Microsoft token exchange, live user or "
                    "practice mapping, product read or federation wiring."
                ),
                "evidence": [PLAN, THREAT, CLOSEOUT],
            }
        )
    compass["map_limits"].insert(
        0,
        (
            "The PostgreSQL Office-host descendant proves one independent "
            "authored-synthetic lifecycle in each tested host through one exact "
            "local role-scoped path. It does not establish real identity, product "
            "data, distributed abuse resistance, deployment or production."
        ),
    )
    compass["orientation_statement"] = (
        "EMR4 shared application authentication now has a real Office-host proof "
        "through its accepted local PostgreSQL LOGIN-to-capability-role path. "
        "Continuity 188 / Compass 169 bind exact RLS, hash-only audit and cleanup "
        "evidence. Protected integration remains paused because it would trigger "
        "public GitHub Pages deployment. Real identity, Microsoft federation, "
        "product data, production and release remain closed."
    )
    compass["map_revision"] = 169
    compass["source_graph_revision"] = 188
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
