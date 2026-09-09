"""Small, newly authored source-capsule fixtures for bootstrap tests."""

from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path

from programme_maintenance_synthetic import _git, create_synthetic_repository


def capsule_entries(
    root: Path,
    files: dict[str, bytes],
    generation: str = "synthetic-maintenance-v1",
) -> dict[str, bytes]:
    """Build capsule members from an authored synthetic repository index."""
    repository = create_synthetic_repository(root, files)
    source_tree = repository.index_tree()
    commit = (
        f"tree {source_tree}\n"
        "author Ariadne Source Capsule <capsule@example.invalid> 946684800 +0000\n"
        "committer Ariadne Source Capsule <capsule@example.invalid> 946684800 +0000\n"
        f"\nMaintenance source capsule: {generation}\n"
    ).encode("ascii")
    source_commit = (
        _git(
            repository.root,
            "hash-object",
            "-t",
            "commit",
            "--stdin",
            payload=commit,
        )
        .decode("ascii")
        .strip()
    )
    manifest = {
        "schema_version": "ariadne.maintenance_code_capsule.v1",
        "generation_id": generation,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "files": {
            path: {"sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}
            for path, payload in files.items()
        },
    }
    return {
        **files,
        "capsule.json": json.dumps(
            manifest, sort_keys=True, separators=(",", ":")
        ).encode("utf-8"),
        "source.commit": commit,
    }


def archive_entries(entries: dict[str, bytes]) -> bytes:
    """Create an in-memory archive containing only explicit regular members."""
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as archive:
        for name, payload in entries.items():
            info = zipfile.ZipInfo(name)
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, payload)
    return output.getvalue()
