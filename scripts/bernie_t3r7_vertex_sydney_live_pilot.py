"""Run the approved T3R7 synthetic-only Sydney Vertex pilot.

The script performs a live cloud-control preflight, uses keyless prediction-
only ADC, pins the Sydney base URL, disables SDK retries and model tools, and
keeps raw prompts/responses in memory only.  Dispatch reservations make every
sample at-most-once.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Mapping
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.ai.evals.bernie_vertex_sydney_live_pilot import (
    DEFAULT_OBSERVATION_PATH,
    DEFAULT_REPORT_PATH,
    DispatchState,
    append_observation,
    build_cases,
    build_prompt,
    build_report,
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
)


RUNTIME_ROOT = ROOT / "local_data" / "t3r7-vertex-sydney-live"
LOCAL_OBSERVATION_PATH = RUNTIME_ROOT / "observations.jsonl"
RESERVATION_PATH = RUNTIME_ROOT / "reservations.jsonl"
TARGET_SERVICE_ACCOUNT_DISPLAY_NAME = "EMR4 Bernie AI Dev"
CUSTOM_ROLE = "projects/bernie-emr4-dev/roles/BernieVertexSyntheticEvaluator"
EXPECTED_BILLING_ACCOUNT_HASH = (
    "sha256:6d5c5b4c3741ad76aad86d91c16f7400ea9f03b8301e22e332996534b46f8b85"
)


def _safe_progress(**values: Any) -> None:
    print(json.dumps(values, ensure_ascii=False, sort_keys=True), flush=True)


def _run_gcloud(arguments: list[str]) -> subprocess.CompletedProcess[str]:
    executable = shutil.which("gcloud.cmd") or shutil.which("gcloud")
    if not executable:
        raise ControlFailure("gcloud_executable_not_found")
    return subprocess.run(
        [executable, *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        timeout=60,
    )


class ControlFailure(RuntimeError):
    pass


class ProviderFailure(RuntimeError):
    pass


def _gcloud_json(arguments: list[str], safe_code: str) -> Any:
    command = list(arguments)
    if not any(item.startswith("--format") for item in command):
        command.append("--format=json")
    completed = _run_gcloud(command)
    if completed.returncode != 0:
        raise ControlFailure(safe_code)
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ControlFailure(f"{safe_code}_invalid_json") from exc


def _request_response_logging_disabled(packet: Mapping[str, Any]) -> bool:
    token_result = _run_gcloud(["auth", "print-access-token"])
    if token_result.returncode != 0 or not token_result.stdout.strip():
        raise ControlFailure("request_response_logging_auth_unavailable")
    url = (
        f"{packet['provider']['base_url']}/v1beta1/projects/"
        f"{packet['provider']['project']}/locations/{packet['provider']['location']}"
        "/publishers/google/models/"
        f"{packet['provider']['model_id']}:fetchPublisherModelConfig"
    )
    request = Request(
        url,
        headers={"Authorization": f"Bearer {token_result.stdout.strip()}"},
        method="GET",
    )
    try:
        # The URL is assembled exclusively from the exact validated approval
        # constants above; no caller-controlled scheme or host is accepted.
        with urlopen(request, timeout=30) as response:  # nosec B310
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code == 404:
            return True
        raise ControlFailure("request_response_logging_check_failed") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise ControlFailure("request_response_logging_check_failed") from exc
    config = payload.get("loggingConfig") or {}
    return config.get("enabled") is not True


def verify_cloud_controls(packet: Mapping[str, Any] | None = None) -> dict[str, bool]:
    approval = packet or load_approval()
    validate_approval(approval)

    billing = _gcloud_json(
        ["billing", "projects", "describe", approval["provider"]["project"]],
        "billing_control_read_failed",
    )
    services = _gcloud_json(
        [
            "services",
            "list",
            "--enabled",
            f"--project={approval['provider']['project']}",
            "--filter=config.name:aiplatform.googleapis.com",
            "--format=json(name,state)",
        ],
        "vertex_service_control_read_failed",
    )
    service_accounts = _gcloud_json(
        [
            "iam",
            "service-accounts",
            "list",
            f"--project={approval['provider']['project']}",
            f"--filter=displayName:{TARGET_SERVICE_ACCOUNT_DISPLAY_NAME}",
            "--format=json(email,displayName,disabled)",
        ],
        "service_account_control_read_failed",
    )
    if (
        len(service_accounts) != 1
        or service_accounts[0].get("displayName")
        != TARGET_SERVICE_ACCOUNT_DISPLAY_NAME
        or service_accounts[0].get("disabled") is True
        or not service_accounts[0].get("email")
    ):
        raise ControlFailure("service_account_selection_not_exact")
    target_service_account = service_accounts[0]["email"]
    role = _gcloud_json(
        [
            "iam",
            "roles",
            "describe",
            "BernieVertexSyntheticEvaluator",
            f"--project={approval['provider']['project']}",
        ],
        "prediction_role_control_read_failed",
    )
    policy = _gcloud_json(
        ["projects", "get-iam-policy", approval["provider"]["project"]],
        "project_iam_control_read_failed",
    )

    member = f"serviceAccount:{target_service_account}"
    bound_roles = {
        item.get("role")
        for item in policy.get("bindings", [])
        if member in (item.get("members") or [])
    }
    vertex_audit = next(
        (
            item
            for item in policy.get("auditConfigs", [])
            if item.get("service") == "aiplatform.googleapis.com"
        ),
        {},
    )
    audit_types = {
        item.get("logType") for item in vertex_audit.get("auditLogConfigs", [])
    }

    import google.auth

    credentials, adc_project = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    adc_target = getattr(credentials, "service_account_email", None)
    role_permissions = set(role.get("includedPermissions") or [])
    checks = {
        "billing_enabled": billing.get("billingEnabled") is True,
        "billing_account_matches_credit": (
            "sha256:"
            + hashlib.sha256(
                str(billing.get("billingAccountName", "")).encode("utf-8")
            ).hexdigest()
        )
        == EXPECTED_BILLING_ACCOUNT_HASH,
        "vertex_ai_api_enabled": len(services) == 1
        and services[0].get("state") == "ENABLED",
        "keyless_impersonated_adc": type(credentials).__module__.endswith(
            "impersonated_credentials"
        )
        and adc_project == approval["provider"]["project"]
        and adc_target == target_service_account,
        "prediction_only_custom_role": role_permissions
        == {approval["provider"]["required_prediction_permission"]},
        "prediction_only_project_binding": bound_roles == {CUSTOM_ROLE},
        "vertex_data_read_audit_enabled": "DATA_READ" in audit_types,
        "vertex_data_write_audit_enabled": "DATA_WRITE" in audit_types,
        "request_response_logging_disabled": _request_response_logging_disabled(
            approval
        ),
        "regional_base_url_pinned": approval["provider"]["base_url"]
        == "https://australia-southeast1-aiplatform.googleapis.com",
        "automatic_sdk_retry_attempts_one": approval["required_pre_call_controls"][
            "automatic_sdk_retry_attempts"
        ]
        == 1,
    }
    failed = sorted(name for name, passed in checks.items() if not passed)
    if failed:
        raise ControlFailure("pre_call_controls_failed_" + "_".join(failed))
    return checks


def _load_reservations(path: Path = RESERVATION_PATH) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    result: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        key = value["observation_key"]
        if key in result:
            raise ValueError("duplicate T3R7 dispatch reservation")
        result[key] = value
    return result


def _reserve(
    *, case_id: str, sample_index: int, prompt_hash: str, path: Path = RESERVATION_PATH
) -> dict[str, Any]:
    value = {
        "schema_version": "emr4.bernie.t3r7_dispatch_reservation.v1",
        "observation_key": observation_key(case_id, sample_index),
        "case_id": case_id,
        "sample_index": sample_index,
        "prompt_hash": prompt_hash,
        "reserved_at": utc_now(),
        "raw_prompt_persisted": False,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(
            json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
            + "\n"
        )
    return value


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def throttle_delay_seconds(
    reservations: Mapping[str, Mapping[str, Any]], *, now: datetime, minimum_interval: float
) -> float:
    if not reservations:
        return 0.0
    latest = max(_parse_utc(str(item["reserved_at"])) for item in reservations.values())
    elapsed = (now.astimezone(timezone.utc) - latest).total_seconds()
    return max(0.0, minimum_interval - elapsed)


def _create_client(packet: Mapping[str, Any]):
    from google import genai
    from google.genai import types

    return genai.Client(
        vertexai=True,
        project=packet["provider"]["project"],
        location=packet["provider"]["location"],
        http_options=types.HttpOptions(
            base_url=packet["provider"]["base_url"],
            timeout=120_000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def _safe_provider_error(error: Exception) -> str:
    diagnostic = str(error).lower()
    categories = (
        (("429", "quota", "rate limit", "resource_exhausted"), "quota_or_rate_limit"),
        (("401", "unauthenticated", "credential"), "authentication_failed"),
        (("403", "permission", "forbidden"), "permission_denied"),
        (("404", "not found", "model"), "model_unavailable"),
        (("timeout", "timed out", "connection"), "transport_connectivity_failed"),
    )
    for needles, code in categories:
        if any(needle in diagnostic for needle in needles):
            return code
    return "provider_error_unclassified"


def _usage_and_revision(response: Any) -> tuple[int, int, str | None]:
    usage = getattr(response, "usage_metadata", None)
    input_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
    total_tokens = int(getattr(usage, "total_token_count", 0) or 0)
    candidate_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
    thoughts_tokens = int(getattr(usage, "thoughts_token_count", 0) or 0)
    output_tokens = max(candidate_tokens + thoughts_tokens, total_tokens - input_tokens, 0)
    revision = getattr(response, "model_version", None)
    return input_tokens, output_tokens, str(revision) if revision else None


def _call_vertex(client: Any, packet: Mapping[str, Any], prompt: str):
    from google.genai import types

    response = client.models.generate_content(
        model=packet["provider"]["model_id"],
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=packet["evidence"]["temperature"],
            candidate_count=1,
            max_output_tokens=packet["execution_limits"][
                "maximum_output_tokens_per_call"
            ],
            response_mime_type="application/json",
            response_json_schema=live_response_schema(),
            tools=[],
            cached_content=None,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            labels={"emr4_evaluation": "t3r7_synthetic"},
        ),
    )
    text = response.text
    if not isinstance(text, str):
        raise ValueError("Vertex returned no text")
    return parse_json_object(text), len(text), _usage_and_revision(response)


def run_pilot(
    *,
    maximum_new_samples: int | None = None,
    observation_path: Path = LOCAL_OBSERVATION_PATH,
    reservation_path: Path = RESERVATION_PATH,
) -> dict[str, Any]:
    if maximum_new_samples is not None and maximum_new_samples < 1:
        raise ValueError("maximum_new_samples must be positive")
    packet = load_approval()
    validate_approval(packet)
    controls = verify_cloud_controls(packet)
    records = load_observations(observation_path)
    reservations = _load_reservations(reservation_path)
    cases = build_cases(packet)
    started_monotonic = time.monotonic()
    new_count = 0
    client = _create_client(packet)
    try:
        for sample_index in (0, 1):
            for case in cases:
                if maximum_new_samples is not None and new_count >= maximum_new_samples:
                    return {
                        "consumed": len(records),
                        "maximum": 48,
                        "newly_consumed": new_count,
                        "complete": len(records) == 48,
                        "controls_passed": all(controls.values()),
                    }
                key = observation_key(case.case_id, sample_index)
                if key in {record["observation_key"] for record in records}:
                    continue
                prompt = build_prompt(case)
                prompt_hash = canonical_hash(prompt)
                if key in reservations:
                    reservation = reservations[key]
                    record = failure_record(
                        packet=packet,
                        case=case,
                        sample_index=sample_index,
                        prompt_hash=prompt_hash,
                        status="provider_error",
                        safe_error_code="indeterminate_after_prior_dispatch_reservation",
                        started_at=reservation["reserved_at"],
                        completed_at=utc_now(),
                        latency_ms=0,
                    )
                    append_observation(record, observation_path)
                    records.append(record)
                    new_count += 1
                    break

                DispatchState(
                    packet,
                    records,
                    (time.monotonic() - started_monotonic) / 60,
                ).assert_allowed(case=case, sample_index=sample_index, prompt=prompt)
                delay = throttle_delay_seconds(
                    reservations,
                    now=datetime.now(timezone.utc),
                    minimum_interval=packet["execution_limits"][
                        "minimum_start_interval_seconds"
                    ],
                )
                if delay:
                    time.sleep(delay)
                reservation = _reserve(
                    case_id=case.case_id,
                    sample_index=sample_index,
                    prompt_hash=prompt_hash,
                    path=reservation_path,
                )
                reservations[key] = reservation
                started_at = reservation["reserved_at"]
                call_started = time.monotonic()
                try:
                    payload, response_chars, usage = _call_vertex(client, packet, prompt)
                    latency_ms = int((time.monotonic() - call_started) * 1000)
                    if response_chars > packet["execution_limits"][
                        "maximum_raw_response_chars_in_memory_per_sample"
                    ]:
                        record = failure_record(
                            packet=packet,
                            case=case,
                            sample_index=sample_index,
                            prompt_hash=prompt_hash,
                            status="response_limit_exceeded",
                            safe_error_code="response_character_ceiling_exceeded",
                            started_at=started_at,
                            completed_at=utc_now(),
                            latency_ms=latency_ms,
                        )
                    else:
                        input_tokens, output_tokens, revision = usage
                        record = success_record(
                            packet=packet,
                            case=case,
                            sample_index=sample_index,
                            prompt_hash=prompt_hash,
                            normalized_payload=payload,
                            started_at=started_at,
                            completed_at=utc_now(),
                            latency_ms=latency_ms,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            model_version_observed=revision,
                        )
                except ValueError:
                    record = failure_record(
                        packet=packet,
                        case=case,
                        sample_index=sample_index,
                        prompt_hash=prompt_hash,
                        status="parse_error",
                        safe_error_code="normalized_response_parse_or_schema_failure",
                        started_at=started_at,
                        completed_at=utc_now(),
                        latency_ms=int((time.monotonic() - call_started) * 1000),
                    )
                except Exception as error:
                    record = failure_record(
                        packet=packet,
                        case=case,
                        sample_index=sample_index,
                        prompt_hash=prompt_hash,
                        status="provider_error",
                        safe_error_code=_safe_provider_error(error),
                        started_at=started_at,
                        completed_at=utc_now(),
                        latency_ms=int((time.monotonic() - call_started) * 1000),
                    )

                append_observation(record, observation_path)
                records.append(record)
                new_count += 1
                _safe_progress(
                    consumed=len(records),
                    maximum=48,
                    status=record["status"],
                )
                if record["status"] != "success":
                    return {
                        "consumed": len(records),
                        "maximum": 48,
                        "newly_consumed": new_count,
                        "complete": False,
                        "stopped_on_consumed_failure": True,
                        "controls_passed": all(controls.values()),
                    }
        return {
            "consumed": len(records),
            "maximum": 48,
            "newly_consumed": new_count,
            "complete": len(records) == 48,
            "controls_passed": all(controls.values()),
        }
    finally:
        client.close()


def finalize_evidence(
    *, source: Path = LOCAL_OBSERVATION_PATH,
    destination: Path = DEFAULT_OBSERVATION_PATH,
    report_destination: Path = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    records = load_observations(source)
    complete = len(records) == 48 and all(
        record["status"] == "success" for record in records
    )
    stopped = (
        bool(records)
        and records[-1]["status"] != "success"
        and all(record["status"] == "success" for record in records[:-1])
    )
    if not (complete or stopped):
        raise ValueError("T3R7 evidence is neither complete nor fail-closed terminal")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    report = build_report(load_approval(), records)
    if report["execution"]["all_authorized_work_complete"] is not True:
        raise ValueError("T3R7 reducer does not recognize terminal evidence")
    report_destination.parent.mkdir(parents=True, exist_ok=True)
    report_destination.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return {
        "observation_count": len(records),
        "report_decision": report["decision"],
        "report_hash": report["report_hash"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-controls", action="store_true")
    parser.add_argument("--maximum-new-samples", type=int)
    parser.add_argument("--finalize", action="store_true")
    args = parser.parse_args()
    try:
        if args.check_controls:
            checks = verify_cloud_controls()
            _safe_progress(status="controls_passed", checks=checks)
            return 0
        if args.finalize:
            print(json.dumps(finalize_evidence(), indent=2))
            return 0
        result = run_pilot(maximum_new_samples=args.maximum_new_samples)
        print(json.dumps(result, indent=2))
        return 0 if result.get("complete") or result.get("newly_consumed") else 2
    except (ControlFailure, OSError, RuntimeError, ValueError) as error:
        _safe_progress(status="blocked", safe_error_code=str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
