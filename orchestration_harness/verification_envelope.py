"""Finite verification-envelope semantics shared by Ariadne command surfaces."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence


DATABASE_AUTHORITIES = ("closed", "open")
VERIFICATION_PHASES = ("prepublication", "postpublication")
ORDINARY_PYTEST_EXECUTABLES = frozenset(
    {"pytest", "pytest.exe", "py.test", "py.test.exe"}
)
SERIAL_PYTEST_MODULE = "scripts.ariadne_serial_pytest"
PROVIDER_FREE_PYTEST_MODULE = "scripts.ariadne_provider_free_pytest"


def _python_module(argv: Sequence[str]) -> str | None:
    if not argv:
        return None
    executable = Path(argv[0]).name.casefold()
    if not (
        executable in {"python", "python.exe", "python3", "python3.exe"}
        or executable.startswith("python3.")
    ):
        return None
    if len(argv) >= 3 and argv[1] == "-m":
        return argv[2]
    return None


def pytest_runner_kind(argv: Sequence[str]) -> str | None:
    """Classify only the three repository-relevant pytest entry points."""
    if not argv:
        return None
    if Path(argv[0]).name.casefold() in ORDINARY_PYTEST_EXECUTABLES:
        return "ordinary"
    module = _python_module(argv)
    if module == "pytest":
        return "ordinary"
    if module == SERIAL_PYTEST_MODULE:
        return "serial"
    if module == PROVIDER_FREE_PYTEST_MODULE:
        return "provider_free"
    return None


def validate_database_authority(value: object) -> str:
    if value not in DATABASE_AUTHORITIES:
        raise ValueError("verification_database_authority_invalid")
    return str(value)


def validate_verification_phase(value: object) -> str:
    if value not in VERIFICATION_PHASES:
        raise ValueError("verification_phase_invalid")
    return str(value)


def validate_phase_order(phases: Sequence[str]) -> None:
    """Require one-way prepublication -> postpublication progression."""
    normalized = [validate_verification_phase(value) for value in phases]
    indexes = [VERIFICATION_PHASES.index(value) for value in normalized]
    if indexes != sorted(indexes):
        raise ValueError("verification_phase_order_invalid")


def validate_runner_for_authority(
    argv: Sequence[str], *, database_authority: str
) -> str | None:
    """Reject database-capable pytest before a closed envelope can launch it."""
    authority = validate_database_authority(database_authority)
    runner = pytest_runner_kind(argv)
    if authority == "closed" and runner == "ordinary":
        raise ValueError("database_closed_ordinary_pytest_forbidden")
    if authority == "closed" and runner == "serial":
        raise ValueError("database_closed_serial_pytest_forbidden")
    return runner
