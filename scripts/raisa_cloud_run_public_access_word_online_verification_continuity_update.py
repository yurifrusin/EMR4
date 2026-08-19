from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "raisa-cloud-run-public-access-word-online-verification"
PARENT_ID = "raisa-cloud-run-public-https-dev-host-deployment"
UPDATED_AT = "2026-07-31T09:32:27Z"


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] != 178:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "Raisa Public Access and Word Online Verification",
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
                            "Disable the Cloud Run Invoker IAM check only for "
                            "raisa-office-web-dev in bernie-emr4-dev/"
                            "australia-southeast1, then run bounded public HTTPS, "
                            "browser, manifest and Word Online verification."
                        ),
                        "source": (
                            "docs/raisa-cloud-run-public-access-word-online-"
                            "verification-plan.md"
                        ),
                    }
                ],
                "notes": [
                    (
                        "No other service, IAM policy or organisation policy was "
                        "authorised or changed."
                    ),
                    (
                        "The public static host remains authored-synthetic, "
                        "provider-free, backend-free, database-free and "
                        "command-free."
                    ),
                    (
                        "Word Online manifest upload stopped before transmission "
                        "because the Chrome extension file-URL access prerequisite "
                        "is not enabled."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "accept-raisa-cloud-run-no-invoker-iam-check-179",
                    "source": (
                        "docs/raisa-cloud-run-public-access-word-online-"
                        "verification-plan.md"
                    ),
                    "status": "accepted",
                    "summary": (
                        "Use the no-invoker-iam-check mechanism on only the exact "
                        "Raisa development service, retaining zero allUsers IAM "
                        "bindings and every frozen runtime boundary."
                    ),
                },
                {
                    "id": "resume-raisa-word-online-manifest-upload-179",
                    "source": (
                        "orchestration/continuity/"
                        "raisa-cloud-run-public-access-word-online-verification/"
                        "browser-word-online-evidence.json"
                    ),
                    "status": "candidate",
                    "summary": (
                        "Resume the exact task-specific manifest upload after Yuri "
                        "enables file-URL access for the ChatGPT Chrome Extension."
                    ),
                },
            ],
            "claim_scope": [
                (
                    "The exact Sydney Cloud Run development service is publicly "
                    "reachable with its Invoker IAM check disabled and zero "
                    "allUsers IAM bindings."
                ),
                (
                    "The accepted public route matrix, security headers, closed "
                    "hosting policy and hosted companion browser surface pass."
                ),
                (
                    "The task-specific Office manifest validates and all of its "
                    "public source, domain and icon URLs return HTTP 200."
                ),
                (
                    "Word Online reached its developer Upload Add-in dialog in a "
                    "fresh blank personal document, but no manifest was transmitted "
                    "because the browser file chooser was unavailable."
                ),
                (
                    "No synthetic request, provider call, backend request, database "
                    "request, document body read/write, command or confirmation "
                    "occurred."
                ),
                (
                    "Task-owned local build directories, local repair image tags, "
                    "containers and networks were removed; two blank task-created "
                    "Word documents require terminal cleanup."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [
                        (
                            "orchestration/continuity/"
                            "raisa-cloud-run-public-access-word-online-verification/"
                            "public-access-and-route-evidence.json"
                        ),
                        (
                            "orchestration/continuity/"
                            "raisa-cloud-run-public-access-word-online-verification/"
                            "browser-word-online-evidence.json"
                        ),
                        "tests/test_raisa_office_web_dev_context.py",
                    ],
                    "note": (
                        "No appointment context, proposal, confirmation or command "
                        "was sent during this partial verification."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [
                        (
                            "orchestration/continuity/"
                            "raisa-cloud-run-public-access-word-online-verification/"
                            "browser-word-online-evidence.json"
                        ),
                        (
                            "docs/raisa-cloud-run-public-access-word-online-"
                            "verification-intervention-closeout.md"
                        ),
                        (
                            "tests/test_reception_one_word_compact_companion_shell.py"
                        ),
                    ],
                    "note": (
                        "No backend, database, event, availability or Diary truth "
                        "path was contacted or changed."
                    ),
                },
            ],
            "evidence": {
                "plans": [
                    (
                        "docs/raisa-cloud-run-public-access-word-online-"
                        "verification-plan.md"
                    )
                ],
                "findings": [
                    (
                        "orchestration/continuity/"
                        "raisa-cloud-run-public-access-word-online-verification/"
                        "public-access-and-route-evidence.json"
                    ),
                    (
                        "orchestration/continuity/"
                        "raisa-cloud-run-public-access-word-online-verification/"
                        "browser-word-online-evidence.json"
                    ),
                    (
                        "orchestration/continuity/"
                        "raisa-cloud-run-public-access-word-online-verification/"
                        "interim-residue-evidence.json"
                    ),
                ],
                "closeouts": [
                    (
                        "docs/raisa-cloud-run-public-access-word-online-"
                        "verification-intervention-closeout.md"
                    )
                ],
                "acceptances": [
                    (
                        "orchestration/agent_inbox/codex/"
                        "raisa-cloud-run-public-access-word-online-verification-"
                        "sol-acceptance.md"
                    )
                ],
                "receipts": [
                    (
                        "orchestration/agent_inbox/codex/"
                        "raisa-cloud-run-public-access-word-online-verification-"
                        "receipt.json"
                    ),
                    (
                        "orchestration/agent_inbox/codex/"
                        "raisa-cloud-run-public-access-word-online-verification-"
                        "preacceptance-receipt.json"
                    ),
                ],
                "tests": [
                    "tests/test_raisa_office_web_dev_context.py",
                    "tests/test_reception_one_word_compact_companion_shell.py",
                ],
            },
            "unresolved_gates": [
                (
                    "Yuri must enable Allow access to file URLs for the ChatGPT "
                    "Chrome Extension before the task-specific manifest can be "
                    "uploaded."
                ),
                (
                    "Word Online add-in loading, Office dialog launch, generic "
                    "summary release and focus restoration remain unproven."
                ),
                (
                    "Two task-created blank Word documents require deletion after "
                    "the terminal Word result."
                ),
                (
                    "Authenticated Office identity and clinician-role authorization "
                    "remain unproven."
                ),
                (
                    "Real, product-derived, patient, health, clinical and historical "
                    "data remain closed."
                ),
                (
                    "Provider, backend, database, microphone, document write, "
                    "production and release remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 179
    graph["updated_at"] = UPDATED_AT
    GRAPH.write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] != 159 or compass["source_graph_revision"] != 178:
        raise SystemExit("Unexpected Compass predecessor revision.")
    if compass["journey"][-1]["node_id"] != PARENT_ID:
        raise SystemExit("Unexpected Compass journey predecessor.")

    evidence = [
        "docs/raisa-cloud-run-public-access-word-online-verification-plan.md",
        (
            "orchestration/continuity/"
            "raisa-cloud-run-public-access-word-online-verification/"
            "public-access-and-route-evidence.json"
        ),
        (
            "orchestration/continuity/"
            "raisa-cloud-run-public-access-word-online-verification/"
            "browser-word-online-evidence.json"
        ),
        (
            "orchestration/continuity/"
            "raisa-cloud-run-public-access-word-online-verification/"
            "interim-residue-evidence.json"
        ),
    ]
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": (
                "Public Sydney development host accepted; Word manifest upload "
                "waiting on local browser permission"
            ),
            "outcome": (
                "The exact service is publicly reachable through the bounded "
                "no-invoker-check mechanism, and its public routes, policy, "
                "headers, manifest resources and hosted companion pass. Word "
                "Online reached the developer upload dialog but transmitted no "
                "manifest because Chrome file-URL access is unavailable."
            ),
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Public Sydney development host accepted; Word manifest upload "
            "waiting on local browser permission"
        ),
        "why_now": (
            "Yuri authorised the exact service-only Cloud Run access mechanism "
            "and bounded public/Word verification. The cloud and public browser "
            "gates passed; the only remaining immediate gate is local Chrome "
            "extension permission for the developer manifest file chooser."
        ),
        "outcome": (
            "The exact service is public without an allUsers IAM binding and the "
            "closed static host is verified. The Office manifest is valid, but "
            "Word Online execution remains unproven because the manifest was not "
            "uploaded. No document content or system data was transmitted."
        ),
        "unlocks": [
            (
                "After Yuri enables file-URL access for the ChatGPT Chrome "
                "Extension, resume the preserved blank Word Online upload dialog."
            ),
            (
                "If upload succeeds, run one authored-synthetic companion request, "
                "Office dialog, generic-summary and focus-restoration check."
            ),
            (
                "After a terminal Word result, remove both task-created blank "
                "documents and complete external audit and closeout."
            ),
        ],
        "does_not_solve": [
            "Word Online add-in execution or Office dialog behavior.",
            "Authenticated Office identity or clinician-role authorization.",
            (
                "Safety for real, product-derived, patient, health, clinical or "
                "historical text."
            ),
            "Microsoft or Google physical or sovereign processing location.",
            "Provider, backend, database, microphone, command or document write.",
            "Production or release readiness.",
        ],
        "evidence": evidence,
    }

    compass["decision_horizon"] = [
        item
        for item in compass["decision_horizon"]
        if item["id"]
        != "authorize-raisa-cloud-run-public-https-dev-host-deployment"
    ]
    compass["decision_horizon"].insert(
        0,
        {
            "id": "resume-raisa-word-online-manifest-upload",
            "title": "Raisa Word Online developer-manifest verification",
            "status": "blocked",
            "strategic_question": (
                "Can the validated public Raisa manifest be uploaded and exercised "
                "in a blank personal Word Online document?"
            ),
            "why_it_matters": (
                "The public host is now ready, but Word Online behavior is the last "
                "unproven surface in this bounded tranche."
            ),
            "prerequisites": [
                (
                    "Yuri enables Allow access to file URLs for the ChatGPT Chrome "
                    "Extension."
                ),
                "Reuse the exact task-specific manifest and public host revision.",
                (
                    "Retain authored-synthetic, provider-free, backend-free, "
                    "database-free, read-only and no-command boundaries."
                ),
                (
                    "Delete both task-created blank Word documents after the "
                    "terminal result."
                ),
            ],
            "boundary_changes": [],
            "evidence": evidence,
        },
    )
    compass["user_owned_decisions"] = [
        item
        for item in compass["user_owned_decisions"]
        if item["id"] != "authorize-raisa-cloud-run-no-invoker-iam-check"
    ]
    permission_id = "enable-chatgpt-chrome-file-url-access"
    if not any(
        item["id"] == permission_id for item in compass["user_owned_decisions"]
    ):
        compass["user_owned_decisions"].insert(
            0,
            {
                "id": permission_id,
                "question": (
                    "Enable Allow access to file URLs for the ChatGPT Chrome "
                    "Extension so the exact local developer manifest can be chosen?"
                ),
                "required_before": (
                    "The preserved Word Online Upload Add-in dialog can transmit "
                    "the task-specific manifest."
                ),
                "evidence": evidence,
            },
        )
    compass["map_limits"].insert(
        0,
        (
            "The public-access descendant proves the exact service-only Cloud Run "
            "access mechanism, public static route/policy/header behavior and "
            "manifest URL availability. It does not prove Word Online add-in "
            "execution: no manifest was uploaded and no synthetic request was "
            "submitted because Chrome file-URL access is not enabled."
        ),
    )
    compass["map_revision"] = 160
    compass["source_graph_revision"] = 179
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
