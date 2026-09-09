"""Pure authored-data tests for maintenance request parsing."""

from __future__ import annotations

import hashlib
from types import MappingProxyType

import pytest

from orchestration_harness.controller_maintenance_request import (
    MaintenanceRequestError,
    canonical_bytes,
    parse_request,
)


def _manifest():
    return {
        "schema_version": "ariadne.g1b2_controller_maintenance_manifest.v1",
        "generation_id": "synthetic-request-v1",
        "base_commit": "a" * 40,
        "base_tree": "b" * 40,
        "source_commit": "c" * 40,
        "source_tree": "d" * 40,
        "candidate_tree": "e" * 40,
        "destination_ref": "refs/heads/codex/raisa-ariadne-recovery-g0",
        "review_record_sha256": "0" * 64,
        "review_subject_sha256": "1" * 64,
        "changed_files": [
            {
                "path": "owned.py",
                "mode": "100644",
                "before_sha256": None,
                "after_sha256": "2" * 64,
            }
        ],
        "frozen_files": [
            {
                "path": "frozen.py",
                "mode": "100644",
                "before_sha256": "3" * 64,
                "after_sha256": "3" * 64,
            }
        ],
    }


def _request(tmp_path):
    review = {
        "schema_version": "ariadne.maintenance_operational_review.v1",
        "review_id": "review-v1",
        "verdict": "PASS",
        "findings": [],
        "subject_sha256": "1" * 64,
    }
    manifest = _manifest()
    manifest["review_record_sha256"] = hashlib.sha256(
        canonical_bytes(review)
    ).hexdigest()
    payload = {
        "schema_version": "ariadne.maintenance_operation_request.v1",
        "operation": "evaluate",
        "target_root": str(tmp_path / "target"),
        "scratch_parent": str(tmp_path / "scratch"),
        "receipt_directory": str(tmp_path / "receipts"),
        "manifest": manifest,
        "manifest_sha256": hashlib.sha256(canonical_bytes(manifest)).hexdigest(),
        "review": review,
        "owner_approval_sha256": "4" * 64,
        "remote_policy": {
            "normalized_push_url": "file:///synthetic-origin",
            "rewrite_count": 0,
        },
        "protected_refs": {
            key: "5" * 40
            for key in (
                "refs/heads/master",
                "refs/heads/handoff/current",
                "refs/remotes/origin/master",
                "refs/remotes/origin/handoff/current",
            )
        },
        "preservation_paths": [str(tmp_path / "preserve")],
        "original_controller": {
            "root": str(tmp_path / "controller"),
            "commit": "6" * 40,
            "tree": "7" * 40,
            "files": [{"path": "controller.py", "sha256": "8" * 64}],
        },
        "preserved_files": [
            {"path": str(tmp_path / "preserve" / "bundle"), "sha256": "9" * 64}
        ],
    }
    return payload


def _encoded(value):
    return canonical_bytes(value)


def test_valid_request_returns_immutable_consistency_record(tmp_path):
    payload = _request(tmp_path)
    result = parse_request(_encoded(payload))
    assert result.operation == "evaluate"
    assert result.manifest.generation_id == "synthetic-request-v1"
    assert isinstance(result.remote_policy, MappingProxyType)
    assert isinstance(result.preservation_paths, tuple)
    with pytest.raises(TypeError):
        result.remote_policy["new"] = "value"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value.update({"extra": 1}),
        lambda value: value.pop("operation"),
    ],
)
def test_unknown_or_missing_top_level_keys_rejected(tmp_path, mutation):
    payload = _request(tmp_path)
    mutation(payload)
    with pytest.raises(MaintenanceRequestError, match="top_level_shape_invalid"):
        parse_request(_encoded(payload))


def test_duplicate_and_nonfinite_json_are_rejected(tmp_path):
    payload = _encoded(_request(tmp_path))
    duplicate = payload[:-1] + b',"operation":"execute"}'
    with pytest.raises(MaintenanceRequestError, match="duplicate_key"):
        parse_request(duplicate)
    nonfinite = payload.replace(b'"operation":"evaluate"', b'"operation":NaN')
    with pytest.raises(MaintenanceRequestError, match="json_constant_forbidden"):
        parse_request(nonfinite)


def test_wrong_operation_and_absolute_path_are_rejected(tmp_path):
    payload = _request(tmp_path)
    payload["operation"] = "publish"
    with pytest.raises(MaintenanceRequestError, match="operation_invalid"):
        parse_request(_encoded(payload))
    payload = _request(tmp_path)
    payload["target_root"] = "relative/../target"
    with pytest.raises(MaintenanceRequestError, match="target_root_invalid"):
        parse_request(_encoded(payload))


def test_bad_manifest_digest_is_rejected(tmp_path):
    payload = _request(tmp_path)
    payload["manifest_sha256"] = "a" * 64
    with pytest.raises(MaintenanceRequestError, match="manifest_invalid"):
        parse_request(_encoded(payload))


@pytest.mark.parametrize("field,value", [("verdict", "FAIL"), ("findings", [{"x": 1}])])
def test_review_status_or_findings_are_rejected(tmp_path, field, value):
    payload = _request(tmp_path)
    payload["review"][field] = value
    with pytest.raises(MaintenanceRequestError):
        parse_request(_encoded(payload))


@pytest.mark.parametrize("field", ["review_record_sha256", "review_subject_sha256"])
def test_review_digest_or_subject_mismatch_is_rejected(tmp_path, field):
    payload = _request(tmp_path)
    payload["manifest"][field] = "b" * 64
    payload["manifest_sha256"] = hashlib.sha256(
        canonical_bytes(payload["manifest"])
    ).hexdigest()
    reason = (
        "review_record_hash_mismatch"
        if field == "review_record_sha256"
        else "review_subject_hash_mismatch"
    )
    with pytest.raises(MaintenanceRequestError, match=reason):
        parse_request(_encoded(payload))


def test_protected_ref_shape_and_value_mismatch_are_rejected(tmp_path):
    payload = _request(tmp_path)
    del payload["protected_refs"]["refs/heads/master"]
    with pytest.raises(MaintenanceRequestError, match="protected_refs_invalid"):
        parse_request(_encoded(payload))
    payload = _request(tmp_path)
    payload["protected_refs"]["refs/heads/master"] = "a" * 40
    with pytest.raises(MaintenanceRequestError, match="protected_refs_mismatch"):
        parse_request(_encoded(payload))


def test_duplicate_preservation_and_controller_paths_are_rejected(tmp_path):
    payload = _request(tmp_path)
    payload["preservation_paths"].append(payload["preservation_paths"][0])
    with pytest.raises(MaintenanceRequestError, match="preservation_path_duplicate"):
        parse_request(_encoded(payload))
    payload = _request(tmp_path)
    payload["original_controller"]["files"].append(
        payload["original_controller"]["files"][0]
    )
    with pytest.raises(MaintenanceRequestError, match="controller_file_duplicate"):
        parse_request(_encoded(payload))


def test_remote_policy_requires_an_object(tmp_path):
    payload = _request(tmp_path)
    payload["remote_policy"] = []
    with pytest.raises(MaintenanceRequestError, match="remote_policy_invalid"):
        parse_request(_encoded(payload))
