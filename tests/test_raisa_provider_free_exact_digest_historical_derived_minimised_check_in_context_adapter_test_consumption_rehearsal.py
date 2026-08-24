from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from orchestration_harness import historical_diary_first_use_candidate_gate as gate
from orchestration_harness import (
    historical_diary_check_in_adapter_test_consumption as consumption,
)


PLAN = Path(
    "docs/raisa-provider-free-exact-digest-historical-derived-minimised-check-in-"
    "context-adapter-test-consumption-rehearsal-plan.md"
)
THREAT = Path(
    "docs/security/raisa-provider-free-exact-digest-historical-derived-minimised-"
    "check-in-context-adapter-test-consumption-rehearsal-threat-model-delta.md"
)
REAL_FIXTURE_FRAGMENT = (
    "local_data/historical-diary-trove/derived-scenarios/"
    "2026-08-24-first-use-check-in-context-v1/scenario.json"
)


def _candidate() -> gate.CandidatePayload:
    events = (
        ("scheduled_slot_present", 0),
        ("scheduled_slot_added", 5),
        ("scheduled_slot_present", 5),
        ("scheduled_slot_added", 12),
        ("scheduled_slot_present", 19),
        ("scheduled_slot_added", 19),
    )
    return gate.CandidatePayload(
        events=tuple(
            gate.StructuralEvent(
                event_kind=kind,
                relative_minute=minute,
                synthetic_subject_slot=0,
                resource_slot=0,
            )
            for kind, minute in events
        )
    )


def _bytes(candidate: gate.CandidatePayload | None = None) -> bytes:
    value = (candidate or _candidate()).model_dump(mode="json")
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _paths(tmp_path: Path, fixture_bytes: bytes) -> consumption.ConsumptionPaths:
    fixture = tmp_path / "ignored" / "scenario.json"
    fixture.parent.mkdir(parents=True)
    fixture.write_bytes(fixture_bytes)
    return consumption.ConsumptionPaths(
        fixture=fixture,
        control=fixture.parent / "adapter-test-consumption-control.json",
        result=tmp_path / "continuity" / "occupied-result.json",
        successor_contract=tmp_path / "successor.json",
        subgate_contract=tmp_path / "subgate.json",
        latch=tmp_path / "latch.json",
    )


def _contract(fixture_bytes: bytes) -> consumption.ConsumptionContract:
    return consumption.ConsumptionContract(
        fixture_sha256=hashlib.sha256(fixture_bytes).hexdigest(),
        expected_utility=dict(consumption.EXPECTED_UTILITY),
    )


def _prepared_control(candidate_source: str, *, state: str = "prepared") -> dict:
    return consumption._control(
        state=state,
        candidate_source=candidate_source,
        logical_read_count=0 if state == "prepared" else 1,
    )


def _bypass_public_bindings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        consumption,
        "_validate_public_bindings",
        lambda candidate_source, paths, require_control_absent: {
            "candidate_source": candidate_source,
            "fixture_content_reads": 0,
        },
    )


def test_plan_freezes_exact_lineage_one_read_and_closed_api_spine_boundary() -> None:
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    for value in (
        consumption.PLAN_SOURCE,
        consumption.FIRST_USE_SOURCE,
        consumption.CANDIDATE_GATE_SOURCE,
        consumption.ORIGINAL_ADAPTER_SOURCE,
        consumption.CURRENT_ADAPTER_SOURCE,
        consumption.CURRENT_ADAPTER_BLOB,
        consumption.FIXTURE_SHA256,
        consumption.PROTECTED_COMMIT,
    ):
        assert value in plan
    assert "No ordinary recurring test may open" in plan
    assert "fixture is evidence context only" in plan
    assert "consuming" in threat
    assert "event becomes command authority" in threat
    assert "no retry" in threat.lower()


def test_prepare_writes_zero_read_lease_without_opening_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture_bytes = b"not parsed during prepare"
    paths = _paths(tmp_path, fixture_bytes)
    _bypass_public_bindings(monkeypatch)

    reading = consumption.prepare(consumption.PLAN_SOURCE, paths=paths)

    assert reading["status"] == "prepared"
    assert reading["fixture_content_reads"] == 0
    assert reading["fixture_hash_operations"] == 0
    assert json.loads(paths.control.read_text(encoding="utf-8")) == _prepared_control(
        consumption.PLAN_SOURCE
    )


def test_one_synthetic_fixture_read_runs_one_exact_patient_free_adapter_test(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture_bytes = _bytes()
    paths = _paths(tmp_path, fixture_bytes)
    _bypass_public_bindings(monkeypatch)
    consumption._exclusive_json(paths.control, _prepared_control(consumption.PLAN_SOURCE))

    result = consumption.consume(
        consumption.PLAN_SOURCE,
        paths=paths,
        contract=_contract(fixture_bytes),
    )

    assert result["decision"] == consumption.SUCCESS_DECISION
    assert result["consumption"] == {
        "fixture_sha256_expected": hashlib.sha256(fixture_bytes).hexdigest(),
        "fixture_digest_match": True,
        "digest_verified_before_parse": True,
        "parsed_from_same_in_memory_bytes": True,
        "logical_fixture_read_count": 1,
        "fixture_retry_authorized": False,
        "historical_archive_reads": 0,
    }
    assert result["structural_utility"] == consumption.EXPECTED_UTILITY
    assert result["adapter_test"]["invocations"] == 1
    assert result["adapter_test"]["waiting_area_preserved_none"] is True
    assert result["adapter_test"]["response_patient_free"] is True
    assert result["authority"]["fixture_is_command_authority"] is False
    serialized = json.dumps(result, sort_keys=True)
    for forbidden in (
        '"events":',
        '"synthetic_subject_slot":',
        '"resource_slot":',
        REAL_FIXTURE_FRAGMENT,
        "opaque-authored-synthetic-evidence",
    ):
        assert forbidden not in serialized
    control = json.loads(paths.control.read_text(encoding="utf-8"))
    assert control["state"] == "complete"
    assert control["logical_fixture_read_count"] == 1
    assert control["fixture_retry_authorized"] is False


def test_digest_mismatch_consumes_lease_without_adapter_or_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture_bytes = _bytes()
    paths = _paths(tmp_path, fixture_bytes)
    _bypass_public_bindings(monkeypatch)
    consumption._exclusive_json(paths.control, _prepared_control(consumption.PLAN_SOURCE))
    calls = []
    monkeypatch.setattr(
        consumption,
        "_run_adapter_once",
        lambda candidate, utility: calls.append((candidate, utility)),
    )
    wrong = consumption.ConsumptionContract(
        fixture_sha256="0" * 64,
        expected_utility=dict(consumption.EXPECTED_UTILITY),
    )

    result = consumption.consume(
        consumption.PLAN_SOURCE,
        paths=paths,
        contract=wrong,
    )

    assert result["decision"] == "revision_required"
    assert result["reason_codes"] == ["fixture_digest_mismatch"]
    assert result["adapter_test"]["invocations"] == 0
    assert calls == []
    control = json.loads(paths.control.read_text(encoding="utf-8"))
    assert control["state"] == "failed_closed"
    assert control["logical_fixture_read_count"] == 1
    assert control["fixture_retry_authorized"] is False
    with pytest.raises(
        consumption.ConsumptionError,
        match="prepared_control_mismatch_or_consumed",
    ):
        consumption.consume(
            consumption.PLAN_SOURCE,
            paths=paths,
            contract=wrong,
        )


def test_structural_utility_mismatch_fails_before_adapter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture_bytes = _bytes()
    paths = _paths(tmp_path, fixture_bytes)
    _bypass_public_bindings(monkeypatch)
    consumption._exclusive_json(paths.control, _prepared_control(consumption.PLAN_SOURCE))
    calls = []
    monkeypatch.setattr(
        consumption,
        "_run_adapter_once",
        lambda candidate, utility: calls.append((candidate, utility)),
    )
    expected = dict(consumption.EXPECTED_UTILITY)
    expected["event_count"] = 5

    result = consumption.consume(
        consumption.PLAN_SOURCE,
        paths=paths,
        contract=consumption.ConsumptionContract(
            fixture_sha256=hashlib.sha256(fixture_bytes).hexdigest(),
            expected_utility=expected,
        ),
    )

    assert result["decision"] == "revision_required"
    assert result["reason_codes"] == ["structural_utility_mismatch"]
    assert calls == []


@pytest.mark.parametrize("state", ["consuming", "complete", "failed_closed"])
def test_nonprepared_control_can_never_reenter_consumption(
    state: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture_bytes = _bytes()
    paths = _paths(tmp_path, fixture_bytes)
    _bypass_public_bindings(monkeypatch)
    control = _prepared_control(consumption.PLAN_SOURCE, state=state)
    if state in {"complete", "failed_closed"}:
        control["decision"] = (
            consumption.SUCCESS_DECISION if state == "complete" else "blocked"
        )
        control["result_sha256"] = "1" * 64
    consumption._exclusive_json(paths.control, control)

    with pytest.raises(
        consumption.ConsumptionError,
        match="prepared_control_mismatch_or_consumed",
    ):
        consumption.consume(
            consumption.PLAN_SOURCE,
            paths=paths,
            contract=_contract(fixture_bytes),
        )


def test_source_contains_one_fixture_open_and_one_read_call() -> None:
    source = Path(consumption.__file__).read_text(encoding="utf-8")
    consume_source = source.split("def consume(", 1)[1].split("def main(", 1)[0]

    assert consume_source.count('paths.fixture.open("rb")') == 1
    assert consume_source.count("handle.read()") == 1
    assert "paths.fixture.read_bytes" not in consume_source
    assert "paths.fixture.read_text" not in consume_source
    adapter_source = source.split("def _run_adapter_once(", 1)[1].split(
        "def _terminal(", 1
    )[0]
    assert adapter_source.count("compose_product_check_in(") == 1
    assert "archive" not in "\n".join(
        line for line in consume_source.splitlines() if "historical_archive_reads" not in line
    )


def test_real_fixture_is_not_a_pytest_input() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden_default = "DEFAULT" + "_PATHS"
    forbidden_real_path = "Path(REAL_FIXTURE" + "_FRAGMENT)"
    assert forbidden_default not in source
    assert "local_data" in REAL_FIXTURE_FRAGMENT
    assert forbidden_real_path not in source
