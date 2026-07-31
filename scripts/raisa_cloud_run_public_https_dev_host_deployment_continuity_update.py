from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "orchestration" / "continuity" / "emr4-continuity-graph.json"
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "raisa-cloud-run-public-https-dev-host-deployment"
PARENT_ID = "raisa-cloud-run-api-runtime-identity-enablement"
UPDATED_AT = "2026-07-31T08:47:48Z"


def update_graph() -> None:
    graph = json.loads(GRAPH.read_text(encoding="utf-8"))
    if graph["graph_revision"] != 177:
        raise SystemExit("Unexpected continuity graph predecessor revision.")
    if any(node["id"] == NODE_ID for node in graph["nodes"]):
        raise SystemExit("Continuity node already exists.")

    graph["nodes"].append(
        {
            "id": NODE_ID,
            "title": "Raisa Cloud Run Public-HTTPS Development Host Deployment",
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
                            "Create the exact Sydney Docker repository, push the "
                            "closed immutable image, deploy the exact min-zero "
                            "static Cloud Run development service, grant public "
                            "invocation and run post-deployment gates."
                        ),
                        "source": (
                            "docs/raisa-cloud-run-public-https-dev-host-"
                            "deployment-plan.md"
                        ),
                    }
                ],
                "notes": [
                    (
                        "Yuri explicitly authorised the frozen repository, image "
                        "push, service creation, public invocation and verification "
                        "boundary."
                    ),
                    (
                        "The allUsers roles/run.invoker binding failed closed "
                        "under Domain Restricted Sharing and no binding was created."
                    ),
                    (
                        "The documented no-invoker-iam-check alternative was not "
                        "executed because the frozen plan required a user decision "
                        "at organisation-policy conflict."
                    ),
                ],
            },
            "decisions": [
                {
                    "id": "raisa-cloud-run-public-access-mechanism-178",
                    "source": (
                        "docs/raisa-cloud-run-public-https-dev-host-deployment-"
                        "blocked-closeout.md"
                    ),
                    "status": "candidate",
                    "summary": (
                        "Choose whether to disable the Invoker IAM check on the "
                        "exact service or obtain an organisation-policy exception; "
                        "the service remains private meanwhile."
                    ),
                }
            ],
            "claim_scope": [
                (
                    "The exact Docker-format Sydney repository exists and holds "
                    "the accepted closed image at immutable digest "
                    "sha256:6696b3c97682ba8d02d3b18bab3d5d3d131f8c56c613c1adfca32400f94b3f5d."
                ),
                (
                    "The exact Sydney Cloud Run service is ready and private at "
                    "https://raisa-office-web-dev-nnbntbx5yq-ts.a.run.app."
                ),
                (
                    "The final private revision matches the exact digest, runtime "
                    "identity, origin, min-zero/max-one and no-secret/no-volume/"
                    "no-VPC posture."
                ),
                (
                    "Domain Restricted Sharing rejected the allUsers invoker "
                    "binding; public HTTP, browser and Word Online acceptance were "
                    "not run."
                ),
                (
                    "All task-owned local build, image-tag, temporary credential "
                    "and error-file residue was removed."
                ),
            ],
            "contract_evidence": [
                {
                    "contract_id": "combined-patient-practitioner-time-duration-intent",
                    "status": "satisfied",
                    "evidence": [
                        (
                            "orchestration/continuity/"
                            "raisa-cloud-run-public-https-dev-host-deployment/"
                            "partial-deployment-evidence.json"
                        ),
                        "tests/test_raisa_cloud_run_public_https_deployment.py",
                    ],
                    "note": (
                        "The private static deployment contains no appointment "
                        "context, proposal, confirmation or command."
                    ),
                },
                {
                    "contract_id": "committed-reschedule-availability-reconciliation",
                    "status": "satisfied",
                    "evidence": [
                        (
                            "docs/raisa-cloud-run-public-https-dev-host-deployment-"
                            "blocked-closeout.md"
                        ),
                        "tests/test_raisa_cloud_run_public_https_deployment.py",
                    ],
                    "note": (
                        "No backend, database, event, availability or Diary truth "
                        "path was contacted or changed."
                    ),
                },
            ],
            "evidence": {
                "plans": [
                    "docs/raisa-cloud-run-public-https-dev-host-deployment-plan.md",
                    "docs/raisa-cloud-run-public-https-dev-host-operator-packet.md",
                ],
                "findings": [
                    (
                        "orchestration/continuity/"
                        "raisa-cloud-run-public-https-dev-host-deployment/"
                        "partial-deployment-evidence.json"
                    ),
                    (
                        "orchestration/continuity/"
                        "raisa-cloud-run-public-https-dev-host-deployment/"
                        "final-local-residue-evidence.json"
                    ),
                ],
                "closeouts": [
                    (
                        "docs/raisa-cloud-run-public-https-dev-host-deployment-"
                        "blocked-closeout.md"
                    )
                ],
                "acceptances": [
                    (
                        "orchestration/agent_inbox/codex/"
                        "raisa-cloud-run-public-https-dev-host-deployment-sol-"
                        "review.md"
                    )
                ],
                "receipts": [
                    (
                        "orchestration/agent_inbox/codex/"
                        "raisa-cloud-run-public-https-dev-host-deployment-receipt.json"
                    ),
                    (
                        "orchestration/agent_inbox/codex/"
                        "raisa-cloud-run-public-https-dev-host-deployment-"
                        "preacceptance-receipt.json"
                    )
                ],
                "tests": [
                    "tests/test_raisa_cloud_run_public_https_deployment.py"
                ],
            },
            "unresolved_gates": [
                (
                    "Yuri must choose whether to disable the Cloud Run Invoker "
                    "IAM check on the exact service or arrange an organisation-"
                    "policy exception for allUsers."
                ),
                (
                    "Public HTTPS route, browser and Office manifest verification "
                    "remain unexecuted."
                ),
                (
                    "Authenticated Word Online behavior, Office identity and "
                    "clinician-role authorization remain unproven."
                ),
                (
                    "Real, product-derived, patient, health, clinical and "
                    "historical data remain closed."
                ),
                (
                    "Provider, backend, database, microphone, document write, "
                    "production and release remain closed."
                ),
            ],
        }
    )
    graph["graph_revision"] = 178
    graph["updated_at"] = UPDATED_AT
    GRAPH.write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_compass() -> None:
    compass = json.loads(COMPASS.read_text(encoding="utf-8"))
    if compass["map_revision"] != 158 or compass["source_graph_revision"] != 177:
        raise SystemExit("Unexpected Compass predecessor revision.")
    if compass["journey"][-1]["node_id"] != PARENT_ID:
        raise SystemExit("Unexpected Compass journey predecessor.")

    evidence = [
        "docs/raisa-cloud-run-public-https-dev-host-deployment-plan.md",
        (
            "orchestration/continuity/"
            "raisa-cloud-run-public-https-dev-host-deployment/"
            "partial-deployment-evidence.json"
        ),
        (
            "orchestration/continuity/"
            "raisa-cloud-run-public-https-dev-host-deployment/"
            "final-local-residue-evidence.json"
        ),
        (
            "docs/raisa-cloud-run-public-https-dev-host-deployment-blocked-"
            "closeout.md"
        ),
        (
            "orchestration/agent_inbox/codex/"
            "raisa-cloud-run-public-https-dev-host-deployment-sol-acceptance.md"
        ),
    ]
    compass["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": (
                "Private Sydney development host ready; public access policy blocked"
            ),
            "outcome": (
                "The exact repository, immutable image and min-zero private Cloud "
                "Run service are ready with the zero-role runtime identity. Domain "
                "Restricted Sharing rejected the allUsers invoker binding, so the "
                "service remains private and public browser/Word checks did not run."
            ),
            "evidence": evidence,
        }
    )
    compass["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Private Sydney development host ready; public access policy blocked"
        ),
        "why_now": (
            "The APIs and runtime identity were ready and Yuri authorised the exact "
            "repository, image and service deployment. The private service passed "
            "its frozen configuration gates, but the public IAM binding encountered "
            "the operator packet's organisation-policy stop condition."
        ),
        "outcome": (
            "A ready private service exists at the exact hash-based run.app URL "
            "with immutable digest, min zero, max one, zero-role/keyless runtime "
            "identity and no secret, volume or VPC configuration. Public access "
            "and Word Online evidence do not yet exist."
        ),
        "unlocks": [
            (
                "Yuri may explicitly authorise the Google-recommended "
                "no-invoker-iam-check mechanism for this exact service."
            ),
            (
                "Alternatively, an authorised organisation administrator may "
                "create a narrow Domain Restricted Sharing exception."
            ),
            (
                "After one public-access path succeeds, the existing service can "
                "proceed directly to HTTP, browser and Office manifest gates."
            ),
        ],
        "does_not_solve": [
            "Public HTTPS reachability.",
            "Authenticated Word Online interoperability or Office identity.",
            "Clinician-role authorization or production document grants.",
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

    deployment_item = next(
        (
            item
            for item in compass["decision_horizon"]
            if item["id"] == "authorize-raisa-cloud-run-public-https-dev-host-deployment"
        ),
        None,
    )
    if deployment_item is None:
        raise SystemExit("Expected Cloud Run deployment decision is missing.")
    deployment_item.update(
        {
            "status": "blocked",
            "strategic_question": (
                "Should the exact private Raisa Cloud Run development service "
                "disable its Invoker IAM check to become public under Domain "
                "Restricted Sharing?"
            ),
            "why_it_matters": (
                "The repository, image and private service are ready, but effective "
                "Domain Restricted Sharing rejects an allUsers IAM binding. Google "
                "recommends disabling the Invoker IAM check for this case; that "
                "changes the frozen access-control mechanism and requires Yuri's "
                "explicit choice."
            ),
            "prerequisites": [
                (
                    "Obtain Yuri's explicit authority for "
                    "--no-invoker-iam-check on only raisa-office-web-dev in "
                    "bernie-emr4-dev/australia-southeast1, or obtain a narrow "
                    "organisation-policy exception from an authorised operator."
                ),
                (
                    "Retain the exact immutable digest, zero-role runtime identity, "
                    "min-zero/max-one and no-secret/no-VPC/no-volume posture."
                ),
                (
                    "After access changes, rerun public IAM/access, route, browser, "
                    "manifest and cleanup gates before Word Online."
                ),
            ],
            "boundary_changes": [
                "api-change",
                "deployment",
            ],
            "evidence": evidence,
        }
    )
    decision_id = "authorize-raisa-cloud-run-no-invoker-iam-check"
    if not any(item["id"] == decision_id for item in compass["user_owned_decisions"]):
        compass["user_owned_decisions"].insert(
            0,
            {
                "id": decision_id,
                "question": (
                    "Should the exact private Raisa development service disable "
                    "the Cloud Run Invoker IAM check, Google's recommended public "
                    "mechanism when Domain Restricted Sharing blocks allUsers?"
                ),
                "required_before": (
                    "Any unauthenticated request, public browser check or Word "
                    "Online exercise against the deployed service."
                ),
                "evidence": evidence,
            },
        )
    compass["map_limits"].insert(
        0,
        (
            "The deployment descendant proves a ready private Sydney service with "
            "the exact immutable image and bounded runtime posture. It does not "
            "prove public reachability, browser or Word Online behavior. Domain "
            "Restricted Sharing rejected the allUsers binding, and no alternative "
            "access-control mechanism was applied."
        ),
    )
    compass["map_revision"] = 159
    compass["source_graph_revision"] = 178
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
    raise SystemExit(main())
