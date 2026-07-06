"""Safe aggregate readiness report for Bernie interpreter provider boundaries."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable, get_args

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.config import LIVE_BERNIE_INTERPRETER_PROVIDERS
from app.schemas.appointments import BernieBookingInterpreterMetadata
from app.services.bernie_booking_interpreter import (
    DisabledBookingInstructionInterpreter,
    FakeBookingInstructionInterpreter,
    GeminiVertexBookingInstructionInterpreter,
    get_booking_instruction_interpreter,
)

REPORT_SCHEMA_VERSION = "bernie.provider_boundary_readiness_report.v1"


def _declared_provider_values() -> set[str]:
    return set(get_args(BernieBookingInterpreterMetadata.model_fields["provider"].annotation))


def _metadata_rows() -> list[dict[str, object]]:
    interpreters = [
        DisabledBookingInstructionInterpreter(),
        FakeBookingInstructionInterpreter(),
        GeminiVertexBookingInstructionInterpreter(),
    ]
    return [
        {
            "provider": interpreter.metadata.provider,
            "mode": interpreter.metadata.mode,
            "live_provider": interpreter.metadata.live_provider,
            "in_live_provider_allowlist": (
                interpreter.metadata.provider in LIVE_BERNIE_INTERPRETER_PROVIDERS
            ),
        }
        for interpreter in interpreters
    ]


def _canonical_providers_for_aliases(aliases: Iterable[str]) -> set[str]:
    return {
        get_booking_instruction_interpreter(alias).metadata.provider
        for alias in aliases
    }


def build_provider_boundary_report() -> dict[str, Any]:
    metadata_rows = _metadata_rows()
    providers = [str(row["provider"]) for row in metadata_rows]
    live_rows = [row for row in metadata_rows if row["live_provider"] is True]
    non_live_rows = [row for row in metadata_rows if row["live_provider"] is False]
    canonical_live_providers = _canonical_providers_for_aliases(
        LIVE_BERNIE_INTERPRETER_PROVIDERS
    )

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "source": "static_provider_boundary",
        "provider_metadata_count": len(metadata_rows),
        "declared_provider_count": len(_declared_provider_values()),
        "live_alias_count": len(LIVE_BERNIE_INTERPRETER_PROVIDERS),
        "live_provider_count": len(live_rows),
        "non_live_provider_count": len(non_live_rows),
        "canonical_live_provider_count": len(canonical_live_providers),
        "provider_metadata_unique": len(providers) == len(set(providers)),
        "all_metadata_providers_schema_declared": set(providers)
        <= _declared_provider_values(),
        "non_live_providers_outside_live_allowlist": all(
            row["in_live_provider_allowlist"] is False for row in non_live_rows
        ),
        "live_providers_inside_live_allowlist": all(
            row["in_live_provider_allowlist"] is True for row in live_rows
        ),
        "live_aliases_resolve_to_canonical_provider": canonical_live_providers
        == {GeminiVertexBookingInstructionInterpreter.metadata.provider},
        "default_provider": "disabled",
        "runtime_or_provider_wiring_ready": False,
        "live_provider_enabled": False,
        "provider_calls_performed": False,
        "route_behavior_changed": False,
        "database_access_performed": False,
        "memory_or_rag_access_performed": False,
        "historical_diary_material_access_performed": False,
    }


def assert_provider_boundary_report_safety(report: dict[str, Any]) -> None:
    assert report["schema_version"] == REPORT_SCHEMA_VERSION
    assert report["source"] == "static_provider_boundary"
    assert report["provider_metadata_count"] == 3
    assert report["declared_provider_count"] == 3
    assert report["live_alias_count"] >= 1
    assert report["live_provider_count"] == 1
    assert report["non_live_provider_count"] == 2
    assert report["canonical_live_provider_count"] == 1
    assert report["provider_metadata_unique"] is True
    assert report["all_metadata_providers_schema_declared"] is True
    assert report["non_live_providers_outside_live_allowlist"] is True
    assert report["live_providers_inside_live_allowlist"] is True
    assert report["live_aliases_resolve_to_canonical_provider"] is True
    assert report["default_provider"] == "disabled"
    assert report["runtime_or_provider_wiring_ready"] is False
    assert report["live_provider_enabled"] is False
    assert report["provider_calls_performed"] is False
    assert report["route_behavior_changed"] is False
    assert report["database_access_performed"] is False
    assert report["memory_or_rag_access_performed"] is False
    assert report["historical_diary_material_access_performed"] is False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Emit a safe aggregate Bernie provider-boundary readiness report."
    )
    parser.parse_args()
    report = build_provider_boundary_report()
    assert_provider_boundary_report_safety(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
