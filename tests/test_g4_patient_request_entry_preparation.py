"""Direct ordinary checks for the separate, prospective G4 request profile."""

import copy
import hashlib
import json
from pathlib import Path

from orchestration_harness import bounded_g1b, raisa_policy


def test_existing_staff_move_scope_is_not_widened():
    assert bounded_g1b.G4_KINDS == {
        "enable_g4_staff_move", "implement_g4_staff_move"}
    assert bounded_g1b.G4_PRODUCT == {
        "app/routers/appointments.py", "app/schemas/appointments.py",
        "app/services/appointment_list_read_adapter.py",
        "tests/test_stage1_staff_move.py",
        "tests/test_stage1_appointment_readback.py"}
    assert raisa_policy.G4_STAFF_MOVE_PROFILE != raisa_policy.G4_PATIENT_REQUEST_PROFILE


def test_request_scope_names_one_additive_migration_and_separate_kinds():
    assert bounded_g1b.G4_PATIENT_REQUEST_KINDS == {
        "enable_g4_patient_request", "implement_g4_patient_request"}
    assert bounded_g1b.G4_PATIENT_REQUEST_PRODUCT == set(
        raisa_policy.G4_PATIENT_REQUEST_PRODUCT_PATHS)
    assert len(bounded_g1b.G4_PATIENT_REQUEST_PRODUCT) == 13
    assert bounded_g1b.G4_PATIENT_REQUEST_SELECTED_MIGRATION_PARENT == "a6b7c8d9e0f1"
    assert bounded_g1b.G4_PATIENT_REQUEST_MIGRATION.split("/")[-1].startswith("b7c8d9e0f1a2_")
    assert {path for path in bounded_g1b.G4_PATIENT_REQUEST_PRODUCT
            if path.startswith("alembic/versions/")} == {
        bounded_g1b.G4_PATIENT_REQUEST_MIGRATION}
    assert bounded_g1b.operation_paths("enable_g4_patient_request") == (
        bounded_g1b.G4_PATIENT_REQUEST_CONTROL)
    assert bounded_g1b.operation_paths("implement_g4_patient_request") == (
        bounded_g1b.G4_PATIENT_REQUEST_PRODUCT)


def test_request_profile_keeps_runtime_and_providers_closed():
    profile = raisa_policy.g4_patient_request_profile()
    assert profile["expected_current_gate"] == "G4"
    assert profile["expected_gate_status"] == "active_bounded_patient_request"
    assert profile["admitted_task_classes"] == ["g4_patient_request_staff_create"]
    assert profile["allowed_paths"] == list(
        raisa_policy.G4_PATIENT_REQUEST_PRODUCT_PATHS)
    assert "migration_change" in profile["allowed_effects"]
    assert "provider_invocation" in profile["forbidden_effects"]
    assert "protected_ref_movement" in profile["forbidden_effects"]
    assert "migration_change" in bounded_g1b.operation_effects(
        "implement_g4_patient_request")


def test_selected_migration_map_rejects_drift_and_revision_collisions():
    raw = Path(bounded_g1b.G4_PATIENT_REQUEST_SELECTED_MAP_PATH).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == (
        bounded_g1b.G4_PATIENT_REQUEST_SELECTED_MAP_SHA256)
    mapping = json.loads(raw)
    bounded_g1b._g4_patient_request_check_selected_map(mapping)

    drift = copy.deepcopy(mapping)
    drift["source_manifest_sha256"] = "0" * 64
    try:
        bounded_g1b._g4_patient_request_check_selected_map(drift)
    except bounded_g1b.BoundedG1BError as error:
        assert error.reason_code == "bounded_g4_patient_request_selected_map_identity"
    else:
        raise AssertionError("selected migration-map provenance drift admitted")

    for duplicate in ("b7c8d9e0f1a2", "a6b7c8d9e0f1"):
        collision = copy.deepcopy(mapping)
        row = next(row for row in collision["physical_rows"]
                   if row["revision"]["value"] == "274919209522")
        row["revision"]["value"] = duplicate
        edge = next(edge for edge in collision["revision_edges"]
                    if edge["revision"] == "274919209522")
        edge["revision"] = duplicate
        try:
            bounded_g1b._g4_patient_request_check_selected_map(collision)
        except bounded_g1b.BoundedG1BError as error:
            assert error.reason_code == (
                "bounded_g4_patient_request_selected_map_revision_unique")
        else:
            raise AssertionError("selected migration revision collision admitted")
