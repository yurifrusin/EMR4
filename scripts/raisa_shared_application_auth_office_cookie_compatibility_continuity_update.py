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
CREATED_AT = "2026-08-01T07:11:00Z"
UPDATED_AT = "2026-08-01T09:18:15Z"
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
POSTCOMPACTION = (
    "orchestration/agent_inbox/codex/"
    "raisa-shared-application-auth-office-cookie-compatibility-"
    "postcompaction-receipt.json"
)
ALERT17_TRIAGE = "docs/security/dependabot-alert-17-triage-2026-08-01.md"
ALERT17_READBACK = (
    "orchestration/continuity/"
    "shared-application-auth-office-cookie-compatibility/"
    "dependabot-alert-17-readback.json"
)
CODEQL_TRIAGE = "docs/security/pr70-codeql-alerts-543-544-triage-2026-08-01.md"
CODEQL_READBACK = (
    "orchestration/continuity/"
    "shared-application-auth-office-cookie-compatibility/"
    "codeql-pr70-alerts-readback.json"
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
        changed = False
        for contract in node["contract_evidence"]:
            if (
                contract["contract_id"]
                == "committed-reschedule-availability-reconciliation"
                and TESTS not in contract["evidence"]
            ):
                contract["evidence"].append(TESTS)
                changed = True
        alert_note = (
            "Task-branch publication exposed post-snapshot Dependabot alert 17; "
            "it is registered open/needs_review and neither the native alert nor "
            "the dependency graph was mutated."
        )
        if alert_note not in node["authority"]["notes"]:
            node["authority"]["notes"].append(alert_note)
            changed = True
        alert_decision = {
            "id": "register-post-snapshot-dependabot-alert-17-open-187",
            "source": ALERT17_READBACK,
            "status": "accepted",
            "summary": (
                "Register development-only high alert 17 as SF-0020 with a "
                "not_actionable static verdict while retaining its native-open "
                "state pending explicit disposition authority."
            ),
        }
        if not any(
            item["id"] == alert_decision["id"] for item in node["decisions"]
        ):
            node["decisions"].append(alert_decision)
            changed = True
        alert_claim = (
            "Dependabot alert 17 reaches only an optional development-lint "
            "project-service/default-project glob matcher absent from the "
            "supported configuration; SF-0020 remains open/needs_review."
        )
        if alert_claim not in node["claim_scope"]:
            node["claim_scope"].append(alert_claim)
            changed = True
        codeql_note = (
            "PR 70 CodeQL alerts 543 and 544 were fixed by narrow source and "
            "regression changes; fresh language analyses and the wrapper passed "
            "without dismissal or native alert mutation."
        )
        if codeql_note not in node["authority"]["notes"]:
            node["authority"]["notes"].append(codeql_note)
            changed = True
        codeql_decision = {
            "id": "remediate-pr70-codeql-alerts-543-544-187",
            "source": CODEQL_READBACK,
            "status": "accepted",
            "summary": (
                "Accept exact CSP directive equality and removal of an ineffective "
                "local-variable assignment after fresh CodeQL marks both PR "
                "instances fixed."
            ),
        }
        if not any(
            item["id"] == codeql_decision["id"] for item in node["decisions"]
        ):
            node["decisions"].append(codeql_decision)
            changed = True
        codeql_claim = (
            "Fresh PR 70 CodeQL readback marks warning 543 and high alert 544 "
            "fixed at head a4262cbc without dismissal; all five PR checks pass."
        )
        if codeql_claim not in node["claim_scope"]:
            node["claim_scope"].append(codeql_claim)
            changed = True
        for finding in (
            ALERT17_TRIAGE,
            ALERT17_READBACK,
            CODEQL_TRIAGE,
            CODEQL_READBACK,
        ):
            if finding not in node["evidence"]["findings"]:
                node["evidence"]["findings"].append(finding)
                changed = True
        if POSTCOMPACTION not in node["evidence"]["receipts"]:
            node["evidence"]["receipts"].append(POSTCOMPACTION)
            changed = True
        alert_gate = (
            "The native disposition of Dependabot alert 17 remains an explicit "
            "user-owned decision; it stays open/needs_review and no forced "
            "dependency override is authorised."
        )
        if alert_gate not in node["unresolved_gates"]:
            node["unresolved_gates"].append(alert_gate)
            changed = True
        if changed:
            node["updated_at"] = UPDATED_AT
            graph["updated_at"] = UPDATED_AT
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
            "created_at": CREATED_AT,
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
                    (
                        "Task-branch publication exposed post-snapshot Dependabot "
                        "alert 17; it is registered open/needs_review and neither "
                        "the native alert nor the dependency graph was mutated."
                    ),
                    (
                        "PR 70 CodeQL alerts 543 and 544 were fixed by narrow "
                        "source and regression changes; fresh language analyses "
                        "and the wrapper passed without dismissal or native "
                        "alert mutation."
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
                {
                    "id": "register-post-snapshot-dependabot-alert-17-open-187",
                    "source": ALERT17_READBACK,
                    "status": "accepted",
                    "summary": (
                        "Register development-only high alert 17 as SF-0020 with "
                        "a not_actionable static verdict while retaining its "
                        "native-open state pending explicit disposition authority."
                    ),
                },
                {
                    "id": "remediate-pr70-codeql-alerts-543-544-187",
                    "source": CODEQL_READBACK,
                    "status": "accepted",
                    "summary": (
                        "Accept exact CSP directive equality and removal of an "
                        "ineffective local-variable assignment after fresh CodeQL "
                        "marks both PR instances fixed."
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
                (
                    "Dependabot alert 17 reaches only an optional development-lint "
                    "project-service/default-project glob matcher absent from the "
                    "supported configuration; SF-0020 remains open/needs_review."
                ),
                (
                    "Fresh PR 70 CodeQL readback marks warning 543 and high alert "
                    "544 fixed at head a4262cbc without dismissal; all five PR "
                    "checks pass."
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
                "findings": [
                    LIVE_EVIDENCE,
                    RESIDUE,
                    EVIDENCE,
                    ALERT17_TRIAGE,
                    ALERT17_READBACK,
                    CODEQL_TRIAGE,
                    CODEQL_READBACK,
                ],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [REHYDRATION, PREACCEPTANCE, POSTCOMPACTION],
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
                (
                    "The native disposition of Dependabot alert 17 remains an "
                    "explicit user-owned decision; it stays open/needs_review and "
                    "no forced dependency override is authorised."
                ),
            ],
        }
    )
    graph["graph_revision"] = 187
    graph["updated_at"] = UPDATED_AT
    _write(GRAPH, graph)


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    evidence = [
        PLAN,
        THREAT,
        LIVE_EVIDENCE,
        RESIDUE,
        EVIDENCE,
        CLOSEOUT,
        ALERT17_TRIAGE,
        ALERT17_READBACK,
        CODEQL_TRIAGE,
        CODEQL_READBACK,
    ]
    outcome = (
        "The accepted default-off authored-synthetic session-cookie lifecycle "
        "passed once in installed Word and once in Word Online through the exact "
        "development origin. Both independent sessions rotated, logged out and "
        "then denied validation; no product, identity, document, provider, cloud "
        "or deployment path ran, and task listeners and registration are absent. "
        "Publication exposed development-only Dependabot alert 17, which is "
        "registered open/needs_review without native or dependency mutation. "
        "PR 70 warning 543 and high alert 544 were repaired and fresh CodeQL "
        "marks both fixed without dismissal."
    )
    alert_unlock = (
        "Make an explicit user decision whether Dependabot alert 17 should remain "
        "open or be dismissed as not_used; do not force a dependency override."
    )
    alert_unsolved = (
        "The user-owned native disposition or removal of Dependabot alert 17."
    )
    alert_decision = {
        "id": "authorize-dependabot-alert-17-native-disposition",
        "question": (
            "Should development-only Dependabot alert 17 be dismissed as not_used "
            "or remain open for upstream remediation?"
        ),
        "required_before": (
            "Any GitHub alert-state mutation. SF-0020 is currently registered "
            "not_actionable and native-open/needs_review; no dependency override "
            "is authorised."
        ),
        "evidence": [ALERT17_TRIAGE, ALERT17_READBACK],
    }
    alert_limit = (
        "Post-snapshot Dependabot alert 17 is statically not_actionable for the "
        "supported development lint configuration but remains native-open and "
        "needs_review pending an explicit user disposition."
    )
    if (
        compass["map_revision"] == 168
        and compass["source_graph_revision"] == 187
        and compass["current_position"]["node_id"] == NODE_ID
    ):
        journey = next(item for item in compass["journey"] if item["node_id"] == NODE_ID)
        journey["outcome"] = outcome
        journey["evidence"] = evidence
        position = compass["current_position"]
        position["outcome"] = outcome
        position["evidence"] = evidence
        if alert_unlock not in position["unlocks"]:
            position["unlocks"].insert(0, alert_unlock)
        if alert_unsolved not in position["does_not_solve"]:
            position["does_not_solve"].append(alert_unsolved)
        if not any(
            item["id"] == alert_decision["id"]
            for item in compass["user_owned_decisions"]
        ):
            compass["user_owned_decisions"].append(alert_decision)
        if alert_limit not in compass["map_limits"]:
            compass["map_limits"].insert(0, alert_limit)
        compass["orientation_statement"] = (
            "EMR4 shared application authentication now has a real Office-host "
            "cookie compatibility proof in installed Word and Word Online. "
            "Continuity 187 / Compass 168 bind the result and the post-snapshot "
            "development-only Dependabot alert 17 remains registered open/"
            "needs_review without mutation. PR 70 CodeQL instances 543 and 544 "
            "are fixed without dismissal. Real identity, Microsoft federation, "
            "product data, organisational deployment, production, release and "
            "protected integration remain closed."
        )
        compass["updated_at"] = UPDATED_AT
        _write(COMPASS, compass)
        return
    if compass["map_revision"] != 167 or compass["source_graph_revision"] != 186:
        raise SystemExit("Unexpected Office cookie Compass predecessor.")

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
            alert_unlock,
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
            alert_unsolved,
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
    if not any(
        item["id"] == alert_decision["id"]
        for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].append(alert_decision)

    compass["map_limits"].insert(0, alert_limit)
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
        "compatibility proof in installed Word and Word Online. Continuity 187 / "
        "Compass 168 bind the result and the post-snapshot development-only "
        "Dependabot alert 17 remains registered open/needs_review without mutation. "
        "PR 70 CodeQL instances 543 and 544 are fixed without dismissal. Real "
        "identity, Microsoft federation, product data, organisational "
        "deployment, production, release and protected integration remain closed."
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
