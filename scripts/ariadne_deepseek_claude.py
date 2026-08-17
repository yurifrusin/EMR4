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
    "Do not run a package manager, install a dependency, or mutate any Python, "
    "Node, user, system, or shared environment. "
    "Run the requested checks and report changed files, tests, and blockers concisely."
)
DEFAULT_TOOLS = "Read,Glob,Grep,Edit,Write,Bash"
SCRUBBED_PACKAGE_ENVIRONMENT = frozenset(
    {
        "virtual_env",
        "pythonhome",
        "pythonpath",
        "pip_index_url",
        "pip_extra_index_url",
        "pip_trusted_host",
        "uv_index",
        "uv_default_index",
        "uv_extra_index_url",
    }
)


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


def deepseek_environment(
    *,
    api_key: str,
    model: str,
    effort: str,
    cwd: Path | None = None,
) -> dict[str, str]:
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY is not set")
    env = os.environ.copy()
    for key in list(env):
        if key.casefold() in SCRUBBED_PACKAGE_ENVIRONMENT:
            env.pop(key)
    env.update(
        {
            "ANTHROPIC_BASE_URL": BASE_URL,
            "ANTHROPIC_API_KEY": api_key,
            "ANTHROPIC_AUTH_TOKEN": api_key,
            "ANTHROPIC_MODEL": model,
            "CLAUDE_CODE_SUBAGENT_MODEL": "deepseek-v4-flash",
            "CLAUDE_CODE_EFFORT_LEVEL": effort,
            "PIP_NO_INDEX": "1",
            "PIP_NO_INPUT": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PYTHONNOUSERSITE": "1",
            "UV_OFFLINE": "1",
            "NPM_CONFIG_OFFLINE": "true",
            "YARN_ENABLE_NETWORK": "0",
        }
    )
    if cwd is not None:
        resolved_cwd = str(cwd.resolve())
        # Some CLI/tool layers consult inherited shell-directory variables
        # instead of the child process' real cwd. Keep every directory signal
        # pinned to the disposable worker worktree.
        env["PWD"] = resolved_cwd
        env["INIT_CWD"] = resolved_cwd
    return env


def run_worker(
    *, packet_path: Path, cwd: Path, output_path: Path, model: str, effort: str
) -> dict:
    packet = packet_path.read_text(encoding="utf-8")
    if not packet.strip():
        raise ValueError("worker packet must not be empty")
    if not cwd.is_dir():
        raise ValueError("worker cwd must be an existing directory")
    resolved_cwd = cwd.resolve()
    bounded_packet = (
        f"AUTHORIZED_WORKTREE_ROOT: {resolved_cwd}\n"
        "All file and shell operations must remain under that root.\n\n"
        "PACKAGE_AND_ENVIRONMENT_MUTATION: FORBIDDEN. Do not run pip, uv, npm, "
        "yarn, pnpm, conda, poetry, or any dependency installer. If a required "
        "dependency is absent, stop and report the blocker without installing it.\n\n"
        f"{packet}"
    )
    command = build_command(packet=bounded_packet, model=model, effort=effort)
    completed = subprocess.run(
        command,
        cwd=resolved_cwd,
        env=deepseek_environment(
            api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
            model=model,
            effort=effort,
            cwd=resolved_cwd,
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
