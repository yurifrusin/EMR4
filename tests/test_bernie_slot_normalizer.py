"""Tests for the deterministic Bernie slot-search command normalizer.

Pure unit tests: no DB, no server, no network, no LLM.
"""

import uuid
from datetime import date, time, timedelta

import pytest

from app.schemas.appointments import SlotSearchCommandIn
from app.services.bernie_slot_normalizer import normalize_slot_search_command

PRAC_ID = uuid.uuid4()
REF_DATE = date(2026, 7, 1)


def _cmd(**kwargs) -> SlotSearchCommandIn:
    return SlotSearchCommandIn(**kwargs)


# ── Happy path ────────────────────────────────────────────────────────────────

def test_well_formed_dict_produces_valid_constraint():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=str(PRAC_ID),
        date_from="2026-07-01",
        date_to="2026-07-03",
        duration_minutes=15,
        earliest_time="09:00",
        latest_time="17:00",
    ))
    assert result.safe is True
    assert result.constraint is not None
    assert result.constraint.practitioner_id == PRAC_ID
    assert result.constraint.date_from == date(2026, 7, 1)
    assert result.constraint.date_to == date(2026, 7, 3)
    assert result.constraint.duration_minutes == 15
    assert result.constraint.earliest_time == time(9, 0)
    assert result.constraint.latest_time == time(17, 0)
    assert result.blocks == []


def test_native_uuid_and_date_types_accepted():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from=date(2026, 7, 5),
    ))
    assert result.safe is True
    assert result.constraint.practitioner_id == PRAC_ID
    assert result.constraint.date_from == date(2026, 7, 5)


def test_date_to_defaults_to_date_from_when_absent():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-10",
    ))
    assert result.safe is True
    assert result.constraint.date_to == date(2026, 7, 10)


def test_string_time_hh_mm_ss_accepted():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        earliest_time="09:00:00",
    ))
    assert result.safe is True
    assert result.constraint.earliest_time == time(9, 0, 0)


def test_native_time_object_accepted():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        earliest_time=time(8, 30),
    ))
    assert result.safe is True
    assert result.constraint.earliest_time == time(8, 30)


def test_optional_uuid_fields_parsed():
    apt_type = uuid.uuid4()
    loc_id = uuid.uuid4()
    pat_id = uuid.uuid4()
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        appointment_type_id=str(apt_type),
        location_id=str(loc_id),
        patient_id=str(pat_id),
    ))
    assert result.safe is True
    assert result.constraint.appointment_type_id == apt_type
    assert result.constraint.location_id == loc_id
    assert result.constraint.patient_id == pat_id


def test_limit_within_range_set():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        limit=5,
    ))
    assert result.safe is True
    assert result.constraint.limit == 5
    assert result.warnings == []


def test_limit_as_string_coerced():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        limit="10",
    ))
    assert result.safe is True
    assert result.constraint.limit == 10


# ── Limit clamping ────────────────────────────────────────────────────────────

def test_limit_above_100_clamped_with_warning():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        limit=200,
    ))
    assert result.safe is True
    assert result.constraint.limit == 100
    assert len(result.warnings) == 1
    assert result.warnings[0].code == "limit_clamped"
    assert result.warnings[0].severity == "warning"


# ── Unknown extra keys ────────────────────────────────────────────────────────

def test_extra_keys_from_llm_ignored():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        unknown_llm_field="irrelevant",
        another_extra=42,
    ))
    assert result.safe is True


# ── Relative date tokens ──────────────────────────────────────────────────────

def test_relative_today_with_reference_date():
    result = normalize_slot_search_command(
        _cmd(practitioner_id=PRAC_ID, date_from="today"),
        reference_date=REF_DATE,
    )
    assert result.safe is True
    assert result.constraint.date_from == REF_DATE


def test_relative_tomorrow_with_reference_date():
    result = normalize_slot_search_command(
        _cmd(practitioner_id=PRAC_ID, date_from="tomorrow"),
        reference_date=REF_DATE,
    )
    assert result.safe is True
    assert result.constraint.date_from == REF_DATE + timedelta(days=1)


def test_relative_token_without_reference_date_blocks():
    result = normalize_slot_search_command(
        _cmd(practitioner_id=PRAC_ID, date_from="today"),
    )
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "relative_date_no_reference" in codes
    assert result.constraint is None


# ── Missing mandatory fields ──────────────────────────────────────────────────

def test_missing_practitioner_id_blocks():
    result = normalize_slot_search_command(_cmd(date_from="2026-07-01"))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "missing_practitioner_id" in codes
    assert result.constraint is None


def test_missing_date_from_blocks():
    result = normalize_slot_search_command(_cmd(practitioner_id=PRAC_ID))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "missing_date_from" in codes
    assert result.constraint is None


def test_both_mandatory_fields_missing_blocks_both():
    result = normalize_slot_search_command(_cmd())
    codes = {b.code for b in result.blocks}
    assert "missing_practitioner_id" in codes
    assert "missing_date_from" in codes


# ── Malformed inputs ──────────────────────────────────────────────────────────

def test_malformed_uuid_blocks():
    result = normalize_slot_search_command(_cmd(
        practitioner_id="not-a-uuid",
        date_from="2026-07-01",
    ))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "invalid_practitioner_id" in codes
    assert result.constraint is None


def test_malformed_date_blocks():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="01/07/2026",
    ))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "invalid_date_from" in codes


def test_malformed_time_blocks():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        earliest_time="9am",
    ))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "invalid_earliest_time" in codes


def test_non_positive_duration_blocks():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        duration_minutes=0,
    ))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "invalid_duration_minutes" in codes


def test_negative_duration_blocks():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        duration_minutes=-5,
    ))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "invalid_duration_minutes" in codes


def test_non_positive_limit_blocks():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        limit=0,
    ))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "invalid_limit" in codes


# ── Range violations (delegated to SlotSearchProposalIn) ─────────────────────

def test_date_to_before_date_from_blocks():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-10",
        date_to="2026-07-05",
    ))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "constraint_validation_error" in codes
    assert result.constraint is None


def test_date_range_exceeds_14_days_blocks():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
        date_to="2026-07-20",
    ))
    assert result.safe is False
    codes = {b.code for b in result.blocks}
    assert "constraint_validation_error" in codes


# ── Purity / non-mutation proof ───────────────────────────────────────────────

def test_function_has_no_db_or_io_imports():
    """The normalizer module must not import DB session, network, or LLM deps."""
    import importlib
    import inspect
    import app.services.bernie_slot_normalizer as mod
    src = inspect.getsource(mod)
    assert "sqlalchemy" not in src.lower()
    assert "asyncpg" not in src.lower()
    assert "google.genai" not in src.lower()
    assert "httpx" not in src.lower()
    assert "requests" not in src.lower()


def test_function_is_idempotent():
    payload = _cmd(practitioner_id=PRAC_ID, date_from="2026-07-01")
    r1 = normalize_slot_search_command(payload)
    r2 = normalize_slot_search_command(payload)
    assert r1.safe == r2.safe
    assert r1.constraint == r2.constraint
    assert r1.blocks == r2.blocks
    assert r1.warnings == r2.warnings


def test_function_accepts_no_db_session_parameter():
    """normalize_slot_search_command signature must not require a DB session."""
    import inspect
    sig = inspect.signature(normalize_slot_search_command)
    param_names = list(sig.parameters.keys())
    assert "db" not in param_names
    assert "session" not in param_names


def test_result_has_no_constraint_when_blocked():
    result = normalize_slot_search_command(_cmd(date_from="2026-07-01"))
    assert result.safe is False
    assert result.constraint is None


def test_summary_populated_on_success():
    result = normalize_slot_search_command(_cmd(
        practitioner_id=PRAC_ID,
        date_from="2026-07-01",
    ))
    assert result.safe is True
    assert len(result.summary) > 0
    assert str(PRAC_ID) in result.summary


def test_summary_populated_on_failure():
    result = normalize_slot_search_command(_cmd())
    assert result.safe is False
    assert len(result.summary) > 0
