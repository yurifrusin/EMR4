"""Run the accepted one-use broker against the isolated recovery contract."""

from __future__ import annotations

from typing import Any

from scripts import model_required_bureau_a3_b3_broker as broker
from scripts import model_required_bureau_a3_b3_recovery_contracts as contracts


def _safe_provider_metadata(value: Any) -> dict[str, Any]:
    safe = _PARENT_SAFE_PROVIDER_METADATA(value)
    if not isinstance(value, dict):
        return safe
    for key in ("content_present",):
        if type(value.get(key)) is bool:
            safe[key] = value[key]
    for key in ("parts_count", "text_utf8_bytes"):
        item = value.get(key)
        if type(item) is int and item >= 0:
            safe[key] = item
    kinds = value.get("part_kinds")
    allowed_kinds = {
        "text", "thought", "function_call", "function_response", "data",
        "non_object", "unknown",
    }
    if isinstance(kinds, list) and len(kinds) <= 32 and all(
        isinstance(item, str) and item in allowed_kinds for item in kinds
    ):
        safe["part_kinds"] = kinds
    block_reason = value.get("prompt_block_reason")
    if block_reason in {
        "BLOCK_REASON_UNSPECIFIED", "SAFETY", "OTHER", "BLOCKLIST",
        "PROHIBITED_CONTENT", "MODEL_ARMOR", "JAILBREAK", "UNRECOGNIZED", None,
    }:
        safe["prompt_block_reason"] = block_reason
    return safe


_PARENT_SAFE_PROVIDER_METADATA = broker._safe_provider_metadata
broker.contracts = contracts
broker.REQUEST_SCHEMA_PATH = contracts.ARTIFACT_ROOT / "cell-request.schema.json"
broker.LEDGER_SCHEMA_PATH = contracts.ARTIFACT_ROOT / "single-use-ledger.schema.json"
broker._safe_provider_metadata = _safe_provider_metadata


def main() -> int:
    return broker.main()


if __name__ == "__main__":
    raise SystemExit(main())
