"""Isolated request-contract recovery adapter for the accepted A3/B3 proof plane."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

from scripts import model_required_bureau_a3_b3_contracts as parent
from scripts.model_required_bureau_a3_b3_contracts import *  # noqa: F403


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / (
    "orchestration/continuity/"
    "model-required-bureau-a3-b3-request-contract-recovery"
)
POLICY_ID = "emr4-model-required-bureau-a3-b3-sydney-recovery-v1"
THINKING_BUDGET = 1024
MAX_OUTPUT_TOKENS = 2048

# The accepted authored-synthetic frames and proofreader schemas are immutable
# inputs. Only new execution outputs and accounting live in ARTIFACT_ROOT.
RAYLEEN_CONTEXT_PATH = parent.RAYLEEN_CONTEXT_PATH
DAVIDA_CONTEXT_PATH = parent.DAVIDA_CONTEXT_PATH


def build_vertex_request(lane: str, context: dict[str, Any]) -> dict[str, Any]:
    """Replace unbounded thinking with an explicit reasoning/output envelope."""
    request = deepcopy(parent.build_vertex_request(lane, context))
    request["generationConfig"]["maxOutputTokens"] = MAX_OUTPUT_TOKENS
    request["generationConfig"]["thinkingConfig"] = {
        "thinkingBudget": THINKING_BUDGET
    }
    if len(canonical_bytes(request)) > MAX_PROVIDER_REQUEST_BYTES:  # noqa: F405
        raise ContractError("provider_request_oversized")  # noqa: F405
    return request


def correction_request(
    lane: str,
    context: dict[str, Any],
    reason_code: str,
    attempt_number: int,
) -> dict[str, Any]:
    if attempt_number != 2 or reason_code != "schema_invalid":
        raise ContractError("correction_not_eligible")  # noqa: F405
    request = build_vertex_request(lane, context)
    repair_text = (
        "CORRECTION_TICKET: The prior object failed the closed response contract. "
        "Return a complete replacement object using the same context and task. "
        "Do not change identifiers, meaning or authority."
    )
    request["contents"][0]["parts"][0]["text"] = "\n".join(
        (repair_text, request["contents"][0]["parts"][0]["text"])
    )
    return request


def provider_request_for_attempt(
    lane: str,
    context: dict[str, Any],
    *,
    attempt_number: int,
    correction_reason_code: str | None,
) -> dict[str, Any]:
    if attempt_number == 1 and correction_reason_code is None:
        return build_vertex_request(lane, context)
    if attempt_number == 2 and correction_reason_code == "schema_invalid":
        return correction_request(
            lane, context, correction_reason_code, attempt_number
        )
    raise ContractError("attempt_contract_invalid")  # noqa: F405


def bounded_provider_metadata(packet: dict[str, Any]) -> dict[str, Any]:
    """Classify response shape without retaining provider-authored values."""
    safe = parent.bounded_provider_metadata(packet)
    candidates = packet.get("candidates")
    first = candidates[0] if isinstance(candidates, list) and candidates else None
    content = first.get("content") if isinstance(first, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    part_kinds: list[str] = []
    text_bytes = 0
    if isinstance(parts, list):
        for part in parts[:32]:
            if not isinstance(part, dict):
                part_kinds.append("non_object")
            elif part.get("thought") is True:
                part_kinds.append("thought")
            elif isinstance(part.get("text"), str):
                part_kinds.append("text")
                text_bytes += len(part["text"].encode("utf-8"))
            elif "functionCall" in part:
                part_kinds.append("function_call")
            elif "functionResponse" in part:
                part_kinds.append("function_response")
            elif "inlineData" in part or "fileData" in part:
                part_kinds.append("data")
            else:
                part_kinds.append("unknown")
    feedback = packet.get("promptFeedback")
    block_reason = feedback.get("blockReason") if isinstance(feedback, dict) else None
    if block_reason not in {
        "BLOCK_REASON_UNSPECIFIED", "SAFETY", "OTHER", "BLOCKLIST",
        "PROHIBITED_CONTENT", "MODEL_ARMOR", "JAILBREAK", None,
    }:
        block_reason = "UNRECOGNIZED"
    safe.update(
        {
            "content_present": isinstance(content, dict),
            "parts_count": len(parts) if isinstance(parts, list) else 0,
            "part_kinds": part_kinds,
            "text_utf8_bytes": text_bytes,
            "prompt_block_reason": block_reason,
        }
    )
    return safe


def extract_provider_candidate(packet: dict[str, Any]) -> dict[str, Any]:
    candidates = packet.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        raise ContractError("provider_candidate_count_invalid")  # noqa: F405
    candidate = candidates[0]
    if not isinstance(candidate, dict) or "content" not in candidate:
        raise ContractError("provider_content_missing")  # noqa: F405
    content = candidate.get("content")
    if not isinstance(content, dict):
        raise ContractError("provider_content_invalid")  # noqa: F405
    parts = content.get("parts")
    if not isinstance(parts, list):
        raise ContractError("provider_parts_invalid")  # noqa: F405
    if not parts:
        raise ContractError("provider_parts_empty")  # noqa: F405
    if len(parts) != 1:
        raise ContractError("provider_parts_count_invalid")  # noqa: F405
    part = parts[0]
    if not isinstance(part, dict):
        raise ContractError("provider_part_non_text_invalid")  # noqa: F405
    if part.get("thought") is True:
        raise ContractError("provider_part_thought_invalid")  # noqa: F405
    text = part.get("text")
    if not isinstance(text, str) or len(text.encode("utf-8")) > 32768:
        raise ContractError("provider_part_non_text_invalid")  # noqa: F405
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise ContractError("provider_candidate_not_json") from error  # noqa: F405
    if not isinstance(value, dict):
        raise ContractError("provider_candidate_not_object")  # noqa: F405
    return value
