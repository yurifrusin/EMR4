from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPASS = ROOT / "orchestration" / "continuity" / "emr4-compass.json"
NODE_ID = "clinician-one-readonly-document-context"


def main() -> int:
    data = json.loads(COMPASS.read_text(encoding="utf-8"))
    if data["map_revision"] != 154 or data["source_graph_revision"] != 173:
        raise SystemExit("Unexpected Compass predecessor revision.")
    if data["journey"][-1]["node_id"] != NODE_ID:
        raise SystemExit("Unexpected Compass journey predecessor.")

    evidence = [
        "docs/raisa-clinician-one-readonly-document-context-plan.md",
        "docs/security/raisa-clinician-one-readonly-document-context-threat-model-delta.md",
        "orchestration/continuity/clinician-one-readonly-document-context/document-context-request.schema.json",
        "orchestration/continuity/clinician-one-readonly-document-context/document-context-response.schema.json",
        "orchestration/continuity/clinician-one-readonly-document-context/adapter-evidence.json",
        "orchestration/continuity/clinician-one-readonly-document-context/browser-acceptance-evidence.json",
        "orchestration/continuity/clinician-one-readonly-document-context/final-residue-evidence.json",
        "docs/raisa-clinician-one-readonly-document-context-closeout.md",
        "orchestration/agent_inbox/codex/clinician-one-readonly-document-context-sol-acceptance.md",
        "tests/test_clinician_one_readonly_document_context.py",
    ]
    data["journey"][-1] = {
        "node_id": NODE_ID,
        "lineage_parent": "raisa-dual-host-foundation",
        "strategic_role": (
            "Accepted provider-free single-use Clinician One "
            "current-selection context adapter"
        ),
        "outcome": (
            "One exact local authored-synthetic fixture grant can read "
            "only the current Word selection once and emit a typed "
            "non-authoritative current_consult_note frame. Desktop and "
            "web fixtures pass, replay and bounded failures stop closed, "
            "and the ordinary-browser card remains disabled without Word."
        ),
        "evidence": evidence,
    }
    data["current_position"] = {
        "node_id": NODE_ID,
        "strategic_role": (
            "Accepted provider-free single-use Clinician One "
            "current-selection context adapter"
        ),
        "why_now": (
            "The shared Raisa host foundation separated technical capability "
            "from authority; the next smallest useful clinician operation was "
            "therefore one explicit, source-labelled and non-authoritative "
            "read of doctor-selected authored-synthetic text."
        ),
        "outcome": (
            "Clinician One now has a closed request/response adapter that "
            "reads only the current selection under an exact local synthetic "
            "grant, rejects instead of truncating, prevents replay reads and "
            "renders counts and provenance only. It opens no provider, "
            "backend, patient-context, microphone, command or write path."
        ),
        "unlocks": [
            (
                "One supervised provider-free installed-Word exercise in a "
                "task-created authored-synthetic blank document."
            ),
            (
                "Later product-authenticated document grants without changing "
                "the selection-only context-frame contract."
            ),
            (
                "A future Access AI handoff that can receive only a separately "
                "admitted minimal context frame under fresh provider authority."
            ),
        ],
        "does_not_solve": [
            "Real installed-Word selection semantics or Office identity.",
            "Authenticated Word Online interoperability or tenant policy.",
            (
                "Safety for real, product-derived, patient, health, clinical "
                "or historical text."
            ),
            "Clinician role enforcement or production document authorization.",
            (
                "Provider interpretation, microphone capture, clinical "
                "finalization, document write or any backend command."
            ),
            "Production, deployment, release or public-brand adoption.",
        ],
        "evidence": evidence,
    }
    data["map_limits"][0] = (
        "The accepted Clinician One document-context descendant proves "
        "only dependency-injected desktop/web current-selection fixtures "
        "and an ordinary-browser fail-closed card. It does not prove real "
        "Word, authenticated Word Online, Office identity, clinician-role "
        "authorization, clinical-data safety, provider readiness, "
        "production, deployment or release."
    )
    data["map_revision"] = 155
    data["source_graph_revision"] = 174
    data["updated_at"] = "2026-07-31T07:20:00Z"
    COMPASS.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
