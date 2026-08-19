"""Fail-closed retirement guard for historical governance publishers."""

from __future__ import annotations

import json
import sys
from pathlib import Path


CLOCKWORK_POINTER = Path("orchestration/continuity/ariadne-governance-clockwork/current.json")
POINTER_VERSION = "ariadne.governance_live_pointer.v1"


class LegacyGovernanceWriterRetired(RuntimeError):
    """A historical publisher attempted direct canonical execution."""


def clockwork_is_active(repo_root: Path) -> bool:
    """Return true only for a structurally valid active clockwork pointer."""

    path = repo_root.resolve() / CLOCKWORK_POINTER
    if not path.is_file():
        return False
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        isinstance(value, dict)
        and value.get("schema_version") == POINTER_VERSION
        and value.get("phase") == "clockwork_active"
        and value.get("writer") == "clockwork"
    )


def refuse_retired_legacy_writer(
    repo_root: Path, executable: str | None = None
) -> None:
    """Reject ordinary direct execution of a retired continuity updater."""

    invoked = Path(executable or sys.argv[0]).name.casefold()
    if clockwork_is_active(repo_root) and invoked.endswith("continuity_update.py"):
        raise LegacyGovernanceWriterRetired(
            f"legacy_governance_writer_retired:{invoked}"
        )
