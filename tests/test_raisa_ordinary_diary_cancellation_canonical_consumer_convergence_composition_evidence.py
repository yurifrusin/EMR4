from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_ROOT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-ordinary-diary-cancellation-canonical-consumer-convergence-composition"
)
SCHEMA = EVIDENCE_ROOT / (
    "ordinary-diary-cancellation-canonical-consumer-convergence-composition-"
    "evidence.schema.json"
)
EVIDENCE = EVIDENCE_ROOT / (
    "ordinary-diary-cancellation-canonical-consumer-convergence-composition-"
    "evidence.json"
)


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_canonical_cancellation_convergence_evidence_is_closed_and_valid() -> None:
    payload = _json(EVIDENCE)
    Draft202012Validator(
        _json(SCHEMA), format_checker=FormatChecker()
    ).validate(payload)

    assert payload["accepted_candidate"] == (
        "bfac65298e1d4aaca85d1c9dcb20329ef298c485"
    )
    assert payload["product_implementation_source"] == (
        "cb6589437bce24c5680c590bc5cf4571435f1a7a"
    )
    assert payload["contract"]["status_or_raw_delete_fallbacks"] == 0
    assert payload["contract"]["appointment_read_model_required"] is False
    assert payload["contract"]["fresh_read_after_every_terminal_or_uncertain_outcome"]
    assert payload["verification"]["combined_browser_tests"] == 170
    assert payload["verification"]["independent_veto"] == "pass"
    assert payload["recovery_provenance"]["incidents"] == [
        "AER-0391",
        "AER-0392",
        "AER-0393",
        "AER-0394",
        "AER-0395",
        "AER-0396",
        "AER-0397",
    ]
    assert set(payload["authority_counts"].values()) == {0}


def test_canonical_cancellation_evidence_labels_interception_and_claim_limit() -> None:
    payload = _json(EVIDENCE)
    assert "route_intercepted_browser" in payload["evidence_modes"]
    assert "live backend/database" in payload["claim_limit"]
    assert "external-adapter" in payload["claim_limit"]
