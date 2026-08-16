"""Run an explicit provider-free pytest allowlist without repository conftest.

This entry point is for tranches whose authority closes database access. It
prevents pytest from loading ``tests/conftest.py``, disables third-party plugin
autoloading, removes inherited pytest options and database configuration, and
accepts only literal repository-relative ``tests/*.py`` paths.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
from collections.abc import Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
PASSTHROUGH_ENVIRONMENT_KEYS = (
    "PATH",
    "PATHEXT",
    "SYSTEMROOT",
    "TEMP",
    "TMP",
    "WINDIR",
)


def _literal_test_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    candidate = PurePosixPath(normalized)
    if (
        not normalized
        or candidate.is_absolute()
        or ".." in candidate.parts
        or not normalized.startswith("tests/")
        or candidate.suffix != ".py"
    ):
        raise argparse.ArgumentTypeError(
            "test paths must be literal repository-relative tests/*.py paths"
        )
    return normalized


def provider_free_environment(source: Mapping[str, str]) -> dict[str, str]:
    """Return a minimal environment with credentials and DB settings absent."""
    environment = {
        key: source[key]
        for key in PASSTHROUGH_ENVIRONMENT_KEYS
        if key in source
    }
    environment.update(
        {
            "ARIADNE_PROVIDER_FREE_VERIFICATION": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTEST_ADDOPTS": "",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTHONHASHSEED": "0",
        }
    )
    return environment


def provider_free_command(test_paths: Sequence[str]) -> list[str]:
    """Return the fixed no-conftest command for an admitted literal allowlist."""
    if not test_paths:
        raise ValueError("at least one literal test path is required")
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
        *test_paths,
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run an explicit provider-free pytest allowlist."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="Exact repository root containing the admitted tests.",
    )
    parser.add_argument("test_paths", nargs="+", type=_literal_test_path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = args.repo_root.resolve(strict=True)
    for relative_path in args.test_paths:
        test_path = (repo_root / relative_path).resolve(strict=True)
        try:
            test_path.relative_to(repo_root)
        except ValueError as error:
            raise SystemExit("test path escaped repository root") from error
        if not test_path.is_file():
            raise SystemExit(f"test path is not a file: {relative_path}")
    completed = subprocess.run(  # noqa: S603
        provider_free_command(args.test_paths),
        cwd=repo_root,
        env=provider_free_environment(os.environ),
        check=False,
        shell=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
