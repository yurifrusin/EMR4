"""Plan-contract freeze tests for the delete-confirm route-mounting readiness
review.

These tests read only the four freeze artifacts:
- docs/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-plan.md
- docs/security/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-threat-model-delta.md
- orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-contract.json
- orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-contract.schema.json

They do not import ``app`` and do not execute any route, database or provider
surface.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PLAN = ROOT / "docs/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-plan.md"
THREAT_DELTA = (
    ROOT
    / "docs/security/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review-threat-model-delta.md"
)
CONTRACT_DIR = (
    ROOT
    / "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review"
)
CONTRACT = CONTRACT_DIR / "route-mounting-readiness-review-contract.json"
SCHEMA = CONTRACT_DIR / "route-mounting-readiness-review-contract.schema.json"

EXPECTED_OWNED_OUTPUTS = {
    "scripts/raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review.py",
    "tests/test_raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review.py",
    "tests/test_raisa_provider_free_read_only_delete_confirm_route_mounting_readiness_review_plan.py",
    "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/provider-free-read-only-evidence.json",
    "orchestration/continuity/raisa-provider-free-read-only-delete-confirm-route-mounting-readiness-review/route-mounting-readiness-review-report.md",
}

EXPECTED_DIMENSIONS = {
    1: ("literal_mounting", "satisfied"),
    2: ("canonical_identity_and_alias", "route_transition_gap"),
    3: ("proposal_version_binding_carriage", "route_transition_gap"),
    4: ("server_authority_and_session_ingress", "route_transition_gap"),
    5: ("physical_seam_composition", "satisfied"),
    6: ("locked_current_truth_readmission", "satisfied"),
    7: ("atomic_effect_audit_private_receipt", "satisfied"),
    8: ("public_response_schema", "route_transition_gap"),
    9: ("canonical_public_byte_delivery", "route_transition_gap"),
    10: ("closed_outcome_http_mapping", "satisfied"),
    11: ("raw_delete_isolation", "satisfied"),
    12: ("accepted_postgresql_foundation", "satisfied"),
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _plan_source_rows(text: str):
    rows = re.findall(r"^\| `([0-9a-f]{64})` \| `([^`]+)` \|\s*$", text, flags=re.MULTILINE)
    return [(digest, path) for digest, path in rows]


def _plan_owned_outputs(text: str) -> set[str]:
    section = text.split("## Exact owned outputs", 1)[1]
    section = section.split("##", 1)[0]
    return {m.group(1) for m in re.finditer(r"`([^`]+\.(?:py|json|md))`", section)}


def test_freeze_artifacts_exist():
    for path in (PLAN, THREAT_DELTA, CONTRACT, SCHEMA):
        assert path.exists(), f"missing freeze artifact: {path}"
        assert path.read_text(encoding="utf-8"), f"empty freeze artifact: {path}"


def test_contract_has_exactly_23_inputs():
    contract = json.loads(_read_text(CONTRACT))
    assert len(contract["inputs"]) == 23
    assert all(set(item) == {"path", "sha256"} for item in contract["inputs"])
    assert all(re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) for item in contract["inputs"])


def test_contract_schema_version_and_hash_mode():
    contract = json.loads(_read_text(CONTRACT))
    assert contract["schema_version"] == "raisa.delete_confirm_route_mounting_readiness_review_contract.v1"
    assert contract["input_hash_mode"] == "strict_utf8_canonical_lf_reject_bare_cr_sha256"
    assert re.fullmatch(r"[0-9a-f]{40}", contract["source_head"])


def test_contract_matches_plan_source_table():
    plan_text = _read_text(PLAN)
    plan_rows = _plan_source_rows(plan_text)
    assert len(plan_rows) == 23, f"expected 23 plan rows, got {len(plan_rows)}"
    contract = json.loads(_read_text(CONTRACT))
    contract_rows = [(item["sha256"], item["path"]) for item in contract["inputs"]]
    assert contract_rows == plan_rows


def test_contract_expected_matrix_and_verdict():
    contract = json.loads(_read_text(CONTRACT))
    acceptance = contract["acceptance"]
    assert acceptance["expected_counts"] == {
        "satisfied": 7,
        "route_transition_gap": 5,
        "blocking_gap": 0,
    }
    assert acceptance["expected_verdict"] == "ready_for_bounded_route_convergence_candidate"
    assert acceptance["minimum_hostile_mutations"] >= 72
    assert acceptance["require_exact_dimension_order"] is True
    assert acceptance["require_exact_source_citations"] is True
    assert acceptance["require_private_public_byte_separation"] is True
    assert acceptance["require_no_app_import"] is True


def test_contract_dimensions_match_plan():
    contract = json.loads(_read_text(CONTRACT))
    dimensions = contract["dimensions"]
    assert len(dimensions) == 12
    for dim in dimensions:
        assert dim["order"] in EXPECTED_DIMENSIONS
        expected_id, expected_classification = EXPECTED_DIMENSIONS[dim["order"]]
        assert dim["id"] == expected_id
        assert dim["expected_classification"] == expected_classification


def test_contract_classifications_and_verdict_rules():
    contract = json.loads(_read_text(CONTRACT))
    assert contract["classifications"] == ["satisfied", "route_transition_gap", "blocking_gap"]
    assert contract["verdict_rules"] == {
        "any_blocking_gap": "route_mounting_not_ready",
        "no_blocker_with_transition_gap": "ready_for_bounded_route_convergence_candidate",
        "all_satisfied": "route_convergence_already_complete",
    }


def test_contract_conforms_to_schema_shape():
    contract = json.loads(_read_text(CONTRACT))
    schema = json.loads(_read_text(SCHEMA))
    assert schema["properties"]["schema_version"]["const"] == contract["schema_version"]
    assert schema["properties"]["input_hash_mode"]["const"] == contract["input_hash_mode"]
    assert schema["properties"]["inputs"]["minItems"] == 23
    assert schema["properties"]["inputs"]["maxItems"] == 23
    assert schema["properties"]["dimensions"]["minItems"] == 12
    assert schema["properties"]["dimensions"]["maxItems"] == 12
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "schema_version",
        "source_head",
        "input_hash_mode",
        "inputs",
        "classifications",
        "verdict_rules",
        "dimensions",
        "acceptance",
        "forbidden_surfaces",
    }


def test_plan_lists_exact_owned_outputs():
    plan_text = _read_text(PLAN)
    owned = _plan_owned_outputs(plan_text)
    assert EXPECTED_OWNED_OUTPUTS <= owned


def test_threat_delta_controls():
    text = _read_text(THREAT_DELTA)
    required_controls = (
        "Private receipt bytes are returned as the public HTTP body",
        "proposal-version binding as opaque server-minted carriage",
        "canonical `/proposals/delete/confirm` plus hidden `/proposals/delete-confirm` decorators",
        "distinct command-session factory",
        "minimal receipt envelope",
        "strict text/hash inspection only, deny `app` imports",
    )
    for control in required_controls:
        assert control in text, f"threat delta missing control: {control}"
    assert "implementation_authorized: false" in text


def test_plan_expected_matrix_prose():
    text = re.sub(r"\s+", " ", _read_text(PLAN))
    assert "seven satisfied dimensions, five route transition gaps and no blocker" in text
    assert "canonical public bytes" in text
    assert "validated minimal public projection" in text
    assert "route_mounting_not_ready" in text
    assert "ready_for_bounded_route_convergence_candidate" in text


def test_plan_forbids_route_and_database_surfaces():
    text = _read_text(PLAN)
    assert "No route edit/mount/call" in text
    assert "database/source watcher/Docker/SQL access" in text
