import ast
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from orchestration_harness import historical_diary_local_measured_privacy_probe as probe


KEY_A = bytes(range(32))
KEY_B = bytes(range(32, 64))


def _cell(
    row: int,
    column: int,
    text: str,
    *,
    table: int = 1,
    shading: int = 0,
    font_color: int = 0,
    bold: bool = False,
    italic: bool = False,
) -> probe.PrivateCell:
    return probe.PrivateCell(
        table_index=table,
        row_index=row,
        column_index=column,
        text=text,
        shading=shading,
        font_color=font_color,
        bold=bold,
        italic=italic,
    )


def synthetic_extraction() -> probe.PrivateExtraction:
    snapshots = (
        probe.PrivateSnapshot(
            sequence_index=0,
            observation_offset_seconds=0,
            cells=(
                _cell(1, 2, "09:00\rAlice Smith\r\x07"),
                _cell(2, 2, "09:15\rBob Brown\r\x07"),
            ),
            error_code=None,
        ),
        probe.PrivateSnapshot(
            sequence_index=1,
            observation_offset_seconds=31,
            cells=(
                _cell(1, 3, "09:00\rAlice Smith\r\x07", shading=7, bold=True),
                _cell(2, 2, "09:15\rBob Brown\r\x07"),
                _cell(3, 2, "09:30\rCarol White\r\x07", italic=True),
            ),
            error_code=None,
        ),
        probe.PrivateSnapshot(
            sequence_index=2,
            observation_offset_seconds=68,
            cells=(
                _cell(1, 3, "09:00\rAlice Smith\r\x07"),
                _cell(2, 2, "09:15\rDavid Green\r\x07"),
            ),
            error_code=None,
        ),
    )
    return probe.PrivateExtraction(
        schema_version="historical_diary.private_word_cell_extraction.v1",
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


def _configure_synthetic_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    root = repo / "local_data/historical-diary-trove/raw/pilot_01"
    attempt = repo / "local_data/historical-diary-trove/measured-probes/2026-08-24-time-axis-v1"
    root.mkdir(parents=True)
    core = repo / "core.py"
    extractor = repo / "extract.ps1"
    core.write_text("core-v1\n", encoding="utf-8")
    extractor.write_text("extractor-v1\n", encoding="utf-8")
    monkeypatch.setattr(probe, "REPO_ROOT", repo)
    monkeypatch.setattr(probe, "BOUND_ROOT", root)
    monkeypatch.setattr(probe, "ATTEMPT_ROOT", attempt)
    monkeypatch.setattr(probe, "MANIFEST_PATH", attempt / "private-binding-manifest.json")
    monkeypatch.setattr(probe, "PRIVATE_PROJECTION_PATH", attempt / "private-derived-projection.json")
    monkeypatch.setattr(probe, "AGGREGATE_PATH", attempt / "aggregate-reading.json")
    monkeypatch.setattr(probe, "CLEANUP_PATH", attempt / "cleanup-receipt.json")
    monkeypatch.setattr(probe, "CONTENT_RUN_TERMINAL_PATH", attempt / "content-run-terminal.json")
    monkeypatch.setattr(probe, "CORE_PATH", core)
    monkeypatch.setattr(probe, "EXTRACTOR_PATH", extractor)
    return root, attempt


def _write_dense_day(root: Path, *, count: int = probe.MAX_FILES) -> None:
    first = datetime(2016, 8, 24, 8, 0, 0)
    for index in range(count):
        observed = first + timedelta(seconds=index * 30)
        path = root / f"Diary_{observed:%Y%m%d%H%M%S}.doc"
        path.write_bytes(b"0" * (probe.MIN_FILE_BYTES + 1))


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("Diary_20160824093015.doc", datetime(2016, 8, 24, 9, 30, 15)),
        ("Diary_24082016093015.doc", datetime(2016, 8, 24, 9, 30, 15)),
        ("2016-08-24 09-30-15 Diary.doc", datetime(2016, 8, 24, 9, 30, 15)),
        ("24-08-2016 09-30-15 Diary.doc", datetime(2016, 8, 24, 9, 30, 15)),
    ],
)
def test_closed_timestamp_families(filename, expected):
    assert probe.parse_observation_timestamp(filename) == expected


def test_two_digit_year_candidates_preserve_am_pm_and_global_orientation():
    candidates = probe.timestamp_candidates("24-8-16 9-30-15 PM.doc")

    assert candidates == {
        "day_month_two_digit_year": datetime(2016, 8, 24, 21, 30, 15)
    }

    assert probe.timestamp_candidates("16-8-24 9-30-15 PM.doc") == {
        "year_month_day_two_digit_year": datetime(2016, 8, 24, 21, 30, 15)
    }


@pytest.mark.parametrize(
    "filename",
    [
        "",
        "Diary.doc",
        "Diary_010203040506.doc",
        "Diary_160824093015.doc",
        "Diary_240816093015.doc",
        "2016-08-24 09-30-15 v2 Diary.doc",
        "x" * 261,
    ],
)
def test_ambiguous_missing_or_unbounded_timestamp_is_rejected(filename):
    assert probe.parse_observation_timestamp(filename) is None


def test_filename_shape_cannot_repeat_source_letters_or_digits():
    source = "AliceSmith_20160824093015.doc"
    shape = probe.filename_shape(source)

    assert shape == "asd"
    assert not set(shape) & set("AliceSmith20160824093015") - set("asd")


def test_numeric_group_shape_emits_lengths_but_no_digit_value():
    source = "2016-08-24 09-30-15 Alice.doc"

    assert probe.numeric_group_shape(source) == "4-2-2-2-2-2"
    assert all(
        value not in probe.numeric_group_shape(source)
        for value in ("2016", "08", "24", "09", "30", "15")
    )


def test_private_models_reject_extra_fields_and_invalid_sequence():
    payload = synthetic_extraction().model_dump(mode="json")
    payload["raw_path"] = r"C:\private\diary.doc"
    with pytest.raises(ValidationError):
        probe.PrivateExtraction.model_validate(payload)

    payload = synthetic_extraction().model_dump(mode="json")
    payload["snapshots"][1]["sequence_index"] = 9
    with pytest.raises(ValidationError, match="snapshot_sequence_invalid"):
        probe.PrivateExtraction.model_validate(payload)


def test_private_models_reject_nonincreasing_offsets_and_unknown_vocabulary():
    payload = synthetic_extraction().model_dump(mode="json")
    payload["snapshots"][1]["observation_offset_seconds"] = 0
    with pytest.raises(ValidationError, match="snapshot_offsets_invalid"):
        probe.PrivateExtraction.model_validate(payload)

    payload = synthetic_extraction().model_dump(mode="json")
    payload["reason_code"] = "plausible_but_untyped"
    with pytest.raises(ValidationError):
        probe.PrivateExtraction.model_validate(payload)


def test_detector_categories_are_counts_only_and_cover_defined_private_shapes():
    source = (
        "Alice Smith alice@example.test +61 412 345 678 1234 56789 1 "
        "12 Long Road urgent pathology"
    )
    categories = probe._detectors(source)

    assert categories == ("address", "email", "likely_name", "medicare", "phone", "sensitive_note")
    assert source not in json.dumps(categories)


def test_hmac_tokens_are_stable_domain_separated_and_key_separated():
    value = "authored synthetic person"

    assert probe._token("cell", "cell", value, KEY_A) == probe._token(
        "cell", "cell", value, KEY_A
    )
    assert probe._token("cell", "cell", value, KEY_A) != probe._token(
        "cell", "content", value, KEY_A
    )
    assert probe._token("cell", "cell", value, KEY_A) != probe._token(
        "cell", "cell", value, KEY_B
    )
    assert value not in probe._token("cell", "cell", value, KEY_A)


def test_projection_preserves_structure_and_every_required_event_type(monkeypatch):
    _fixed_keys(monkeypatch)
    projection, reading = probe.project_and_measure(synthetic_extraction())

    assert reading["decision"] == "locally_restricted_candidate"
    assert reading["scope"] == {
        "root_count": 1,
        "dense_day_count": 1,
        "snapshot_count": 3,
        "opened_snapshot_count": 3,
        "parsed_snapshot_count": 3,
        "rejected_snapshot_count": 0,
        "source_day_policy": "relative_day_zero_only",
    }
    assert reading["utility"]["stable_linkage_records"] > 0
    assert reading["utility"]["mapped_time_observations"] == 7
    assert reading["utility"]["change_counts"] == {
        "added": 2,
        "format_changed": 2,
        "moved": 1,
        "removed": 2,
        "same_position_replaced": 1,
    }
    assert [item.observation_interval_start_seconds for item in projection.snapshots] == [0, 30, 60]
    assert {cell.resource_ordinal for item in projection.snapshots for cell in item.cells} == {
        "resource_1_2",
        "resource_1_3",
    }
    assert {cell.segment_ordinal for item in projection.snapshots for cell in item.cells} == {1}
    assert {
        cell.time_mapping for item in projection.snapshots for cell in item.cells
    } == {"explicit_same_cell_anchor"}


def test_cell_segmentation_preserves_empty_positions_and_closed_terminators():
    assert probe._cell_segments("Header\r\r09:00\vAlice Smith\r\x07") == (
        "Header",
        "",
        "09:00",
        "Alice Smith",
    )


def test_time_mapping_uses_only_preceding_anchor_in_same_cell(monkeypatch):
    _fixed_keys(monkeypatch)
    source = synthetic_extraction()
    snapshots = tuple(
        snapshot.model_copy(
            update={
                "cells": (
                    _cell(1, 1, "09:00\r\x07"),
                    _cell(1, 2, "Header\rAlice Smith\r\x07"),
                    _cell(2, 2, "09:15\rBob Brown\r\x07"),
                    _cell(3, 2, "09:30\rCarol White\r\x07"),
                )
            }
        )
        for snapshot in source.snapshots
    )

    projection, reading = probe.project_and_measure(
        source.model_copy(update={"snapshots": snapshots})
    )

    first = projection.snapshots[0].cells
    alice = next(cell for cell in first if cell.segment_ordinal == 1 and cell.column_index == 2)
    assert alice.time_minute is None
    assert alice.time_mapping == "unmapped"
    assert reading["utility"]["mapped_time_observations"] == 6
    assert reading["utility"]["mapped_time_ratio_denominator"] == 12


def test_decreasing_same_cell_axis_requires_revision_and_releases_no_mapping(monkeypatch):
    _fixed_keys(monkeypatch)
    source = synthetic_extraction()
    snapshots = tuple(
        snapshot.model_copy(
            update={
                "cells": (
                    _cell(
                        1,
                        2,
                        "09:30\rAlice Smith\r09:00\rBob Brown\r09:00\rCarol White\r\x07",
                    ),
                )
            }
        )
        for snapshot in source.snapshots
    )

    projection, reading = probe.project_and_measure(
        source.model_copy(update={"snapshots": snapshots})
    )

    assert reading["decision"] == "revision_required"
    assert "decreasing_same_cell_time_axis" in reading["reason_codes"]
    assert reading["utility"]["decreasing_axis_cell_count"] == 3
    assert all(cell.time_minute is None for item in projection.snapshots for cell in item.cells)


def test_repeated_time_anchor_is_allowed_for_double_booking_shape(monkeypatch):
    _fixed_keys(monkeypatch)
    source = synthetic_extraction()
    snapshots = tuple(
        snapshot.model_copy(
            update={
                "cells": (
                    _cell(
                        1,
                        2,
                        "09:00\rAlice Smith\r09:00\rBob Brown\r09:10\rCarol White\r09:20\rDavid Green\r\x07",
                    ),
                )
            }
        )
        for snapshot in source.snapshots
    )

    _, reading = probe.project_and_measure(source.model_copy(update={"snapshots": snapshots}))

    assert reading["utility"]["decreasing_axis_cell_count"] == 0
    assert reading["utility"]["distinct_time_minutes"] == 3
    assert reading["utility"]["positive_interval_mode_minutes"] == 10


def test_projection_contains_no_source_text_filename_path_timestamp_key_or_mapping(monkeypatch):
    _fixed_keys(monkeypatch)
    projection, reading = probe.project_and_measure(synthetic_extraction())
    rendered = projection.model_dump_json().casefold()

    for forbidden in ("alice", "smith", "bob", "brown", "carol", "white", "david", "green"):
        assert forbidden not in rendered
    assert "c:\\" not in rendered
    assert "2016-08-24" not in rendered
    assert KEY_A.hex() not in rendered
    assert reading["privacy"]["source_value_leakage_count"] == 0
    assert reading["authority"]["fixture_provider_model_memory_product_or_publication_allowed"] is False


def test_risk_reading_has_exact_numerators_denominators_and_zero_safe_ratio(monkeypatch):
    _fixed_keys(monkeypatch)
    _, reading = probe.project_and_measure(synthetic_extraction())

    for label in (
        "record_uniqueness",
        "trajectory_uniqueness",
        "rare_trajectories",
        "record_linkage_attack",
        "trajectory_linkage_attack",
        "cross_key_structural_differencing",
    ):
        assert set(reading["risk"][label]) == {"successes", "trials", "rate"}
        assert reading["risk"][label]["trials"] > 0
    assert probe._ratio(0, 0) == {"successes": 0, "trials": 0, "rate": None}


@pytest.mark.parametrize(
    "mutator,reason",
    [
        (
            lambda value: value.model_copy(
                update={
                    "snapshots": (
                        value.snapshots[0],
                        value.snapshots[0].model_copy(
                            update={"sequence_index": 1, "observation_offset_seconds": 31}
                        ),
                    )
                }
            ),
            "no_adjacent_changes",
        ),
        (
            lambda value: value.model_copy(
                update={
                    "snapshots": tuple(
                        item.model_copy(
                            update={
                                "cells": tuple(
                                    cell.model_copy(
                                        update={
                                            "text": "\r".join(
                                                segment
                                                for segment in probe._cell_segments(cell.text)
                                                if probe._time_minute(segment) is None
                                            )
                                        }
                                    )
                                    for cell in item.cells
                                )
                            }
                        )
                        for item in value.snapshots
                    )
                }
            ),
            "insufficient_time_mapping",
        ),
    ],
)
def test_contained_but_low_utility_inputs_require_revision(monkeypatch, mutator, reason):
    _fixed_keys(monkeypatch)
    source = mutator(synthetic_extraction())
    _, reading = probe.project_and_measure(source)

    assert reading["decision"] == "revision_required"
    assert reason in reading["reason_codes"]


def test_no_structural_records_is_revision_required_with_zero_denominators(monkeypatch):
    keys = iter((KEY_A, KEY_B))
    monkeypatch.setattr(probe.secrets, "token_bytes", lambda _size: next(keys))
    source = synthetic_extraction()
    snapshots = tuple(
        item.model_copy(
            update={
                "cells": tuple(
                    cell.model_copy(
                        update={
                            "text": "\r".join(
                                segment
                                for segment in probe._cell_segments(cell.text)
                                if probe._time_minute(segment) is not None
                            )
                        }
                    )
                    for cell in item.cells
                )
            }
        )
        for item in source.snapshots
    )

    _, reading = probe.project_and_measure(source.model_copy(update={"snapshots": snapshots}))

    assert reading["decision"] == "revision_required"
    assert "no_structural_occupancy_records" in reading["reason_codes"]
    assert reading["risk"]["record_uniqueness"] == {
        "successes": 0,
        "trials": 0,
        "rate": None,
    }


def test_word_boundary_booleans_fail_closed(monkeypatch):
    extraction = synthetic_extraction().model_copy(update={"link_updates_disabled": False})
    _fixed_keys(monkeypatch)

    with pytest.raises(probe.ProbeError, match="word_extraction_boundary_failed"):
        probe.project_and_measure(extraction)


def test_phase_a_binds_exactly_80_nonrecursive_files_without_content_hash(monkeypatch, tmp_path):
    root, attempt = _configure_synthetic_paths(monkeypatch, tmp_path)
    _write_dense_day(root)
    nested = root / "nested"
    nested.mkdir()
    (nested / "Diary_20160824070000.doc").write_bytes(b"nested private bytes")
    (root / "Diary_20160825070000.doc").write_bytes(b"too small")
    oversized = root / "Diary_20160825070030.doc"
    with oversized.open("wb") as handle:
        handle.truncate(probe.MAX_FILE_BYTES + 1)

    reading = probe.bind()
    manifest = probe.BindingManifest.model_validate_json(probe.MANIFEST_PATH.read_text())

    assert reading["selected_file_count"] == probe.MAX_FILES
    assert reading["below_minimum_file_count"] == 1
    assert reading["above_maximum_file_count"] == 1
    assert reading["numeric_group_length_distribution"] == {"14": 82}
    assert reading["numeric_digit_total_distribution"] == {"14": 82}
    assert reading["archive_content_reads"] == 0
    assert reading["raw_filename_path_or_timestamp_emitted"] is False
    assert len(manifest.files) == probe.MAX_FILES
    assert all(Path(item.absolute_path).parent == root for item in manifest.files)
    assert attempt.exists()


def test_phase_a_rejects_fewer_than_80_observations(monkeypatch, tmp_path):
    root, _ = _configure_synthetic_paths(monkeypatch, tmp_path)
    _write_dense_day(root, count=79)

    with pytest.raises(probe.ProbeError, match="insufficient_dense_day_observations"):
        probe.build_binding_manifest()


def test_phase_a_rejects_two_globally_complete_date_conventions(monkeypatch, tmp_path):
    root, _ = _configure_synthetic_paths(monkeypatch, tmp_path)
    first = datetime(2016, 8, 9, 8, 0, 0)
    for index in range(probe.MAX_FILES):
        observed = first + timedelta(seconds=index * 30)
        path = root / f"08-09-16 {observed:%H-%M-%S} AM.doc"
        path.write_bytes(b"0" * (probe.MIN_FILE_BYTES + 1))

    with pytest.raises(probe.ProbeError, match="timestamp_binding_revision_required"):
        probe.build_binding_manifest()


def test_phase_a_uses_metadata_concordance_only_to_resolve_full_coverage_tie(
    monkeypatch, tmp_path
):
    root, _ = _configure_synthetic_paths(monkeypatch, tmp_path)
    first = datetime(2016, 8, 9, 8, 0, 0)
    for index in range(probe.MAX_FILES):
        observed = first + timedelta(seconds=index * 30)
        path = root / f"08-09-16 {observed:%H-%M-%S} AM.doc"
        path.write_bytes(b"0" * (probe.MIN_FILE_BYTES + 1))
        timestamp = observed.timestamp()
        os.utime(path, (timestamp, timestamp))

    manifest, reading = probe.build_binding_manifest()

    assert manifest.timestamp_convention == "month_day_two_digit_year"
    assert reading["timestamp_metadata_concordance_count"] == probe.MAX_FILES
    assert reading["timestamp_metadata_concordance_seconds"] == 86400


def test_phase_a_rejects_reparse_before_following_file_type(monkeypatch, tmp_path):
    root, _ = _configure_synthetic_paths(monkeypatch, tmp_path)
    _write_dense_day(root)
    marker = root / "unselected-link.txt"
    marker.write_text("synthetic", encoding="utf-8")
    original = probe._is_reparse
    monkeypatch.setattr(probe, "_is_reparse", lambda path: path == marker or original(path))

    with pytest.raises(probe.ProbeError, match="selected_reparse_forbidden"):
        probe.build_binding_manifest()


def test_binding_manifest_rejects_path_escape_and_parser_digest_drift(monkeypatch, tmp_path):
    root, _ = _configure_synthetic_paths(monkeypatch, tmp_path)
    _write_dense_day(root)
    probe.bind()
    payload = json.loads(probe.MANIFEST_PATH.read_text(encoding="utf-8"))
    payload["files"][0]["absolute_path"] = str(tmp_path / "escape.doc")
    probe.MANIFEST_PATH.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(probe.ProbeError, match="binding_manifest_scope_invalid"):
        probe._load_manifest()

    payload = json.loads(probe.MANIFEST_PATH.read_text(encoding="utf-8"))
    payload["files"][0]["absolute_path"] = str(root / "Diary_20160824080000.doc")
    payload["core_sha256"] = "0" * 64
    probe.MANIFEST_PATH.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(probe.ProbeError, match="binding_parser_or_path_drift"):
        probe._load_manifest()


def test_binding_manifest_rejects_metadata_timestamp_and_offset_drift(monkeypatch, tmp_path):
    root, _ = _configure_synthetic_paths(monkeypatch, tmp_path)
    _write_dense_day(root)
    probe.bind()
    pristine = json.loads(probe.MANIFEST_PATH.read_text(encoding="utf-8"))
    payload = json.loads(json.dumps(pristine))
    payload["files"][0]["size_bytes"] += 1
    probe.MANIFEST_PATH.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(probe.ProbeError, match="binding_file_metadata_drift"):
        probe._load_manifest()

    payload = json.loads(json.dumps(pristine))
    payload["files"][1]["observation_offset_seconds"] += 30
    probe.MANIFEST_PATH.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(probe.ProbeError, match="binding_offset_drift"):
        probe._load_manifest()


def test_manifest_models_enforce_file_and_total_byte_caps():
    with pytest.raises(ValidationError):
        probe.BoundFile(
            sequence_index=0,
            absolute_path="synthetic.doc",
            observation_timestamp="2016-08-24T09:00:00",
            observation_offset_seconds=0,
            size_bytes=probe.MAX_FILE_BYTES + 1,
            modified_time_ns=1,
        )

    assert probe.MAX_FILES == 80
    assert probe.MAX_TOTAL_BYTES == 128 * 1024 * 1024
    assert probe.MAX_FILE_BYTES == 8 * 1024 * 1024


def test_cleanup_removes_private_outputs_but_preserves_aggregate_receipt(monkeypatch, tmp_path):
    _, attempt = _configure_synthetic_paths(monkeypatch, tmp_path)
    attempt.mkdir(parents=True)
    probe.MANIFEST_PATH.write_text("private manifest", encoding="utf-8")
    probe.PRIVATE_PROJECTION_PATH.write_text("private projection", encoding="utf-8")

    receipt = probe._cleanup_private_outputs(
        retained=False, decision="revision_required", word_cleanup=True
    )

    assert not probe.MANIFEST_PATH.exists()
    assert not probe.PRIVATE_PROJECTION_PATH.exists()
    assert probe.CLEANUP_PATH.exists()
    assert receipt["ephemeral_key_persisted"] is False
    assert receipt["provider_network_model_calls"] == 0


def test_python_and_powershell_sources_have_no_provider_product_database_or_raw_logging():
    python_source = Path(probe.__file__).read_text(encoding="utf-8")
    powershell_source = Path("scripts/historical_diary_local_measured_privacy_probe.ps1").read_text(
        encoding="utf-8"
    )
    tree = ast.parse(python_source)
    imported = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }

    assert not imported & {
        "app",
        "boto3",
        "google",
        "httpx",
        "openai",
        "psycopg",
        "requests",
        "socket",
        "sqlalchemy",
    }
    assert "Documents.Open" in powershell_source
    assert "$false, $true, $false" in powershell_source
    assert "AutomationSecurity = 3" in powershell_source
    assert "UpdateLinksAtOpen = $false" in powershell_source
    assert "Where-Object { $baselineWordProcessIds -notcontains $_.Id }" in powershell_source
    assert "Stop-Process -Id $ownedWordProcessId" in powershell_source
    assert "Set-Content" not in powershell_source
    assert "Write-Output" not in powershell_source
    assert powershell_source.count("ConvertTo-Json") == 1


def test_failure_output_is_closed_and_forbids_automatic_content_retry(monkeypatch, tmp_path):
    _configure_synthetic_paths(monkeypatch, tmp_path)
    result = probe._failure("binding_manifest_invalid", phase="execute")

    assert result == {
        "schema_version": "historical_diary.measured_privacy_failure.v1",
        "phase": "execute",
        "decision": "blocked",
        "reason_code": "binding_manifest_invalid",
        "source_value_emitted": False,
        "archive_content_retry_authorized": False,
    }
