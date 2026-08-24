import hashlib
import inspect
import json
from pathlib import Path

import pytest

from orchestration_harness import historical_diary_first_use_candidate_gate as gate
from orchestration_harness import historical_diary_first_use_materialiser as materialiser
from orchestration_harness import historical_diary_local_measured_privacy_probe as probe


PLAN = Path(
    "docs/raisa-local-only-historical-derived-minimised-check-in-context-"
    "scenario-first-use-materialisation-rehearsal-plan.md"
)
THREAT = Path(
    "docs/security/raisa-local-only-historical-derived-minimised-check-in-context-"
    "scenario-first-use-materialisation-rehearsal-threat-model-delta.md"
)
CONTRACT = Path(
    "orchestration/continuity/raisa-provider-free-governance-clockwork-"
    "historical-derived-first-use-materialisation-subgate-rehearsal/"
    "next-tranche-contract.json"
)
EXTRACTOR = Path("scripts/historical_diary_local_measured_privacy_probe.ps1")


def _cell(
    token_digit: str,
    *,
    sequence: int,
    row: int,
    resource_column: int = 1,
    format_bucket: str = "format_0",
) -> probe.ProjectedCell:
    return probe.ProjectedCell(
        cell_token=f"cell_{token_digit * 32}",
        content_token=f"content_{token_digit * 32}",
        sequence_index=sequence,
        observation_interval_start_seconds=sequence * 600,
        observation_interval_end_seconds=sequence * 600 + 30,
        table_index=1,
        row_index=row,
        column_index=resource_column,
        segment_ordinal=0,
        resource_ordinal=f"resource_1_{resource_column}",
        time_minute=None,
        time_mapping="unmapped",
        format_bucket=format_bucket,
        length_bucket="short",
        content_bucket="structural_text",
        detector_categories=(),
    )


def _snapshot(
    sequence: int, cells: tuple[probe.ProjectedCell, ...]
) -> probe.ProjectedSnapshot:
    return probe.ProjectedSnapshot(
        sequence_index=sequence,
        observation_interval_start_seconds=sequence * 600,
        observation_interval_end_seconds=sequence * 600 + 30,
        cells=cells,
    )


def _synthetic_projection() -> probe.PrivateProjection:
    snapshots = (
        _snapshot(
            0,
            (
                _cell("a", sequence=0, row=1),
                _cell("b", sequence=0, row=2),
            ),
        ),
        _snapshot(
            1,
            (
                _cell("a", sequence=1, row=1, format_bucket="format_1"),
                _cell("c", sequence=1, row=3, resource_column=2),
            ),
        ),
        _snapshot(
            2,
            (
                _cell("a", sequence=2, row=4, format_bucket="format_1"),
                _cell("c", sequence=2, row=3, resource_column=2),
                _cell("d", sequence=2, row=5, resource_column=2),
            ),
        ),
        _snapshot(
            4,
            (
                _cell("a", sequence=4, row=4, format_bucket="format_1"),
                _cell("c", sequence=4, row=3, resource_column=2),
                _cell("d", sequence=4, row=5, resource_column=2),
            ),
        ),
    )
    return probe.PrivateProjection(
        schema_version="historical_diary.private_derived_grid_projection.v3",
        evidence_label="private_derived_ignored_local_only",
        source_day_policy="relative_day_zero_only",
        source_filename_or_path_emitted=False,
        exact_source_timestamp_emitted=False,
        key_or_mapping_emitted=False,
        page_coordinate_or_distance_emitted=False,
        snapshots=snapshots,
    )


def test_plan_and_contract_freeze_one_gate_bound_local_write_or_nothing():
    plan = PLAN.read_text(encoding="utf-8")
    threat = THREAT.read_text(encoding="utf-8")
    contract_bytes = CONTRACT.read_bytes()
    contract = json.loads(contract_bytes)

    assert hashlib.sha256(contract_bytes).hexdigest() == materialiser.CONTRACT_SHA256
    assert contract["operation_id"] == materialiser.OPERATION_ID
    assert contract["candidate_gate_source"] == materialiser.GATE_SOURCE_COMMIT
    assert contract["private_input_ceiling"]["retry_count"] == 0
    assert contract["writer_ceiling"]["maximum_fixture_count"] == 1
    assert "There is no second bind, no second content run" in plan
    assert "persisted slots are small ephemeral ordinals" in threat


def test_existing_binder_defaults_and_all_three_word_profiles_remain_exact():
    signature = inspect.signature(probe.build_binding_manifest)
    assert signature.parameters["attempt_root"].default is None
    assert signature.parameters["core_path"].default is None
    assert signature.parameters["extractor_path"].default is None
    function_source = inspect.getsource(probe.build_binding_manifest)
    assert "attempt_root = ATTEMPT_ROOT if attempt_root is None" in function_source
    assert "core_path = CORE_PATH if core_path is None" in function_source
    assert "extractor_path = EXTRACTOR_PATH if extractor_path is None" in function_source

    source = EXTRACTOR.read_text(encoding="utf-8")
    assert '"HistoricalMeasuredProbe"' in source
    assert '"HistoricalFirstUseMaterialisation"' in source
    assert '"AuthoredSyntheticRecovery"' in source
    assert "2026-08-24-leading-token-v3" in source
    assert "2026-08-24-check-in-context-v1" in source


def test_direct_cli_wrapper_bootstraps_the_repository_import_path():
    source = Path(
        "scripts/raisa_local_only_historical_derived_minimised_check_in_context_"
        "scenario_first_use_materialisation_rehearsal.py"
    ).read_text(encoding="utf-8")

    assert "Path(__file__).resolve().parents[1]" in source
    assert "sys.path.insert(0" in source


def test_observation_timeline_reduces_to_an_admitted_closed_candidate():
    candidate = materialiser.derive_candidate(_synthetic_projection())

    assert candidate is not None
    assert candidate.relative_day_offset == 0
    assert all(event.relative_minute in {0, 10, 30} for event in candidate.events)
    assert all(event.synthetic_subject_slot <= 3 for event in candidate.events)
    assert all(event.resource_slot <= 1 for event in candidate.events)
    result = gate.evaluate(materialiser._candidate_envelope(candidate))
    assert result.decision == "admitted_for_exact_declared_artifact_only"
    assert result.binding is not None
    assert result.binding.candidate_sha256 == hashlib.sha256(
        materialiser._candidate_bytes(candidate)
    ).hexdigest()


def test_candidate_bytes_contain_only_closed_relative_structural_fields():
    candidate = materialiser.derive_candidate(_synthetic_projection())
    assert candidate is not None
    parsed = json.loads(materialiser._candidate_bytes(candidate))

    assert set(parsed) == {"schema_version", "relative_day_offset", "events"}
    assert all(
        set(event)
        == {
            "schema_version",
            "event_kind",
            "relative_minute",
            "synthetic_subject_slot",
            "resource_slot",
        }
        for event in parsed["events"]
    )
    forbidden = (
        '"cell_',
        '"content_',
        '"resource_1_',
        '"source_',
        '"filename',
        '"path',
    )
    encoded = materialiser._candidate_bytes(candidate).decode("ascii")
    assert all(token not in encoded for token in forbidden)


def test_atomic_writer_creates_one_exact_digest_bound_fixture(tmp_path, monkeypatch):
    candidate = materialiser.derive_candidate(_synthetic_projection())
    assert candidate is not None
    fixture_root = tmp_path / "local_data/historical-diary-trove/derived-scenarios/run"
    fixture = fixture_root / "scenario.json"
    temporary = fixture_root / ".scenario.json.tmp"
    monkeypatch.setattr(materialiser, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        materialiser,
        "ATTEMPT_ROOT",
        tmp_path / "local_data/historical-diary-trove/first-use-attempts/run",
    )
    monkeypatch.setattr(materialiser, "FIXTURE_ROOT", fixture_root)
    monkeypatch.setattr(materialiser, "FIXTURE_PATH", fixture)
    monkeypatch.setattr(materialiser, "FIXTURE_TEMP_PATH", temporary)
    digest = gate.canonical_candidate_sha256(candidate)

    assert materialiser._write_fixture(candidate, digest) == digest
    assert sorted(path.name for path in fixture_root.iterdir()) == ["scenario.json"]
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == digest


def test_atomic_writer_removes_partial_output_after_replace_failure(
    tmp_path, monkeypatch
):
    candidate = materialiser.derive_candidate(_synthetic_projection())
    assert candidate is not None
    fixture_root = tmp_path / "local_data/historical-diary-trove/derived-scenarios/run"
    monkeypatch.setattr(materialiser, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        materialiser,
        "ATTEMPT_ROOT",
        tmp_path / "local_data/historical-diary-trove/first-use-attempts/run",
    )
    monkeypatch.setattr(materialiser, "FIXTURE_ROOT", fixture_root)
    monkeypatch.setattr(materialiser, "FIXTURE_PATH", fixture_root / "scenario.json")
    monkeypatch.setattr(
        materialiser, "FIXTURE_TEMP_PATH", fixture_root / ".scenario.json.tmp"
    )
    monkeypatch.setattr(materialiser.os, "replace", lambda *_args: (_ for _ in ()).throw(OSError()))

    with pytest.raises(OSError):
        materialiser._write_fixture(candidate, gate.canonical_candidate_sha256(candidate))
    assert not fixture_root.exists()


def test_failure_reasons_never_copy_paths_or_unbounded_exception_text():
    assert materialiser._sanitized_reason(OSError("C:/private/person.doc")) == (
        "internal_local_materialisation_failure"
    )
    assert materialiser._sanitized_reason(
        materialiser.MaterialisationError("candidate_bytes_digest_mismatch")
    ) == "candidate_bytes_digest_mismatch"
    assert materialiser._sanitized_reason(
        probe.ProbeError("timestamp_binding_revision_required:{private material}")
    ) == "timestamp_binding_revision_required"


def test_materialiser_has_no_provider_network_product_or_database_surface():
    source = Path(materialiser.__file__).read_text(encoding="utf-8")
    forbidden = (
        "requests",
        "httpx",
        "socket",
        "sqlalchemy",
        "from app",
        "import app",
        "clipboard",
        "telemetry",
    )
    assert all(token not in source for token in forbidden)
