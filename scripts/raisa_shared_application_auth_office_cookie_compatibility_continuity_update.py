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
NODE_ID = "raisa-shared-application-auth-office-cookie-compatibility"
PARENT_ID = "raisa-shared-application-auth-operational-hardening"
PREDECESSOR_ID = "security-finding-governance"
UPDATED_AT = "2026-08-01T07:11:00Z"
SOURCE_HEAD = "30d5e0116148529da3c41c728504c69d8833f544"

PLAN = "docs/raisa-shared-application-auth-office-cookie-compatibility-plan.md"
THREAT = (
    "docs/security/"
    "raisa-shared-application-auth-office-cookie-compatibility-threat-model-delta.md"
)
LIVE_EVIDENCE = (
    "orchestration/continuity/"
    "shared-application-auth-office-cookie-compatibility/"
    "live-office-host-evidence.json"
)
RESIDUE = (
    "orchestration/continuity/"
    "shared-application-auth-office-cookie-compatibility/"
    "final-residue-evidence.json"
)
EVIDENCE = (
    "orchestration/continuity/"
    "shared-application-auth-office-cookie-compatibility/"
    "acceptance-evidence.json"
)
CLOSEOUT = (
    "docs/raisa-shared-application-auth-office-cookie-compatibility-closeout.md"
)
REHYDRATION = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-office-cookie-compatibility-"
    "rehydration-receipt.json"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-office-cookie-compatibility-"
    "preacceptance-receipt.json"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-office-cookie-compatibility-"
    "sol-acceptance.md"
)
HARNESS = "scripts/raisa_shared_application_auth_office_cookie_compatibility.py"
TESTS = "tests/test_raisa_shared_application_auth_office_cookie_compatibility.py"
DESKTOP_MANIFEST = (
    "orchestration/continuity/"
    "shared-application-auth-office-cookie-compatibility/"
    "word-desktop-manifest.xml"
)
ONLINE_MANIFEST = (
    "orchestration/continuity/"
    "shared-application-auth-office-cookie-compatibility/"
    "word-online-manifest.xml"
)


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 187:
        if graph["nodes"][-1]["id"] != NODE_ID:
            raise SystemExit("Revision 187 is missing the Office cookie node.")
        node = graph["nodes"][-1]
        for contract in node["contract_evidence"]:
            if (
                contract["contract_id"]
                == "committed-reschedule-availability-reconciliation"
                and TESTS not in contract["evidence"]
            ):
                contract["evidence"].append(TESTS)
                _write(GRAPH, graph)
        return
    if (
        graph["graph_revision"] != 186
        or graph["nodes"][-1]["id"] != PREDECESSOR_ID
    ):
        raise SystemExit("Unexpected Office cookie graph predecessor.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "Raisa Shared Application-Auth Office Cookie Compatibility",
            "kind": "integration",
            "status": "accepted",
            "created_at": UPDATED_AT,
            "updated_at": UPDATED_AT,
            "coordinates": {
                "git_ref": "codex/shared-auth-office-cookie-compatibility",
                "source_head": SOURCE_HEAD,
                "thread_id": None,
                "worktree_role": "integration",
            },
            "relationships": [
                {"node_id": PARENT_ID, "relation": "builds_on"},
                {
                    "node_id": "raisa-shared-application-auth-runtime-role-secure-transport",
                    "relation": "validates",
                },
            ],
            "authority": {
                "authorized_openings": [
                    {
                        "boundary": "api-change",
                        "source": PLAN,
                        "scope": (
                            "One supervised provider-free authored-synthetic "
                            "exercise of the existing session-cookie transport "
                            "in installed Word and Word Online through an "
                            "ephemeral HTTPS relay to a local in-memory harness."
                        ),
                    }
                ],
                "notes": [
                    (
                        "Yuri authorised the leading Compass 167 Office "
                        "cookie-compatibility candidate."
                    ),
                    (
                        "Yuri separately permitted the supplied Raisa branding "
                        "direction in future UI renders; the concurrent brand "
                        "assets remained untouched and excluded."
                    ),
                    (
                        "No Trust Center, catalogue, tenant, Office policy, "
                        "cloud/IAM, deployment or protected-ref change occurred."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-real-office-cookie-lifecycle-187",
                    "source": LIVE_EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept one independent create, validate, rotate, "
                        "revalidate, logout and post-logout denial result in "
                        "installed Word and Word Online."
                    ),
                },
                {
                    "id": "accept-direct-developer-sideload-repair-187",
                    "source": CLOSEOUT,
                    "status": "accepted",
                    "summary": (
                        "Accept the fail-closed desktop preflight and direct-debug "
                        "host-admission repair with complete registration cleanup."
                    ),
                },
                {
                    "id": "accept-parent-source-digest-reconciliation-187",
                    "source": EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Reconcile two stale PR 69 source digests to the already "
                        "accepted source bytes without runtime behavior change."
                    ),
                },
                {
                    "id": "keep-real-identity-product-and-release-closed-187",
                    "source": THREAT,
                    "status": "accepted",
                    "summary": (
                        "Keep real identity, Microsoft federation, product data, "
                        "database-backed Office behavior, deployment, production "
                        "and release outside this pass."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "The existing Secure, HttpOnly, SameSite=None, Partitioned "
                    "session-cookie lifecycle passed once in each supervised "
                    "Office host through the exact development origin."
                ),
                (
                    "Each host used an independent authored-synthetic principal, "
                    "one-use bootstrap and result channel; both logged out and "
                    "proved the ordinary post-logout denial."
                ),
                (
                    "The desktop admission failure occurred before page delivery; "
                    "direct developer debugging repaired only host admission and "
                    "was fully unregistered."
                ),
                (
                    "No document, product, patient, clinical, external identity, "
                    "provider, cloud, deployment or production path ran."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [PLAN, THREAT, LIVE_EVIDENCE, TESTS],
                    "note": (
                        "The harness contains no product context, appointment "
                        "proposal or command path."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [LIVE_EVIDENCE, RESIDUE, CLOSEOUT, TESTS],
                    "note": (
                        "No Diary, database, event, availability or appointment "
                        "state was read or changed."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, THREAT],
                "findings": [LIVE_EVIDENCE, RESIDUE, EVIDENCE],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [REHYDRATION, PREACCEPTANCE],
                "tests": [HARNESS, TESTS, DESKTOP_MANIFEST, ONLINE_MANIFEST],
            },
            "unresolved_gates": [
                (
                    "The pass covers one Office/WebView/browser/tenant posture and "
                    "one exact development origin, not every enterprise policy."
                ),
                (
                    "PostgreSQL, multi-instance and capability-role behavior was "
                    "not exercised through either real Office host."
                ),
                (
                    "Real identity mapping, Microsoft federation and product-data "
                    "authorization remain separately closed."
                ),
                (
                    "Organisational Office deployment, production, release and "
                    "protected integration require separate authority."
                ),
            ],
        }
    )
    graph["graph_revision"] = 187
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 168
        and compass["source_graph_revision"] == 187
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        return
    if compass["map_revision"] != 167 or compass["source_graph_revision"] != 186:
        raise SystemExit("Unexpected Office cookie Compass predecessor.")

    evidence = [PLAN, THREAT, LIVE_EVIDENCE, RESIDUE, EVIDENCE, CLOSEOUT]
    outcome = (
        "The accepted default-off authored-synthetic session-cookie lifecycle "
        "passed once in installed Word and once in Word Online through the exact "
        "development origin. Both independent sessions rotated, logged out and "
        "then denied validation; no product, identity, document, provider, cloud "
        "or deployment path ran, and task listeners and registration are absent."
    )
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": "Real Office-host cookie compatibility proof",
            "outcome": outcome,
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Real Office-host cookie compatibility proof",
        "why_now": (
            "The protected shared-auth and governance foundations were integrated, "
            "leaving real Office host cookie carriage as the leading bounded gap."
        ),
        "outcome": outcome,
        "unlocks": [
            (
                "Seek fresh authority for a provider-free authored-synthetic "
                "Office-host exercise through the accepted local PostgreSQL "
                "persistence and capability-role boundary."
            ),
            (
                "Separately decide whether to design a real-identity and Microsoft "
                "federation boundary without yet wiring product reads."
            ),
            (
                "Publish and review this task branch without moving protected refs."
            ),
        ],
        "does_not_solve": [
            "Every Office/WebView/browser/tenant cookie policy.",
            "PostgreSQL or multi-instance behavior through a real Office host.",
            "Real identity, Microsoft federation or product-data authorization.",
            "Organisational deployment, production, release or protected integration.",
        ],
        "evidence": evidence,
    }
    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"] != "shared-application-auth-office-cookie-compatibility"
    ]
    decision_id = "authorize-shared-application-auth-office-cookie-compatibility"
    if not any(item["id"] == decision_id for item in compass["user_owned_decisions"]):
        compass["user_owned_decisions"].append(
            {
                "id": decision_id,
                "question": (
                    "Should EMR4 exercise its accepted authored-synthetic "
                    "session-cookie transport in installed Word and Word Online?"
                ),
                "required_before": (
                    "Satisfied on 2026-08-01 for one provider-free in-memory "
                    "supervised exercise through the exact development origin. "
                    "Real identity, product data, organisational deployment, "
                    "production and release remain closed."
                ),
                "evidence": evidence,
            }
        )

    compass["map_limits"].insert(
        0,
        (
            "The Office cookie descendant proves one independent session lifecycle "
            "in installed Word and Word Online through one development origin. It "
            "does not cover every policy, PostgreSQL/multi-instance behavior, real "
            "identity, product data, organisational deployment or production."
        ),
    )
    compass["orientation_statement"] = (
        "EMR4 shared application authentication now has a real Office-host cookie "
        "compatibility proof: independent authored-synthetic sessions passed create, "
        "validate, rotate, revalidate, logout and post-logout denial in installed "
        "Word and Word Online. Continuity 187 / Compass 168 bind the result. Real "
        "identity, Microsoft federation, product data, organisational deployment, "
        "production, release and protected integration remain closed."
    )
    compass["map_revision"] = 168
    compass["source_graph_revision"] = 187
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
