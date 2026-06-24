"""Send EMR4 operational notifications to Yuri.

This helper is intentionally for non-clinical operational alerts only. Do not
send PHI, secrets, patient identifiers, credentials, or clinical content.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = REPO_ROOT / ".env"
PUSHOVER_MESSAGES_URL = "https://api.pushover.net/1/messages.json"
MAX_TITLE_LENGTH = 250
MAX_MESSAGE_LENGTH = 1024


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_value(name: str) -> str:
    return os.environ.get(name, "").strip()


def clamp(value: str, limit: int) -> str:
    cleaned = " ".join(value.strip().split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


def infer_provider(explicit_provider: str | None) -> str:
    if explicit_provider:
        return explicit_provider.strip().lower()

    provider = env_value("NOTIFY_PROVIDER").lower()
    if provider:
        return provider
    if env_value("PUSHOVER_USER_KEY") and env_value("PUSHOVER_API_TOKEN"):
        return "pushover"
    if (
        env_value("WHATSAPP_PHONE_NUMBER_ID")
        and env_value("WHATSAPP_ACCESS_TOKEN")
        and env_value("WHATSAPP_TO_NUMBER")
    ):
        return "whatsapp"
    raise SystemExit(
        "No notification provider configured. Set NOTIFY_PROVIDER=pushover "
        "with PUSHOVER_USER_KEY and PUSHOVER_API_TOKEN, or configure WhatsApp."
    )


def require_env(name: str) -> str:
    value = env_value(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def build_pushover_payload(args: argparse.Namespace) -> dict[str, str]:
    return {
        "token": require_env("PUSHOVER_API_TOKEN"),
        "user": require_env("PUSHOVER_USER_KEY"),
        "title": clamp(args.title, MAX_TITLE_LENGTH),
        "message": clamp(args.message, MAX_MESSAGE_LENGTH),
    }


def redact_pushover_payload(payload: dict[str, str]) -> dict[str, str]:
    redacted = dict(payload)
    redacted["token"] = "<redacted>"
    redacted["user"] = "<redacted>"
    return redacted


def send_pushover(args: argparse.Namespace) -> dict[str, Any]:
    payload = build_pushover_payload(args)
    if args.dry_run:
        return {
            "provider": "pushover",
            "dry_run": True,
            "payload": redact_pushover_payload(payload),
        }

    request = urllib.request.Request(
        PUSHOVER_MESSAGES_URL,
        data=urllib.parse.urlencode(payload).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        # The request URL is the fixed HTTPS Pushover API endpoint above.
        with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Pushover API error HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Pushover API connection error: {exc}") from exc


def send_whatsapp(args: argparse.Namespace) -> dict[str, Any]:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "notify_yuri_whatsapp.py"),
        "--env-file",
        str(args.env_file),
        "--title",
        args.title,
        "--message",
        args.message,
        "--action",
        args.action,
    ]
    if args.dry_run:
        command.append("--dry-run")

    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or completed.stdout.strip())
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"provider": "whatsapp", "output": completed.stdout.strip()}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a non-clinical EMR4 operational notification to Yuri.",
    )
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH), help="Path to .env file.")
    parser.add_argument("--provider", choices=["pushover", "whatsapp"], help="Override NOTIFY_PROVIDER.")
    parser.add_argument("--dry-run", action="store_true", help="Show redacted payload without sending.")
    parser.add_argument("--title", default="EMR4 Ariadne", help="Short notification title.")
    parser.add_argument(
        "--message",
        default="EMR4 notification. Open Codex for details.",
        help="Short non-PHI notification message.",
    )
    parser.add_argument("--action", default="Open Codex for details.", help="WhatsApp template action field.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    args.env_file = Path(args.env_file)
    load_env_file(args.env_file)

    provider = infer_provider(args.provider)
    if provider == "pushover":
        result = send_pushover(args)
    elif provider == "whatsapp":
        result = send_whatsapp(args)
    else:
        raise SystemExit(f"Unsupported notification provider: {provider}")

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
