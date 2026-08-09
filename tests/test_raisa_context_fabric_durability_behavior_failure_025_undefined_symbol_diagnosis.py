from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import (
    raisa_context_fabric_durability_behavior_failure_024_undefined_symbol_diagnosis as prior,
)
from scripts import (
    raisa_context_fabric_durability_behavior_failure_025_undefined_symbol_diagnosis as diagnosis,
)


ROOT = Path(__file__).resolve().parents[1]
FAILURE = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-disposable-postgresql-durability-behavior-transaction-rehearsal"
    / "provider-free-behavior-transaction-failure-evidence-025.json"
)
MUTABLE = FAILURE.with_name("provider-free-behavior-transaction-evidence.json")
RECEIPT = (
    ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "raisa-context-fabric-durability-behavior-failure-025-undefined-symbol-diagnosis-receipt.json"
)


def test_failure_025_is_preserved_byte_identically() -> None:
    failure_bytes = FAILURE.read_bytes()
    if MUTABLE.exists():
        mutable_bytes = MUTABLE.read_bytes()
        mutable_payload = json.loads(mutable_bytes)
        if mutable_payload.get("attempt_id") == diagnosis.PARENT_ATTEMPT_ID:
            assert failure_bytes == mutable_bytes
    assert hashlib.sha256(failure_bytes).hexdigest() == (
        diagnosis.PARENT_EVIDENCE_SHA256.removeprefix("sha256:")
    )
    payload = json.loads(FAILURE.read_text(encoding="utf-8"))
    assert payload["attempt_id"] == diagnosis.PARENT_ATTEMPT_ID
    assert payload["environment"]["failure"] == {
        "code": "unexpected_rejection",
        "detail_digest": "sha256:7c02450d2309736e88b3191a8618f98fc5cad1a95ca672cb0f551d2cde529216",
        "scenario_id": "BTR-E02",
        "sqlstate": "42883",
        "stage": "scenario",
    }
    assert payload["cleanup"]["status"] == "cleanup_verified"
    assert payload["cleanup"]["absence_verified"] is True


def test_diagnosis_reuses_only_bounded_prior_capture_primitives() -> None:
    assert diagnosis.prior is prior
    assert diagnosis.EXPECTED_REPAIRED_ABSENCE == ("pg_catalog.int4_times_interval")


def test_durable_diagnosis_binds_failure_and_releases_only_bounded_symbol() -> None:
    payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert payload["status"] == ("undefined_symbol_diagnosis_complete_cleanup_verified")
    assert payload["parent_failure"] == {
        "evidence_sha256": diagnosis.PARENT_EVIDENCE_SHA256,
        "internal_attempt_id": diagnosis.PARENT_ATTEMPT_ID,
        "run_sequence": 25,
    }
    assert payload["diagnosis_runtime"]["raw_error_persisted"] is False
    assert payload["diagnosis_runtime"]["cleanup_absence_verified"] is True
    assert payload["observation"]["raw_message_symbol_id"] == (
        "repository_function::pg_catalog.min"
    )
    assert payload["observation"]["known_absent_but_not_executed"] == (
        diagnosis.EXPECTED_REPAIRED_ABSENCE
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (
            b"ERROR:  42883: function pg_catalog.jsonb_build_object(text, text) does not exist\n",
            "pg_catalog.jsonb_build_object",
        ),
        (
            b"ERROR:  42883: function pg_catalog.to_char(timestamp with time zone, unknown) does not exist\n",
            "pg_catalog.to_char",
        ),
    ],
)
def test_prior_classifier_admits_only_fixed_safe_symbols(
    raw: bytes, expected: str
) -> None:
    assert prior.classify_undefined_symbol(raw) == expected


def test_raw_postgresql_text_is_not_part_of_durable_shape() -> None:
    source = (ROOT / "scripts" / diagnosis.__name__.split(".")[-1]).with_suffix(".py")
    text = source.read_text(encoding="utf-8")
    assert '"raw_error_persisted": False' in text
    assert '"raw_message_symbol_id": raw_symbol' in text
    assert '"raw_error"' not in text


def test_repository_bounded_classifier_releases_only_known_call_name() -> None:
    raw = (
        b"ERROR:  42883: function emr4_context_fabric.fixed_projection(uuid) "
        b"does not exist\n"
    )
    symbol = diagnosis.classify_repository_bounded_symbol(
        raw,
        target_sql=b"SELECT emr4_context_fabric.fixed_projection('x');",
        artifact=b"",
    )
    assert symbol == ("repository_function::emr4_context_fabric.fixed_projection")


def test_repository_bounded_classifier_releases_only_safe_type_operator() -> None:
    raw = b"ERROR:  42883: operator does not exist: xid = xid8\n"
    symbol = diagnosis.classify_repository_bounded_symbol(
        raw, target_sql=b"SELECT 1;", artifact=b""
    )
    assert symbol == "postgresql_operator::xid = xid8"


def test_repository_bounded_classifier_rejects_unrelated_function() -> None:
    raw = b"ERROR:  42883: function unrelated.secret(text) does not exist\n"
    with pytest.raises(RuntimeError, match="single_repository_bounded_symbol_missing"):
        diagnosis.classify_repository_bounded_symbol(
            raw, target_sql=b"SELECT 1;", artifact=b""
        )
