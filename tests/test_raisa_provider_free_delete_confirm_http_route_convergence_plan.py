"""Plan and reviewer-script tests for the provider-free delete-confirm HTTP route
convergence. Runs with ``--noconftest`` and touches no database.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs" / "raisa-provider-free-delete-confirm-http-route-convergence-plan.md"
THREAT_DELTA = (
    ROOT
    / "docs"
    / "security"
    / "raisa-provider-free-delete-confirm-http-route-convergence-threat-model-delta.md"
)
CONTRACT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-delete-confirm-http-route-convergence"
    / "route-convergence-contract.json"
)
REVIEWER = ROOT / "scripts" / "raisa_provider_free_delete_confirm_http_route_convergence.py"
OPENAPI = ROOT / "docs" / "api-spine" / "openapi" / "appointment-commands.yaml"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_plan_is_frozen_and_lists_five_transition_gaps():
    text = _read_text(PLAN)
    assert "Status: frozen" in text
    for gap in (
        "canonical public-envelope bytes",
        "raisa.delete_proposal_version_binding.v1",
        "compose_product_delete_confirm",
        "canonical_delete_confirm_envelope_bytes",
        "stored_response_bytes",
    ):
        assert gap in text
    assert "delete_proposal_version_binding" in text


def test_threat_delta_pins_five_domains_and_private_byte_boundary():
    text = _read_text(THREAT_DELTA)
    assert "five keys are server-derived" in text
    assert "stored_response_bytes" in text
    assert "never response content" in text
    # The two explicit domain strings live in the frozen contract.
    contract = json.loads(_read_text(CONTRACT))
    assert contract["proposal_contract"]["evidence_secret_domain"] == (
        "emr4.delete-confirm.evidence.v1"
    )
    assert contract["proposal_contract"]["proposal_version_secret_domain"] == (
        "emr4.delete-confirm.proposal-version.v1"
    )


def test_contract_pins_route_and_public_response_contract():
    contract = json.loads(_read_text(CONTRACT))
    assert contract["route_contract"]["canonical_path"] == (
        "/api/v1/appointments/proposals/delete/confirm"
    )
    assert contract["route_contract"]["compatibility_alias"] == (
        "/api/v1/appointments/proposals/delete-confirm"
    )
    assert contract["route_contract"]["alias_hidden_from_openapi"] is True
    assert contract["route_contract"]["single_handler"] == "confirm_delete_proposal_route"
    assert contract["route_contract"]["adapter"] == "compose_product_delete_confirm"
    assert contract["route_contract"]["adapter_call_count"] == 1
    assert contract["proposal_contract"]["binding_schema"] == (
        "raisa.delete_proposal_version_binding.v1"
    )
    assert contract["proposal_contract"]["binding_required_on_confirmation"] is True
    assert contract["public_response"]["serializer"] == "canonical_delete_confirm_envelope_bytes"
    assert contract["public_response"]["private_receipt_may_be_http_content"] is False
    assert "appointment" in contract["public_response"]["forbidden_fields"]
    assert set(contract["scenarios"]) == {f"DHC-S{i:02d}" for i in range(1, 13)}


def test_openapi_uses_dedicated_strict_delete_confirm_response():
    document = yaml.safe_load(_read_text(OPENAPI))
    response_schema = document["paths"]["/appointments/proposals/delete/confirm"][
        "post"
    ]["responses"]["200"]["content"]["application/json"]["schema"]
    assert response_schema == {
        "$ref": "#/components/schemas/AppointmentDeleteConfirmResultEnvelope"
    }

    schemas = document["components"]["schemas"]
    result = schemas["AppointmentDeleteConfirmResultEnvelope"]
    receipt = schemas["AppointmentDeleteConfirmationReceipt"]
    assert result["additionalProperties"] is False
    assert "appointment" not in result["properties"]
    assert receipt["additionalProperties"] is False
    assert receipt["properties"]["waiting_area_id"]["type"] == "null"
    assert receipt["properties"]["warning_codes"]["items"]["enum"] == [
        "waiting_area_cleared"
    ]
    assert receipt["properties"]["warning_codes"]["maxItems"] == 1


def test_reviewer_no_write_returns_zero_and_changes_nothing():
    before_evidence = (
        ROOT
        / "orchestration"
        / "continuity"
        / "raisa-provider-free-delete-confirm-http-route-convergence"
        / "provider-free-route-convergence-evidence.json"
    )
    before_report = (
        ROOT
        / "orchestration"
        / "continuity"
        / "raisa-provider-free-delete-confirm-http-route-convergence"
        / "route-convergence-report.md"
    )
    before_evidence_bytes = before_evidence.read_bytes() if before_evidence.exists() else None
    before_report_bytes = before_report.read_bytes() if before_report.exists() else None

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.raisa_provider_free_delete_confirm_http_route_convergence",
            "--no-write",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "16/16 checks passed" in proc.stdout
    assert "no-write mode: artifacts unchanged" in proc.stdout

    if before_evidence_bytes is None:
        assert not before_evidence.exists()
    else:
        assert before_evidence.read_bytes() == before_evidence_bytes
    if before_report_bytes is None:
        assert not before_report.exists()
    else:
        assert before_report.read_bytes() == before_report_bytes


def test_reviewer_write_generates_owned_artifacts_byte_deterministically():
    proc1 = subprocess.run(
        [sys.executable, "-m", "scripts.raisa_provider_free_delete_confirm_http_route_convergence"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc1.returncode == 0, proc1.stdout + proc1.stderr
    evidence_path = (
        ROOT
        / "orchestration"
        / "continuity"
        / "raisa-provider-free-delete-confirm-http-route-convergence"
        / "provider-free-route-convergence-evidence.json"
    )
    report_path = (
        ROOT
        / "orchestration"
        / "continuity"
        / "raisa-provider-free-delete-confirm-http-route-convergence"
        / "route-convergence-report.md"
    )
    evidence1 = evidence_path.read_bytes()
    report1 = report_path.read_bytes()

    proc2 = subprocess.run(
        [sys.executable, "-m", "scripts.raisa_provider_free_delete_confirm_http_route_convergence"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc2.returncode == 0
    evidence2 = evidence_path.read_bytes()
    report2 = report_path.read_bytes()

    assert evidence1 == evidence2
    assert report1 == report2

    report_text = report1.decode("utf-8")
    assert report_text.startswith("# Provider-free delete-confirm HTTP route convergence report")
    assert "Date: 2026-08-17" in report_text
    assert "Timestamp: 2026-08-17T04:36:29.1514011+10:00" in report_text

    evidence = json.loads(evidence1)
    assert evidence["schema_version"] == "raisa.delete_confirm_http_route_convergence_evidence.v1"
    assert evidence["result"] == "raisa_provider_free_delete_confirm_http_route_convergence_pass"
    assert evidence["summary"]["checks_failed"] == 0
    assert set(evidence["scenario_outcomes"]) == {f"DHC-S{i:02d}" for i in range(1, 13)}
    assert all(value == "passed" for value in evidence["scenario_outcomes"].values())
    assert evidence["hostile_mutations_rejected"] >= 100
    assert evidence["closed_boundaries"]["database_opened"] is False
    assert evidence["closed_boundaries"]["network_opened"] is False
    assert evidence["closed_boundaries"]["sql_executed"] is False
    assert evidence["private_public_byte_separation"] is True
    assert evidence["one_handler"] is True
    assert evidence["one_adapter_call"] is True
    assert evidence["raw_delete_unchanged"] is True
