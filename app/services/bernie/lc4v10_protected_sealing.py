"""Bind and seal the sole fresh LC4V10 certification attempt."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from app.services.bernie.lc4v10_content_blind_framework import (
    MANIFEST_KEYS,
    MANIFEST_SCHEMA,
    SEAL_KEYS,
    SEAL_SCHEMA,
)
from app.services.bernie.lc4v10_protected_authoring import (
    ATTEMPT_ID,
    FIXTURE_PATH,
    PROTECTED_ROOT,
    THRESHOLDS_PATH,
)

SOURCE_COMMIT = "d07b0c80c0e4834116167e280099bcfaaf681997"
FRAMEWORK_PATH = Path("app/services/bernie/lc4v10_content_blind_framework.py")
EVALUATOR_PATH = FRAMEWORK_PATH
MANIFEST_PATH = PROTECTED_ROOT / "manifest.json"
SEAL_PATH = PROTECTED_ROOT / "seal.json"
MARKER_PATH = PROTECTED_ROOT / "attempt.marker.json"
REPORT_PATH = PROTECTED_ROOT / "aggregate.json"


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8") + b"\n"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _git_blob(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()  # noqa: S324 -- Git identity


def _source_blob(repo_root: Path, relative: Path) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{SOURCE_COMMIT}:{relative.as_posix()}"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    return completed.stdout


def build_manifest(repo_root: Path) -> dict[str, Any]:
    paths = {
        "fixture": FIXTURE_PATH,
        "framework": FRAMEWORK_PATH,
        "evaluator": EVALUATOR_PATH,
        "thresholds": THRESHOLDS_PATH,
    }
    payloads: dict[str, bytes] = {}
    for name, relative in paths.items():
        working = (repo_root / relative).read_bytes()
        source = _source_blob(repo_root, relative)
        if working != source:
            raise ValueError(f"{name} working bytes differ from source commit")
        payloads[name] = working
    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA,
        "attempt_id": ATTEMPT_ID,
        "corpus_source_commit": SOURCE_COMMIT,
    }
    for name, relative in paths.items():
        manifest[f"{name}_path"] = relative.as_posix()
        manifest[f"{name}_sha256"] = _sha256(payloads[name])
        manifest[f"{name}_git_blob"] = _git_blob(payloads[name])
    if set(manifest) != MANIFEST_KEYS:
        raise ValueError("manifest key population drifted")
    return manifest


def build_seal(repo_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    threshold_bytes = (repo_root / THRESHOLDS_PATH).read_bytes()
    seal = {
        "schema_version": SEAL_SCHEMA,
        "attempt_id": ATTEMPT_ID,
        "manifest_sha256": _sha256(_canonical(manifest)),
        "thresholds_sha256": _sha256(threshold_bytes),
        "state": "unconsumed",
    }
    if set(seal) != SEAL_KEYS:
        raise ValueError("seal key population drifted")
    return seal


def write_seal(repo_root: Path) -> dict[str, str]:
    marker = repo_root / MARKER_PATH
    report = repo_root / REPORT_PATH
    if marker.exists() or report.exists():
        raise FileExistsError("attempt marker or aggregate report already exists")
    manifest = build_manifest(repo_root)
    seal = build_seal(repo_root, manifest)
    manifest_path = repo_root / MANIFEST_PATH
    seal_path = repo_root / SEAL_PATH
    manifest_path.write_bytes(_canonical(manifest))
    seal_path.write_bytes(_canonical(seal))
    return {
        "manifest_sha256": _sha256(manifest_path.read_bytes()),
        "seal_sha256": _sha256(seal_path.read_bytes()),
    }


__all__ = [
    "EVALUATOR_PATH",
    "FRAMEWORK_PATH",
    "MANIFEST_PATH",
    "MARKER_PATH",
    "REPORT_PATH",
    "SEAL_PATH",
    "SOURCE_COMMIT",
    "build_manifest",
    "build_seal",
    "write_seal",
]
