import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-sdl-alignment-evidence.json"
EVIDENCE_MD = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-sdl-alignment-evidence.md"
SDL = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"


def _payload() -> dict:
    return json.loads(EVIDENCE.read_text(encoding="utf-8"))


def _type_body(type_name: str) -> str:
    text = SDL.read_text(encoding="utf-8")
    match = re.search(rf"type {type_name}\s*\{{(?P<body>.*?)\n\}}", text, re.S)
    assert match, f"Missing SDL type {type_name}"
    return match.group("body")


def test_sdl_alignment_evidence_shape_is_specific():
    payload = _payload()

    assert payload["schema_version"] == "api_spine.practitioner_directory_graphql_sdl_alignment_evidence.v1"
    assert payload["sprint"] == 266
    assert payload["decision"] == "graphql_sdl_aligned_runtime_resolver_still_blocked"
    assert payload["target_sdl"] == "docs/api-spine/graphql/appointment-diary-read.graphql"
    assert payload["runtime_code_added"] is False


def test_evidence_matches_current_sdl_shape():
    payload = _payload()
    practice = _type_body("Practice")
    practitioner = _type_body("Practitioner")
    brief = _type_body("PracticeLocationBrief")

    assert (
        "practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0): "
        "[Practitioner!]!"
    ) in practice
    assert "defaultLocation: PracticeLocationBrief" in practitioner
    assert {line.strip().split(":", 1)[0] for line in brief.splitlines() if ":" in line} == {
        "id",
        "name",
    }
    assert payload["changes"]["practice_location_brief_fields"] == ["id", "name"]
    assert payload["changes"]["practitioner_default_location_type"] == "PracticeLocationBrief"


def test_evidence_keeps_runtime_and_adjacent_gates_false():
    payload = _payload()

    assert all(value is False for value in payload["must_remain_false"].values())
    assert payload["resolved_former_drift"] == {
        "default_location_shape_status": "sdl_aligned_to_brief_shape",
        "graphql_pagination_shape_status": "sdl_aligned_with_limit_offset",
    }
    assert payload["next_allowed_step"] == (
        "practitioner_directory_graphql_runtime_gate_or_resolver_approval_packet"
    )


def test_markdown_records_no_runtime_readiness_claim():
    text = " ".join(EVIDENCE_MD.read_text(encoding="utf-8").split())

    assert "non-runtime GraphQL SDL" in text
    assert "does not add a GraphQL runtime dependency" in text
    assert "GraphQL readiness remains false" in text
