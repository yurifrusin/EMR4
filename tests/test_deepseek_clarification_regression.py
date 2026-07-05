"""DeepSeek Flash regression lane: clarification merge invariants.

This file provides independent test/review coverage for Sprint R2
clarification merge semantics. It focuses on three areas:

1.  Slot normalizer pure invariants — proofs that the deterministic
    normalizer does not corrupt, drop, or cross-pollinate fields.
2.  Replay harness preserved_fields invariant — unit-level checks on
    the scenario replay engine's preserved-fields tracking.
3.  Clarification merge fixture integrity — structural consistency
    checks on existing YAML corpus fixtures that target merge semantics.

No production code, no UI, no live provider calls.
Authorship: DeepSeek Flash (Sprint R2-C regression lane).
"""

from __future__ import annotations

import re
import uuid
from datetime import date, time
from pathlib import Path

import pytest

from app.schemas.appointments import SlotSearchCommandIn
from app.services.bernie_slot_normalizer import normalize_slot_search_command

_REF = date(2026, 7, 6)

def _uuid_str() -> str:
    return str(uuid.uuid4())


class TestSlotNormalizerPureInvariants:
    def test_field_independence_practitioner_id_does_not_affect_date(self):
        pid_a = _uuid_str()
        pid_b = _uuid_str()
        result_a = normalize_slot_search_command(
            SlotSearchCommandIn(practitioner_id=pid_a, date_from=_REF.isoformat()),
            reference_date=_REF,
        )
        result_b = normalize_slot_search_command(
            SlotSearchCommandIn(practitioner_id=pid_b, date_from=_REF.isoformat()),
            reference_date=_REF,
        )
        assert result_a.safe and result_b.safe
        assert result_a.constraint.date_from == result_b.constraint.date_from

    def test_field_independence_date_does_not_affect_practitioner(self):
        pid = _uuid_str()
        result_a = normalize_slot_search_command(
            SlotSearchCommandIn(practitioner_id=pid, date_from="2026-07-06"),
            reference_date=_REF,
        )
        result_b = normalize_slot_search_command(
            SlotSearchCommandIn(practitioner_id=pid, date_from="2026-07-07"),
            reference_date=_REF,
        )
        assert result_a.safe and result_b.safe
        assert result_a.constraint.practitioner_id == result_b.constraint.practitioner_id

    def test_field_independence_duration_does_not_affect_other_fields(self):
        pid = _uuid_str()
        base = dict(practitioner_id=pid, date_from=_REF.isoformat())
        r15 = normalize_slot_search_command(SlotSearchCommandIn(**base, duration_minutes=15), reference_date=_REF)
        r30 = normalize_slot_search_command(SlotSearchCommandIn(**base, duration_minutes=30), reference_date=_REF)
        assert r15.safe and r30.safe
        assert r15.constraint.practitioner_id == r30.constraint.practitioner_id
        assert r15.constraint.date_from == r30.constraint.date_from
        assert r15.constraint.duration_minutes == 15
        assert r30.constraint.duration_minutes == 30

    def test_optional_fields_are_independent(self):
        pid = _uuid_str()
        result = normalize_slot_search_command(
            SlotSearchCommandIn(practitioner_id=pid, date_from=_REF.isoformat(), earliest_time="09:00", latest_time="12:00", limit=5),
            reference_date=_REF,
        )
        assert result.safe
        assert result.constraint.earliest_time == time(9, 0)
        assert result.constraint.latest_time == time(12, 0)
        assert result.constraint.limit == 5

    def test_unknown_fields_are_ignored(self):
        pid = _uuid_str()
        command = SlotSearchCommandIn.model_validate({
            "practitioner_id": pid, "date_from": _REF.isoformat(), "duration_minutes": 15,
            "unknown_llm_key": "should_be_ignored", "extra_noise": {"nested": True},
        })
        result = normalize_slot_search_command(command, reference_date=_REF)
        assert result.safe
        assert result.constraint.practitioner_id == uuid.UUID(pid)
        assert result.constraint.date_from == _REF

    def test_idempotent_same_input_same_output(self):
        pid = _uuid_str()
        command = SlotSearchCommandIn(practitioner_id=pid, date_from=_REF.isoformat(), duration_minutes=30, patient_id=_uuid_str(), earliest_time="14:00", latest_time="16:00")
        first = normalize_slot_search_command(command, reference_date=_REF)
        second = normalize_slot_search_command(command, reference_date=_REF)
        assert first.model_dump(mode="json") == second.model_dump(mode="json")

    def test_idempotent_across_multiple_calls(self):
        pid = _uuid_str()
        command = SlotSearchCommandIn(practitioner_id=pid, date_from=_REF.isoformat(), duration_minutes=20)
        results = [normalize_slot_search_command(command, reference_date=_REF) for _ in range(3)]
        serialized = [r.model_dump(mode="json") for r in results]
        assert serialized[0] == serialized[1] == serialized[2]

    def test_reference_date_only_affects_relative_date(self):
        pid = _uuid_str()
        abs_result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id=pid, date_from="2026-07-06"), reference_date=_REF)
        diff_ref_result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id=pid, date_from="2026-07-06"), reference_date=date(2026, 8, 1))
        assert abs_result.safe and diff_ref_result.safe
        assert abs_result.constraint.date_from == diff_ref_result.constraint.date_from

    def test_today_resolves_from_reference_date(self):
        pid = _uuid_str()
        result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id=pid, date_from="today"), reference_date=_REF)
        assert result.safe
        assert result.constraint.date_from == _REF

    def test_tomorrow_resolves_from_reference_date(self):
        pid = _uuid_str()
        result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id=pid, date_from="tomorrow"), reference_date=_REF)
        assert result.safe
        assert result.constraint.date_from == date(2026, 7, 7)

    def test_relative_date_without_reference_is_blocked(self):
        pid = _uuid_str()
        result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id=pid, date_from="today"), reference_date=None)
        assert result.safe is False
        codes = {b.code for b in result.blocks}
        assert "relative_date_no_reference" in codes

    def test_missing_practitioner_id_is_blocked(self):
        result = normalize_slot_search_command(SlotSearchCommandIn(date_from=_REF.isoformat(), duration_minutes=15), reference_date=_REF)
        assert result.safe is False
        codes = {b.code for b in result.blocks}
        assert "missing_practitioner_id" in codes

    def test_missing_date_from_is_blocked(self):
        pid = _uuid_str()
        result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id=pid, duration_minutes=15), reference_date=_REF)
        assert result.safe is False
        codes = {b.code for b in result.blocks}
        assert "missing_date_from" in codes

    def test_invalid_uuid_rejected(self):
        result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id="not-a-uuid-at-all", date_from=_REF.isoformat()), reference_date=_REF)
        assert result.safe is False
        codes = {b.code for b in result.blocks}
        assert "invalid_practitioner_id" in codes

    def test_negative_duration_blocked(self):
        pid = _uuid_str()
        result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id=pid, date_from=_REF.isoformat(), duration_minutes=-5), reference_date=_REF)
        assert result.safe is False
        codes = {b.code for b in result.blocks}
        assert "invalid_duration_minutes" in codes

    def test_summary_includes_all_resolved_parts(self):
        pid = _uuid_str()
        result = normalize_slot_search_command(SlotSearchCommandIn(practitioner_id=pid, date_from=_REF.isoformat(), duration_minutes=30), reference_date=_REF)
        assert result.safe
        assert str(pid) in result.summary
        assert _REF.isoformat() in result.summary
        assert "30" in result.summary

class TestReplayPreservedFieldsInvariants:
    def test_get_nested_traverses_dotted_paths(self):
        from tests.bernie_scenarios.replay import _get_nested
        data = {"a": {"b": {"c": "deep_value"}}}
        assert _get_nested(data, "a") == {"b": {"c": "deep_value"}}
        assert _get_nested(data, "a.b") == {"c": "deep_value"}
        assert _get_nested(data, "a.b.c") == "deep_value"

    def test_get_nested_returns_none_for_missing_path(self):
        from tests.bernie_scenarios.replay import _get_nested
        data = {"safe": True, "constraint": {"date_from": "2026-07-06"}}
        assert _get_nested(data, "nonexistent") is None
        assert _get_nested(data, "constraint.missing_field") is None
        assert _get_nested(data, "a.b.c") is None

    def test_get_nested_handles_non_dict_intermediate(self):
        from tests.bernie_scenarios.replay import _get_nested
        data = {"a": "scalar_value"}
        assert _get_nested(data, "a.b") is None

    def test_replay_context_normalize_property_returns_last(self):
        from tests.bernie_scenarios.replay import ReplayContext
        ctx = ReplayContext(
            client=None, db=None, token="x",
            reference_date="2026-07-06",
            practitioner_id=uuid.uuid4(),
            patient_id=uuid.uuid4(),
            practice_id=uuid.uuid4(),
        )
        t1 = type("obj", (), {"action": "normalize", "request_body": {"practitioner_id": "first"}, "status_code": 200, "response": {}})()
        t2 = type("obj", (), {"action": "normalize", "request_body": {"practitioner_id": "second"}, "status_code": 200, "response": {}})()
        ctx._turns.extend([t1, t2])
        assert ctx.last_normalize_input == {"practitioner_id": "second"}

    def test_replay_context_search_property_returns_last(self):
        from tests.bernie_scenarios.replay import ReplayContext
        ctx = ReplayContext(
            client=None, db=None, token="x",
            reference_date="2026-07-06",
            practitioner_id=uuid.uuid4(),
            patient_id=uuid.uuid4(),
            practice_id=uuid.uuid4(),
        )
        t1 = type("obj", (), {"action": "search", "request_body": {}, "status_code": 200, "response": {"intent": "search_slots", "safe": True}})()
        t2 = type("obj", (), {"action": "search", "request_body": {}, "status_code": 200, "response": {"intent": "search_slots", "safe": False}})()
        ctx._turns.extend([t1, t2])
        assert ctx.last_search_response == {"intent": "search_slots", "safe": False}


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "bernie_scenarios"

CLARIFICATION_MERGE_FIXTURES = frozenset({
    "clarification_reply_merges_missing_field_only.yaml",
    "booking_clarify_long_duration_preserves_patient_date_time.yaml",
    "booking_clarify_long_duration_preserves_practitioner.yaml",
})

_YAML = None

def _get_yaml():
    global _YAML
    if _YAML is None:
        _YAML = pytest.importorskip("yaml", reason="PyYAML not installed")
    return _YAML

def _load_clarification_fixtures():
    yaml = _get_yaml()
    if not FIXTURE_DIR.is_dir():
        pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")
    for path in sorted(FIXTURE_DIR.iterdir()):
        if path.name not in CLARIFICATION_MERGE_FIXTURES:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as exc:
            yield path.name, None, str(exc)
            continue
        yield path.name, data, None


class TestClarificationMergeFixtureIntegrity:
    def test_clarification_fixtures_have_correct_category(self):
        for fn, data, err in _load_clarification_fixtures():
            assert err is None, f"{fn}: parse error: {err}"
            assert isinstance(data, dict), f"{fn}: expected dict"
            assert data.get("category") == "booking_clarification", (
                f"{fn}: expected 'booking_clarification', got {data.get('category')!r}"
            )

    def test_clarification_fixtures_have_xfail_with_reason(self):
        for fn, data, err in _load_clarification_fixtures():
            assert err is None, f"{fn}: {err}"
            xfail = data.get("xfail")
            assert xfail is not None, f"{fn}: missing xfail"
            reason = xfail.get("reason", "") if isinstance(xfail, dict) else str(xfail)
            assert "Sprint R2" in reason, f"{fn}: xfail reason must reference Sprint R2, got: {reason}"

    def test_clarification_fixtures_have_forbidden_list(self):
        for fn, data, err in _load_clarification_fixtures():
            assert err is None, f"{fn}: {err}"
            forbidden = data.get("forbidden", [])
            assert isinstance(forbidden, list), f"{fn}: 'forbidden' must be a list"
            assert len(forbidden) > 0, f"{fn}: 'forbidden' must not be empty"

    def test_clarification_fixtures_preserve_fields_across_turns(self):
        for fn, data, err in _load_clarification_fixtures():
            assert err is None, f"{fn}: {err}"
            turns = data.get("turns", [])
            assert isinstance(turns, list) and len(turns) == 2, f"{fn}: expected 2 turns"
            first_preserved = {}
            for i, turn in enumerate(turns):
                expect = turn.get("expect", {})
                preserved = expect.get("preserved", {})
                assert isinstance(preserved, dict), f"{fn}: turn[{i}] 'preserved' must be a dict"
                assert len(preserved) > 0, f"{fn}: turn[{i}] 'preserved' must have entries"
                if i == 0:
                    first_preserved = preserved
                else:
                    for key in first_preserved:
                        assert key in preserved, f"{fn}: turn[{i}] missing preserved key '{key}' from turn[0]"

    def test_clarification_fixtures_reference_valid_reference_date(self):
        for fn, data, err in _load_clarification_fixtures():
            assert err is None, f"{fn}: {err}"
            ref = data.get("reference_date", "")
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ref)), f"{fn}: invalid date format: {ref!r}"
            date.fromisoformat(str(ref))

    def test_all_clarification_fixtures_are_found(self):
        missing = [fn for fn in sorted(CLARIFICATION_MERGE_FIXTURES) if not (FIXTURE_DIR / fn).is_file()]
        assert not missing, f"Fixture files not found: {missing}"

    def test_non_merge_fixtures_have_consistent_turns(self):
        yaml = _get_yaml()
        if not FIXTURE_DIR.is_dir():
            pytest.skip(f"Fixture directory not found: {FIXTURE_DIR}")
        issues = []
        for path in sorted(FIXTURE_DIR.iterdir()):
            if path.suffix.lower() not in (".yaml", ".yml"):
                continue
            if path.name in CLARIFICATION_MERGE_FIXTURES or path.name.startswith("harness_demo"):
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except Exception:
                continue
            if data is None:
                continue
            for i, turn in enumerate(data.get("turns", [])):
                preserved = turn.get("expect", {}).get("preserved")
                if preserved is not None and not isinstance(preserved, dict):
                    issues.append(f"{path.name}: turn[{i}] 'preserved' should be a dict")
        assert not issues, "Fixture shape issues:\n" + "\n".join(issues)


class TestClarificationMergeSourceReview:
    def test_slot_normalizer_imports_no_db_or_llm(self):
        import app.services.bernie_slot_normalizer as norm
        import inspect
        source = inspect.getsource(norm)
        import_lines = [
            line.lower()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        ]
        forbidden = ["sqlalchemy", "gemini", "vertex", "generate_content", "asyncio", "httpx", "requests"]
        hits = [
            token
            for token in forbidden
            if any(token in line for line in import_lines)
        ]
        assert not hits, f"Normalizer imports forbidden modules: {hits}"
        assert "db." not in source.lower()

    def test_replay_harness_imports_no_live_provider(self):
        import tests.bernie_scenarios.replay as replay
        import inspect
        source = inspect.getsource(replay)
        assert "_install_forbidden_ai_provider_guard" in source, "Replay must have AI provider guard"
        assert "AssertionError" in source or "forbidden" in source.lower(), "Replay must enforce no provider calls"

    def test_replay_harness_no_db_mutation_outside_scenario_expected(self):
        import tests.bernie_scenarios.replay as replay
        import inspect
        source = inspect.getsource(replay)
        db_writes = ["db.add(", "db.commit(", "db.flush("]
        hits = [p for p in db_writes if p in source]
        assert not hits, f"Replay harness has DB write calls: {hits}"
