"""Send EMR4 operational notifications to Yuri via WhatsApp Cloud API.

This helper is intentionally for non-clinical operational alerts only. Do not
send PHI, secrets, patient identifiers, credentials, or clinical content.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = REPO_ROOT / ".env"
DEFAULT_GRAPH_VERSION = "v24.0"
DEFAULT_TEMPLATE_NAME = "emr4_ops_alert"
MAX_FIELD_LENGTH = 900


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env_required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def env_or_dry_run_placeholder(name: str, dry_run: bool, placeholder: str) -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value
    if dry_run:
        return placeholder
    raise SystemExit(f"Missing required environment variable: {name}")


def clamp_field(value: str) -> str:
    cleaned = " ".join(value.strip().split())
    if len(cleaned) <= MAX_FIELD_LENGTH:
        return cleaned
    return cleaned[: MAX_FIELD_LENGTH - 1] + "…"


def build_template_payload(args: argparse.Namespace) -> dict[str, Any]:
    template_name = args.template or os.environ.get("WHATSAPP_TEMPLATE_NAME", DEFAULT_TEMPLATE_NAME)
    language = args.language or os.environ.get("WHATSAPP_TEMPLATE_LANGUAGE", "en_US")
    fields = [clamp_field(field) for field in args.field]
    if not fields:
        summary = clamp_field(
            args.message
            or os.environ.get("WHATSAPP_DEFAULT_MESSAGE", "EMR4 notification. Open Codex for details.")
        )
        fields = [
            clamp_field(args.title or "EMR4 notification"),
            summary,
            clamp_field(args.action or "Open Codex for details."),
        ]

    payload: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": env_or_dry_run_placeholder("WHATSAPP_TO_NUMBER", args.dry_run, "+61400000000"),
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language},
        },
    }
    if fields:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": field} for field in fields],
            }
        ]
    return payload


def build_text_payload(args: argparse.Namespace) -> dict[str, Any]:
    if not args.message:
        raise SystemExit("--text requires --message")
    return {
        "messaging_product": "whatsapp",
        "to": env_or_dry_run_placeholder("WHATSAPP_TO_NUMBER", args.dry_run, "+61400000000"),
        "type": "text",
        "text": {"preview_url": False, "body": clamp_field(args.message)},
    }


def post_message(payload: dict[str, Any]) -> dict[str, Any]:
    graph_version = os.environ.get("WHATSAPP_GRAPH_VERSION", DEFAULT_GRAPH_VERSION).strip() or DEFAULT_GRAPH_VERSION
    phone_number_id = env_required("WHATSAPP_PHONE_NUMBER_ID")
    access_token = env_required("WHATSAPP_ACCESS_TOKEN")
    url = f"https://graph.facebook.com/{graph_version}/{phone_number_id}/messages"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        # The request URL is the fixed HTTPS Meta Graph API endpoint above.
        with urllib.request.urlopen(request, timeout=30) as response:  # nosec B310
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"WhatsApp API error HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"WhatsApp API connection error: {exc}") from exc


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Send a non-clinical EMR4 operational notification via WhatsApp Cloud API.",
    )
    parser.add_argument("--env-file", default=str(DEFAULT_ENV_PATH), help="Path to .env file. Defaults to repo .env.")
    parser.add_argument("--dry-run", action="store_true", help="Print the API payload without sending.")
    parser.add_argument("--text", action="store_true", help="Send a free-form text message. Use only inside an open 24h WhatsApp service window.")
    parser.add_argument("--template", help="Override WHATSAPP_TEMPLATE_NAME.")
    parser.add_argument("--language", help="Override WHATSAPP_TEMPLATE_LANGUAGE, e.g. en_US.")
    parser.add_argument("--field", action="append", default=[], help="Template body variable. Repeat for each {{n}} variable.")
    parser.add_argument("--title", help="Default template field 1 when --field is omitted.")
    parser.add_argument("--message", help="Default template field 2, or text body with --text.")
    parser.add_argument("--action", help="Default template field 3 when --field is omitted.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    load_env_file(Path(args.env_file))

    payload = build_text_payload(args) if args.text else build_template_payload(args)
    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    result = post_message(payload)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
