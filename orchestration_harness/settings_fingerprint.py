"""Stable cross-platform fingerprint over every Ariadne YAML settings artifact."""

from __future__ import annotations

import hashlib
from pathlib import Path


def settings_fingerprint(settings_dir: Path) -> str:
    paths = sorted(settings_dir.glob("*.yaml"), key=lambda path: path.name)
    if not paths:
        raise ValueError("harness settings directory contains no YAML files")
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.name.encode("utf-8"))
        digest.update(b"\0")
        normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
        normalized = normalized.replace("\r", "\n")
        digest.update(normalized.encode("utf-8"))
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"
