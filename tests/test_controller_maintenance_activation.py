"""Invented inert record bytes only; no claim that a maintenance commit exists."""

from dataclasses import FrozenInstanceError
import hashlib
import json

import pytest

from orchestration_harness.controller_maintenance_activation import (
    MaintenanceActivationError,
    parse_maintenance_activation,
)


def _bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _sha(value):
    return hashlib.sha256(value).hexdigest()


def _records():
    manifest = {
        "schema_version": "ariadne.g1b2_controller_maintenance_manifest.v1",
        "generation_id": "invented-activation-example",
        "base_commit": "f726021a71e08f81529d3eecd807a695f7ba7e3a",
        "base_tree": "e2d41bc658e836587c34bbff201462f45beca8c3",
        "source_commit": "3" * 40,
        "source_tree": "4" * 40,
        "candidate_tree": "5" * 40,
        "destination_ref": "refs/heads/codex/raisa-ariadne-recovery-g0",
        "review_record_sha256": "a" * 64,
        "review_subject_sha256": "b" * 64,
        "changed_files": [
            {
                "path": "repair.py",
                "mode": "100644",
                "before_sha256": None,
                "after_sha256": "c" * 64,
            }
        ],
        "frozen_files": [
            {
                "path": "frozen.txt",
                "mode": "100644",
                "before_sha256": "d" * 64,
                "after_sha256": "d" * 64,
            }
        ],
    }
    activation = {
        "schema_version": "ariadne.g1b2_controller_activation.v1",
        "status": "activated",
        "generation_id": manifest["generation_id"],
        "accepted_manifest_sha256": _sha(_bytes(manifest)),
        "original_controller_commit": "9334903cbdc7fe04e1c58759ca4babf0fd6d453b",
        "original_controller_tree": "b78dd45caadad2bee651aaec6601a9072a7edeaa",
        "governing_transition_commit": manifest["base_commit"],
        "maintenance_commit": "6" * 40,
        "maintenance_tree": manifest["candidate_tree"],
        "maintenance_parent": manifest["base_commit"],
        "source_commit": manifest["source_commit"],
        "source_tree": manifest["source_tree"],
        "journal_base_commit": "6" * 40,
        "publication_receipt_sha256": "e" * 64,
        "review_record_sha256": manifest["review_record_sha256"],
        "review_subject_sha256": manifest["review_subject_sha256"],
    }
    return manifest, activation


def _parse(manifest, activation):
    raw = _bytes(activation)
    return parse_maintenance_activation(
        raw, expected_sha256=_sha(raw), manifest_payload=_bytes(manifest)
    )


def test_consistent_claims_return_immutable_data_without_authority():
    manifest, activation = _records()
    result = _parse(manifest, activation)
    assert result.journal_base_commit == result.maintenance_commit == "6" * 40
    assert result.maintenance_parent == manifest["base_commit"]
    assert not hasattr(result, "admitted")
    assert not hasattr(result, "authorized")
    with pytest.raises(FrozenInstanceError):
        result.status = "different"


@pytest.mark.parametrize("field", list(_records()[1]))
@pytest.mark.parametrize("mutation", ["missing", "wrong_type"])
def test_closed_top_level_contract(field, mutation):
    manifest, activation = _records()
    if mutation == "missing":
        del activation[field]
    else:
        activation[field] = True
    with pytest.raises(MaintenanceActivationError):
        _parse(manifest, activation)


@pytest.mark.parametrize("status", ["draft", "pending", "accepted", "complete"])
def test_other_statuses_do_not_parse_as_activation(status):
    manifest, activation = _records()
    activation["status"] = status
    with pytest.raises(MaintenanceActivationError, match="status_invalid"):
        _parse(manifest, activation)


@pytest.mark.parametrize(
    "field,reason",
    [
        ("generation_id", "generation_id_mismatch"),
        ("original_controller_commit", "original_controller_commit_invalid"),
        ("original_controller_tree", "original_controller_tree_invalid"),
        ("governing_transition_commit", "governing_parent_invalid"),
        ("maintenance_parent", "governing_parent_invalid"),
        ("maintenance_tree", "manifest_identity_mismatch"),
        ("source_commit", "source_identity_mismatch"),
        ("source_tree", "source_identity_mismatch"),
        ("journal_base_commit", "journal_base_commit_invalid"),
        ("review_record_sha256", "review_identity_mismatch"),
        ("review_subject_sha256", "review_identity_mismatch"),
    ],
)
def test_individually_well_formed_cross_record_substitutions_fail(field, reason):
    manifest, activation = _records()
    activation[field] = (
        "another-generation"
        if field == "generation_id"
        else "7" * len(activation[field])
    )
    with pytest.raises(MaintenanceActivationError, match=reason):
        _parse(manifest, activation)


def test_maintenance_cannot_equal_its_governing_parent():
    manifest, activation = _records()
    activation["maintenance_commit"] = activation["journal_base_commit"] = activation[
        "maintenance_parent"
    ]
    with pytest.raises(
        MaintenanceActivationError, match="maintenance_commit_parent_invalid"
    ):
        _parse(manifest, activation)


@pytest.mark.parametrize(
    "field,reason",
    [
        ("base_commit", "manifest_identity_mismatch"),
        ("base_tree", "governing_tree_mismatch"),
    ],
)
def test_rehashed_manifest_cannot_change_governing_baseline(field, reason):
    manifest, activation = _records()
    manifest[field] = "8" * 40
    activation["accepted_manifest_sha256"] = _sha(_bytes(manifest))
    with pytest.raises(MaintenanceActivationError, match=reason):
        _parse(manifest, activation)


def test_inner_and_outer_exact_bytes_are_both_bound():
    manifest, activation = _records()
    raw = _bytes(activation)
    with pytest.raises(MaintenanceActivationError, match="payload_sha256_mismatch"):
        parse_maintenance_activation(
            raw + b" ", expected_sha256=_sha(raw), manifest_payload=_bytes(manifest)
        )
    with pytest.raises(MaintenanceActivationError, match="manifest_invalid"):
        parse_maintenance_activation(
            raw, expected_sha256=_sha(raw), manifest_payload=_bytes(manifest) + b" "
        )


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":1,"x":2}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b"[]",
        b"null",
        b"\xff",
        b"[" * 1200 + b"0" + b"]" * 1200,
    ],
)
def test_ambiguous_or_malformed_json_fails_closed(raw):
    with pytest.raises(MaintenanceActivationError):
        parse_maintenance_activation(
            raw, expected_sha256=_sha(raw), manifest_payload=b"{}"
        )


def test_foreign_protocols_size_and_extra_authority_fields_are_closed():
    class Foreign:
        def __len__(self):
            raise AssertionError("foreign length")

        def __eq__(self, other):
            raise AssertionError("foreign equality")

    with pytest.raises(MaintenanceActivationError, match="payload_invalid"):
        parse_maintenance_activation(
            Foreign(), expected_sha256="a" * 64, manifest_payload=b"{}"
        )
    with pytest.raises(MaintenanceActivationError, match="expected_sha256_invalid"):
        parse_maintenance_activation(
            b"{}", expected_sha256=Foreign(), manifest_payload=b"{}"
        )
    with pytest.raises(MaintenanceActivationError, match="payload_invalid"):
        parse_maintenance_activation(
            b" " * 65537, expected_sha256="a" * 64, manifest_payload=b"{}"
        )
    manifest, activation = _records()
    activation["admitted"] = True
    with pytest.raises(MaintenanceActivationError, match="top_level_shape_invalid"):
        _parse(manifest, activation)
