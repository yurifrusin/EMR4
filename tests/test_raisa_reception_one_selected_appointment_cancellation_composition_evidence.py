from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "orchestration/continuity/raisa-reception-one-selected-appointment-cancellation-composition"
)
SCHEMA = EVIDENCE_ROOT / "selected-appointment-cancellation-composition-evidence.schema.json"
EVIDENCE = EVIDENCE_ROOT / "selected-appointment-cancellation-composition-evidence.json"


def _json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence_is_schema_valid_and_exact_candidate_bound() -> None:
    schema = _json(SCHEMA)
    evidence = _json(EVIDENCE)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(evidence)
    assert evidence["reviewed_candidate"] == (
        "856ebc3d832d5b64ce65c2e0732eaa63d926c600"
    )
    assert evidence["planning_baseline"] == (
        "36edc1e5b36b83a54f6af28c9519853290e4189b"
    )


def test_evidence_freezes_adapter_freedom_below_deterministic_meaning() -> None:
    projection = _json(EVIDENCE)["projection_adapter_contract"]
    assert projection["raisa_output"] == (
        "typed_minimized_projection_and_action_envelope_not_raw_rows"
    )
    assert projection["first_party_client"] == "reference_rendering"
    assert set(projection["adapter_freedom"]) == {
        "layout",
        "modality",
        "visual_hierarchy",
        "bounded_copy",
    }
    assert "action_identity_and_consequence" in projection["immutable_semantics"]
    assert "receipt_and_fresh_reconciliation" in projection["immutable_semantics"]


def test_evidence_records_one_canonical_command_path_and_closed_authority() -> None:
    evidence = _json(EVIDENCE)
    assert evidence["command_contract"] == {
        "graphql": "read_only_unchanged",
        "proposal": "post_appointments_proposals_delete_appointment_id_only",
        "confirm": "post_appointments_proposals_delete_confirm_canonical_only",
        "explicit_staff_confirmation": True,
        "status_cancel_fallbacks": 0,
        "raw_delete_fallbacks": 0,
        "new_routes": 0,
        "new_schemas": 0,
        "optimistic_mutations": 0,
    }
    assert not any(evidence["authority_counts"].values())


def test_evidence_covers_fail_closed_reconciliation_and_responsive_rendering() -> None:
    interaction = _json(EVIDENCE)["interaction_acceptance"]
    assert interaction["viewports"] == ["1280x720", "768x1024", "390x844"]
    assert interaction["minimum_target_css_pixels"] >= 44
    assert interaction["horizontal_overflow"] is False
    assert interaction["console_errors"] == 0
    for outcome in (
        "safe_commit",
        "staff_cancel",
        "blocked",
        "stale_or_authority_denial",
        "malformed_public_envelope",
        "interruption",
    ):
        assert interaction[outcome].startswith("pass")
