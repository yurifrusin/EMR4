import inspect
import json
from pathlib import Path

import pytest

from orchestration_harness import historical_diary_local_measured_privacy_probe as probe


PLAN = Path(
    "docs/raisa-provider-free-authored-synthetic-historical-diary-leading-explicit-time-token-recovery-rehearsal-plan.md"
)
THREAT = Path(
    "docs/security/raisa-provider-free-authored-synthetic-historical-diary-leading-explicit-time-token-recovery-rehearsal-threat-model-delta.md"
)
CONTRACT = Path(
    "orchestration/continuity/raisa-local-only-historical-diary-document-story-time-coordinate-bounded-measurement-recovery-rehearsal/next-tranche-contract.json"
)
KEY_A = bytes(range(32))
KEY_B = bytes(range(32, 64))


def _cell(text: str, *, column: int = 1) -> probe.PrivateCell:
    segments = probe._cell_segments(text)
    return probe.PrivateCell(
        table_index=1,
        row_index=1,
        column_index=column,
        text=text,
        shading=0,
        font_color=0,
        bold=False,
        italic=False,
        segment_coordinates=tuple(
            probe.PrivateSegmentCoordinate(
                segment_ordinal=ordinal,
                coordinate_available=False,
                page_ordinal=None,
                vertical_quarter_points=None,
            )
            for ordinal, _segment in enumerate(segments)
        ),
    )


def _extraction(*values: str) -> probe.PrivateExtraction:
    return _extraction_snapshots(*(values for _index in range(3)))


def _extraction_snapshots(*snapshots_values: tuple[str, ...]) -> probe.PrivateExtraction:
    snapshots = tuple(
        probe.PrivateSnapshot(
            sequence_index=index,
            observation_offset_seconds=index * 30,
            cells=tuple(
                _cell(value, column=column)
                for column, value in enumerate(values, 1)
            ),
            story_time_anchors=(),
            error_code=None,
        )
        for index, values in enumerate(snapshots_values)
    )
    return probe.PrivateExtraction(
        schema_version="historical_diary.private_word_story_coordinate_extraction.v2",
        status="passed",
        reason_code="passed",
        word_invisible=True,
        alerts_disabled=True,
        macro_security_forced_disabled=True,
        link_updates_disabled=True,
        documents_opened_read_only=True,
        word_cleanup_completed=True,
        snapshots=snapshots,
    )


def _fixed_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    keys = iter((KEY_A, KEY_B))
    monkeypatch.setattr(probe.secrets, "token_bytes", lambda _size: next(keys))


def test_plan_contract_and_threat_keep_history_and_first_use_closed():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    assert "does not reopen or enumerate the historical archive" in plan
    assert "first-use gate remains `closed_pending_candidate_specific_evaluation`" in plan
    assert "Authored-synthetic proof reopens private historical data" in threat
    assert contract["input_boundary"]["authored_synthetic_segments_only"] is True
    assert contract["input_boundary"]["historical_archive_enumeration_or_content_access"] is False
    assert contract["mapping"]["forward_fill_to_later_segments"] is False
    assert contract["mapping"]["token_removed_before_private_payload_hashing"] is True


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("00:00 Alpha", (0, "Alpha")),
        ("9:05\tAlpha", (545, "Alpha")),
        ("09.05-Alpha", (545, "Alpha")),
        ("23:59 - Alpha", (1439, "Alpha")),
        ("12:00am Alpha", (0, "Alpha")),
        ("12:00 PM-Alpha", (720, "Alpha")),
        ("1.15pM\tAlpha", (795, "Alpha")),
    ],
)
def test_strict_leading_parser_accepts_closed_positive_matrix(value, expected):
    assert probe._leading_explicit_time_payload(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "24:00 Alpha",
        "09:60 Alpha",
        "00:00am Alpha",
        "13:00pm Alpha",
        "09:00",
        "09:00Alpha",
        "09:001 Alpha",
        "09:00/Alice",
        "09:00:30 Alpha",
        "09:00–Alpha",
        "Appointment 09:00 Alpha",
        "09:00 24/08/2016 Alpha",
        "09:00 0412 345 678",
        "09:00 alice@example.test",
        "09:00 - \t",
        "09:00\rAlpha",
    ],
)
def test_strict_leading_parser_rejects_hostile_matrix(value):
    assert probe._leading_explicit_time_payload(value) is None


def test_structural_segmentation_trims_before_strict_parser():
    segments = probe._cell_segments(" 09:00 - Alpha \r\x07")

    assert segments == ("09:00 - Alpha",)
    assert probe._leading_explicit_time_payload(segments[0]) == (540, "Alpha")


def test_direct_mapping_is_same_segment_only_and_never_forward_fills(monkeypatch):
    _fixed_keys(monkeypatch)
    projection, reading = probe.project_and_measure(
        _extraction("09:00 - Alpha payload", "Later payload")
    )

    for snapshot in projection.snapshots:
        direct, later = snapshot.cells
        assert direct.time_minute == 540
        assert direct.time_mapping == "leading_explicit_time_token"
        assert later.time_minute is None
        assert later.time_mapping == "unmapped"
    assert reading["utility"]["mapped_time_observations"] == 3
    assert reading["utility"]["leading_explicit_time_token_observations"] == 3
    assert reading["utility"]["mapping_outcome_counts"] == {
        "coordinate_unavailable": 3,
        "leading_explicit_time_token": 3,
    }


def test_token_and_separator_are_removed_before_private_hashing(monkeypatch):
    _fixed_keys(monkeypatch)
    with_clock, _reading = probe.project_and_measure(_extraction("09:00 - Alpha payload"))
    _fixed_keys(monkeypatch)
    without_clock, _reading = probe.project_and_measure(_extraction("Alpha payload"))

    clock_cell = with_clock.snapshots[0].cells[0]
    plain_cell = without_clock.snapshots[0].cells[0]
    assert clock_cell.content_token == plain_cell.content_token
    assert clock_cell.cell_token == plain_cell.cell_token
    assert clock_cell.time_minute == 540
    assert plain_cell.time_minute is None


def test_sufficient_leading_tokens_are_first_class_explicit_time_sources(monkeypatch):
    _fixed_keys(monkeypatch)
    projection, reading = probe.project_and_measure(
        _extraction_snapshots(
            ("09:00 Alpha", "09:15 Beta", "09:30 Gamma"),
            ("09:00 Alpha", "09:15 Beta", "09:30 Gamma", "09:45 Delta"),
            ("09:00 Alpha", "09:15 Beta", "09:30 Gamma", "09:45 Delta"),
        )
    )

    assert reading["decision"] == "locally_restricted_candidate"
    assert reading["utility"]["leading_explicit_time_token_observations"] == 11
    assert reading["utility"]["explicit_story_time_anchor_observations"] == 0
    assert reading["utility"]["positive_interval_mode_minutes"] == 15
    assert reading["utility"]["stable_linkage_records"] == 4
    assert reading["utility"]["total_changes"] == 1
    assert all(
        cell.time_mapping == "leading_explicit_time_token"
        for snapshot in projection.snapshots
        for cell in snapshot.cells
    )


def test_projection_proof_does_not_enumerate_or_open_historical_files(monkeypatch):
    def forbidden_iterdir(_path):
        pytest.fail("authored-synthetic parser proof must not enumerate a filesystem root")

    monkeypatch.setattr(Path, "iterdir", forbidden_iterdir)
    _fixed_keys(monkeypatch)
    projection, _reading = probe.project_and_measure(_extraction("09:00 Alpha payload"))

    assert projection.snapshots[0].cells[0].time_minute == 540
    source = inspect.getsource(probe._leading_explicit_time_payload)
    assert "BOUND_ROOT" not in source
    assert "ATTEMPT_ROOT" not in source
    assert "open(" not in source
