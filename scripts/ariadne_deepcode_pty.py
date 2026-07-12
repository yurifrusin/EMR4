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
        "allow": ["read-in-cwd", "query-git-log", "write-in-cwd", "mutate-git-log"],
        "deny": [
            "read-out-cwd",
            "write-out-cwd",
            "delete-in-cwd",
            "delete-out-cwd",
            "network",
            "mcp",
        ],
        "ask": [],
        "defaultMode": "askAll",
    },
}


def ensure_project_settings(
    cwd: Path, model: str | None = None, reasoning: str | None = None
) -> None:
    if not cwd.is_dir():
        raise ValueError("Deep Code worker cwd must already exist")
    settings_path = cwd / ".deepcode" / "settings.json"
    if settings_path.exists():
        payload = json.loads(settings_path.read_text(encoding="utf-8"))
        permissions = payload.get("permissions", {})
        required_allows = set(PROJECT_SETTINGS["permissions"]["allow"])
        if not required_allows.issubset(permissions.get("allow", [])):
            raise ValueError("existing Deep Code project settings must retain all required allowed capabilities")
        if required_allows.intersection(permissions.get("ask", [])):
            raise ValueError("existing Deep Code project settings must not ask for required allowed capabilities")
        required_denies = set(PROJECT_SETTINGS["permissions"]["deny"])
        if not required_denies.issubset(permissions.get("deny", [])):
            raise ValueError("existing Deep Code project settings must retain all required denied capabilities")
    else:
        payload = json.loads(json.dumps(PROJECT_SETTINGS))
        settings_path.parent.mkdir(parents=True, exist_ok=True)
    if model:
        payload.setdefault("env", {})["MODEL"] = model
    if reasoning:
        payload["reasoningEffort"] = reasoning
    settings_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Deep Code packet in a bounded real PTY.")
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--artifact-kind", choices=("decision", "completion"), default="decision")
    parser.add_argument("--model", choices=("deepseek-v4-flash", "deepseek-v4-pro"))
    parser.add_argument("--reasoning", choices=("high", "max"))
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
        ensure_project_settings(cwd, model=args.model, reasoning=args.reasoning)
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
    if args.model:
        command.extend(("--model", args.model))
    if args.reasoning:
        command.extend(("--reasoning", args.reasoning))
    environment = os.environ.copy()
    if args.fixture:
        command.extend(("--fixture", args.fixture))
        environment["ARIADNE_PTY_TEST_MODE"] = "1"
    return subprocess.run(command, cwd=REPO_ROOT, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
