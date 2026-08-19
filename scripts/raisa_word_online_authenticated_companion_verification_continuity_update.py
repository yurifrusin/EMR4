from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "raisa-word-online-authenticated-companion-verification"
PARENT_ID = "raisa-cloud-run-public-access-word-online-verification"
UPDATED_AT = "2026-07-31T11:08:30Z"


PLAN = "docs/raisa-word-online-authenticated-companion-verification-plan.md"
THREAT_MODEL = (
    "docs/security/"
    "raisa-word-online-authenticated-companion-verification-threat-model-delta.md"
)
BROWSER_EVIDENCE = (
    "orchestration/continuity/"
    "raisa-word-online-authenticated-companion-verification/"
    "browser-word-online-evidence.json"
)
AUDIT_EVIDENCE = (
    "orchestration/continuity/"
    "raisa-word-online-authenticated-companion-verification/"
    "external-audit-analysis.json"
)
RESIDUE_EVIDENCE = (
    "orchestration/continuity/"
    "raisa-word-online-authenticated-companion-verification/"
    "final-residue-evidence.json"
)
CLOSEOUT = (
    "docs/raisa-word-online-authenticated-companion-verification-closeout.md"
)
ACCEPTANCE = (
    "orchestration/agent_inbox/codex/"
    "raisa-word-online-authenticated-companion-verification-sol-acceptance.md"
)
RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-word-online-authenticated-companion-verification-"
    "preacceptance-receipt.json"
)
POSTCOMPACTION_RECEIPT = (
    "orchestration/agent_inbox/codex/"
    "raisa-word-online-authenticated-companion-verification-"
    "postcompaction-receipt.json"
)


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] != 179:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "Raisa Word Online Authenticated Companion Verification",
            "kind": "integration",
            "status": "accepted",
            "created_at": UPDATED_AT,
            "updated_at": UPDATED_AT,
            "coordinates": {
                "git_ref": "codex/ariadne-terra-gemini-comparative-rehearsal",
                "source_head": "5b1ea7952fb08eea333da0e63f166d3895ccea32",
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
                        "boundary": "deployment",
                        "scope": (
                            "Resume the exact task-specific Word Online manifest "
                            "gate, make an ordinary repository-local repair and "
                            "redeploy only raisa-office-web-dev while preserving "
                            "the frozen zero-authority posture."
                        ),
                        "source": PLAN,
                    }
                ],
                "notes": [
                    (
                        "The existing signed-in Word Online session and validated "
                        "ReadDocument manifest were reused; no Office tenant or "
                        "account setting changed."
                    ),
                    (
                        "The repair admits only smoke and "
                        "reception_one_companion_demo under the exact "
                        "origin-bound authored-synthetic public policy."
                    ),
                    (
                        "No other service, IAM policy, organisation policy, "
                        "identity, region or origin changed."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-raisa-word-online-companion-180",
                    "source": BROWSER_EVIDENCE,
                    "status": "accepted",
                    "summary": (
                        "Accept the one bounded signed-in Word Online companion "
                        "exchange with native-Diary-only detail and generic "
                        "proofreader-admitted Word release."
                    ),
                },
                {
                    "id": "accept-hosted-diary-zero-authority-repair-180",
                    "source": THREAT_MODEL,
                    "status": "accepted",
                    "summary": (
                        "Accept the exact hosted capability allowlist repair while "
                        "backend, provider, credential, microphone, command, "
                        "document-write and production authority remain false."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "The task-specific ReadDocument manifest loaded in one "
                    "signed-in personal Word Online session."
                ),
                (
                    "The first hosted attempt failed closed before request "
                    "admission; the exact-service repair then admitted one typed "
                    "authored-synthetic request."
                ),
                (
                    "Three synthetic appointment matches remained in the native "
                    "Diary and Word received only the exact generic result count."
                ),
                (
                    "Observed taskpane and Diary resource timing contained zero "
                    "API, credential and provider requests; no document body, "
                    "database, command or confirmation path ran."
                ),
                (
                    "Both task-created blank documents were moved to the "
                    "recoverable OneDrive Recycle Bin and task-local residue is "
                    "zero."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": (
                        "combined-patient-practitioner-time-duration-intent"
                    ),
                    "status": "satisfied",
                    "evidence": [
                        BROWSER_EVIDENCE,
                        AUDIT_EVIDENCE,
                        (
                            "tests/"
                            "test_reception_one_word_compact_companion_shell.py"
                        ),
                    ],
                    "note": (
                        "The typed request was read-only and authored-synthetic; "
                        "no appointment context, proposal, confirmation or command "
                        "was released to Word."
                    ),
                },
                {
                    "contract_id": (
                        "committed-reschedule-availability-reconciliation"
                    ),
                    "status": "satisfied",
                    "evidence": [
                        BROWSER_EVIDENCE,
                        RESIDUE_EVIDENCE,
                        CLOSEOUT,
                        "tests/test_raisa_office_web_dev_context.py",
                    ],
                    "note": (
                        "No backend, database, committed event, availability or "
                        "Diary truth path was contacted or changed."
                    ),
                },
            ],
            "evidence": {
                "plans": [PLAN, THREAT_MODEL],
                "findings": [
                    BROWSER_EVIDENCE,
                    AUDIT_EVIDENCE,
                    RESIDUE_EVIDENCE,
                ],
                "closeouts": [CLOSEOUT],
                "acceptances": [ACCEPTANCE],
                "receipts": [RECEIPT, POSTCOMPACTION_RECEIPT],
                "tests": [
                    "tests/test_raisa_office_web_dev_context.py",
                    (
                        "tests/"
                        "test_raisa_cloud_run_public_access_word_online_verification.py"
                    ),
                    (
                        "tests/"
                        "test_reception_one_word_compact_companion_shell.py"
                    ),
                ],
            },
            "unresolved_gates": [
                (
                    "EMR4 application authentication and clinician-role "
                    "authorization remain unproven."
                ),
                (
                    "Organisational Office tenant deployment and central add-in "
                    "administration remain unproven."
                ),
                (
                    "Real, product-derived, patient, health, clinical and "
                    "historical data remain closed."
                ),
                (
                    "Provider, backend, database, microphone, appointment command, "
                    "document write, production and release remain closed."
                ),
                (
                    "This evidence makes no Microsoft or Google physical or "
                    "sovereign processing claim."
                ),
            ],
        }
    )
    graph["graph_revision"] = 180
    graph["updated_at"] = UPDATED_AT
    GRAPH.write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if (
        compass["map_revision"] != 160
        or compass["source_graph_revision"] != 179
    ):
        raise SystemExit("Unexpected Compass predecessor revision.")

    evidence = [
        PLAN,
        BROWSER_EVIDENCE,
        AUDIT_EVIDENCE,
        RESIDUE_EVIDENCE,
        CLOSEOUT,
    ]
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": (
                "Signed-in Word Online companion verified with native-only detail "
                "and generic typed release"
            ),
            "outcome": (
                "The validated manifest loaded, one authored-synthetic request "
                "produced three native Diary matches, and Word received only the "
                "generic proofreader-admitted count. The exact hosted-capability "
                "repair preserved the zero-authority public policy."
            ),
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Signed-in Word Online companion verified with native-only detail and "
            "generic typed release"
        ),
        "why_now": (
            "Yuri enabled the documented file-upload prerequisite and selected "
            "the already validated manifest, allowing the final bounded Word "
            "Online gate to run. Its one repository-local mismatch was repaired "
            "on only the exact existing Sydney service."
        ),
        "outcome": (
            "One provider-free authored-synthetic Word-to-Diary exchange now "
            "passes in Word Online. Three synthetic matches stayed in the Diary, "
            "Word retained only the admitted generic count, no backend or provider "
            "path ran, and task cleanup is complete."
        ),
        "unlocks": [
            (
                "Use the accepted local, desktop and Word Online companion "
                "contracts as the dual-host interaction baseline."
            ),
            (
                "Plan a separately authorised EMR4 application-authentication and "
                "clinician-role boundary before any product-derived read."
            ),
            (
                "Retain the hosted zero-authority synthetic lane for regression "
                "testing while product, provider and write authority stay closed."
            ),
        ],
        "does_not_solve": [
            "EMR4 application authentication or clinician-role authorization.",
            "Organisational Office tenant deployment or central add-in management.",
            (
                "Safety for real, product-derived, patient, health, clinical or "
                "historical data."
            ),
            (
                "Backend, database, provider, microphone, appointment command or "
                "document-write readiness."
            ),
            "Microsoft or Google physical or sovereign processing location.",
            "Production or release readiness.",
        ],
        "evidence": evidence,
    }

    completed_horizon_ids = {
        "resume-raisa-word-online-manifest-upload",
        "reception-one-word-online-authenticated-dialog-check",
    }
    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"] not in completed_horizon_ids
    ]
    compass["user_owned_decisions"] = [
        item
        for item in compass["user_owned_decisions"]
        if item["id"] != "enable-chatgpt-chrome-file-url-access"
    ]
    compass["map_limits"].insert(
        0,
        (
            "The accepted Word Online descendant proves one task-specific "
            "ReadDocument manifest and provider-free authored-synthetic "
            "Word-to-Diary exchange in a signed-in personal session, with "
            "native-only detail and generic typed release. It does not prove "
            "EMR4 application authentication, clinician-role authorization, "
            "organisational deployment, real-data safety, backend or provider "
            "readiness, processing geography, production or release."
        ),
    )
    compass["map_revision"] = 161
    compass["source_graph_revision"] = 180
    compass["updated_at"] = UPDATED_AT
    COMPASS.write_text(
        json.dumps(compass, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    update_graph()
    update_compass()
    return 0


if __name__ == "__main__":
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from orchestration_harness.governance_writer_guard import refuse_retired_legacy_writer
    refuse_retired_legacy_writer(ROOT)
    raise SystemExit(main())
