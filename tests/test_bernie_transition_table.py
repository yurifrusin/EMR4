from app.services.bernie_transition_table import resolve_booking_date_transition


def test_date_transition_preserves_explicit_date():
    transition = resolve_booking_date_transition(
        date_from="2026-07-22",
        context_frames=[{"type": "visible_diary_page", "visible_date": "2026-07-23"}],
    )

    assert transition.transition_id == "date.explicit"
    assert transition.action == "preserve"
    assert transition.date_from == "2026-07-22"


def test_date_transition_uses_selected_proposal_before_visible_page():
    transition = resolve_booking_date_transition(
        date_from=None,
        context_frames=[
            {"type": "visible_diary_page", "visible_date": "2026-07-22"},
            {"type": "selected_proposal", "appointment_date": "2026-07-24"},
        ],
    )

    assert transition.transition_id == "date.from_selected_proposal"
    assert transition.action == "assume"
    assert transition.date_from == "2026-07-24"
    assert transition.warning_code == "date_assumed_from_selected_context"


def test_date_transition_uses_selected_diary_appointment_before_visible_page():
    transition = resolve_booking_date_transition(
        date_from=None,
        context_frames=[
            {"type": "visible_diary_page", "visible_date": "2026-07-22"},
            {"type": "selected_diary_appointment", "appointment_date": "2026-07-23"},
        ],
    )

    assert transition.transition_id == "date.from_selected_diary_appointment"
    assert transition.action == "assume"
    assert transition.date_from == "2026-07-23"


def test_date_transition_uses_visible_diary_page():
    transition = resolve_booking_date_transition(
        date_from=None,
        context_frames=[{"type": "visible_diary_page", "visible_date": "2026-07-22"}],
    )

    assert transition.transition_id == "date.from_visible_diary_page"
    assert transition.action == "assume"
    assert transition.date_from == "2026-07-22"
    assert transition.warning_code == "date_assumed_from_visible_diary"


def test_date_transition_asks_without_context():
    transition = resolve_booking_date_transition(date_from=None, context_frames=[])

    assert transition.transition_id == "date.ask_missing_context"
    assert transition.action == "ask"
    assert transition.clarifying_question == "Which day would you like me to check?"
