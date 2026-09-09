"""Capsule/source checks in authored repositories, never real EMR4 admission."""

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile
from types import SimpleNamespace

import pytest

from maintenance_capsule_synthetic import archive_entries, capsule_entries

_BOOTSTRAP = (
    Path(__file__).resolve().parents[1]
    / "scripts/raisa_ariadne_maintenance_bootstrap.py"
)
_SPEC = importlib.util.spec_from_file_location(
    "bounded_maintenance_bootstrap_test", _BOOTSTRAP
)
boot = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = boot
_SPEC.loader.exec_module(boot)
_SHA = lambda raw: hashlib.sha256(raw).hexdigest()


@pytest.fixture
def entries(tmp_path):
    return capsule_entries(
        tmp_path / "source",
        {
            "orchestration_harness/__init__.py": b"# inert authored package\n",
            "orchestration_harness/support.py": b"VALUE = 17\n",
            "orchestration_harness/controller_maintenance_runner.py": (
                b"from .support import VALUE\nimport sys\n"
                b"def run_request(payload, *, verified_source, source_file, request_file):\n"
                b"    source_file.revalidate()\n    request_file.revalidate()\n"
                b"    return {'value': VALUE, 'source': __file__, 'no_site': sys.flags.no_site, 'isolated': sys.flags.isolated}\n"
            ),
        },
    )


def _verify(entries):
    raw = archive_entries(entries)
    return boot.verify_capsule(raw, expected_sha256=_SHA(raw))


def _manifest_change(entries, change):
    manifest = json.loads(entries["capsule.json"])
    change(manifest)
    entries["capsule.json"] = json.dumps(manifest).encode()


def test_complete_capsule_matches_actual_git_tree_and_has_immutable_sources(entries):
    capsule = _verify(entries)
    manifest = json.loads(entries["capsule.json"])
    assert capsule.source_tree == manifest["source_tree"]
    assert capsule.source_commit == manifest["source_commit"]
    assert capsule.modules["orchestration_harness.support"][1] == b"VALUE = 17\n"
    with pytest.raises(TypeError):
        capsule.modules["replacement"] = ("replacement.py", b"", False)


def test_wrong_external_digest_rejects_before_archive_use(entries, monkeypatch):
    raw = archive_entries(entries)

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Archive parsing occurred after digest rejection")

    monkeypatch.setattr(boot.zipfile, "ZipFile", forbidden)
    with pytest.raises(boot.CapsuleError, match="capsule_digest_mismatch"):
        boot.verify_capsule(raw, expected_sha256="0" * 64)


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (lambda m: m.update(extra=True), "capsule_schema_invalid"),
        (lambda m: m.update(generation_id=False), "capsule_generation_invalid"),
        (lambda m: m.update(source_tree="0" * 40), "capsule_source_tree_mismatch"),
        (lambda m: m.update(source_commit="0" * 40), "capsule_source_commit_mismatch"),
        (
            lambda m: m["files"]["orchestration_harness/support.py"].update(bytes=True),
            "capsule_file_size_invalid",
        ),
        (
            lambda m: m["files"]["orchestration_harness/support.py"].update(
                sha256="0" * 64
            ),
            "capsule_source_bytes_mismatch",
        ),
    ],
)
def test_strict_manifest_and_source_bindings_reject_substitutions(
    entries, mutation, reason
):
    _manifest_change(entries, mutation)
    with pytest.raises(boot.CapsuleError, match=reason):
        _verify(entries)


def test_duplicate_json_key_is_rejected(entries):
    entries["capsule.json"] = b'{"schema_version":1,"schema_version":2}'
    with pytest.raises(boot.CapsuleError, match="capsule_duplicate_key"):
        _verify(entries)


@pytest.mark.parametrize("extra", ["unexpected.py", "yaml/native.pyd", "../outside.py"])
def test_undeclared_archive_member_is_rejected(entries, extra):
    entries[extra] = b"inert"
    with pytest.raises(boot.CapsuleError, match="capsule_inventory_invalid"):
        _verify(entries)


def test_duplicate_zip_entry_and_nonregular_mode_are_rejected(entries):
    for duplicate in (True, False):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            for name, raw in entries.items():
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                info.external_attr = (0o100644 if duplicate else 0o120777) << 16
                archive.writestr(info, raw)
            if duplicate:
                with pytest.warns(UserWarning, match="Duplicate name"):
                    archive.writestr("capsule.json", entries["capsule.json"])
        raw = stream.getvalue()
        with pytest.raises(
            boot.CapsuleError, match="capsule_inventory_invalid|capsule_entry_invalid"
        ):
            boot.verify_capsule(raw, expected_sha256=_SHA(raw))


def test_noncanonical_commit_cannot_supply_another_source_identity(entries):
    entries["source.commit"] = entries["source.commit"].replace(
        b"\nauthor ", b"\nparent " + b"1" * 40 + b"\nauthor "
    )
    raw = entries["source.commit"]
    oid = hashlib.sha1(b"commit " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    _manifest_change(entries, lambda m: m.update(source_commit=oid))
    with pytest.raises(boot.CapsuleError, match="capsule_source_commit_tree_mismatch"):
        _verify(entries)


def test_verification_does_not_execute_definition_time_source(tmp_path):
    entries = capsule_entries(
        tmp_path / "source",
        {
            "orchestration_harness/__init__.py": b"raise RuntimeError('source was executed')\n",
            "orchestration_harness/controller_maintenance_runner.py": b"raise RuntimeError('runner was executed')\n",
        },
    )
    assert _verify(entries).modules


def _run(tmp_path, entries, *, request_digest=None):
    archive = tmp_path / "source.zip"
    archive.write_bytes(archive_entries(entries))
    request = tmp_path / "request.json"
    request.write_bytes(b"{}")
    environment = {
        key: value
        for key, value in os.environ.items()
        if key.upper()
        in {"SYSTEMROOT", "WINDIR", "COMSPEC", "PATH", "TEMP", "TMP", "SYSTEMDRIVE"}
    }
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            "-S",
            str(_BOOTSTRAP),
            "--capsule",
            str(archive),
            "--capsule-sha256",
            _SHA(archive.read_bytes()),
            "--request",
            str(request),
            "--request-sha256",
            request_digest or _SHA(request.read_bytes()),
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_isolated_bootstrap_executes_only_verified_memory_sources(entries, tmp_path):
    ambient = tmp_path / "orchestration_harness"
    ambient.mkdir()
    (ambient / "__init__.py").write_text(
        "raise RuntimeError('ambient package executed')\n"
    )
    result = _run(tmp_path, entries)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {
        "value": 17,
        "source": "capsule:/orchestration_harness/controller_maintenance_runner.py",
        "no_site": 1,
        "isolated": 1,
    }


def test_request_digest_failure_prevents_capsule_import(tmp_path):
    entries = capsule_entries(
        tmp_path / "source",
        {
            "orchestration_harness/__init__.py": b"raise RuntimeError('source was executed')\n",
            "orchestration_harness/controller_maintenance_runner.py": b"raise RuntimeError('runner was executed')\n",
        },
    )
    result = _run(tmp_path, entries, request_digest="0" * 64)
    assert result.returncode == 2
    assert json.loads(result.stdout)["reason"] == "bootstrap_request_digest_mismatch"
    assert result.stderr == ""


def test_missing_capsule_submodule_cannot_fall_back(entries):
    finder = boot._CapsuleImporter(_verify(entries))
    with pytest.raises(ModuleNotFoundError, match="absent from accepted capsule"):
        finder.find_spec("orchestration_harness.settings_fingerprint")
    with pytest.raises(ModuleNotFoundError):
        finder.find_spec("yaml.cyaml")
    assert finder.find_spec("json") is None


def test_verified_external_input_rejects_later_byte_drift(tmp_path):
    path = tmp_path / "owned.json"
    path.write_bytes(b"one")
    bound = boot._read_file(path, 10)
    bound.revalidate()
    path.write_bytes(b"two")
    with pytest.raises(boot.CapsuleError, match="bootstrap_input_drift"):
        bound.revalidate()


def test_input_size_is_rejected_before_open(tmp_path, monkeypatch):
    path = tmp_path / "owned.json"
    path.write_bytes(b"too large")

    def forbidden(*_args, **_kwargs):
        raise AssertionError("Oversized input was opened")

    monkeypatch.setattr(Path, "open", forbidden)
    with pytest.raises(boot.CapsuleError, match="bootstrap_file_invalid"):
        boot._read_file(path, 2)


def _stat_namespace(value, **changes):
    fields = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
    return SimpleNamespace(
        **{field: changes.get(field, getattr(value, field)) for field in fields}
    )


def test_read_file_accepts_fixed_descriptor_timestamp_offset(tmp_path, monkeypatch):
    path = tmp_path / "owned.json"
    path.write_bytes(b"stable")
    original = os.fstat

    def offset(fd):
        observed = original(fd)
        return _stat_namespace(
            observed,
            st_mtime_ns=observed.st_mtime_ns + 7,
            st_ctime_ns=observed.st_ctime_ns + 7,
        )

    monkeypatch.setattr(os, "fstat", offset)
    assert boot._read_file(path, 32).data == b"stable"


def test_read_file_rejects_descriptor_timestamp_change_during_read(
    tmp_path, monkeypatch
):
    path = tmp_path / "owned.json"
    path.write_bytes(b"stable")
    original = os.fstat
    calls = 0

    def changing(fd):
        nonlocal calls
        calls += 1
        observed = original(fd)
        delta = 7 + calls
        return _stat_namespace(
            observed,
            st_mtime_ns=observed.st_mtime_ns + delta,
            st_ctime_ns=observed.st_ctime_ns + delta,
        )

    monkeypatch.setattr(os, "fstat", changing)
    with pytest.raises(boot.CapsuleError, match="bootstrap_file_drift"):
        boot._read_file(path, 32)


def test_read_file_rejects_pathname_timestamp_change_during_read(tmp_path, monkeypatch):
    path = tmp_path / "owned.json"
    path.write_bytes(b"stable")
    original = Path.stat
    calls = 0

    def changing(self, *args, **kwargs):
        nonlocal calls
        observed = original(self, *args, **kwargs)
        if self == path:
            calls += 1
            if calls == 2:
                return _stat_namespace(
                    observed,
                    st_mtime_ns=observed.st_mtime_ns + 1,
                    st_ctime_ns=observed.st_ctime_ns + 1,
                )
        return observed

    monkeypatch.setattr(Path, "stat", changing)
    with pytest.raises(boot.CapsuleError, match="bootstrap_file_drift"):
        boot._read_file(path, 32)
