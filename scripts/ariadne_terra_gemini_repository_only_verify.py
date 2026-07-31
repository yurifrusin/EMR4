"""Run the fixed provider-free Ariadne closeout population without conftest."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Mapping
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIXED_TEST_PATHS = (
    "tests/test_ariadne_bounded_cognitive_work_cell.py",
    "tests/test_ariadne_bounded_agent_admission.py",
    "tests/test_ariadne_continuity_engine.py",
    "tests/test_ariadne_compass.py",
    "tests/test_ariadne_deepseek_in_cell_rehearsal.py",
    "tests/test_ariadne_real_isolation_rehearsal.py",
    "tests/test_ariadne_scripted_cognitive_work_cell_rehearsal.py",
    "tests/test_ariadne_sandbox_dag.py",
    "tests/test_ariadne_synaptic_event_router.py",
    "tests/test_ariadne_terra_gemini_comparative_rehearsal.py",
    "tests/test_api_spine_artifacts.py",
)

PASSTHROUGH_ENVIRONMENT_KEYS = (
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "WINDIR",
)


def verification_command() -> list[str]:
    """Return an immutable test allowlist with repository conftest disabled."""
    return [
        sys.executable,
        "-m",
        "pytest",
        "--noconftest",
        "-p",
        "no:cacheprovider",
        "--strict-config",
        "--strict-markers",
        "-q",
        *FIXED_TEST_PATHS,
    ]


def verification_environment(
    source: Mapping[str, str],
) -> dict[str, str]:
    """Construct a minimal child environment without credentials or DB config."""
    environment = {
        key: source[key]
        for key in PASSTHROUGH_ENVIRONMENT_KEYS
        if key in source
    }
    environment.update(
        {
            "ARIADNE_REPOSITORY_ONLY_VERIFICATION": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTEST_ADDOPTS": "",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTHONHASHSEED": "0",
        }
    )
    return environment


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description=(
            "Run the fixed Terra/Gemini repository-only closeout population."
        )
    )


def main(argv: list[str] | None = None) -> int:
    build_parser().parse_args(argv)
    completed = subprocess.run(  # noqa: S603
        verification_command(),
        cwd=ROOT,
        env=verification_environment(os.environ),
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
