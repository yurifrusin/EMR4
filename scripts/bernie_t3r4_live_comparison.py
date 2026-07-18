"""Run the explicitly approved T3R4 synthetic-only provider comparison.

Raw prompts and provider responses remain in process memory. The only durable
provider evidence is normalized JSON, hashes, safe error codes, latency, and
usage metadata. Each lane/case/repeat key is reserved before dispatch and is
never retried.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.evals.bernie_shadow_live_comparison import (
    DEEPSEEK_LANE,
    DEFAULT_OBSERVATION_PATH,
    DispatchState,
    LANE_IDS,
    append_observation,
    build_lane_cases,
    build_prompt,
    canonical_hash,
    failure_record,
    live_response_schema,
    load_approval,
    load_observations,
    observation_key,
    parse_json_object,
    success_record,
    utc_now,
    validate_approval,
    validate_observations,
    write_report,
)
from scripts.ariadne_deepseek_claude import deepseek_environment


RUNTIME_ROOT = ROOT / "local_data" / "t3r4-live"
WORKSPACE_ROOT = RUNTIME_ROOT / "empty-workspaces"
LANE_OBSERVATION_PATHS = {
    lane_id: RUNTIME_ROOT / f"{lane_id}-observations.jsonl" for lane_id in LANE_IDS
}
LANE_RESERVATION_PATHS = {
    lane_id: RUNTIME_ROOT / f"{lane_id}-reservations.jsonl" for lane_id in LANE_IDS
}


def _safe_progress(**values: Any) -> None:
    print(json.dumps(values, ensure_ascii=False, sort_keys=True), flush=True)


def _run(
    command: list[str],
    *,
    cwd: Path,
    prompt: str | None = None,
    env: Mapping[str, str] | None = None,
    timeout_seconds: int = 600,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=dict(env) if env is not None else None,
        input=prompt,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=timeout_seconds,
    )


def _usage_pair(value: Mapping[str, Any] | None) -> dict[str, int | None]:
    payload = value or {}
    input_tokens = payload.get("input_tokens")
    output_tokens = payload.get("output_tokens")
    if input_tokens is None:
        input_tokens = payload.get("input_tokens_total")
    if output_tokens is None:
        output_tokens = payload.get("output_tokens_total")
    return {
        "input_tokens": int(input_tokens) if input_tokens is not None else None,
        "output_tokens": int(output_tokens) if output_tokens is not None else None,
    }


def _walk_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_dicts(child)


def _parse_codex(stdout: str) -> tuple[dict[str, Any], dict[str, int | None], bool]:
    agent_messages: list[str] = []
    usage: dict[str, int | None] = {"input_tokens": None, "output_tokens": None}
    observed_tool_use = False
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        event_type = str(event.get("type", ""))
        item = event.get("item")
        if isinstance(item, dict):
            item_type = str(item.get("type", ""))
            if item_type == "agent_message" and isinstance(item.get("text"), str):
                agent_messages.append(item["text"])
            elif item_type and item_type not in {"reasoning"}:
                observed_tool_use = True
        if event_type in {"turn.completed", "turn_complete"} and isinstance(event.get("usage"), dict):
            usage = _usage_pair(event["usage"])
        for nested in _walk_dicts(event):
            if nested is event or nested is item:
                continue
            if nested.get("type") == "agent_message" and isinstance(nested.get("text"), str):
                agent_messages.append(nested["text"])
    if observed_tool_use:
        raise ObservedToolUse("Codex emitted a non-reasoning agent item")
    for message in reversed(agent_messages):
        try:
            return parse_json_object(message), usage, False
        except ValueError:
            continue
    raise ValueError("Codex emitted no schema-valid final agent message")


def _parse_gemini(stdout: str) -> tuple[dict[str, Any], dict[str, int | None], bool]:
    return parse_json_object(stdout), {"input_tokens": None, "output_tokens": None}, False


def _parse_deepseek(
    stdout: str,
) -> tuple[dict[str, Any], dict[str, int | None], bool, float | None, int | None]:
    wrapper = json.loads(stdout)
    if not isinstance(wrapper, dict) or wrapper.get("subtype") != "success":
        raise ValueError("DeepSeek transport did not return a successful result envelope")
    permission_denials = wrapper.get("permission_denials") or []
    if permission_denials:
        raise ObservedToolUse("DeepSeek transport recorded a permission denial")
    structured = wrapper.get("structured_output")
    if isinstance(structured, dict):
        payload = structured
        response_chars = len(json.dumps(structured, ensure_ascii=False))
    else:
        result = wrapper.get("result")
        if not isinstance(result, str):
            raise ValueError("DeepSeek result envelope lacks structured output")
        payload = parse_json_object(result)
        response_chars = len(result)
    usage = _usage_pair(wrapper.get("usage") if isinstance(wrapper.get("usage"), dict) else None)
    cost = wrapper.get("total_cost_usd")
    return payload, usage, False, float(cost) if cost is not None else None, response_chars


class ObservedToolUse(RuntimeError):
    pass


def _safe_transport_error(prefix: str, completed: subprocess.CompletedProcess[str]) -> str:
    """Reduce in-memory transport diagnostics to an allowlisted non-content code."""

    diagnostic = f"{completed.stderr}\n{completed.stdout}".lower()
    categories = (
        (("unauthorized", "authentication", "not logged in", "401"), "authentication_failed"),
        (("rate limit", "rate_limit", "quota", "429"), "quota_or_rate_limit"),
        (("model not found", "unknown model", "unsupported model", "model_not_found"), "model_unavailable"),
        (("output schema", "json schema", "response schema"), "structured_output_rejected"),
        (("unexpected argument", "unrecognized option", "unknown option"), "cli_argument_rejected"),
        (("connection", "network", "timed out", "timeout"), "transport_connectivity_failed"),
    )
    for needles, category in categories:
        if any(needle in diagnostic for needle in needles):
            return f"{prefix}_{category}"
    return f"{prefix}_exit_{completed.returncode}_unclassified"


def _codex_call(prompt: str, workspace: Path, schema_path: Path):
    codex_executable = shutil.which("codex.cmd") or shutil.which("codex")
    if not codex_executable:
        raise ProviderFailure("codex_executable_not_found")
    command = [
        codex_executable,
        "-m",
        "gpt-5.5",
        "-s",
        "read-only",
        "-a",
        "never",
        "exec",
        "-C",
        str(workspace),
        "--skip-git-repo-check",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--json",
        "-",
    ]
    completed = _run(command, cwd=workspace, prompt=prompt)
    if completed.returncode != 0:
        raise ProviderFailure(_safe_transport_error("codex", completed))
    payload, usage, _ = _parse_codex(completed.stdout)
    response_chars = len(_canonical_response(payload))
    return payload, usage, "observed_none", None, response_chars


def _gemini_call(prompt: str, workspace: Path, _schema_path: Path):
    command = [
        "agy",
        "-p",
        prompt,
        "--new-project",
        "--add-dir",
        str(workspace),
        "--model",
        "Gemini 3.5 Flash (Medium)",
        "--mode",
        "plan",
        "--sandbox",
        "--print-timeout",
        "10m",
    ]
    completed = _run(command, cwd=workspace, timeout_seconds=650)
    if completed.returncode != 0:
        raise ProviderFailure(_safe_transport_error("antigravity", completed))
    payload, usage, _ = _parse_gemini(completed.stdout)
    response_chars = len(completed.stdout)
    return payload, usage, "unobservable_on_transport", None, response_chars


def _deepseek_call(prompt: str, workspace: Path, _schema_path: Path):
    schema_json = json.dumps(live_response_schema(), ensure_ascii=False, separators=(",", ":"))
    system_prompt = (
        "Perform only the supplied synthetic evaluation. Do not use tools, files, shell, network, "
        "skills, or external context. Return the schema-constrained JSON result only."
    )
    command = [
        "claude",
        "-p",
        prompt,
        "--bare",
        "--system-prompt",
        system_prompt,
        "--model",
        "deepseek-v4-flash",
        "--effort",
        "high",
        "--output-format",
        "json",
        "--json-schema",
        schema_json,
        "--no-session-persistence",
        "--permission-mode",
        "dontAsk",
        "--tools",
        "",
        "--strict-mcp-config",
        "--mcp-config",
        '{"mcpServers":{}}',
        "--disable-slash-commands",
        "--no-chrome",
        "--max-budget-usd",
        "0.1",
    ]
    env = deepseek_environment(
        api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
        model="deepseek-v4-flash",
        effort="high",
        cwd=workspace,
    )
    completed = _run(command, cwd=workspace, env=env)
    if completed.returncode != 0:
        raise ProviderFailure(_safe_transport_error("deepseek", completed))
    payload, usage, _, cost, response_chars = _parse_deepseek(completed.stdout)
    return payload, usage, "mechanically_disabled", cost, response_chars


def _canonical_response(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


class ProviderFailure(RuntimeError):
    pass


CALLERS = {
    "openai_gpt_subscription": _codex_call,
    "google_gemini_subscription": _gemini_call,
    "deepseek_v4_flash_api": _deepseek_call,
}


def _load_reservations(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        key = item["observation_key"]
        if key in result:
            raise ValueError("duplicate T3R4 dispatch reservation")
        result[key] = item
    return result


def _reserve(path: Path, *, key: str, lane_id: str, case_id: str, sample_index: int, prompt_hash: str) -> None:
    item = {
        "schema_version": "emr4.bernie.t3r4_dispatch_reservation.v1",
        "observation_key": key,
        "lane_id": lane_id,
        "case_id": case_id,
        "sample_index": sample_index,
        "prompt_hash": prompt_hash,
        "reserved_at": utc_now(),
        "raw_prompt_persisted": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(item, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n")


def run_lane(
    lane_id: str,
    observation_path: Path,
    reservation_path: Path,
    *,
    maximum_new_samples: int | None = None,
) -> dict[str, Any]:
    if maximum_new_samples is not None and maximum_new_samples < 1:
        raise ValueError("maximum_new_samples must be positive")
    packet = load_approval()
    validate_approval(packet)
    records = load_observations(observation_path)
    reservations = _load_reservations(reservation_path)
    started_monotonic = time.monotonic()
    caller = CALLERS[lane_id]
    cases = build_lane_cases(packet, lane_id)
    total = len(cases) * 2
    newly_consumed = 0

    for case in cases:
        for sample_index in range(2):
            if maximum_new_samples is not None and newly_consumed >= maximum_new_samples:
                return {
                    "lane_id": lane_id,
                    "consumed": len(records),
                    "scheduled": total,
                    "complete": len(records) == total,
                    "newly_consumed": newly_consumed,
                    "requested_tranche_complete": True,
                }
            key = observation_key(lane_id, case.case_id, sample_index)
            current_keys = {record["observation_key"] for record in records}
            if key in current_keys:
                continue
            prompt = build_prompt(case)
            prompt_hash = canonical_hash(prompt)
            if key in reservations:
                now = utc_now()
                record = failure_record(
                    packet=packet,
                    lane_id=lane_id,
                    case=case,
                    sample_index=sample_index,
                    prompt_hash=prompt_hash,
                    status="provider_error",
                    safe_error_code="indeterminate_after_prior_dispatch_reservation",
                    started_at=reservations[key]["reserved_at"],
                    completed_at=now,
                    latency_ms=0,
                )
                append_observation(record, observation_path)
                records.append(record)
                newly_consumed += 1
                _safe_progress(lane_id=lane_id, consumed=len(records), scheduled=total, status=record["status"])
                continue

            elapsed_minutes = (time.monotonic() - started_monotonic) / 60
            DispatchState(packet, records, elapsed_minutes).assert_allowed(
                lane_id=lane_id,
                case=case,
                sample_index=sample_index,
                prompt=prompt,
            )
            _reserve(
                reservation_path,
                key=key,
                lane_id=lane_id,
                case_id=case.case_id,
                sample_index=sample_index,
                prompt_hash=prompt_hash,
            )
            reservations[key] = {"reserved_at": utc_now()}
            started_at = utc_now()
            start = time.monotonic()
            try:
                WORKSPACE_ROOT.mkdir(parents=True, exist_ok=True)
                workspace = Path(
                    tempfile.mkdtemp(prefix=f"{lane_id}-", dir=WORKSPACE_ROOT)
                )
                schema_path = workspace / "normalized-response-schema.json"
                schema_path.write_text(
                    json.dumps(live_response_schema(), ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
                payload, usage, tool_observation, cost, response_chars = caller(
                    prompt, workspace, schema_path
                )
                latency_ms = int((time.monotonic() - start) * 1000)
                completed_at = utc_now()
                maximum_chars = packet["execution_limits"][
                    "maximum_raw_response_chars_in_memory_per_sample"
                ]
                if response_chars > maximum_chars:
                    record = failure_record(
                        packet=packet,
                        lane_id=lane_id,
                        case=case,
                        sample_index=sample_index,
                        prompt_hash=prompt_hash,
                        status="response_limit_exceeded",
                        safe_error_code="response_character_ceiling_exceeded",
                        started_at=started_at,
                        completed_at=completed_at,
                        latency_ms=latency_ms,
                        usage=usage,
                        tool_observation=tool_observation,
                    )
                else:
                    record = success_record(
                        packet=packet,
                        lane_id=lane_id,
                        case=case,
                        sample_index=sample_index,
                        prompt_hash=prompt_hash,
                        normalized_payload=payload,
                        started_at=started_at,
                        completed_at=completed_at,
                        latency_ms=latency_ms,
                        usage=usage,
                        tool_observation=tool_observation,
                        estimated_cost_usd=cost,
                    )
            except ObservedToolUse:
                record = failure_record(
                    packet=packet,
                    lane_id=lane_id,
                    case=case,
                    sample_index=sample_index,
                    prompt_hash=prompt_hash,
                    status="observed_tool_use",
                    safe_error_code="transport_observed_tool_activity",
                    started_at=started_at,
                    completed_at=utc_now(),
                    latency_ms=int((time.monotonic() - start) * 1000),
                    tool_observation="observed",
                )
            except ProviderFailure as error:
                record = failure_record(
                    packet=packet,
                    lane_id=lane_id,
                    case=case,
                    sample_index=sample_index,
                    prompt_hash=prompt_hash,
                    status="provider_error",
                    safe_error_code=str(error),
                    started_at=started_at,
                    completed_at=utc_now(),
                    latency_ms=int((time.monotonic() - start) * 1000),
                )
            except (json.JSONDecodeError, ValueError) as error:
                del error
                record = failure_record(
                    packet=packet,
                    lane_id=lane_id,
                    case=case,
                    sample_index=sample_index,
                    prompt_hash=prompt_hash,
                    status="parse_error",
                    safe_error_code="normalized_response_parse_or_schema_failure",
                    started_at=started_at,
                    completed_at=utc_now(),
                    latency_ms=int((time.monotonic() - start) * 1000),
                )
            except subprocess.TimeoutExpired:
                record = failure_record(
                    packet=packet,
                    lane_id=lane_id,
                    case=case,
                    sample_index=sample_index,
                    prompt_hash=prompt_hash,
                    status="provider_error",
                    safe_error_code="provider_transport_timeout",
                    started_at=started_at,
                    completed_at=utc_now(),
                    latency_ms=int((time.monotonic() - start) * 1000),
                )

            append_observation(record, observation_path)
            records.append(record)
            newly_consumed += 1
            _safe_progress(
                lane_id=lane_id,
                consumed=len(records),
                scheduled=total,
                status=record["status"],
            )

    return {
        "lane_id": lane_id,
        "consumed": len(records),
        "scheduled": total,
        "complete": len(records) == total,
        "newly_consumed": newly_consumed,
        "requested_tranche_complete": True,
    }


def merge_lane_observations(output_path: Path = DEFAULT_OBSERVATION_PATH) -> dict[str, Any]:
    combined: list[dict[str, Any]] = []
    for lane_id in LANE_IDS:
        combined.extend(load_observations(LANE_OBSERVATION_PATHS[lane_id]))
    validate_observations(combined)
    combined.sort(key=lambda item: (LANE_IDS.index(item["lane_id"]), item["case_id"], item["sample_index"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "".join(
            json.dumps(item, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
            for item in combined
        ),
        encoding="utf-8",
        newline="\n",
    )
    report = write_report()
    if report["execution"]["all_authorized_work_complete"] is not True:
        raise ValueError("cannot close T3R4 before every lane reaches its schedule or hard stop")
    return {
        "observation_count": len(combined),
        "report_decision": report["decision"],
        "report_hash": report["report_hash"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=LANE_IDS)
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--observations", type=Path)
    parser.add_argument("--reservations", type=Path)
    parser.add_argument("--maximum-new-samples", type=int)
    args = parser.parse_args()
    try:
        if args.merge:
            print(json.dumps(merge_lane_observations(args.observations or DEFAULT_OBSERVATION_PATH), indent=2))
            return 0
        if not args.lane:
            parser.error("--lane is required unless --merge is used")
        result = run_lane(
            args.lane,
            args.observations or LANE_OBSERVATION_PATHS[args.lane],
            args.reservations or LANE_RESERVATION_PATHS[args.lane],
            maximum_new_samples=args.maximum_new_samples,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["complete"] or result["requested_tranche_complete"] else 2
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        _safe_progress(status="blocked", safe_error_code=type(error).__name__)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
