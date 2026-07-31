from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "raisa-cloud-run-public-https-dev-host-readiness"
PARENT_ID = "clinician-one-word-desktop-selection-check"


def main() -> int:
    data = json.loads(COMPASS.read_text(encoding="utf-8"))
    if data["map_revision"] != 156 or data["source_graph_revision"] != 175:
        raise SystemExit("Unexpected Compass predecessor revision.")
    if data["journey"][-1]["node_id"] != PARENT_ID:
        raise SystemExit("Unexpected Compass journey predecessor.")

    evidence = [
        "docs/raisa-cloud-run-public-https-dev-host-readiness-plan.md",
        "docs/security/raisa-cloud-run-public-https-dev-host-readiness-threat-model-delta.md",
        "deploy/raisa-office-web-dev/Dockerfile",
        "deploy/raisa-office-web-dev/server.mjs",
        "deploy/raisa-office-web-dev/manifest-template.xml",
        "scripts/prepare_raisa_office_web_dev_context.py",
        "orchestration/continuity/raisa-cloud-run-public-https-dev-host-readiness/local-container-browser-evidence.json",
        "orchestration/continuity/raisa-cloud-run-public-https-dev-host-readiness/final-residue-evidence.json",
        "docs/raisa-cloud-run-public-https-dev-host-operator-packet.md",
        "docs/raisa-cloud-run-public-https-dev-host-readiness-closeout.md",
        "orchestration/agent_inbox/codex/raisa-cloud-run-public-https-dev-host-readiness-sol-acceptance.md",
        "tests/test_raisa_office_web_dev_context.py",
    ]
    data["journey"].append(
        {
            "node_id": NODE_ID,
            "lineage_parent": PARENT_ID,
            "strategic_role": (
                "Accepted repository-local synthetic-only Cloud Run public-host readiness"
            ),
            "outcome": (
                "A deterministic closed context now builds and locally verifies "
                "a non-root, read-only Cloud Run-compatible static taskpane and "
                "Diary host with an exact origin-bound zero-authority policy and "
                "ReadDocument manifest. No cloud resource, IAM state, image push "
                "or deployment occurred."
            ),
            "evidence": evidence,
        }
    )
    data["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Accepted repository-local synthetic-only Cloud Run public-host readiness"
        ),
        "why_now": (
            "The installed-Word selection check passed and the remaining Word "
            "Online blocker was a non-loopback public HTTPS host, so the next "
            "smallest safe step was to prepare and verify that host locally "
            "before authorising external state."
        ),
        "outcome": (
            "The compiled taskpane and required Diary development assets now "
            "have a closed Cloud Run-compatible image, exact hosted policy, "
            "valid ReadDocument manifest template and operator packet. Local "
            "container, browser, Office manifest and inherited API Spine gates "
            "pass; all task residue is absent."
        ),
        "unlocks": [
            (
                "A separately authorised read-only Google Cloud entitlement "
                "preflight for the frozen project, Sydney region and resources."
            ),
            (
                "A later explicitly authorised minimal Artifact Registry, "
                "runtime identity and public Cloud Run development deployment."
            ),
            (
                "After deployment verification, one supervised authenticated "
                "Word Online authored-synthetic check."
            ),
        ],
        "does_not_solve": [
            "Cloud Run or Artifact Registry enablement, entitlement or deployment.",
            "Public IAM or organisation-policy compatibility.",
            "Authenticated Word Online interoperability or Office identity.",
            "Clinician-role authorization or production document grants.",
            (
                "Safety for real, product-derived, patient, health, clinical "
                "or historical text."
            ),
            (
                "Microsoft or Google physical or sovereign processing location."
            ),
            "Provider, backend, database, microphone, command or document write.",
            "Production or release readiness.",
        ],
        "evidence": evidence,
    }
    data["decision_horizon"].insert(
        0,
        {
            "id": "authorize-raisa-cloud-run-public-https-dev-host-deployment",
            "title": "Raisa public-HTTPS development host external creation",
            "status": "candidate",
            "strategic_question": (
                "Should an authorised operator create and deploy the frozen "
                "synthetic-only Sydney Cloud Run development host?"
            ),
            "why_it_matters": (
                "Word Online cannot load the strict loopback taskpane. The "
                "repository-local package is ready, but API enablement, a "
                "dedicated runtime identity, Artifact Registry, public IAM, "
                "image push and Cloud Run deployment would change external state."
            ),
            "prerequisites": [
                (
                    "Run the operator packet's read-only entitlement and "
                    "existing-resource preflight."
                ),
                (
                    "Obtain explicit authority for each missing API or frozen "
                    "resource before creating or enabling it."
                ),
                (
                    "Use project bernie-emr4-dev, region australia-southeast1, "
                    "service raisa-office-web-dev and a dedicated runtime "
                    "identity with no project role."
                ),
                (
                    "Keep authored-synthetic, backend-free, provider-free, "
                    "credential-free, no-write and non-production boundaries."
                ),
                (
                    "Deploy an immutable digest with min zero, max one and no "
                    "secret, VPC, volume or custom domain."
                ),
            ],
            "boundary_changes": [
                "api-change",
                "deployment",
            ],
            "evidence": [
                "docs/raisa-cloud-run-public-https-dev-host-operator-packet.md",
                "docs/raisa-cloud-run-public-https-dev-host-readiness-closeout.md",
                "orchestration/continuity/raisa-cloud-run-public-https-dev-host-readiness/local-container-browser-evidence.json",
            ],
        },
    )
    data["map_limits"].insert(
        0,
        (
            "The accepted Cloud Run public-host readiness descendant proves a "
            "local deterministic synthetic-only static image, exact origin-bound "
            "zero-authority policy, rendered card and valid ReadDocument manifest "
            "shape. It does not prove cloud entitlement, deployment, public IAM, "
            "authenticated Word Online behavior, Office identity, real-data "
            "safety, processing geography, production or release readiness."
        ),
    )
    data["map_revision"] = 157
    data["source_graph_revision"] = 176
    data["updated_at"] = "2026-07-31T07:00:00Z"
    COMPASS.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
