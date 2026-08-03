"""Deterministic acceptance for the Davida provider-free pure-read tranche.

Mirrors the accepted Davida boundary test style: reads public docs, contract
JSON/schema and read-only application sources; composes frames with the pure
context-desk composer; never opens a database. The SELECT-presence regression
imports only the pure case-consistent classifier helper from the acceptance
script, which itself makes no database connection at import time. Root holds
the serial database/test lease; this file is deterministic and provider-free.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.schemas.practice import (
    PractitionerDefaultLocationOut,
    PractitionerOut,
)
from app.schemas.practice_administration import ActivePracticeLocationOut
from app.services.practice.practice_administration_context_desk import (
    ResourceReferenceBinding,
    ResourceReferenceRegistry,
    compose_practice_administration_context,
)
from scripts.davida_provider_free_practice_administration_pure_read_acceptance import (
    _select_reads_present,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (
    ROOT
    / "orchestration/continuity/davida-provider-free-practice-administration-pure-read/context-contract.json"
)
SCHEMA = (
    ROOT
    / "orchestration/continuity/davida-provider-free-practice-administration-pure-read/context-contract.schema.json"
)
PLAN = ROOT / "docs/davida-provider-free-practice-administration-pure-read-plan.md"
DESIGN = ROOT / "docs/davida-provider-free-practice-administration-pure-read-design.md"
THREAT = (
    ROOT
    / "docs/security/davida-provider-free-practice-administration-pure-read-threat-model-delta.md"
)
LOCATION_READ = (
    ROOT / "app/services/practice/active_location_directory_read.py"
)
CONTEXT_DESK = (
    ROOT / "app/services/practice/practice_administration_context_desk.py"
)

UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)
OBSERVED = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)
PRACTICE_REF = "practice_synth_primary"
PRINCIPAL_REF = "principal_synth_primary"
CORRELATION_ID = "correlation-davida-pure-read-primary"

EXPECTED_BLOCKED_SOURCES = [
    {
        "name": "diary_rooms",
        "path": "GET /api/v1/diary/rooms",
        "reason": "normalizes_and_commits_during_nominal_read",
    },
    {
        "name": "diary_waiting_areas",
        "path": "GET /api/v1/diary/waiting-areas",
        "reason": "normalizes_and_commits_during_nominal_read",
    },
    {
        "name": "appointment_waiting_room_queue",
        "path": "GET /api/v1/appointments/waiting-room",
        "reason": "patient_linked_appointment_queue_closed_data",
    },
]
EXPECTED_AUTHORITY_CEILING = {
    "command": False,
    "confirmation": False,
    "write": False,
    "proposal_apply": False,
    "provider": False,
    "event_actuator": False,
    "model_to_database": False,
}
EXPECTED_LABELS = {
    "minimal": True,
    "non_authoritative": True,
    "database_truth_authoritative": True,
}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _function_body(source: str, name: str) -> str:
    start = source.find(f"def {name}(")
    assert start != -1, f"def {name}( not found in source"
    end = source.find("\ndef ", start + 1)
    if end == -1:
        end = len(source)
    return source[start:end]


def _ast_attribute_name(node) -> str:
    import ast

    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def _sample_data() -> dict:
    practitioner_id = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    location_id = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    second_location_id = uuid.UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
    practitioners = [
        PractitionerOut(
            id=practitioner_id,
            displayName="Alpha Synthetic",
            roleLabel="GP",
            active=True,
            defaultLocation=PractitionerDefaultLocationOut(
                id=location_id,
                name="Alpha Clinic",
            ),
        )
    ]
    locations = [
        ActivePracticeLocationOut(id=location_id, name="Alpha Clinic"),
        ActivePracticeLocationOut(id=second_location_id, name="Midtown Clinic"),
    ]
    registry = ResourceReferenceRegistry.build(
        (
            ResourceReferenceBinding(
                kind="practitioner",
                resource_id=practitioner_id,
                reference="prac_synth_0001",
                practice_ref=PRACTICE_REF,
            ),
            ResourceReferenceBinding(
                kind="location",
                resource_id=location_id,
                reference="loc_synth_0001",
                practice_ref=PRACTICE_REF,
            ),
            ResourceReferenceBinding(
                kind="location",
                resource_id=second_location_id,
                reference="loc_synth_0002",
                practice_ref=PRACTICE_REF,
            ),
        )
    )
    return {
        "practitioners": practitioners,
        "locations": locations,
        "registry": registry,
    }


def _compose(overrides: dict | None = None) -> dict:
    data = _sample_data()
    kwargs = {
        "practitioners": data["practitioners"],
        "active_locations": data["locations"],
        "practice_ref": PRACTICE_REF,
        "principal_ref": PRINCIPAL_REF,
        "correlation_id": CORRELATION_ID,
        "observed_at": OBSERVED,
        "resource_references": data["registry"],
    }
    if overrides:
        kwargs.update(overrides)
    return compose_practice_administration_context(**kwargs)


def test_contract_validates_against_draft_2020_12_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator(_json(SCHEMA)).validate(_json(CONTRACT))


def test_contract_is_representative_context_frame() -> None:
    contract = _json(CONTRACT)
    assert contract["schema_version"] == (
        "emr4.davida.practice_administration_context.v1"
    )
    assert contract["data_class"] == "authored_synthetic"
    assert contract["blocked_sources"] == EXPECTED_BLOCKED_SOURCES
    assert contract["authority_ceiling"] == EXPECTED_AUTHORITY_CEILING
    assert contract["labels"] == EXPECTED_LABELS
    assert re.fullmatch(r"[0-9a-f]{64}", contract["content_revision"])
    assert set(contract["frames"]) == {"practitioners", "locations"}
    for frame in contract["frames"].values():
        assert frame["label"] == "live_api_fact"
        assert frame["projection"] == "pure"
        assert frame["active_only"] is True


def test_active_location_schema_is_strict_extra_forbid() -> None:
    with pytest.raises(Exception):
        ActivePracticeLocationOut(
            id=uuid.uuid4(),
            name="Alpha Clinic",
            display_order=1,
            waiting_rooms=[],
        )
    with pytest.raises(Exception):
        ActivePracticeLocationOut(id=uuid.uuid4(), name="")
    with pytest.raises(Exception):
        ActivePracticeLocationOut(id=uuid.uuid4(), name="x" * 256)
    row = ActivePracticeLocationOut(id=uuid.uuid4(), name="Alpha Clinic")
    assert set(row.model_dump().keys()) == {"id", "name"}


def test_active_location_projection_is_pure_read() -> None:
    source = LOCATION_READ.read_text(encoding="utf-8")
    body = _function_body(source, "list_active_location_directory")

    assert "MAX_ACTIVE_LOCATION_DIRECTORY_ROWS = 200" in source
    assert "db.commit(" not in body
    assert "db.flush(" not in body
    assert "db.add(" not in body
    assert "db.delete(" not in body
    assert "normalize" not in body.lower()
    assert "db.no_autoflush" in body
    assert ".limit(MAX_ACTIVE_LOCATION_DIRECTORY_ROWS)" in body
    assert "PracticeLocation.id" in body
    assert "PracticeLocation.name" in body
    assert "order_by(" in body


def test_context_desk_has_no_db_network_provider_or_clock_read() -> None:
    import ast

    module = ast.parse(CONTEXT_DESK.read_text(encoding="utf-8"))
    imported_names: list[str] = []
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            imported_names.extend(
                alias.name.split(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_names.append(node.module.split(".")[0])
    forbidden_modules = {
        "sqlalchemy",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "http",
        "time",
    }
    assert not forbidden_modules.intersection(imported_names)
    for node in ast.walk(module):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            dotted = _ast_attribute_name(node.func)
            if dotted in {"datetime.now", "datetime.utcnow", "time.time"}:
                raise AssertionError(f"clock read forbidden: {dotted}")
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"time", "clock"}
        ):
            raise AssertionError(f"clock read forbidden: {node.func.id}")


def test_composed_frame_is_deterministic_with_recomputable_revision() -> None:
    frame_one = _compose()
    frame_two = _compose()
    assert frame_one == frame_two
    payload = {
        key: value for key, value in frame_one.items() if key != "content_revision"
    }
    recomputed = hashlib.sha256(
        _canonical(payload).encode("utf-8")
    ).hexdigest()
    assert recomputed == frame_one["content_revision"]
    assert re.fullmatch(r"[0-9a-f]{64}", frame_one["content_revision"])


def test_composed_frame_emits_no_uuid() -> None:
    serialized = json.dumps(_compose(), sort_keys=True)
    assert UUID_RE.search(serialized) is None


def test_composed_frame_uses_opaque_references() -> None:
    frame = _compose()
    practitioner_row = frame["frames"]["practitioners"]["rows"][0]
    assert practitioner_row["resource_ref"] == "prac_synth_0001"
    assert practitioner_row["default_location_ref"] == "loc_synth_0001"
    location_rows = frame["frames"]["locations"]["rows"]
    assert [row["resource_ref"] for row in location_rows] == [
        "loc_synth_0001",
        "loc_synth_0002",
    ]
    for row in location_rows:
        assert re.fullmatch(r"[A-Za-z0-9._~-]{8,64}", row["resource_ref"])


def test_composed_frame_observed_expires_exactly_two_minutes_apart() -> None:
    frame = _compose()
    observed = datetime.fromisoformat(
        frame["observed_at"].replace("Z", "+00:00")
    )
    expires = datetime.fromisoformat(frame["expires_at"].replace("Z", "+00:00"))
    assert expires - observed == timedelta(minutes=2)


def test_composed_frame_authority_ceiling_is_read_only() -> None:
    frame = _compose()
    assert frame["authority_ceiling"] == EXPECTED_AUTHORITY_CEILING
    assert all(value is False for value in frame["authority_ceiling"].values())


def test_composed_frame_blocked_sources_and_labels_are_exact() -> None:
    frame = _compose()
    assert frame["blocked_sources"] == EXPECTED_BLOCKED_SOURCES
    assert frame["labels"] == EXPECTED_LABELS


def test_composed_frame_two_fixed_live_api_fact_frames() -> None:
    frame = _compose()
    assert set(frame["frames"]) == {"practitioners", "locations"}
    for frame_name in ("practitioners", "locations"):
        sub = frame["frames"][frame_name]
        assert sub["label"] == "live_api_fact"
        assert sub["projection"] == "pure"
        assert sub["active_only"] is True
        assert sub["count"] == len(sub["rows"])
    assert frame["frames"]["practitioners"]["source"] == (
        "app.services.practice.practitioner_directory_read."
        "list_practitioner_directory"
    )
    assert frame["frames"]["locations"]["source"] == (
        "app.services.practice.active_location_directory_read."
        "list_active_location_directory"
    )


def test_composed_frame_validates_against_contract_schema() -> None:
    jsonschema = pytest.importorskip("jsonschema")
    jsonschema.Draft202012Validator(_json(SCHEMA)).validate(_compose())


def test_fail_closed_naive_time() -> None:
    with pytest.raises(ValueError):
        _compose(overrides={"observed_at": datetime(2026, 8, 3, 12, 0)})


def test_fail_closed_missing_binding() -> None:
    practitioner_id = uuid.uuid4()
    practitioner = PractitionerOut(
        id=practitioner_id,
        displayName="Unknown",
        active=True,
    )
    with pytest.raises(ValueError, match="missing"):
        _compose(overrides={"practitioners": [practitioner]})


def test_fail_closed_wrong_kind_binding() -> None:
    data = _sample_data()
    location_id = data["locations"][0].id
    practitioner = PractitionerOut(
        id=location_id,
        displayName="Wrong Kind",
        active=True,
    )
    with pytest.raises(ValueError, match="wrong-kind"):
        _compose(overrides={"practitioners": [practitioner]})


def test_fail_closed_cross_practice_binding() -> None:
    with pytest.raises(ValueError, match="cross-practice"):
        _compose(overrides={"practice_ref": "practice_synth_foreign"})


def test_fail_closed_duplicate_opaque_reference() -> None:
    first = uuid.uuid4()
    second = uuid.uuid4()
    with pytest.raises(ValueError, match="duplicate"):
        ResourceReferenceRegistry.build(
            (
                ResourceReferenceBinding(
                    kind="practitioner",
                    resource_id=first,
                    reference="dup_synth_0001",
                    practice_ref="practice_synth_primary",
                ),
                ResourceReferenceBinding(
                    kind="location",
                    resource_id=second,
                    reference="dup_synth_0001",
                    practice_ref="practice_synth_primary",
                ),
            )
        )


def test_fail_closed_inactive_practitioner() -> None:
    data = _sample_data()
    practitioner = PractitionerOut(
        id=data["practitioners"][0].id,
        displayName="Inactive",
        active=False,
    )
    with pytest.raises(ValueError, match="inactive"):
        _compose(overrides={"practitioners": [practitioner]})


def test_fail_closed_unsupported_correlation_id() -> None:
    with pytest.raises(ValueError, match="correlation_id"):
        _compose(overrides={"correlation_id": "not-a-correlation"})


def _mutation_fails(mutator) -> None:
    """Assert a mutated contract fails Draft202012 schema validation."""
    jsonschema = pytest.importorskip("jsonschema")
    contract = _json(CONTRACT)
    mutator(contract)
    validator = jsonschema.Draft202012Validator(_json(SCHEMA))
    errors = list(validator.iter_errors(contract))
    assert errors, "mutated contract unexpectedly passed schema validation"


def test_mutation_authority_command_true_fails() -> None:
    _mutation_fails(lambda c: c["authority_ceiling"].update(command=True))


def test_mutation_authority_write_true_fails() -> None:
    _mutation_fails(lambda c: c["authority_ceiling"].update(write=True))


def test_mutation_authority_event_actuator_true_fails() -> None:
    _mutation_fails(
        lambda c: c["authority_ceiling"].update(event_actuator=True)
    )


def test_mutation_data_class_real_fails() -> None:
    _mutation_fails(lambda c: c.update(data_class="real"))


def test_mutation_practitioner_label_model_fails() -> None:
    _mutation_fails(
        lambda c: c["frames"]["practitioners"].update(label="model_interpretation")
    )


def test_mutation_location_source_changed_fails() -> None:
    _mutation_fails(
        lambda c: c["frames"]["locations"].update(
            source="app.services.practice.other.list_locations"
        )
    )


def test_mutation_active_only_false_fails() -> None:
    _mutation_fails(
        lambda c: c["frames"]["practitioners"].update(active_only=False)
    )


def test_mutation_unknown_top_level_field_fails() -> None:
    _mutation_fails(lambda c: c.update(unauthorized_apply=True))


def test_mutation_unknown_row_field_fails() -> None:
    _mutation_fails(
        lambda c: c["frames"]["practitioners"]["rows"][0].update(
            internal_id="secret"
        )
    )


def test_mutation_removed_required_field_fails() -> None:
    _mutation_fails(lambda c: c.pop("schema_version"))


def test_mutation_reordered_blocked_sources_fails() -> None:
    def mutate(contract: dict) -> None:
        blocked = contract["blocked_sources"]
        blocked.insert(0, blocked.pop())

    _mutation_fails(mutate)


def test_mutation_blocked_source_path_changed_fails() -> None:
    def mutate(contract: dict) -> None:
        contract["blocked_sources"][0]["path"] = "GET /api/v1/diary/cubicles"

    _mutation_fails(mutate)


def test_mutation_count_exceeds_bounded_maximum_fails() -> None:
    _mutation_fails(lambda c: c["frames"]["practitioners"].update(count=201))


def test_mutation_bad_content_revision_fails() -> None:
    _mutation_fails(lambda c: c.update(content_revision="not-a-sha256"))


def test_mutation_labels_minimal_false_fails() -> None:
    _mutation_fails(lambda c: c["labels"].update(minimal=False))


def test_mutation_unknown_authority_ceiling_field_fails() -> None:
    _mutation_fails(
        lambda c: c["authority_ceiling"].update(deployment=True)
    )


def test_mutation_extra_frame_key_fails() -> None:
    _mutation_fails(lambda c: c["frames"].update(rooms={"count": 0}))


def test_public_artifacts_state_non_authority_and_branding_exclusion() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (PLAN, DESIGN, THREAT)
    )

    assert "database truth remains authoritative" in combined
    assert "provider-free" in combined
    assert "no runtime claim" in combined
    assert "docs/branding/" in combined
    assert "authority_ceiling" in combined or "authority ceiling" in combined
    assert "fail closed" in combined
    assert "provider_free_in_process_backend_postgres" in combined


def test_select_presence_classifier_requires_both_pure_table_reads() -> None:
    # Mixed-case SQL exactly as SQLAlchemy emits it: upper-case keywords,
    # lower-case identifiers. The historical classifier upper-cased the
    # statement and then searched for lower-case fragments, so these never
    # matched and `select_reads_present` was always false. This assertion is
    # the deterministic regression for that mixed-case defect.
    lower_mixed = [
        "SELECT practice_locations.id, practice_locations.name\n"
        "FROM practice_locations\n"
        "WHERE practice_locations.practice_id = $1 "
        "AND practice_locations.is_active = true",
        "SELECT practitioners.id\n"
        "FROM practitioners\n"
        "WHERE practitioners.practice_id = $1 "
        "AND practitioners.is_active = true",
    ]
    upper_mixed = [
        "SELECT ID FROM PRACTICE_LOCATIONS WHERE IS_ACTIVE = TRUE",
        "SELECT ID FROM PRACTITIONERS WHERE IS_ACTIVE = TRUE",
    ]
    assert _select_reads_present(lower_mixed) is True
    assert _select_reads_present(upper_mixed) is True


def test_select_presence_classifier_rejects_missing_table_or_dml_ddl() -> None:
    # Both pure tables must be present: one read alone is insufficient.
    assert _select_reads_present(["SELECT id FROM practice_locations"]) is False
    assert _select_reads_present(["SELECT id FROM practitioners"]) is False
    # No captured statements prove no read.
    assert _select_reads_present([]) is False
    # Any DML statement makes the gate fail even when both reads are present.
    assert (
        _select_reads_present(
            [
                "SELECT id FROM practice_locations",
                "SELECT id FROM practitioners",
                "UPDATE practitioners SET is_active = false",
            ]
        )
        is False
    )
    # Any DDL statement makes the gate fail even when both reads are present.
    assert (
        _select_reads_present(
            [
                "SELECT id FROM practice_locations",
                "SELECT id FROM practitioners",
                "CREATE TABLE practitioners_tmp (id uuid)",
            ]
        )
        is False
    )
