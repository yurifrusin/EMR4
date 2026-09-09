"""Stdlib-only bootstrap for an externally accepted, immutable code capsule.

The trusted outer invocation owns the expected bootstrap, capsule and request
digests. A matching caller-supplied digest is integrity, not independent review.
This file must itself be authenticated before execution. No target source is
imported; accepted capsule modules execute from the exact verified bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.abc
import importlib.util
import io
import json
import os
import re
import stat
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

_MAX_ARCHIVE = 4 * 1024 * 1024
_MAX_TOTAL = 8 * 1024 * 1024
_ROOTS = frozenset({"orchestration_harness", "yaml"})
_RUNNER = "orchestration_harness.controller_maintenance_runner"
_HEX40 = re.compile(r"[0-9a-f]{40}\Z")
_HEX64 = re.compile(r"[0-9a-f]{64}\Z")
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_GENERATION = re.compile(r"[a-z][a-z0-9-]{1,95}\Z")


class CapsuleError(ValueError):
    def __init__(self, reason_code: str):
        self.reason_code = reason_code
        super().__init__(reason_code)


def _fail(reason: str) -> None:
    raise CapsuleError(reason)


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            _fail("capsule_duplicate_key")
        value[key] = item
    return value


def _text(value, pattern, reason):
    if type(value) is not str or pattern.fullmatch(value) is None:
        _fail(reason)
    return value


def _git_object(kind: bytes, payload: bytes) -> str:
    return hashlib.sha1(
        kind + b" " + str(len(payload)).encode("ascii") + b"\0" + payload
    ).hexdigest()


def _source_commit(tree: str, generation: str) -> bytes:
    """Canonical code-package identity, not a project-history publication."""
    return (
        "tree " + tree + "\n"
        "author Ariadne Source Capsule <capsule@example.invalid> 946684800 +0000\n"
        "committer Ariadne Source Capsule <capsule@example.invalid> 946684800 +0000\n"
        "\nMaintenance source capsule: " + generation + "\n"
    ).encode("ascii")


def _source_tree(files: Mapping[str, bytes]) -> str:
    """Derive the complete ordinary-file Git tree of this code-only capsule."""
    root = {}
    for path, payload in files.items():
        node = root
        parts = path.split("/")
        for part in parts[:-1]:
            existing = node.setdefault(part, {})
            if type(existing) is not dict:
                _fail("capsule_file_directory_collision")
            node = existing
        if parts[-1] in node:
            _fail("capsule_file_directory_collision")
        node[parts[-1]] = payload

    def tree(node):
        rows = []
        for name, value in node.items():
            directory = type(value) is dict
            oid = tree(value) if directory else _git_object(b"blob", value)
            raw_name = name.encode("ascii")
            rows.append(
                (
                    raw_name + (b"/" if directory else b""),
                    (b"40000 " if directory else b"100644 ")
                    + raw_name
                    + b"\0"
                    + bytes.fromhex(oid),
                )
            )
        return _git_object(b"tree", b"".join(row[1] for row in sorted(rows)))

    return tree(root)


def _module(path: str) -> tuple[str, bool]:
    if type(path) is not str or len(path) > 200 or not path.endswith(".py"):
        _fail("capsule_source_path_invalid")
    parts = path[:-3].split("/")
    if len(parts) < 2 or len(parts) > 8 or parts[0] not in _ROOTS:
        _fail("capsule_source_path_invalid")
    if any(
        _IDENTIFIER.fullmatch(part) is None or part == "__pycache__" for part in parts
    ):
        _fail("capsule_source_path_invalid")
    package = parts[-1] == "__init__"
    name = ".".join(parts[:-1] if package else parts)
    return name, package


@dataclass(frozen=True, slots=True)
class VerifiedCapsule:
    generation_id: str
    archive_sha256: str
    source_commit: str
    source_tree: str
    modules: Mapping[str, tuple[str, bytes, bool]]


def verify_capsule(payload: bytes, *, expected_sha256: str) -> VerifiedCapsule:
    """Validate a closed source object; this alone does not establish acceptance."""
    _text(expected_sha256, _HEX64, "capsule_expected_digest_invalid")
    if type(payload) is not bytes or len(payload) > _MAX_ARCHIVE:
        _fail("capsule_size_invalid")
    if hashlib.sha256(payload).hexdigest() != expected_sha256:
        _fail("capsule_digest_mismatch")
    try:
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            infos = archive.infolist()
            if len(infos) < 4 or len(infos) > 66:
                _fail("capsule_inventory_invalid")
            names = [entry.filename for entry in infos]
            if len(set(names)) != len(names) or len(
                {name.casefold() for name in names}
            ) != len(names):
                _fail("capsule_inventory_invalid")
            if sum(entry.file_size for entry in infos) > _MAX_TOTAL:
                _fail("capsule_size_invalid")
            content = {}
            for entry in infos:
                if (
                    entry.is_dir()
                    or entry.orig_filename != entry.filename
                    or entry.file_size > 2 * 1024 * 1024
                    or entry.flag_bits & 1
                    or entry.compress_type
                    not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)
                    or entry.external_attr >> 16 != 0o100644
                ):
                    _fail("capsule_entry_invalid")
                content[entry.filename] = archive.read(entry)
    except (
        OSError,
        ValueError,
        zipfile.BadZipFile,
        RuntimeError,
        NotImplementedError,
    ) as error:
        if isinstance(error, CapsuleError):
            raise
        raise CapsuleError("capsule_archive_invalid") from error
    try:
        manifest = json.loads(
            content["capsule.json"].decode("utf-8"),
            object_pairs_hook=_object,
            parse_constant=lambda _value: _fail("capsule_json_invalid"),
        )
    except (KeyError, UnicodeError, ValueError, RecursionError) as error:
        if isinstance(error, CapsuleError):
            raise
        raise CapsuleError("capsule_json_invalid") from error
    if type(manifest) is not dict or set(manifest) != {
        "schema_version",
        "generation_id",
        "source_commit",
        "source_tree",
        "files",
    }:
        _fail("capsule_schema_invalid")
    if (
        type(manifest["schema_version"]) is not str
        or manifest["schema_version"] != "ariadne.maintenance_code_capsule.v1"
    ):
        _fail("capsule_schema_invalid")
    generation = _text(
        manifest["generation_id"], _GENERATION, "capsule_generation_invalid"
    )
    source_commit = _text(
        manifest["source_commit"], _HEX40, "capsule_source_identity_invalid"
    )
    source_tree = _text(
        manifest["source_tree"], _HEX40, "capsule_source_identity_invalid"
    )
    files = manifest["files"]
    if (
        type(files) is not dict
        or not 2 <= len(files) <= 64
        or set(content) != {*files, "capsule.json", "source.commit"}
    ):
        _fail("capsule_inventory_invalid")
    modules = {}
    source_files = {}
    for path, row in files.items():
        name, package = _module(path)
        if type(row) is not dict or set(row) != {"sha256", "bytes"}:
            _fail("capsule_file_record_invalid")
        digest = _text(row["sha256"], _HEX64, "capsule_file_digest_invalid")
        if type(row["bytes"]) is not int or not 0 <= row["bytes"] <= 2 * 1024 * 1024:
            _fail("capsule_file_size_invalid")
        raw = content[path]
        if len(raw) != row["bytes"] or hashlib.sha256(raw).hexdigest() != digest:
            _fail("capsule_source_bytes_mismatch")
        if name in modules or name.casefold() in {key.casefold() for key in modules}:
            _fail("capsule_module_alias")
        try:
            compile(raw, "capsule:/" + path, "exec", dont_inherit=True)
        except (SyntaxError, ValueError, RecursionError) as error:
            raise CapsuleError("capsule_source_compile_failed") from error
        modules[name] = (path, raw, package)
        source_files[path] = raw
    for name in modules:
        parts = name.split(".")
        for length in range(1, len(parts)):
            parent = modules.get(".".join(parts[:length]))
            if parent is None or not parent[2]:
                _fail("capsule_package_missing")
    if _RUNNER not in modules or modules[_RUNNER][2]:
        _fail("capsule_runner_missing")
    if _source_tree(source_files) != source_tree:
        _fail("capsule_source_tree_mismatch")
    commit = content["source.commit"]
    if len(commit) > 16384 or _git_object(b"commit", commit) != source_commit:
        _fail("capsule_source_commit_mismatch")
    if commit != _source_commit(source_tree, generation):
        _fail("capsule_source_commit_tree_mismatch")
    return VerifiedCapsule(
        generation,
        expected_sha256,
        source_commit,
        source_tree,
        MappingProxyType(modules),
    )


class _CapsuleImporter(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, capsule: VerifiedCapsule):
        self.modules = capsule.modules

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.modules:
            return importlib.util.spec_from_loader(
                fullname, self, is_package=self.modules[fullname][2]
            )
        if fullname.split(".", 1)[0] in _ROOTS:
            raise ModuleNotFoundError(
                "module absent from accepted capsule", name=fullname
            )
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        path, source, package = self.modules[module.__name__]
        module.__file__ = "capsule:/" + path
        if package:
            module.__path__ = []
        exec(
            compile(source, module.__file__, "exec", dont_inherit=True), module.__dict__
        )


@dataclass(frozen=True, slots=True)
class VerifiedInput:
    path: Path
    data: bytes
    components: tuple[tuple[int, int, int], ...]
    identity: tuple[int, ...]
    limit: int

    def revalidate(self) -> None:
        if _read_file(self.path, self.limit) != self:
            _fail("bootstrap_input_drift")


def _read_file(path: Path, limit: int) -> VerifiedInput:
    absolute = path.absolute()

    def components():
        current = Path(absolute.anchor)
        identities = []
        for part in absolute.parts[1:]:
            current /= part
            observed = current.lstat()
            if (
                stat.S_ISLNK(observed.st_mode)
                or getattr(observed, "st_file_attributes", 0) & 0x400
            ):
                _fail("bootstrap_file_alias")
            identities.append((observed.st_dev, observed.st_ino, observed.st_mode))
        return tuple(identities)

    paths_before = components()
    before = absolute.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
        _fail("bootstrap_file_invalid")
    with absolute.open("rb") as stream:
        opened = os.fstat(stream.fileno())
        if (opened.st_dev, opened.st_ino, opened.st_mode) != paths_before[-1]:
            _fail("bootstrap_file_drift")
        raw = stream.read(limit + 1)
        finished = os.fstat(stream.fileno())
    after = absolute.stat()
    common_fields = ("st_dev", "st_ino", "st_mode", "st_size")
    timestamp_fields = ("st_mtime_ns", "st_ctime_ns")
    stat_fields = (*common_fields, *timestamp_fields)
    identity = tuple(getattr(before, field) for field in stat_fields)
    if (
        components() != paths_before
        or any(
            any(
                getattr(item, field) != getattr(before, field)
                for field in common_fields
            )
            for item in (opened, finished, after)
        )
        or len(raw) > limit
        or len(raw) != before.st_size
        # Windows path-stat and handle-stat can report different ctime values.
        # Compare time within each observation method, identity across both.
        or any(
            getattr(before, field) != getattr(after, field)
            for field in timestamp_fields
        )
        or any(
            getattr(opened, field) != getattr(finished, field)
            for field in timestamp_fields
        )
    ):
        _fail("bootstrap_file_drift")
    return VerifiedInput(absolute, raw, paths_before, identity, limit)


def main(argv=None) -> int:
    if not (sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode):
        _fail("bootstrap_isolation_required")
    if any(name.split(".", 1)[0] in _ROOTS for name in sys.modules):
        _fail("bootstrap_ambient_capsule_module")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capsule", type=Path, required=True)
    parser.add_argument("--capsule-sha256", required=True)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--request-sha256", required=True)
    args = parser.parse_args(argv)
    source_file = _read_file(args.capsule, _MAX_ARCHIVE)
    capsule = verify_capsule(source_file.data, expected_sha256=args.capsule_sha256)
    _text(args.request_sha256, _HEX64, "bootstrap_request_digest_invalid")
    request_file = _read_file(args.request, 65536)
    if hashlib.sha256(request_file.data).hexdigest() != args.request_sha256:
        _fail("bootstrap_request_digest_mismatch")
    source_file.revalidate()
    request_file.revalidate()
    importer = _CapsuleImporter(capsule)
    sys.meta_path.insert(0, importer)
    module = importlib.import_module(_RUNNER)
    result = module.run_request(
        request_file.data,
        verified_source=capsule,
        source_file=source_file,
        request_file=request_file,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CapsuleError, OSError) as error:
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "reason": getattr(error, "reason_code", "bootstrap_io_failed"),
                }
            )
        )
        raise SystemExit(2)
