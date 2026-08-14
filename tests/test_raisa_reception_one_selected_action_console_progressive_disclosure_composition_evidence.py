from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
CONTINUITY = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-reception-one-selected-action-console-progressive-disclosure-composition"
)
EVIDENCE = CONTINUITY / "selected-action-console-composition-evidence.json"
SCHEMA = CONTINUITY / "selected-action-console-composition-evidence.schema.json"
META = ROOT / "docs" / "diary" / "meta-grid.js"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_selected_action_console_evidence_is_schema_valid() -> None:
    schema = _json(SCHEMA)
    evidence = _json(EVIDENCE)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER).validate(
        evidence
    )


def test_evidence_binds_zero_or_one_editor_and_inert_multi_field_intent() -> None:
    evidence = _json(EVIDENCE)
    presentation = evidence["presentation_contract"]
    assert presentation["states"] == [None, "status", "time", "duration", "practitioner"]
    assert presentation["initial_field_editors"] == 0
    assert presentation["maximum_field_editors"] == 1
    assert presentation["palette_routes"] == 0
    assert presentation["automatic_command_sequence"] is False
    assert presentation["compound_update_claim"] is False


def test_palette_activation_slice_contains_no_command_or_route_marker() -> None:
    source = META.read_text(encoding="utf-8")
    activation = source[
        source.index("function activateSelectedAction") : source.index(
            "function statusActionMessage"
        )
    ]
    for marker in (
        "apiFetch(",
        "fetch(",
        "/appointments/proposals/",
        "confirm_endpoint",
        "Idempotency-Key",
    ):
        assert marker not in activation
    for forbidden in (
        "executorMap",
        "compoundDraft",
        "multiFieldDraft",
        "executeMany",
        "sequentialRun",
    ):
        assert forbidden not in source


def test_authority_surfaces_are_blob_identical_to_planning_baseline() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["unchanged_authority_blobs"] == {
        "docs/diary/diary.js": "789c5e43078bdc08c7e060938dda606b4b98d199",
        "app/routers/appointments.py": "ccae18334f82fc29822c1e32f0d99585cf850657",
        "docs/api-spine/openapi/appointment-commands.yaml": (
            "42e24524e069fe12a15911cee98f9df22f0d51fb"
        ),
    }


def test_evidence_claim_and_counts_remain_bounded() -> None:
    evidence = _json(EVIDENCE)
    verification = evidence["verification"]
    assert verification == {
        "new_console_cases": 23,
        "existing_field_cases": 49,
        "two_projection_parity_cases": 1,
        "broader_packet": 167,
        "canonical_fast": 196,
        "maintained_python_sources": 209,
        "independent_veto": 167,
        "javascript_syntax": "pass",
        "ruff": "pass",
        "git_whitespace": "pass",
    }
    claim = evidence["claim_limit"].lower()
    for phrase in (
        "route-intercepted",
        "does not prove live backend/database",
        "patient-data",
        "atomic compound-update",
    ):
        assert phrase in claim
