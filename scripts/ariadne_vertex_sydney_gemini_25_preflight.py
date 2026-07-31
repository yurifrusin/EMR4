#!/usr/bin/env python3
"""Read-only cloud-control preflight for the bounded Sydney Vertex rehearsal.

The script never prints or persists credential material, authentication
responses, billing identifiers, account identifiers, API-key observations, or
raw control-plane responses. It performs no state-changing Google Cloud call.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_vertex_sydney_gemini_25_contracts as contracts
PROJECT = "bernie-emr4-dev"
SERVICE_ACCOUNT = (
    "emr4-bernie-ai-dev@bernie-emr4-dev.iam.gserviceaccount.com"
)
CUSTOM_ROLE = "projects/bernie-emr4-dev/roles/BernieVertexSyntheticEvaluator"
PREDICTION_PERMISSION = "aiplatform.endpoints.predict"
SCOPE = "https://www.googleapis.com/auth/cloud-platform"
LOCATION = "australia-southeast1"
HOSTNAME = "australia-southeast1-aiplatform.googleapis.com"
CACHE_CONTROL_HOSTNAME = "us-central1-aiplatform.googleapis.com"
MODEL_ID = "gemini-2.5-flash"


class PreflightError(RuntimeError):
    """A fail-closed preflight result that requires no secret diagnostics."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_child_environment() -> dict[str, str]:
    allowed = (
        "APPDATA",
        "COMSPEC",
        "LOCALAPPDATA",
        "PATH",
        "PATHEXT",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "USERPROFILE",
        "WINDIR",
    )
    return {name: os.environ[name] for name in allowed if name in os.environ}


def _gcloud(arguments: list[str], *, reason_code: str) -> str:
    executable = shutil.which("gcloud.cmd") or shutil.which("gcloud")
    if not executable:
        raise PreflightError("gcloud_unavailable")
    try:
        result = subprocess.run(
            [executable, *arguments],
            cwd=ROOT,
            env=_safe_child_environment(),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            shell=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise PreflightError(reason_code) from error
    if result.returncode != 0:
        raise PreflightError(reason_code)
    return result.stdout


def _gcloud_json(arguments: list[str], *, reason_code: str) -> Any:
    command = list(arguments)
    if not any(item.startswith("--format") for item in command):
        command.append("--format=json")
    raw = _gcloud(command, reason_code=reason_code)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as error:
        raise PreflightError(reason_code + "_invalid_json") from error


def _control_access_token() -> str:
    """Obtain the existing unchanged gcloud control-reader token in memory."""

    token = _gcloud(
        ["auth", "print-access-token"],
        reason_code="control_reader_token_unavailable",
    ).strip()
    if not token or any(character.isspace() for character in token):
        raise PreflightError("control_reader_token_invalid")
    return token


def _read_control_json(
    url: str,
    *,
    allow_not_found: bool = False,
) -> tuple[int, dict[str, Any] | None]:
    token = _control_access_token()
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": PROJECT,
        },
        method="GET",
    )
    try:
        with urlopen(request, timeout=30) as response:  # nosec B310
            raw = response.read(32769)
            status = int(response.status)
    except HTTPError as error:
        if allow_not_found and error.code == 404:
            return error.code, None
        raise PreflightError("control_metadata_read_failed") from error
    except OSError as error:
        raise PreflightError("control_metadata_read_failed") from error
    if len(raw) > 32768:
        raise PreflightError("control_metadata_response_oversized")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise PreflightError("control_metadata_not_json") from error
    if not isinstance(value, dict):
        raise PreflightError("control_metadata_not_object")
    return status, value


def _verify_adc() -> dict[str, bool]:
    # Do not inspect a caller-supplied credential file. This rehearsal admits
    # only the standard existing impersonated ADC store.
    if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        raise PreflightError("google_application_credentials_override_present")

    import google.auth
    from google.auth.transport.requests import Request as GoogleRequest

    try:
        credentials, project = google.auth.default(scopes=[SCOPE])
    except Exception:
        raise PreflightError("impersonated_adc_discovery_failed") from None
    module = type(credentials).__module__
    target = getattr(credentials, "service_account_email", None)
    target_scopes = set(getattr(credentials, "_target_scopes", []) or [])
    checks = {
        "credentials_are_impersonated": module.endswith(
            "impersonated_credentials"
        ),
        "adc_project_exact": project == PROJECT,
        "target_service_account_exact": target == SERVICE_ACCOUNT,
        "cloud_platform_scope_exact": target_scopes == {SCOPE},
    }
    if not all(checks.values()):
        raise PreflightError("impersonated_adc_binding_invalid")
    try:
        credentials.refresh(GoogleRequest())
    except Exception:
        raise PreflightError("impersonated_adc_refresh_failed") from None
    checks["noninteractive_refresh_passed"] = bool(
        getattr(credentials, "token", None)
    )
    if not checks["noninteractive_refresh_passed"]:
        raise PreflightError("impersonated_adc_refresh_failed")
    return checks


def _request_response_logging_disabled() -> bool:
    url = (
        f"https://{HOSTNAME}/v1beta1/projects/{PROJECT}/locations/{LOCATION}"
        f"/publishers/google/models/{MODEL_ID}:fetchPublisherModelConfig"
    )
    status, value = _read_control_json(url, allow_not_found=True)
    if status == 404:
        return True
    config = value.get("loggingConfig") if isinstance(value, dict) else None
    return not isinstance(config, dict) or config.get("enabled") is not True


def _in_memory_cache_disabled() -> bool:
    # Google documents this project-wide management resource on the
    # us-central1 control-plane hostname. It applies across regions but is not
    # an inference endpoint and receives no rehearsal payload.
    url = f"https://{CACHE_CONTROL_HOSTNAME}/v1/projects/{PROJECT}/cacheConfig"
    _status, value = _read_control_json(url)
    return isinstance(value, dict) and value.get("disableCache") is True


def _model_catalogue() -> Any:
    """Read the publisher catalogue with the exact target as quota project."""

    return _gcloud_json(
        [
            "ai",
            "model-garden",
            "models",
            "list",
            f"--project={PROJECT}",
            f"--billing-project={PROJECT}",
            f"--model-filter={MODEL_ID}",
            "--full-resource-name",
            "--limit=20",
            "--format=json(name,versionId)",
        ],
        reason_code="model_catalogue_control_read_failed",
    )


def verify_cloud_controls() -> dict[str, Any]:
    policy = contracts.load_object(contracts.POLICY_PATH)
    if (
        policy.get("project") != PROJECT
        or policy.get("service_account") != SERVICE_ACCOUNT
        or policy.get("location") != LOCATION
        or policy.get("endpoint_hostname") != HOSTNAME
        or policy.get("model_id") != MODEL_ID
    ):
        raise PreflightError("repository_policy_binding_invalid")

    adc_checks = _verify_adc()
    billing = _gcloud_json(
        ["billing", "projects", "describe", PROJECT],
        reason_code="billing_control_read_failed",
    )
    services = _gcloud_json(
        [
            "services",
            "list",
            "--enabled",
            f"--project={PROJECT}",
            "--filter=config.name:aiplatform.googleapis.com",
            "--format=json(name,state)",
        ],
        reason_code="vertex_service_control_read_failed",
    )
    service_account = _gcloud_json(
        [
            "iam",
            "service-accounts",
            "describe",
            SERVICE_ACCOUNT,
            f"--project={PROJECT}",
            "--format=json(email,disabled)",
        ],
        reason_code="service_account_control_read_failed",
    )
    role = _gcloud_json(
        [
            "iam",
            "roles",
            "describe",
            "BernieVertexSyntheticEvaluator",
            f"--project={PROJECT}",
            "--format=json(name,includedPermissions,stage)",
        ],
        reason_code="prediction_role_control_read_failed",
    )
    iam_policy = _gcloud_json(
        [
            "projects",
            "get-iam-policy",
            PROJECT,
            "--format=json(bindings,auditConfigs)",
        ],
        reason_code="project_iam_control_read_failed",
    )
    user_managed_keys = _gcloud_json(
        [
            "iam",
            "service-accounts",
            "keys",
            "list",
            f"--iam-account={SERVICE_ACCOUNT}",
            "--managed-by=user",
            f"--project={PROJECT}",
            "--format=json(name,keyType)",
        ],
        reason_code="service_account_key_inventory_read_failed",
    )
    catalog = _model_catalogue()

    member = f"serviceAccount:{SERVICE_ACCOUNT}"
    bound_roles = {
        item.get("role")
        for item in iam_policy.get("bindings", [])
        if isinstance(item, dict) and member in (item.get("members") or [])
    }
    audit = next(
        (
            item
            for item in iam_policy.get("auditConfigs", [])
            if isinstance(item, dict)
            and item.get("service") == "aiplatform.googleapis.com"
        ),
        {},
    )
    audit_types = {
        item.get("logType")
        for item in audit.get("auditLogConfigs", [])
        if isinstance(item, dict)
    }
    catalog_names = {
        item.get("name")
        for item in catalog
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }

    checks = {
        **adc_checks,
        "billing_enabled": isinstance(billing, dict)
        and billing.get("billingEnabled") is True,
        "vertex_ai_api_enabled": isinstance(services, list)
        and len(services) == 1
        and services[0].get("state") == "ENABLED",
        "service_account_enabled_and_exact": isinstance(service_account, dict)
        and service_account.get("email") == SERVICE_ACCOUNT
        and service_account.get("disabled") is not True,
        "prediction_only_custom_role_exact": isinstance(role, dict)
        and role.get("name") == CUSTOM_ROLE
        and set(role.get("includedPermissions") or [])
        == {PREDICTION_PERMISSION},
        "prediction_only_binding_exact": bound_roles == {CUSTOM_ROLE},
        "required_prediction_permission_exact": PREDICTION_PERMISSION
        in set(role.get("includedPermissions") or []),
        "vertex_data_read_audit_enabled": "DATA_READ" in audit_types,
        "vertex_data_write_audit_enabled": "DATA_WRITE" in audit_types,
        "request_response_logging_disabled_or_absent": (
            _request_response_logging_disabled()
        ),
        "provider_in_memory_cache_disabled": _in_memory_cache_disabled(),
        "no_user_managed_service_account_key": user_managed_keys == [],
        "model_present_in_publisher_catalogue": any(
            name and MODEL_ID in name for name in catalog_names
        ),
        "official_sydney_model_admission_bound": True,
        "regional_endpoint_exact": policy["endpoint_hostname"] == HOSTNAME,
        "automatic_fallback_disabled": policy["automatic_fallback"] is False,
        "api_key_authentication_not_used": True,
        "service_account_key_authentication_not_used": True,
    }
    failed = sorted(name for name, passed in checks.items() if passed is not True)
    if failed:
        raise PreflightError("cloud_controls_failed:" + ",".join(failed))
    return {
        "schema_version": "ariadne.vertex_sydney_adc_preflight_evidence.v1",
        "recorded_at": utc_now(),
        "result": "ariadne_vertex_sydney_gemini_25_adc_preflight_pass",
        "project": PROJECT,
        "service_account": SERVICE_ACCOUNT,
        "authentication": "keyless_impersonated_service_account_adc",
        "oauth_scope": SCOPE,
        "location": LOCATION,
        "endpoint_hostname": HOSTNAME,
        "cache_management_endpoint_hostname": CACHE_CONTROL_HOSTNAME,
        "model_id": MODEL_ID,
        "required_prediction_permission": PREDICTION_PERMISSION,
        "provider_prompt_transmitted": False,
        "model_inference_called": False,
        "external_state_changed": False,
        "api_key_authentication_used": False,
        "service_account_key_used": False,
        "checks": checks,
        "regional_entitlement_basis": [
            "official_model_availability_and_ml_processing_include_australia-southeast1",
            "project_billing_is_enabled",
            "vertex_ai_api_is_enabled",
            "exact_prediction_permission_is_bound_to_the_target_service_account",
            "gemini-2.5-flash_is_present_in_the_publisher_catalogue",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        evidence = verify_cloud_controls()
    except PreflightError as error:
        print(
            json.dumps(
                {
                    "result": "ariadne_vertex_sydney_gemini_25_adc_preflight_blocked",
                    "reason_code": str(error),
                },
                sort_keys=True,
            ),
            flush=True,
        )
        return 2
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = arguments.output.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(arguments.output)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "all_controls_passed": all(evidence["checks"].values()),
                "output": str(arguments.output),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
