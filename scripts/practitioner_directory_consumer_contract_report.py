from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app


ROUTE = "/api/v1/practice/practitioners"
DETAIL_ROUTE_PREFIX = "/api/v1/practice/practitioners/"
SENSITIVE_FIELDS = {
    "practice_id",
    "provider_number",
    "prescriber_number",
    "ahpra_number",
    "hpi_i",
    "email",
    "phone",
    "address",
    "password_hash",
    "created_at",
    "is_active",
}


def _schema_ref_name(ref: str) -> str:
    return ref.rsplit("/", 1)[-1]


def _nullable_ref_name(schema: dict[str, Any]) -> str | None:
    for option in schema.get("anyOf", []):
        ref = option.get("$ref")
        if ref:
            return _schema_ref_name(ref)
    return None


def build_report() -> dict[str, Any]:
    openapi = app.openapi()
    paths = openapi.get("paths", {})
    route = paths.get(ROUTE, {})
    get = route.get("get", {})
    components = openapi.get("components", {}).get("schemas", {})
    practitioner = components.get("PractitionerOut", {})
    default_location = components.get("PractitionerDefaultLocationOut", {})

    params = {
        param["name"]: param.get("schema", {})
        for param in get.get("parameters", [])
        if param.get("in") == "query"
    }
    response_schema = (
        get.get("responses", {})
        .get("200", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    response_item_ref = response_schema.get("items", {}).get("$ref", "")
    fields = practitioner.get("properties", {})
    default_location_field = fields.get("defaultLocation", {})

    report = {
        "schema_version": "api_spine.practitioner_directory_consumer_contract_report.v1",
        "route": "GET /api/v1/practice/practitioners",
        "source": "fastapi_openapi_introspection",
        "operation_id": get.get("operationId"),
        "security_declared": bool(get.get("security")),
        "methods_on_route": sorted(route),
        "detail_route_present": any(path.startswith(DETAIL_ROUTE_PREFIX) for path in paths),
        "response": {
            "status_200_array": response_schema.get("type") == "array",
            "item_schema": _schema_ref_name(response_item_ref) if response_item_ref else None,
            "fields": sorted(fields),
            "required_fields": practitioner.get("required", []),
            "sensitive_fields_present": sorted(set(fields) & SENSITIVE_FIELDS),
        },
        "default_location": {
            "schema": _nullable_ref_name(default_location_field),
            "fields": sorted(default_location.get("properties", {})),
            "required_fields": default_location.get("required", []),
        },
        "query_parameters": {
            "activeOnly": {
                "type": params.get("activeOnly", {}).get("type"),
                "default": params.get("activeOnly", {}).get("default"),
            },
            "limit": {
                "type": params.get("limit", {}).get("type"),
                "default": params.get("limit", {}).get("default"),
                "minimum": params.get("limit", {}).get("minimum"),
                "maximum": params.get("limit", {}).get("maximum"),
            },
            "offset": {
                "type": params.get("offset", {}).get("type"),
                "default": params.get("offset", {}).get("default"),
                "minimum": params.get("offset", {}).get("minimum"),
            },
        },
        "adjacent_scope": {
            "graphql_delivery_ready": False,
            "provider_or_memory_ready": False,
            "write_authority_ready": False,
            "external_patient_client_ready": False,
            "deployment_ready": False,
            "production_ready": False,
        },
    }
    assert_consumer_contract_report(report)
    return report


def assert_consumer_contract_report(report: dict[str, Any]) -> None:
    assert report["source"] == "fastapi_openapi_introspection"
    assert report["security_declared"] is True
    assert report["methods_on_route"] == ["get"]
    assert report["detail_route_present"] is False
    assert report["response"]["status_200_array"] is True
    assert report["response"]["item_schema"] == "PractitionerOut"
    assert report["response"]["fields"] == [
        "active",
        "defaultLocation",
        "displayName",
        "id",
        "roleLabel",
    ]
    assert report["response"]["required_fields"] == ["id", "displayName", "active"]
    assert report["response"]["sensitive_fields_present"] == []
    assert report["default_location"]["schema"] == "PractitionerDefaultLocationOut"
    assert report["default_location"]["fields"] == ["id", "name"]
    assert report["default_location"]["required_fields"] == ["id", "name"]
    assert report["query_parameters"] == {
        "activeOnly": {"type": "boolean", "default": True},
        "limit": {"type": "integer", "default": 50, "minimum": 1, "maximum": 200},
        "offset": {"type": "integer", "default": 0, "minimum": 0},
    }
    assert all(value is False for value in report["adjacent_scope"].values())


if __name__ == "__main__":
    print(json.dumps(build_report(), indent=2, sort_keys=True))
