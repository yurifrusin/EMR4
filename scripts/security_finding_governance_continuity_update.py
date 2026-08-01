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
NODE_ID = "security-finding-governance"
PARENT_ID = "raisa-shared-application-auth-operational-hardening"
UPDATED_AT = "2026-08-01T05:30:00Z"
SOURCE_HEAD = "2ae8f2173276147e59be361e0182f6cb4b7453fa"

PLAN = "docs/security/security-finding-governance-plan.md"
THREAT = "docs/security/security-finding-governance-threat-model-delta.md"
REGISTER = "docs/security/security-finding-register.json"
REGISTER_SCHEMA = "docs/security/security-finding-register.schema.json"
TRIAGE = "docs/security/dependabot-alerts-8-15-triage-2026-08-01.md"
NATIVE_EVIDENCE = (
    "orchestration/continuity/security-finding-governance/"
    "native-alert-disposition-evidence.json"
)
EVIDENCE = (
    "orchestration/continuity/security-finding-governance/acceptance-evidence.json"
)
CLOSEOUT = "docs/security/security-finding-governance-closeout-2026-08-01.md"
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "security-finding-governance-sol-acceptance.md"
)
REHYDRATION = (
    "orchestration/agent_inbox/codex/"
    "security-finding-governance-rehydration-receipt.json"
)
PREACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "security-finding-governance-preacceptance-receipt.json"
)
SCRIPT = "scripts/security_finding_governance_acceptance.py"
TESTS = "tests/test_security_finding_governance.py"
SECURITY = "SECURITY.md"


def _write(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] == 186:
        if graph["nodes"][-1]["id"] != NODE_ID:
            raise SystemExit("Revision 186 is missing the governance node.")
        return
    if graph["graph_revision"] != 185 or graph["nodes"][-1]["id"] != PARENT_ID:
        raise SystemExit("Unexpected governance graph predecessor.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "EMR4 Security-Finding Governance",
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
                            "Exact evidence-backed native GitHub disposition of "
                            "Dependabot 5 and 8-15 plus CodeQL 295, 272 and 268; "
                            "repository workflow schedules and SECURITY.md policy."
                        ),
                    }
                ],
                "notes": [
                    "Yuri authorised the leading Compass 166 governance candidate.",
                    (
                        "Yuri then granted full SECURITY.md and native-alert "
                        "disposition authority plus task-branch Git publication."
                    ),
                    (
                        "No force dependency override, product/provider/cloud change "
                        "or protected-ref movement occurred."
                    ),
                    (
                        "GPT-5.6 Luna was not exposed in the current subagent "
                        "interface; no substitute worker was dispatched."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-durable-security-register-186",
                    "source": REGISTER,
                    "status": "accepted",
                    "summary": (
                        "Accept one schema-validated sanitized register joining 12 "
                        "native alerts to owners, SLAs, evidence, review/expiry and "
                        "exact native disposition."
                    ),
                },
                {
                    "id": "accept-daily-security-workflow-schedules-186",
                    "source": EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept distinct daily Python and Node schedules while "
                        "preserving push/PR triggers and blocking dependency gates."
                    ),
                },
                {
                    "id": "accept-native-alert-reconciliation-186",
                    "source": NATIVE_EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept exact REST readback of nine dismissed Dependabot and "
                        "three dismissed validated CodeQL highs with zero remaining "
                        "open alerts in those queues."
                    ),
                },
                {
                    "id": "accept-security-owner-sla-policy-186",
                    "source": SECURITY,
                    "status": "accepted",
                    "summary": (
                        "Accept the owner, response targets, laptop-ingestion and "
                        "time-bounded accepted-risk policy."
                    ),
                },
                {
                    "id": "keep-product-provider-and-protected-refs-closed-186",
                    "source": CLOSEOUT,
                    "status": "accepted",
                    "summary": (
                        "Keep product, identity, provider, cloud, deployment, "
                        "production and protected integration outside this pass."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "Twelve native security alerts have unique durable rows with "
                    "owner, SLA, evidence, risk review and exact final GitHub state."
                ),
                (
                    "Dependabot alerts 8-15 are genuine upstream defects but are "
                    "not actionable at this revision because every instance is "
                    "development-only and the advisory product boundary is absent."
                ),
                (
                    "The 14 Bandit and 10 CodeQL validated instances remain linked "
                    "through immutable instance-preserving ledgers."
                ),
                (
                    "Python and Node workflow definitions have staggered daily "
                    "schedules and preserve their existing blocking gates."
                ),
                (
                    "The accepted policy makes laptop-only output insufficient and "
                    "requires time-bounded owner disposition."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [PLAN, THREAT, EVIDENCE],
                    "note": (
                        "Governance touches repository metadata and GitHub alerts "
                        "only; no product context or command path is opened."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [THREAT, NATIVE_EVIDENCE, CLOSEOUT],
                    "note": (
                        "No Diary state, event, appointment, patient or clinical "
                        "data was read or changed."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, THREAT, REGISTER_SCHEMA, SECURITY],
                "findings": [REGISTER, TRIAGE, NATIVE_EVIDENCE, EVIDENCE],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [REHYDRATION, PREACCEPTANCE],
                "tests": [SCRIPT, TESTS],
            },
            "unresolved_gates": [
                (
                    "Daily schedules become operational on GitHub's default branch "
                    "only after protected integration; the draft PR does not move it."
                ),
                (
                    "The development dependency defects remain in the lockfile until "
                    "compatible upstream updates exist; force overrides remain closed."
                ),
                (
                    "No incident paging, SIEM, runner-availability or production "
                    "monitoring result is established."
                ),
                (
                    "Real identity, product data, providers, deployment, production "
                    "and release remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 186
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] == 167
        and compass["source_graph_revision"] == 186
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        return
    if compass["map_revision"] != 166 or compass["source_graph_revision"] != 185:
        raise SystemExit("Unexpected governance Compass predecessor.")

    evidence = [PLAN, THREAT, REGISTER, TRIAGE, NATIVE_EVIDENCE, EVIDENCE, CLOSEOUT]
    outcome = (
        "EMR4 now has one schema-validated owner/SLA register joining 12 native "
        "security alerts to evidence and exact GitHub disposition, with zero open "
        "Dependabot or security-high CodeQL alerts in the reconciled queues. The "
        "14 Bandit and 10 CodeQL validation rows remain linked. Python and Node "
        "workflow definitions now carry staggered daily schedules; activation on "
        "the default branch still awaits protected integration."
    )
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": "Durable security-finding governance",
            "outcome": outcome,
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": "Durable security-finding governance",
        "why_now": (
            "The accepted operational-hardening inventory proved detection was not "
            "laptop-only but exposed an unowned register, schedule and disposition gap."
        ),
        "outcome": outcome,
        "unlocks": [
            (
                "Seek fresh authority for the supervised authored-synthetic "
                "Office cookie-compatibility candidate."
            ),
            (
                "Integrate the published draft PR through protected review so the "
                "daily schedules become active on the default branch."
            ),
            (
                "Reassess accepted development-tool risks when compatible upstream "
                "Office dependencies are released."
            ),
        ],
        "does_not_solve": [
            "Default-branch activation before protected integration.",
            "Removal of development-only vulnerable dependency resolutions.",
            "Incident paging, SIEM, runner availability or production monitoring.",
            "Real identity, product data, provider, deployment, production or release.",
        ],
        "evidence": evidence,
    }
    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"] != "security-finding-governance"
    ]
    for decision in compass["user_owned_decisions"]:
        if decision["id"] == "authorize-security-finding-governance":
            decision["required_before"] = (
                "Satisfied on 2026-08-01 for the exact repository governance, "
                "SECURITY.md, named native-alert disposition and task-branch "
                "publication scope. Protected integration remains separate."
            )
            decision["evidence"] = evidence
            break
    else:
        raise SystemExit("Missing governance authority decision.")

    compass["map_limits"].insert(
        0,
        (
            "The governance descendant proves a repository schema/register, exact "
            "static triage, 12 native GitHub dispositions and daily workflow "
            "definitions. Scheduled runs are not active on the default branch until "
            "protected integration, and vulnerable dev-only lock entries remain."
        ),
    )
    compass["orientation_statement"] = (
        "EMR4 security finding governance is now repository-owned rather than "
        "laptop-dependent: 12 native alerts have owner/SLA/evidence rows and exact "
        "GitHub dispositions; validated Bandit and CodeQL ledgers remain linked; "
        "and Python/Node workflow definitions have staggered daily schedules. "
        "Continuity 186 / Compass 167 bind the repository result. Default-branch "
        "schedule activation awaits protected integration; product, identity, "
        "provider, deployment, production and release boundaries remain closed."
    )
    compass["map_revision"] = 167
    compass["source_graph_revision"] = 186
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
