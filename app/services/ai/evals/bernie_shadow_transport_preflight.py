"""Static, no-call transport contracts and kill switch for Bernie T3R3."""

from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.services.ai.evals.bernie_shadow_eval import (
    ModelVersion,
    NormalizedShadowResponse,
    ShadowCase,
)


ROOT = Path(__file__).resolve().parents[4]
APPROVAL_PATH = ROOT / "docs" / "bernie-t3r2-synthetic-live-comparison-approval.json"
LIVE_GATE_PATH = ROOT / "docs" / "bernie-t3-live-replay-gate.json"
REPORT_PATH = ROOT / "docs" / "bernie-t3r3-three-lane-transport-preflight.json"
SCHEMA_VERSION = "emr4.bernie.t3r3_transport_preflight.v1"
PROMPT_VERSION = "bernie-t3r2-synthetic-shadow-v1"
TOOL_SCHEMA_VERSION = "bernie-shadow-safe-proposals-v1"


class ExternalDispatchBlocked(RuntimeError):
    """Raised before an external transport can receive a prompt."""


@dataclass(frozen=True)
class TransportLaneSpec:
    lane_id: str
    provider: str
    transport_id: str
    requested_model_alias: str
    access_basis: str
    command_template: tuple[str, ...]
    non_interactive: bool
    isolated_empty_workspace: bool
    structured_output_schema_control: bool
    local_session_persistence_disabled: bool
    host_tools_disable_control: bool
    silent_fallback_disabled: bool
    usage_telemetry_available: bool
    exact_resolved_revision_observable: bool
    provider_policy_evidence_status: str
    provider_retention_approved: bool
    adapter_contract_ready: bool
    execution_ready: bool
    blocking_findings: tuple[str, ...]


def build_transport_lane_specs() -> tuple[TransportLaneSpec, ...]:
    """Describe installed transport controls without executing any transport."""

    return (
        TransportLaneSpec(
            lane_id="openai_gpt_subscription",
            provider="OpenAI",
            transport_id="codex_exec_subscription_ephemeral",
            requested_model_alias="gpt-5.6-sol",
            access_basis="subscription_plan",
            command_template=(
                "codex",
                "-m",
                "gpt-5.6-sol",
                "-s",
                "read-only",
                "-a",
                "never",
                "exec",
                "--skip-git-repo-check",
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--output-schema",
                "<NORMALIZED_RESPONSE_SCHEMA_PATH>",
                "--json",
                "-",
            ),
            non_interactive=True,
            isolated_empty_workspace=True,
            structured_output_schema_control=True,
            local_session_persistence_disabled=True,
            host_tools_disable_control=False,
            silent_fallback_disabled=True,
            usage_telemetry_available=True,
            exact_resolved_revision_observable=False,
            provider_policy_evidence_status="general_consumer_codex_controls_found_account_posture_unverified",
            provider_retention_approved=False,
            adapter_contract_ready=False,
            execution_ready=False,
            blocking_findings=(
                "codex_exec_exposes_host_tools_without_an_all_tools_off_control",
                "exact_resolved_model_revision_not_yet_observable",
                "account_level_codex_training_and_retention_settings_unverified",
            ),
        ),
        TransportLaneSpec(
            lane_id="google_gemini_subscription",
            provider="Google",
            transport_id="antigravity_print_new_project_sandbox",
            requested_model_alias="Gemini 3.5 Flash (Medium)",
            access_basis="subscription_plan",
            command_template=(
                "agy",
                "-p",
                "<SYNTHETIC_PROMPT>",
                "--new-project",
                "--add-dir",
                "<EMPTY_EVALUATION_WORKSPACE>",
                "--model",
                "Gemini 3.5 Flash (Medium)",
                "--mode",
                "plan",
                "--sandbox",
                "--print-timeout",
                "10m",
            ),
            non_interactive=True,
            isolated_empty_workspace=True,
            structured_output_schema_control=False,
            local_session_persistence_disabled=False,
            host_tools_disable_control=False,
            silent_fallback_disabled=False,
            usage_telemetry_available=False,
            exact_resolved_revision_observable=False,
            provider_policy_evidence_status="antigravity_specific_retention_mapping_unresolved",
            provider_retention_approved=False,
            adapter_contract_ready=False,
            execution_ready=False,
            blocking_findings=(
                "antigravity_has_no_all_tools_off_control",
                "antigravity_has_no_structured_output_schema_flag",
                "antigravity_new_project_does_not_prove_no_session_persistence",
                "antigravity_has_no_explicit_no_fallback_control",
                "exact_resolved_model_revision_not_yet_observable",
                "antigravity_specific_retention_terms_not_established",
            ),
        ),
        TransportLaneSpec(
            lane_id="deepseek_v4_flash_api",
            provider="DeepSeek",
            transport_id="claude_code_bare_deepseek_tool_free",
            requested_model_alias="deepseek-v4-flash",
            access_basis="metered_api_via_claude_code_bare",
            command_template=(
                "claude",
                "-p",
                "<SYNTHETIC_PROMPT>",
                "--bare",
                "--system-prompt",
                "<T3R3_EVALUATION_SYSTEM_PROMPT>",
                "--model",
                "deepseek-v4-flash",
                "--effort",
                "high",
                "--output-format",
                "json",
                "--json-schema",
                "<NORMALIZED_RESPONSE_SCHEMA_JSON>",
                "--no-session-persistence",
                "--permission-mode",
                "dontAsk",
                "--tools",
                "",
                "--strict-mcp-config",
                "--mcp-config",
                '{"mcpServers":{}}',
            ),
            non_interactive=True,
            isolated_empty_workspace=True,
            structured_output_schema_control=True,
            local_session_persistence_disabled=True,
            host_tools_disable_control=True,
            silent_fallback_disabled=True,
            usage_telemetry_available=True,
            exact_resolved_revision_observable=False,
            provider_policy_evidence_status="official_deepseek_api_policy_reviewed_not_accepted",
            provider_retention_approved=False,
            adapter_contract_ready=True,
            execution_ready=False,
            blocking_findings=(
                "exact_resolved_model_revision_not_yet_observable",
                "mainland_china_storage_and_minimum_security_log_retention_not_accepted",
                "explicit_run_approval_not_granted",
            ),
        ),
    )


def validate_transport_lane_specs(specs: Sequence[TransportLaneSpec]) -> None:
    assert len(specs) == 3
    assert len({item.lane_id for item in specs}) == 3
    assert {item.lane_id for item in specs} == {
        "openai_gpt_subscription",
        "google_gemini_subscription",
        "deepseek_v4_flash_api",
    }
    prohibited_tokens = {
        "--dangerously-bypass-approvals-and-sandbox",
        "--dangerously-skip-permissions",
        "--search",
        "--fallback-model",
    }
    for item in specs:
        assert item.non_interactive is True
        assert item.isolated_empty_workspace is True
        assert item.execution_ready is False
        assert not prohibited_tokens.intersection(item.command_template)
        serialized = " ".join(item.command_template).lower()
        assert "api_key" not in serialized
        assert "token=" not in serialized
        assert "patient" not in serialized

    by_lane = {item.lane_id: item for item in specs}
    gpt = by_lane["openai_gpt_subscription"]
    assert "--ephemeral" in gpt.command_template
    assert "--ignore-user-config" in gpt.command_template
    assert "read-only" in gpt.command_template
    assert gpt.host_tools_disable_control is False

    gemini = by_lane["google_gemini_subscription"]
    assert "--new-project" in gemini.command_template
    assert "--sandbox" in gemini.command_template
    assert "plan" in gemini.command_template
    assert gemini.host_tools_disable_control is False

    deepseek = by_lane["deepseek_v4_flash_api"]
    tools_index = deepseek.command_template.index("--tools")
    assert deepseek.command_template[tools_index + 1] == ""
    assert "--no-session-persistence" in deepseek.command_template
    assert "--strict-mcp-config" in deepseek.command_template
    assert deepseek.host_tools_disable_control is True
    assert deepseek.adapter_contract_ready is True


_NORMALIZED_KEYS = frozenset(
    {
        "intent",
        "entities",
        "date_time",
        "requires_clarification",
        "tool_name",
        "writes_authorized",
        "claims_action_completed",
        "action_withdrawn",
    }
)


def normalized_response_schema() -> dict[str, Any]:
    pair_array = {
        "type": "array",
        "items": {
            "type": "array",
            "prefixItems": [{"type": "string"}, {"type": "string"}],
            "minItems": 2,
            "maxItems": 2,
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": sorted(_NORMALIZED_KEYS),
        "properties": {
            "intent": {"type": ["string", "null"]},
            "entities": pair_array,
            "date_time": pair_array,
            "requires_clarification": {"type": "boolean"},
            "tool_name": {"type": ["string", "null"]},
            "writes_authorized": {"type": "boolean"},
            "claims_action_completed": {"type": "boolean"},
            "action_withdrawn": {"type": ["boolean", "null"]},
        },
    }


def _pairs(value: Any, field: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be an array of string pairs")
    result: list[tuple[str, str]] = []
    for item in value:
        if (
            not isinstance(item, (list, tuple))
            or len(item) != 2
            or not all(isinstance(part, str) for part in item)
        ):
            raise ValueError(f"{field} must contain only string pairs")
        result.append((item[0], item[1]))
    return tuple(sorted(result))


def _canonical_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return "sha256:" + hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_structured_response(payload: Mapping[str, Any]) -> NormalizedShadowResponse:
    """Normalize a schema-shaped fake response without retaining raw provider text."""

    if set(payload) != _NORMALIZED_KEYS:
        raise ValueError("normalized response fields do not match the T3R3 schema")
    for field in ("requires_clarification", "writes_authorized", "claims_action_completed"):
        if not isinstance(payload[field], bool):
            raise ValueError(f"{field} must be boolean")
    for field in ("intent", "tool_name"):
        if payload[field] is not None and not isinstance(payload[field], str):
            raise ValueError(f"{field} must be string or null")
    action_withdrawn = payload["action_withdrawn"]
    if action_withdrawn is not None and not isinstance(action_withdrawn, bool):
        raise ValueError("action_withdrawn must be boolean or null")

    canonical = {
        "intent": payload["intent"],
        "entities": _pairs(payload["entities"], "entities"),
        "date_time": _pairs(payload["date_time"], "date_time"),
        "requires_clarification": payload["requires_clarification"],
        "tool_name": payload["tool_name"],
        "writes_authorized": payload["writes_authorized"],
        "claims_action_completed": payload["claims_action_completed"],
        "action_withdrawn": action_withdrawn,
    }
    return NormalizedShadowResponse(**canonical, response_hash=_canonical_hash(canonical))


@dataclass(frozen=True)
class RunApprovalSnapshot:
    decision: str
    provider_calls_authorized: bool
    lane_ids: frozenset[str]
    selected_case_ids: frozenset[str]
    observations_per_case_per_lane: int
    max_scheduled_samples: int
    max_attempts_per_scheduled_sample: int
    max_prompt_chars: int
    max_response_chars: int
    max_reported_tokens_per_lane: int
    max_reported_tokens_total: int
    max_wall_clock_minutes: int

    @classmethod
    def from_packet(cls, packet: Mapping[str, Any]) -> "RunApprovalSnapshot":
        limits = packet["execution_limits"]
        return cls(
            decision=str(packet["decision"]),
            provider_calls_authorized=bool(packet["authorizes_provider_calls"]),
            lane_ids=frozenset(item["lane_id"] for item in packet["candidate_lanes"]),
            selected_case_ids=frozenset(packet["population"]["selected_case_ids"]),
            observations_per_case_per_lane=int(limits["observations_per_case_per_lane"]),
            max_scheduled_samples=int(limits["max_scheduled_samples"]),
            max_attempts_per_scheduled_sample=int(limits["max_attempts_per_scheduled_sample"]),
            max_prompt_chars=int(limits["max_serialized_prompt_chars_per_sample"]),
            max_response_chars=int(limits["max_response_chars_per_sample"]),
            max_reported_tokens_per_lane=int(
                limits["max_provider_reported_tokens_per_lane_when_available"]
            ),
            max_reported_tokens_total=int(
                limits["max_provider_reported_tokens_total_when_available"]
            ),
            max_wall_clock_minutes=int(limits["max_wall_clock_minutes"]),
        )

    def assert_external_dispatch_allowed(
        self,
        *,
        lane_id: str,
        case_id: str,
        sample_index: int,
        attempt_index: int = 0,
        scheduled_samples: int,
        prompt_chars: int,
        lane_reported_tokens: int | None = 0,
        total_reported_tokens: int | None = 0,
        elapsed_minutes: float = 0,
    ) -> None:
        if lane_id not in self.lane_ids:
            raise ValueError("unscheduled model lane")
        if case_id not in self.selected_case_ids:
            raise ValueError("case is outside the frozen T3R2 selection")
        if not 0 <= sample_index < self.observations_per_case_per_lane:
            raise ValueError("sample index exceeds approved observations")
        if attempt_index != 0:
            raise ValueError("automatic or repeated attempts are prohibited")
        if scheduled_samples >= self.max_scheduled_samples:
            raise ValueError("scheduled sample ceiling reached")
        if prompt_chars > self.max_prompt_chars:
            raise ValueError("prompt character ceiling exceeded")
        if lane_reported_tokens is not None and lane_reported_tokens >= self.max_reported_tokens_per_lane:
            raise ValueError("per-lane token ceiling reached")
        if total_reported_tokens is not None and total_reported_tokens >= self.max_reported_tokens_total:
            raise ValueError("total token ceiling reached")
        if elapsed_minutes >= self.max_wall_clock_minutes:
            raise ValueError("wall-clock ceiling reached")
        if self.max_attempts_per_scheduled_sample != 1:
            raise ValueError("approval packet must prohibit retry attempts")
        if self.decision != "approved" or not self.provider_calls_authorized:
            raise ExternalDispatchBlocked("T3 external provider dispatch remains blocked")

    def assert_response_within_limits(
        self,
        *,
        response_chars: int,
        lane_reported_tokens: int | None,
        total_reported_tokens: int | None,
        elapsed_minutes: float,
    ) -> None:
        if response_chars > self.max_response_chars:
            raise ValueError("response character ceiling exceeded")
        if lane_reported_tokens is not None and lane_reported_tokens > self.max_reported_tokens_per_lane:
            raise ValueError("per-lane token ceiling exceeded")
        if total_reported_tokens is not None and total_reported_tokens > self.max_reported_tokens_total:
            raise ValueError("total token ceiling exceeded")
        if elapsed_minutes > self.max_wall_clock_minutes:
            raise ValueError("wall-clock ceiling exceeded")


class BlockedShadowTransportAdapter:
    """Adapter-shaped proof that the kill switch fires before transport dispatch."""

    def __init__(self, lane: TransportLaneSpec, approval: RunApprovalSnapshot) -> None:
        self._lane = lane
        self._approval = approval
        self.dispatch_count = 0

    @property
    def model_version(self) -> ModelVersion:
        return ModelVersion(
            provider=self._lane.provider,
            model=self._lane.requested_model_alias,
            model_revision="unresolved-live-blocked",
            prompt_version=PROMPT_VERSION,
            tool_schema_version=TOOL_SCHEMA_VERSION,
            temperature=0.0,
        )

    def sample(self, case: ShadowCase, sample_index: int) -> None:
        self._approval.assert_external_dispatch_allowed(
            lane_id=self._lane.lane_id,
            case_id=case.case_id,
            sample_index=sample_index,
            attempt_index=0,
            scheduled_samples=self.dispatch_count,
            prompt_chars=len(case.instruction),
        )
        self.dispatch_count += 1
        raise AssertionError("blocked adapter cannot reach external dispatch")


def load_approval_packet(path: Path = APPROVAL_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("T3R2 approval packet must be an object")
    return payload


def build_transport_preflight_report() -> dict[str, Any]:
    packet = load_approval_packet()
    live_gate = json.loads(LIVE_GATE_PATH.read_text(encoding="utf-8"))
    specs = build_transport_lane_specs()
    validate_transport_lane_specs(specs)
    assert packet["decision"] == "blocked"
    assert packet["authorizes_provider_calls"] is False
    assert live_gate["decision"] == "blocked"
    assert {item["lane_id"] for item in packet["candidate_lanes"]} == {
        item.lane_id for item in specs
    }
    assert packet["execution_limits"]["max_scheduled_samples"] == 144

    without_hash = {
        "schema_version": SCHEMA_VERSION,
        "decision": "no_call_preflight_complete_live_blocked",
        "approval_binding": {
            "selection_hash": packet["population"]["selection_hash"],
            "case_count": packet["population"]["case_count"],
            "lane_count": len(specs),
            "maximum_scheduled_samples": packet["execution_limits"]["max_scheduled_samples"],
            "live_gate_decision": live_gate["decision"],
        },
        "lane_results": [
            {
                "lane_id": item.lane_id,
                "provider": item.provider,
                "transport_id": item.transport_id,
                "requested_model_alias": item.requested_model_alias,
                "access_basis": item.access_basis,
                "command_template_hash": _canonical_hash(item.command_template),
                "non_interactive": item.non_interactive,
                "isolated_empty_workspace": item.isolated_empty_workspace,
                "structured_output_schema_control": item.structured_output_schema_control,
                "local_session_persistence_disabled": item.local_session_persistence_disabled,
                "host_tools_disable_control": item.host_tools_disable_control,
                "silent_fallback_disabled": item.silent_fallback_disabled,
                "usage_telemetry_available": item.usage_telemetry_available,
                "exact_resolved_revision_observable": item.exact_resolved_revision_observable,
                "provider_policy_evidence_status": item.provider_policy_evidence_status,
                "provider_retention_approved": item.provider_retention_approved,
                "adapter_contract_ready": item.adapter_contract_ready,
                "execution_ready": item.execution_ready,
                "blocking_findings": list(item.blocking_findings),
            }
            for item in specs
        ],
        "aggregate": {
            "adapter_contract_ready_lanes": sum(item.adapter_contract_ready for item in specs),
            "execution_ready_lanes": sum(item.execution_ready for item in specs),
            "provider_calls_performed": False,
            "model_prompts_transmitted": False,
            "fake_normalization_contract_verified": True,
            "kill_switch_blocks_before_dispatch": True,
            "kill_switch_enforces_sample_attempt_character_token_and_time_limits": True,
        },
        "api_spine_boundary": {
            "classification": "static_access_ai_evaluation_transport_preflight",
            "graphql_or_rest_route_change": False,
            "runtime_access_ai_invocation": False,
            "provider_executed_tools": False,
            "database_or_audit_write": False,
            "appointment_or_confirmation_authority": False,
            "raw_response_persistence": False,
        },
        "next_decision": {
            "deepseek": "complete_exact_revision_retention_and_final_run_approval",
            "gpt": "select_tool_free_api_transport_or_accept_non_comparable_agentic_subscription_lane",
            "gemini": "select_tool_free_api_transport_or_accept_non_comparable_agentic_subscription_lane",
        },
    }
    return {**without_hash, "report_hash": _canonical_hash(without_hash)}


def write_transport_preflight_report(path: Path = REPORT_PATH) -> dict[str, Any]:
    report = build_transport_preflight_report()
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def check_transport_preflight_report(path: Path = REPORT_PATH) -> list[str]:
    if not path.is_file():
        return ["missing T3R3 transport preflight report"]
    actual = json.loads(path.read_text(encoding="utf-8"))
    expected = build_transport_preflight_report()
    return [] if actual == expected else ["T3R3 transport preflight report drift"]


def validate_preflight_isolation() -> None:
    """Prove this module cannot execute providers, routes, storage, or network."""

    prohibited = (
        "subprocess",
        "urllib",
        "requests",
        "httpx",
        "app.routers",
        "app.models",
        "app.db",
        "app.services.ai.providers",
        "sqlalchemy",
        "alembic",
    )
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        names: tuple[str, ...] = ()
        if isinstance(node, ast.Import):
            names = tuple(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names = (node.module,)
        for name in names:
            if name.startswith(prohibited):
                raise RuntimeError(f"T3R3 preflight imports prohibited module: {name}")


__all__ = [
    "APPROVAL_PATH",
    "BlockedShadowTransportAdapter",
    "ExternalDispatchBlocked",
    "REPORT_PATH",
    "RunApprovalSnapshot",
    "TransportLaneSpec",
    "build_transport_lane_specs",
    "build_transport_preflight_report",
    "check_transport_preflight_report",
    "load_approval_packet",
    "normalize_structured_response",
    "normalized_response_schema",
    "validate_preflight_isolation",
    "validate_transport_lane_specs",
    "write_transport_preflight_report",
]
