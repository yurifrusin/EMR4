from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from app.services.bernie.temporal import (
    TemporalExtraction,
    TemporalRelationKind,
    adjust_search_window_for_relation,
    evaluate_same_day_window,
    extract_natural_date_constraint,
    extract_natural_time_constraints,
    infer_temporal_relation,
    parse_time_fragment,
    resolve_week_relative_date,
    should_classify_exact_booking,
)
from app.schemas.appointments import SlotSearchCommandIn


def _dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, 3, hour, minute, tzinfo=ZoneInfo("Australia/Brisbane"))


# ── Week-relative date tests ────────────────────────────────────────────────


def test_week_relative_date_uses_reference_date():
    assert resolve_week_relative_date("in a week's time", date(2026, 7, 3)) == "2026-07-10"
    assert resolve_week_relative_date("next week please", date(2026, 7, 3)) == "2026-07-10"
    assert resolve_week_relative_date("tomorrow please", date(2026, 7, 3)) is None


def test_natural_date_extracts_explicit_before_week_relative():
    assert extract_natural_date_constraint("tomorrow next week", date(2026, 7, 3)) == "tomorrow"
    assert extract_natural_date_constraint("next week please", date(2026, 7, 3)) == "2026-07-10"
    assert extract_natural_date_constraint("next week please", None) is None


# ── parse_time_fragment tests ───────────────────────────────────────────────


def test_parse_time_fragment_business_hours():
    assert parse_time_fragment("3") == "15:00"
    assert parse_time_fragment("3.45 pm") == "15:45"
    assert parse_time_fragment("3.00pm") == "15:00"
    assert parse_time_fragment("3.00 pm") == "15:00"
    assert parse_time_fragment("15:00") == "15:00"
    assert parse_time_fragment("9am") == "09:00"
    assert parse_time_fragment("12pm") == "12:00"
    assert parse_time_fragment("12am") == "00:00"


def test_zero_padded_clock_forms_keep_24_hour_meaning():
    assert parse_time_fragment("09:00") == "09:00"
    assert parse_time_fragment("10:00") == "10:00"
    assert parse_time_fragment("11:00") == "11:00"
    assert parse_time_fragment("3:45") == "15:45"


# ── extract_natural_time_constraints tests (new TemporalExtraction return) ──


def test_between_returns_interval():
    result = extract_natural_time_constraints("between 2 pm and 3:45")
    assert isinstance(result, TemporalExtraction)
    assert result.earliest == "14:00"
    assert result.latest == "15:45"
    assert result.temporal_relation == "interval"


def test_after_returns_not_before():
    result = extract_natural_time_constraints("after 9")
    assert result.earliest == "21:00"
    assert result.latest is None
    assert result.temporal_relation == "not_before"


def test_before_returns_not_after():
    result = extract_natural_time_constraints("before 11")
    assert result.earliest is None
    assert result.latest == "23:00"
    assert result.temporal_relation == "not_after"


def test_after_and_before_returns_relevant_relation():
    result = extract_natural_time_constraints("after 9 before 11")
    assert result.earliest == "21:00"
    assert result.latest == "23:00"
    # after matched first; before also matched. earliest+latest both set → interval.
    assert result.temporal_relation in ("interval", "not_before", "not_after")


def test_at_time_returns_exact():
    """'at 3pm' must no longer produce (None, None) — it must be exact with earliest=latest."""
    result = extract_natural_time_constraints("at 3pm")
    assert result.earliest == "15:00"
    assert result.latest == "15:00"
    assert result.temporal_relation == "exact"


def test_at_time_variants():
    """Test _AT_TIME_RE matches all required variants."""
    cases = [
        ("at 3pm", "15:00"),
        ("at 3 pm", "15:00"),
        ("at 3.00pm", "15:00"),
        ("at 15:00", "15:00"),
        ("at 3:00pm", "15:00"),
        ("at 3:00 pm", "15:00"),
    ]
    for instruction, expected in cases:
        result = extract_natural_time_constraints(instruction)
        assert result.earliest == expected, f"Failed for {instruction!r}: got {result.earliest}"
        assert result.latest == expected, f"Failed for {instruction!r}: got {result.latest}"
        assert result.temporal_relation == "exact", f"Failed for {instruction!r}: got {result.temporal_relation}"


def test_around_time_returns_approximate():
    """'around 3pm' should produce approximate with ±30 min window."""
    result = extract_natural_time_constraints("around 3pm")
    assert result.earliest == "14:30"
    assert result.latest == "15:30"
    assert result.temporal_relation == "approximate"


def test_about_time_variants():
    """Test _ABOUT_TIME_RE matches all variants with ±30 min window."""
    cases = [
        ("around 3pm", "14:30", "15:30"),
        ("about 3pm", "14:30", "15:30"),
        ("around 3 pm", "14:30", "15:30"),
        ("about 3 pm", "14:30", "15:30"),
        ("around 15:00", "14:30", "15:30"),
        ("about 15:00", "14:30", "15:30"),
    ]
    for instruction, exp_earliest, exp_latest in cases:
        result = extract_natural_time_constraints(instruction)
        assert result.earliest == exp_earliest, f"Failed for {instruction!r}: got earliest={result.earliest}"
        assert result.latest == exp_latest, f"Failed for {instruction!r}: got latest={result.latest}"
        assert result.temporal_relation == "approximate", f"Failed for {instruction!r}: got {result.temporal_relation}"


def test_bare_hhmm_positional_is_unspecified():
    """Bare HH:MM with no operator keyword should return unspecified."""
    result = extract_natural_time_constraints("some text 14:30 here")
    assert result.earliest == "14:30"
    assert result.latest is None
    assert result.temporal_relation == "unspecified"


def test_no_time_returns_empty():
    result = extract_natural_time_constraints("book me in")
    assert result.earliest is None
    assert result.latest is None
    assert result.temporal_relation == "unspecified"


# ── Priority ordering tests ─────────────────────────────────────────────────


def test_between_takes_priority_over_at():
    """BETWEEN takes priority over AT."""
    result = extract_natural_time_constraints("between 2 pm and 3:45 at 3pm")
    assert result.earliest == "14:00"
    assert result.latest == "15:45"
    assert result.temporal_relation == "interval"


def test_at_takes_priority_over_about():
    """AT takes priority over ABOUT."""
    result = extract_natural_time_constraints("at 3pm around 4pm")
    assert result.earliest == "15:00"
    assert result.latest == "15:00"
    assert result.temporal_relation == "exact"


def test_about_takes_priority_over_after():
    """ABOUT takes priority over AFTER."""
    result = extract_natural_time_constraints("around 3pm after 2pm")
    assert result.earliest == "14:30"
    assert result.latest == "15:30"
    assert result.temporal_relation == "approximate"


# ── infer_temporal_relation tests ───────────────────────────────────────────


def test_infer_temporal_relation_edge_cases():
    assert infer_temporal_relation("09:00", "09:00") == "exact"
    assert infer_temporal_relation("09:00", None) == "not_before"
    assert infer_temporal_relation(None, "17:00") == "not_after"
    assert infer_temporal_relation("09:00", "17:00") == "interval"
    assert infer_temporal_relation(None, None) == "unspecified"


# ── adjust_search_window_for_relation tests ─────────────────────────────────


def test_adjust_exact_widens_latest():
    """For exact temporal relation, latest is widened to earliest+5min."""
    e, l = adjust_search_window_for_relation("15:00", "15:00", "exact")
    assert e == "15:00"
    assert l == "15:05"


def test_adjust_exact_with_none_latest():
    e, l = adjust_search_window_for_relation("15:00", None, "exact")
    assert e == "15:00"
    assert l == "15:05"


def test_adjust_approximate_passthrough():
    e, l = adjust_search_window_for_relation("14:30", "15:30", "approximate")
    assert e == "14:30"
    assert l == "15:30"


def test_adjust_not_before_passthrough():
    e, l = adjust_search_window_for_relation("09:00", None, "not_before")
    assert e == "09:00"
    assert l is None


def test_adjust_unspecified_passthrough():
    e, l = adjust_search_window_for_relation("14:00", "15:00", "unspecified")
    assert e == "14:00"
    assert l == "15:00"


def test_adjust_none_str_passthrough():
    e, l = adjust_search_window_for_relation("10:00", "11:00", None)
    assert e == "10:00"
    assert l == "11:00"


# ── should_classify_exact_booking tests ─────────────────────────────────────


def test_only_exact_classifies_exact_booking():
    assert should_classify_exact_booking("exact") is True
    assert should_classify_exact_booking("approximate") is False
    assert should_classify_exact_booking("unspecified") is False
    assert should_classify_exact_booking("not_before") is False
    assert should_classify_exact_booking("not_after") is False
    assert should_classify_exact_booking("interval") is False
    assert should_classify_exact_booking(None) is False
    assert should_classify_exact_booking("") is False


# ── SlotSearchCommandIn backward compat tests ───────────────────────────────-


def test_slot_search_command_in_accepts_temporal_relation():
    """SlotSearchCommandIn must accept temporal_relation as an optional string field."""
    cmd = SlotSearchCommandIn(temporal_relation="exact")
    assert cmd.temporal_relation == "exact"

    cmd2 = SlotSearchCommandIn()
    assert cmd2.temporal_relation is None

    cmd3 = SlotSearchCommandIn(temporal_relation=None)
    assert cmd3.temporal_relation is None


def test_bare_meridiem_time_is_losslessly_preserved_as_unspecified():
    result = extract_natural_time_constraints("tomorrow 3pm")
    assert result.earliest == "15:00"
    assert result.latest is None
    assert result.temporal_relation == "unspecified"


def test_approximate_late_time_never_emits_invalid_24_hour_value():
    result = extract_natural_time_constraints("tomorrow around 11:45pm")
    assert result.earliest == "23:15"
    assert result.latest == "23:59"
    assert result.temporal_relation == "approximate"


def test_exact_late_time_window_never_emits_invalid_24_hour_value():
    assert adjust_search_window_for_relation("23:59", "23:59", "exact") == (
        "23:59",
        None,
    )


# ── Same-day window tests ───────────────────────────────────────────────────


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
