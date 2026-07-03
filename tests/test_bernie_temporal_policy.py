from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from app.services.bernie.temporal import (
    evaluate_same_day_window,
    extract_natural_date_constraint,
    extract_natural_time_constraints,
    parse_time_fragment,
    resolve_week_relative_date,
)


def _dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, 3, hour, minute, tzinfo=ZoneInfo("Australia/Brisbane"))


def test_week_relative_date_uses_reference_date():
    assert resolve_week_relative_date("in a week's time", date(2026, 7, 3)) == "2026-07-10"
    assert resolve_week_relative_date("next week please", date(2026, 7, 3)) == "2026-07-10"
    assert resolve_week_relative_date("tomorrow please", date(2026, 7, 3)) is None


def test_natural_date_extracts_explicit_before_week_relative():
    assert extract_natural_date_constraint("tomorrow next week", date(2026, 7, 3)) == "tomorrow"
    assert extract_natural_date_constraint("next week please", date(2026, 7, 3)) == "2026-07-10"
    assert extract_natural_date_constraint("next week please", None) is None


def test_natural_time_helpers_keep_business_hours_assumption():
    assert parse_time_fragment("3") == "15:00"
    assert parse_time_fragment("3.45 pm") == "15:45"
    assert extract_natural_time_constraints("between 2 pm and 3:45") == ("14:00", "15:45")
    assert extract_natural_time_constraints("after 9 before 11") == ("21:00", "23:00")


def test_same_day_window_not_same_day():
    decision = evaluate_same_day_window(
        date(2026, 7, 4),
        time(9, 0),
        time(10, 0),
        _dt(12, 0),
    )
    assert decision.kind == "not_same_day"
    assert decision.clamp_hhmm is None


def test_same_day_window_fully_past_when_latest_is_not_after_now():
    decision = evaluate_same_day_window(
        date(2026, 7, 3),
        time(9, 0),
        time(10, 0),
        _dt(10, 0),
    )
    assert decision.kind == "window_fully_past"
    assert decision.now_time == time(10, 0)


def test_same_day_window_clamps_partly_past_bounded_window():
    decision = evaluate_same_day_window(
        date(2026, 7, 3),
        time(9, 0),
        time(11, 0),
        _dt(10, 15),
    )
    assert decision.kind == "clamp_earliest"
    assert decision.clamp_hhmm == "10:15"


def test_same_day_window_clamps_open_ended_past_start():
    decision = evaluate_same_day_window(
        date(2026, 7, 3),
        time(9, 0),
        None,
        _dt(10, 15),
    )
    assert decision.kind == "clamp_earliest"
    assert decision.clamp_hhmm == "10:15"


def test_same_day_window_ok_at_exact_earliest_boundary():
    decision = evaluate_same_day_window(
        date(2026, 7, 3),
        time(10, 15),
        None,
        _dt(10, 15),
    )
    assert decision.kind == "ok"
