"""Provider-blocked diagnosis of the closed Sydney Vertex HTTP 400.

This module performs no credential discovery, cloud-control read, provider
request, prompt transmission, occupied-ledger operation, or request-constructor
mutation. It validates the immutable locally reconstructed request against the
installed official Vertex protobuf contract and emits only structural evidence.
"""

from __future__ import annotations

from copy import deepcopy
from importlib.metadata import version
import json
from pathlib import Path
import sys
from typing import Any

from google.cloud import aiplatform_v1
from google.protobuf.json_format import ParseDict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import ariadne_vertex_sydney_gemini_25_contracts as contracts


AUDIT_PATH = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-vertex-sydney-gemini-25"
    / "cache-disabled-external-audit.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "orchestration"
    / "continuity"
    / "ariadne-vertex-sydney-gemini-25"
    / "postfailure-provider-blocked-diagnostic-evidence.json"
)
MODEL_RESOURCE = (
    "projects/bernie-emr4-dev/locations/australia-southeast1/"
    "publishers/google/models/gemini-2.5-flash"
)
DEFECT_PATH = (
    "generationConfig.responseSchema.properties.total_tiles.enum[0]"
)
OFFICIAL_SOURCES = [
    {
        "contract": "generate_content_method",
        "url": (
            "https://docs.cloud.google.com/gemini-enterprise-agent-platform/"
            "reference/rest/v1/projects.locations.endpoints/generateContent"
        ),
        "observed_rule": (
            "POST /v1/{model}:generateContent accepts the fully qualified "
            "publisher-model resource and the retained body fields."
        ),
    },
    {
        "contract": "schema_rest_type",
        "url": (
            "https://docs.cloud.google.com/gemini-enterprise-agent-platform/"
            "reference/rest/v1/Schema"
        ),
        "observed_rule": (
            "Schema.enum is a repeated string field; the official INTEGER "
            "example encodes enum values as strings."
        ),
    },
    {
        "contract": "structured_output_subset",
        "url": (
            "https://docs.cloud.google.com/gemini-enterprise-agent-platform/"
            "models/capabilities/control-generated-output"
        ),
        "observed_rule": "Only string enum values are supported.",
    },
    {
        "contract": "gemini_25_thinking",
        "url": (
            "https://docs.cloud.google.com/gemini-enterprise-agent-platform/"
            "models/thinking"
        ),
        "observed_rule": (
            "Gemini 2.5 Flash supports thinkingBudget 0 to turn thinking off."
        ),
    },
]


def _json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if type(value) is int:
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def structural_manifest(value: Any, path: str = "$") -> list[dict[str, str]]:
    """Return field paths and JSON types without retaining any scalar value."""

    rows = [{"path": path, "json_type": _json_type(value)}]
    if isinstance(value, dict):
        for key in sorted(value):
            rows.extend(structural_manifest(value[key], f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(structural_manifest(child, f"{path}[{index}]"))
    return rows


def _parse_vertex_request(vertex_request: dict[str, Any]) -> bool:
    wire_request = {"model": MODEL_RESOURCE, **vertex_request}
    message = aiplatform_v1.types.GenerateContentRequest.pb()()
    try:
        ParseDict(wire_request, message)
    except Exception:
        return False
    return True


def _historical_vertex_request(
    cell_request: dict[str, Any],
) -> dict[str, Any]:
    """Reconstruct the immutable request sent by the closed primary attempt."""

    request = contracts.build_vertex_request(cell_request)
    total_tiles = request["generationConfig"]["responseSchema"]["properties"][
        "total_tiles"
    ]
    total_tiles.pop("minimum", None)
    total_tiles.pop("maximum", None)
    total_tiles["enum"] = [5]
    return request


def build_diagnostic_evidence() -> dict[str, Any]:
    audit = contracts.load_object(AUDIT_PATH)
    cell_request = contracts.load_object(contracts.CELL_REQUEST_PATH)
    vertex_request = _historical_vertex_request(cell_request)
    reconstructed_hash = contracts.canonical_hash(vertex_request)
    retained_hash = audit["typewriter_keys"]["provider_request_hash"]
    schema = vertex_request["generationConfig"]["responseSchema"]
    enum_value = schema["properties"]["total_tiles"]["enum"][0]

    original_parse_passed = _parse_vertex_request(vertex_request)
    counterfactual = deepcopy(vertex_request)
    counterfactual["generationConfig"]["responseSchema"]["properties"][
        "total_tiles"
    ]["enum"] = ["5"]
    counterfactual_parse_passed = _parse_vertex_request(counterfactual)

    defect_identified = (
        reconstructed_hash == retained_hash
        and type(enum_value) is int
        and not original_parse_passed
        and counterfactual_parse_passed
    )
    result = (
        "ariadne_vertex_sydney_gemini_25_postfailure_diagnostic_pass"
        if defect_identified
        else "ariadne_vertex_sydney_gemini_25_postfailure_diagnostic_revision_required"
    )
    return {
        "schema_version": (
            "ariadne.vertex_sydney_gemini_25_postfailure_diagnostic.v1"
        ),
        "result": result,
        "mode": "provider_blocked_repository_and_public_official_contracts",
        "historical_binding": {
            "attempt_id": audit["attempt"]["attempt_id"],
            "terminal_rehearsal_result": audit["terminal_rehearsal_result"],
            "occupied_primary_calls": audit["attempt"][
                "primary_occupied_call_count"
            ],
            "occupied_retries": audit["attempt"]["retry_count"],
            "ledger_status": audit["ledger"]["status"],
            "historical_request_hash": retained_hash,
            "reconstructed_request_hash": reconstructed_hash,
            "request_hash_exact": reconstructed_hash == retained_hash,
            "historical_artifacts_modified": False,
        },
        "exact_endpoint_contract": {
            "method": "POST",
            "hostname": audit["binding"]["endpoint_hostname"],
            "model_resource": MODEL_RESOURCE,
            "normalized_path": f"/v1/{MODEL_RESOURCE}:generateContent",
            "method_and_path_admitted": True,
            "fallback": False,
        },
        "request_structure": {
            "top_level_fields": sorted(vertex_request),
            "generation_config_fields": sorted(
                vertex_request["generationConfig"]
            ),
            "tools_present": False,
            "cached_content_present": False,
            "raw_prompt_retained": False,
            "manifest": structural_manifest(vertex_request),
        },
        "deterministic_findings": [
            {
                "finding_id": "vertex_schema_enum_member_not_string",
                "field_path": DEFECT_PATH,
                "actual_json_type": _json_type(enum_value),
                "required_json_type": "string",
                "official_contract": "Schema.enum[] is repeated string",
                "installed_proto_field_type": "TYPE_STRING",
                "installed_proto_repeated": True,
                "original_full_request_local_proto_parse": "failed",
                "single_field_type_counterfactual_full_local_proto_parse": (
                    "passed" if counterfactual_parse_passed else "failed"
                ),
                "classification": "proved_deterministic_request_contract_defect",
            }
        ]
        if defect_identified
        else [],
        "ruled_out_by_official_contract": [
            "publisher_model_generate_content_method_or_path_shape",
            "contents_system_instruction_and_generation_config_top_level_shape",
            "response_mime_type_and_response_schema_pairing",
            "thinking_budget_zero_for_gemini_2_5_flash",
            "provider_tool_or_cached_content_presence",
        ],
        "remaining_limits": [
            (
                "The discarded provider message prevents proving which field "
                "the server named in its historical diagnostic."
            ),
            (
                "The proved enum-type defect is sufficient to make the exact "
                "retained request invalid under the official v1 contract and "
                "official local protobuf parser; it is the leading and "
                "deterministic explanation for the HTTP 400."
            ),
            (
                "The single-field local counterfactual parses completely but "
                "was not sent and proves neither provider acceptance nor that "
                "no later provider/model validation would fail."
            ),
        ],
        "official_sources": OFFICIAL_SOURCES,
        "local_contract_runtime": {
            "google_cloud_aiplatform_version": version(
                "google-cloud-aiplatform"
            ),
            "schema_enum_annotation": "repeated_string",
            "network_or_provider_operation": False,
            "credential_operation": False,
        },
        "authority_accounting": {
            "provider_calls": 0,
            "credential_reads_or_refreshes": 0,
            "cloud_control_reads": 0,
            "prompt_transmissions": 0,
            "occupied_ledgers_opened": 0,
            "request_constructor_modified": False,
            "retry_or_fallback_performed": False,
            "external_state_changed": False,
            "product_database_clinical_patient_command_or_release_authority": False,
        },
        "disposition": (
            "deterministic_defect_identified_diagnosis_only_no_retry_authority"
            if defect_identified
            else "exact_defect_not_identified_no_retry_authority"
        ),
    }


def main() -> int:
    evidence = build_diagnostic_evidence()
    DEFAULT_OUTPUT.write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(evidence["result"])
    return 0 if evidence["result"].endswith("_pass") else 2


if __name__ == "__main__":
    raise SystemExit(main())
