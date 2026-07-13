"""Run a bounded DeepSeek worker through Claude Code's headless bare mode."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


BASE_URL = "https://api.deepseek.com/anthropic"
MODELS = {"deepseek-v4-flash", "deepseek-v4-pro"}
EFFORTS = {"high", "max"}
SYSTEM_PROMPT = (
    "Execute the bounded coding packet in the current isolated worktree. "
    "Do not change scope, access protected master, push, deploy, or expose secrets. "
    "Run the requested checks and report changed files, tests, and blockers concisely."
)
DEFAULT_TOOLS = "Read,Glob,Grep,Edit,Write,Bash"


def build_command(*, packet: str, model: str, effort: str) -> list[str]:
    if model not in MODELS:
        raise ValueError(f"unsupported DeepSeek model: {model}")
    if effort not in EFFORTS:
        raise ValueError(f"unsupported reasoning effort: {effort}")
    return [
        "claude",
        "-p",
        packet,
        "--bare",
        "--system-prompt",
        SYSTEM_PROMPT,
        "--model",
        model,
        "--effort",
        effort,
        "--output-format",
        "json",
        "--no-session-persistence",
        "--permission-mode",
        "dontAsk",
        "--allowedTools",
        DEFAULT_TOOLS,
    ]


def deepseek_environment(*, api_key: str, model: str, effort: str) -> dict[str, str]:
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is not set")
    env = os.environ.copy()
    env.update(
        {
            "ANTHROPIC_BASE_URL": BASE_URL,
            "ANTHROPIC_API_KEY": api_key,
            "ANTHROPIC_AUTH_TOKEN": api_key,
            "ANTHROPIC_MODEL": model,
            "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4-flash",
            "CLAUDE_CODE_EFFORT_LEVEL": effort,
        }
    )
    return env


def run_worker(
    *, packet_path: Path, cwd: Path, output_path: Path, model: str, effort: str
) -> dict:
    packet = packet_path.read_text(encoding="utf-8")
    if not packet.strip():
        raise ValueError("worker packet must not be empty")
    if not cwd.is_dir():
        raise ValueError("worker cwd must be an existing directory")
    command = build_command(packet=packet, model=model, effort=effort)
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=deepseek_environment(
            api_key=os.environ.get("DEEPSEEK_API_KEY", ""), model=model, effort=effort
        ),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Claude Code DeepSeek transport failed ({completed.returncode}): "
            f"{completed.stderr.strip()}"
        )
    payload = json.loads(completed.stdout)
    if not isinstance(payload, dict) or payload.get("subtype") != "success":
        raise RuntimeError("Claude Code did not return a successful JSON result")
    receipt = {
        "schema_version": "ariadne.worker_receipt.v1",
        "status": "completed",
        "transport": "claude_code_bare_deepseek",
        "model": model,
        "effort": effort,
        "result": payload.get("result", ""),
        "usage": payload.get("usage", {}),
        "adapter_cost_estimate_usd": payload.get("total_cost_usd"),
        "adapter_cost_estimate_authoritative": False,
        "authoritative_billing_source": "deepseek_provider_usage",
        "provider_billed_cost_usd": None,
        "permission_denials": payload.get("permission_denials", []),
        "terminal_reason": payload.get("terminal_reason"),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a DeepSeek coding packet through Claude Code bare mode."
    )
    parser.add_argument("--packet", type=Path, required=True)
    parser.add_argument("--cwd", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", choices=sorted(MODELS), default="deepseek-v4-flash")
    parser.add_argument("--effort", choices=sorted(EFFORTS), default="high")
    args = parser.parse_args()
    try:
        receipt = run_worker(
            packet_path=args.packet.resolve(),
            cwd=args.cwd.resolve(),
            output_path=args.output.resolve(),
            model=args.model,
            effort=args.effort,
        )
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"DeepSeek Claude transport failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps({key: receipt[key] for key in ("status", "transport", "model")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
