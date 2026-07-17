"""Run Bandit and permit only EMR4's exact reviewed findings."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = REPO_ROOT / ".bandit-baseline.json"


def _normalized_path(value: str) -> str:
    return value.replace("\\", "/").removeprefix("./")


def _fingerprint(result: dict[str, object]) -> tuple[str, str, int, str]:
    code = str(result["code"])
    return (
        _normalized_path(str(result["filename"])),
        str(result["test_id"]),
        int(result["line_number"]),
        hashlib.sha256(code.encode("utf-8")).hexdigest(),
    )


def _allowed_fingerprints() -> set[tuple[str, str, int, str]]:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    if baseline.get("schema_version") != "emr4.bandit-reviewed-baseline.v1":
        raise ValueError("unrecognized Bandit baseline schema")
    reviewed = baseline.get("reviewed_findings")
    if not isinstance(reviewed, list) or len(reviewed) != 2:
        raise ValueError("Bandit baseline must contain exactly two reviewed findings")
    return {
        (
            _normalized_path(str(item["path"])),
            str(item["test_id"]),
            int(item["line_number"]),
            str(item["code_sha256"]),
        )
        for item in reviewed
    }


def main() -> int:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "bandit",
            "-r",
            "app",
            "scripts",
            "-ll",
            "-ii",
            "-c",
            "pyproject.toml",
            "-f",
            "json",
            "-q",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode not in {0, 1}:
        sys.stderr.write(completed.stderr)
        return completed.returncode

    try:
        report = json.loads(completed.stdout)
        actual = {_fingerprint(result) for result in report["results"]}
        allowed = _allowed_fingerprints()
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"Bandit gate invalid: {exc}", file=sys.stderr)
        return 2

    unexpected = actual - allowed
    missing = allowed - actual
    if unexpected or missing:
        print("Bandit reviewed baseline mismatch", file=sys.stderr)
        mismatch = {
            "unexpected": sorted(unexpected),
            "missing": sorted(missing),
        }
        print(json.dumps(mismatch, indent=2), file=sys.stderr)
        return 1

    print(
        "Bandit gate safe: "
        f"{len(actual)} exact reviewed finding(s), no new medium/high findings"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
