"""Authored structural records only; no Git, filesystem or authority activation."""

from dataclasses import FrozenInstanceError
import hashlib
import json

import pytest

from orchestration_harness.controller_maintenance_record import (
    MaintenanceRecordError,
    parse_maintenance_record,
)


def _record():
    return {
        "schema_version": "ariadne.g1b2_controller_maintenance_manifest.v1",
        "generation_id": "authored-maintenance-01",
        "base_commit": "1" * 40,
        "base_tree": "2" * 40,
        "source_commit": "3" * 40,
        "source_tree": "4" * 40,
        "candidate_tree": "5" * 40,
        "destination_ref": "refs/heads/codex/raisa-ariadne-recovery-g0",
        "review_record_sha256": "a" * 64,
        "review_subject_sha256": "b" * 64,
        "changed_files": [
            {
                "path": "orchestration_harness/one.py",
                "mode": "100644",
                "before_sha256": "c" * 64,
                "after_sha256": "d" * 64,
            },
            {
                "path": "orchestration_harness/two.py",
                "mode": "100644",
                "before_sha256": None,
                "after_sha256": "e" * 64,
            },
        ],
        "frozen_files": [
            {
                "path": "orchestration/programme/current-state.json",
                "mode": "100644",
                "before_sha256": "f" * 64,
                "after_sha256": "f" * 64,
            },
        ],
    }


def _parse(value):
    raw = json.dumps(value).encode()
    return parse_maintenance_record(
        raw, expected_sha256=hashlib.sha256(raw).hexdigest()
    )


def test_nested_sibling_files_parse_into_deeply_immutable_records():
    value = _record()
    record = _parse(value)
    assert tuple(item.path for item in record.changed_files) == (
        "orchestration_harness/one.py",
        "orchestration_harness/two.py",
    )
    assert record.frozen_files[0].before_sha256 == record.frozen_files[0].after_sha256
    value["changed_files"][0]["path"] = "changed-after-parsing"
    assert record.changed_files[0].path == "orchestration_harness/one.py"
    with pytest.raises(FrozenInstanceError):
        record.generation_id = "changed"
    with pytest.raises(FrozenInstanceError):
        record.changed_files[0].path = "changed"


@pytest.mark.parametrize("field", list(_record()))
@pytest.mark.parametrize("kind", ["missing", "foreign_type"])
def test_every_top_level_field_is_required_and_typed(field, kind):
    value = _record()
    if kind == "missing":
        del value[field]
    else:
        value[field] = True
    with pytest.raises(MaintenanceRecordError):
        _parse(value)


def test_unrecognised_authority_flag_is_not_admitted():
    value = _record()
    value["accepted"] = True
    with pytest.raises(MaintenanceRecordError, match="top_level_shape_invalid"):
        _parse(value)


@pytest.mark.parametrize(
    "path",
    [
        "",
        "/absolute.py",
        "../escape.py",
        "a//b.py",
        "a/./b.py",
        "a/../b.py",
        ".git/config",
        "a/.GIT/index",
        "a/file.",
        "a/CON.txt",
        "a/COM1.py",
        "a/Lpt9.txt",
        "a\\b.py",
        "C:/file.py",
        ":(glob)**",
        "a/space name.py",
        "a/é.py",
    ],
)
def test_path_alias_and_expansion_forms_are_closed(path):
    value = _record()
    value["changed_files"][0]["path"] = path
    with pytest.raises(MaintenanceRecordError):
        _parse(value)


@pytest.mark.parametrize(
    "first,second",
    [
        ("x.py", "x.py"),
        ("x.py", "X.py"),
        ("Dir/a.py", "dir/b.py"),
        ("a", "a/b.py"),
        ("a/b.py", "a"),
    ],
)
def test_duplicates_case_aliases_and_directory_collisions_are_closed(first, second):
    value = _record()
    value["changed_files"][0]["path"] = first
    value["changed_files"][1]["path"] = second
    with pytest.raises(MaintenanceRecordError):
        _parse(value)


def test_changed_and_frozen_paths_cannot_overlap():
    value = _record()
    value["changed_files"][0]["path"] = value["frozen_files"][0]["path"]
    with pytest.raises(MaintenanceRecordError, match="path_duplicate_or_overlap"):
        _parse(value)


@pytest.mark.parametrize(
    "collection,key,value",
    [
        ("changed_files", "mode", "100755"),
        ("changed_files", "mode", 100644),
        ("changed_files", "before_sha256", True),
        ("changed_files", "after_sha256", None),
        ("changed_files", "after_sha256", "c" * 64),
        ("frozen_files", "before_sha256", None),
        ("frozen_files", "after_sha256", "e" * 64),
    ],
)
def test_file_type_and_before_after_invariants(collection, key, value):
    record = _record()
    record[collection][0][key] = value
    with pytest.raises(MaintenanceRecordError):
        _parse(record)


@pytest.mark.parametrize(
    "collection,limit", [("changed_files", 32), ("frozen_files", 128)]
)
def test_file_collections_are_nonempty_and_bounded(collection, limit):
    record = _record()
    record[collection] *= limit + 1
    with pytest.raises(MaintenanceRecordError, match="file_list_invalid"):
        _parse(record)
    record[collection] = []
    with pytest.raises(MaintenanceRecordError, match="file_list_invalid"):
        _parse(record)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"duplicate":1,"duplicate":2}',
        b'{"x":{"duplicate":1,"duplicate":2}}',
        b'{"x":NaN}',
        b'{"x":Infinity}',
        b'{"x":-Infinity}',
        b"\xff",
        b"[]",
        b"null",
        b"{} trailing",
        b"[" * 1200 + b"0" + b"]" * 1200,
    ],
)
def test_ambiguous_nonfinite_malformed_and_deep_json_is_closed(raw):
    with pytest.raises(MaintenanceRecordError):
        parse_maintenance_record(raw, expected_sha256=hashlib.sha256(raw).hexdigest())


def test_payload_bytes_require_the_exact_external_digest():
    raw = json.dumps(_record()).encode()
    with pytest.raises(MaintenanceRecordError, match="payload_sha256_mismatch"):
        parse_maintenance_record(raw, expected_sha256="0" * 64)
    with pytest.raises(MaintenanceRecordError, match="expected_sha256_invalid"):
        parse_maintenance_record(raw, expected_sha256="A" * 64)
    with pytest.raises(MaintenanceRecordError, match="payload_invalid"):
        parse_maintenance_record(b" " * 65537, expected_sha256="0" * 64)


def test_foreign_caller_protocols_are_not_invoked():
    class Foreign:
        def __len__(self):
            raise AssertionError("caller length invoked")

        def __eq__(self, other):
            raise AssertionError("caller equality invoked")

        def __str__(self):
            raise AssertionError("caller conversion invoked")

    with pytest.raises(MaintenanceRecordError, match="expected_sha256_invalid"):
        parse_maintenance_record(b"{}", expected_sha256=Foreign())
    with pytest.raises(MaintenanceRecordError, match="payload_invalid"):
        parse_maintenance_record(Foreign(), expected_sha256="0" * 64)


@pytest.mark.parametrize("path", ["x" * 513, "/".join(["a"] * 33)])
def test_path_prefix_work_is_bounded(path):
    value = _record()
    value["changed_files"][0]["path"] = path
    with pytest.raises(MaintenanceRecordError, match="path_invalid"):
        _parse(value)


@pytest.mark.parametrize("collection", ["changed_files", "frozen_files"])
@pytest.mark.parametrize("mutation", ["missing", "extra"])
def test_file_record_keys_are_exact(collection, mutation):
    value = _record()
    file = value[collection][0]
    if mutation == "missing":
        del file["before_sha256"]
    else:
        file["approved"] = True
    with pytest.raises(MaintenanceRecordError, match="file_shape_invalid"):
        _parse(value)


@pytest.mark.parametrize("changed,frozen", [("a", "a/b.py"), ("Dir/a.py", "dir/b.py")])
def test_cross_collection_hierarchy_and_case_aliases_are_closed(changed, frozen):
    value = _record()
    value["changed_files"][0]["path"] = changed
    value["frozen_files"][0]["path"] = frozen
    with pytest.raises(MaintenanceRecordError):
        _parse(value)
