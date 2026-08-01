from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scripts import (
    ariadne_vertex_sydney_gemini_25_postfailure_diagnostic as diagnostic,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-vertex-sydney-gemini-25"
    / "postfailure-provider-blocked-diagnostic-evidence.json"
)
AUDIT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-vertex-sydney-gemini-25"
    / "postfailure-provider-blocked-diagnostic-external-audit.json"
)


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def test_diagnostic_reconstructs_exact_historical_request_without_network() -> None:
    evidence = diagnostic.build_diagnostic_evidence()

    assert evidence["historical_binding"]["request_hash_exact"] is True
    assert (
        evidence["historical_binding"]["reconstructed_request_hash"]
        == "sha256:6710af194aba6a2731008475e5509fa27ba12c8b58e995e1952faa036ecba61c"
    )
    assert evidence["authority_accounting"]["provider_calls"] == 0
    assert evidence["authority_accounting"]["credential_reads_or_refreshes"] == 0
    assert evidence["authority_accounting"]["cloud_control_reads"] == 0
    assert evidence["authority_accounting"]["prompt_transmissions"] == 0


def test_numeric_enum_is_a_proved_deterministic_vertex_contract_defect() -> None:
    evidence = diagnostic.build_diagnostic_evidence()
    findings = evidence["deterministic_findings"]

    assert evidence["result"].endswith("_pass")
    assert len(findings) == 1
    assert findings[0] == {
        "finding_id": "vertex_schema_enum_member_not_string",
        "field_path": (
            "generationConfig.responseSchema.properties.total_tiles.enum[0]"
        ),
        "actual_json_type": "integer",
        "required_json_type": "string",
        "official_contract": "Schema.enum[] is repeated string",
        "installed_proto_field_type": "TYPE_STRING",
        "installed_proto_repeated": True,
        "original_full_request_local_proto_parse": "failed",
        "single_field_type_counterfactual_full_local_proto_parse": "passed",
        "classification": "proved_deterministic_request_contract_defect",
    }
    assert evidence["disposition"].endswith("diagnosis_only_no_retry_authority")


def test_diagnostic_evidence_retains_no_prompt_or_provider_message() -> None:
    evidence = diagnostic.build_diagnostic_evidence()
    serialized = json.dumps(evidence, ensure_ascii=False)

    assert "Project Lark" not in serialized
    assert "fact_alpha" not in serialized
    assert "fact_beta" not in serialized
    assert "provider_diagnostic_redacted" not in serialized
    assert evidence["request_structure"]["raw_prompt_retained"] is False
    assert evidence["historical_binding"]["historical_artifacts_modified"] is False
    assert evidence["authority_accounting"]["request_constructor_modified"] is False
    assert evidence["authority_accounting"]["retry_or_fallback_performed"] is False


def test_persisted_diagnostic_evidence_matches_the_pure_local_builder() -> None:
    persisted = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))

    assert persisted == diagnostic.build_diagnostic_evidence()


def test_external_audit_binds_the_diagnosis_without_retry_authority() -> None:
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))

    assert audit["result"] == (
        "ariadne_vertex_sydney_gemini_25_postfailure_external_audit_pass"
    )
    assert audit["diagnostic_result"] == (
        "ariadne_vertex_sydney_gemini_25_postfailure_diagnostic_pass"
    )
    assert audit["artifact_hashes"]["diagnostic_evidence"] == _sha256(
        EVIDENCE_PATH
    )
    assert audit["verified"]["exact_historical_request_hash_reconstructed"] is True
    assert audit["verified"]["original_full_local_protobuf_parse"] == "failed"
    assert audit["verified"]["single_field_counterfactual_local_parse"] == "passed"
    assert audit["authority_accounting"]["provider_calls"] == 0
    assert audit["authority_accounting"]["credential_operations"] == 0
    assert audit["authority_accounting"]["request_constructor_modified"] is False
    assert audit["authority_accounting"]["retry_authorized"] is False
