"""Launch the bounded Deep Code PTY lifecycle adapter."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = REPO_ROOT / "orchestration" / "deepcode_pty" / "runner.mjs"
PROJECT_SETTINGS = {
    "telemetryEnabled": False,
    "permissions": {
        "allow": ["read-in-cwd", "query-git-log", "write-in-cwd"],
        "deny": [
            "read-out-cwd",
            "write-out-cwd",
            "delete-in-cwd",
            "delete-out-cwd",
            "mutate-git-log",
            "network",
            "mcp",
        ],
        "ask": [],
        "defaultMode": "askAll",
    },
}


def ensure_project_settings(cwd: Path) -> None:
    if not cwd.is_dir():
        raise ValueError("Deep Code worker cwd must already exist")
    settings_path = cwd / ".deepcode" / "settings.json"
    if settings_path.exists():
        payload = json.loads(settings_path.read_text(encoding="utf-8"))
        permissions = payload.get("permissions", {})
        if "write-in-cwd" not in permissions.get("allow", []):
            raise ValueError("existing Deep Code project settings must allow write-in-cwd")
        if "write-in-cwd" in permissions.get("ask", []):
            raise ValueError("existing Deep Code project settings must not ask for write-in-cwd")
        required_denies = set(PROJECT_SETTINGS["permissions"]["deny"])
        if not required_denies.issubset(permissions.get("deny", [])):
            raise ValueError("existing Deep Code project settings must retain all required denied capabilities")
        return
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(PROJECT_SETTINGS, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Deep Code packet in a bounded real PTY.")
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--artifact-kind", choices=("decision", "completion"), default="decision")
    parser.add_argument("--outbox", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=0, help="Artifact deadline seconds; 0 disables it")
    parser.add_argument("--exit-timeout", type=int, default=30)
    parser.add_argument(
        "--fixture",
        choices=("success", "permission", "hang", "ignore_exit", "markdown_decision", "completion"),
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()
    cwd = args.cwd.resolve()
    try:
        ensure_project_settings(cwd)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"Deep Code project-settings preflight failed: {error}", file=sys.stderr)
        return 2

    command = [
        "node",
        str(RUNNER),
        "--cwd",
        str(cwd),
        "--packet",
        str(args.packet),
        "--artifact",
        str(args.artifact),
        "--artifact-kind",
        args.artifact_kind,
        "--outbox",
        str(args.outbox),
        "--receipt",
        str(args.receipt),
        "--timeout",
        str(args.timeout),
        "--exit-timeout",
        str(args.exit_timeout),
    ]
    environment = os.environ.copy()
    if args.fixture:
        command.extend(("--fixture", args.fixture))
        environment["ARIADNE_PTY_TEST_MODE"] = "1"
    return subprocess.run(command, cwd=REPO_ROOT, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
