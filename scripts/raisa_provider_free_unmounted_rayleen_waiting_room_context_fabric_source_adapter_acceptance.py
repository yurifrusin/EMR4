"""Generate deterministic evidence for the unmounted Rayleen source adapter."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.raisa_provider_free_practice_context_fabric_bureau_memory_contract import (
    canonical_sha256,
    seal,
)
from scripts.raisa_provider_free_practice_context_fabric_current_operational_weave import (
    assemble_current_operational_weave,
    build_authored_synthetic_packet,
    proofread_current_operational_weave,
)
from scripts.raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter import (
    EVIDENCE_LABEL,
    WaitingRoomSourceAdapterViolation,
    adapt_waiting_room_source,
    build_authored_synthetic_alias_manifest,
    build_authored_synthetic_waiting_room_frame,
)


CONTINUITY_DIR = (
    ROOT
    / "orchestration"
    / "continuity"
    / "raisa-provider-free-unmounted-rayleen-waiting-room-context-fabric-source-adapter"
)
EVIDENCE_SCHEMA_PATH = CONTINUITY_DIR / "adapter-result.schema.json"
DEFAULT_FIXTURE_PATH = CONTINUITY_DIR / "authored-synthetic-waiting-room-frame.json"
DEFAULT_EVIDENCE_PATH = CONTINUITY_DIR / "provider-free-acceptance-evidence.json"
ASSEMBLED_AT = "2026-08-06T03:00:00Z"


def _sha256_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _replacement_packet() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    parent = build_authored_synthetic_packet()
    frame = build_authored_synthetic_waiting_room_frame()
    manifest = build_authored_synthetic_alias_manifest(
        frame, parent["authority_binding"], parent["scope_grant"]
    )
    adapter_result = adapt_waiting_room_source(
        frame,
        parent["authority_binding"],
        parent["scope_grant"],
        manifest,
        assembled_at=ASSEMBLED_AT,
    )
    sources = [
        adapter_result["source_envelope"]
        if item["frame_type"] == "current_waiting_room_projection"
        else item
        for item in parent["source_envelopes"]
    ]
    frame_set, source_trace, weave_trace = assemble_current_operational_weave(
        parent["candidate"],
        parent["context_need"],
        parent["authority_binding"],
        parent["scope_grant"],
        sources,
        assembled_at=ASSEMBLED_AT,
    )
    proofreader_trace = proofread_current_operational_weave(
        parent["candidate"],
        parent["context_need"],
        parent["authority_binding"],
        parent["scope_grant"],
        sources,
        frame_set,
        source_trace,
        weave_trace,
        assembled_at=ASSEMBLED_AT,
    )
    if proofreader_trace["release_decision"] != "RELEASE":
        raise RuntimeError("parent_proofreader_did_not_release")
    return frame, adapter_result, {
        "frame_set": frame_set,
        "source_trace": source_trace,
        "weave_trace": weave_trace,
        "proofreader_trace": proofreader_trace,
    }


def _expect_block(
    mutator: Callable[[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]], None],
) -> str:
    parent = build_authored_synthetic_packet()
    frame = build_authored_synthetic_waiting_room_frame()
    binding = deepcopy(parent["authority_binding"])
    grant = deepcopy(parent["scope_grant"])
    manifest = build_authored_synthetic_alias_manifest(frame, binding, grant)
    mutator(frame, binding, grant, manifest)
    try:
        adapt_waiting_room_source(
            frame,
            binding,
            grant,
            manifest,
            assembled_at=ASSEMBLED_AT,
        )
    except WaitingRoomSourceAdapterViolation as error:
        return str(error)
    raise AssertionError("negative case unexpectedly released")


def _reseal(value: dict[str, Any], digest_field: str) -> None:
    replacement = seal({k: v for k, v in value.items() if k != digest_field}, digest_field)
    value.clear()
    value.update(replacement)


def _negative_results() -> list[str]:
    results = []

    results.append(
        _expect_block(lambda frame, _b, _g, _m: frame.__setitem__("extra", True))
    )
    results.append(
        _expect_block(
            lambda frame, _b, _g, _m: frame.__setitem__(
                "expires_at", "2026-08-06T03:02:31Z"
            )
        )
    )
    results.append(
        _expect_block(
            lambda frame, _b, _g, _m: frame["derived_signals"][0].__setitem__(
                "value", 11
            )
        )
    )
    results.append(
        _expect_block(
            lambda frame, _b, _g, _m: frame["derived_signals"].append(
                deepcopy(frame["derived_signals"][0])
            )
        )
    )
    results.append(
        _expect_block(
            lambda _f, _b, _g, manifest: (
                manifest["appointment_aliases"].clear(),
                _reseal(manifest, "alias_manifest_digest"),
            )
        )
    )
    results.append(
        _expect_block(
            lambda _f, _b, _g, manifest: manifest.__setitem__(
                "alias_manifest_digest", "sha256:" + "0" * 64
            )
        )
    )

    def wrong_role(_f: dict[str, Any], binding: dict[str, Any], _g: dict[str, Any], _m: dict[str, Any]) -> None:
        binding["roles"] = ["GP"]
        _reseal(binding, "binding_digest")

    results.append(_expect_block(wrong_role))

    def command_authority(_f: dict[str, Any], _b: dict[str, Any], grant: dict[str, Any], _m: dict[str, Any]) -> None:
        grant["command_authority"] = True
        _reseal(grant, "grant_digest")

    results.append(_expect_block(command_authority))

    def wrong_bureau(_f: dict[str, Any], _b: dict[str, Any], grant: dict[str, Any], _m: dict[str, Any]) -> None:
        grant["requesting_bureau"] = "BERNIE"
        _reseal(grant, "grant_digest")

    results.append(_expect_block(wrong_bureau))

    def cross_location(_f: dict[str, Any], _b: dict[str, Any], _g: dict[str, Any], manifest: dict[str, Any]) -> None:
        manifest["fabric_location_ref"] = "synthetic:location:foreign"
        _reseal(manifest, "alias_manifest_digest")

    results.append(_expect_block(cross_location))

    def orphan_signal(frame: dict[str, Any], _b: dict[str, Any], _g: dict[str, Any], _m: dict[str, Any]) -> None:
        frame["derived_signals"][0]["appointment_id"] = (
            "22000000-0000-4000-8000-000000000001"
        )

    results.append(_expect_block(orphan_signal))

    def label_tamper(frame: dict[str, Any], _b: dict[str, Any], _g: dict[str, Any], _m: dict[str, Any]) -> None:
        frame["derived_signals"][0]["label"]["expires_at"] = (
            "2026-08-06T03:01:00Z"
        )

    results.append(_expect_block(label_tamper))
    return results


def build_acceptance_evidence() -> tuple[dict[str, Any], dict[str, Any]]:
    frame, adapter_result, parent = _replacement_packet()
    negative_codes = _negative_results()
    case_count = 1 + len(negative_codes)
    fixture_bytes = (json.dumps(frame, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    evidence = {
        "schema_version": "emr4.practice_context_fabric_source_adapter_acceptance.v1",
        "result": "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter_pass",
        "evidence_label": EVIDENCE_LABEL,
        "case_count": case_count,
        "passed_case_count": case_count,
        "source_frame_file_digest": _sha256_bytes(fixture_bytes),
        "source_frame_digest": adapter_result["source_frame_digest"],
        "alias_manifest_digest": adapter_result["alias_manifest_digest"],
        "source_envelope_digest": adapter_result["source_envelope"]["source_digest"],
        "adapter_trace_digest": adapter_result["adapter_trace"]["adapter_trace_digest"],
        "adapter_result_digest": adapter_result["adapter_result_digest"],
        "parent_frame_set_digest": parent["frame_set"]["frame_set_digest"],
        "parent_proofreader_trace_digest": parent["proofreader_trace"][
            "proofreader_trace_digest"
        ],
        "parent_proofreader_decision": parent["proofreader_trace"]["release_decision"],
        "negative_reason_codes": sorted(set(negative_codes)),
        "zero_action_posture": {
            "provider_calls": 0,
            "network_calls": 0,
            "database_calls": 0,
            "product_api_calls": 0,
            "commands_or_writes": 0,
            "watcher_or_event_subscriptions": 0,
            "deployments_or_releases": 0,
            "protected_actions": 0,
        },
        "artifact_hashes": {
            "adapter_module": _sha256_file(
                ROOT
                / "scripts"
                / "raisa_provider_free_unmounted_rayleen_waiting_room_context_fabric_source_adapter.py"
            ),
            "current_weave_module": _sha256_file(
                ROOT
                / "scripts"
                / "raisa_provider_free_practice_context_fabric_current_operational_weave.py"
            ),
        },
        "claim_boundary": "Provider-free authored-synthetic unmounted source-adapter evidence only; no real data, live source, watcher, provider, runtime, command, deployment or production claim.",
    }
    schema = json.loads(EVIDENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = list(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(
            evidence
        )
    )
    if errors:
        raise RuntimeError("acceptance_evidence_schema_invalid")
    if canonical_sha256(frame) != evidence["source_frame_digest"]:
        raise RuntimeError("source_frame_digest_mismatch")
    return frame, evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-output", type=Path, default=DEFAULT_FIXTURE_PATH)
    parser.add_argument("--evidence-output", type=Path, default=DEFAULT_EVIDENCE_PATH)
    args = parser.parse_args()
    frame, evidence = build_acceptance_evidence()
    _write_json(args.fixture_output, frame)
    _write_json(args.evidence_output, evidence)
    print(
        json.dumps(
            {
                "result": evidence["result"],
                "case_count": evidence["case_count"],
                "parent_proofreader_decision": evidence[
                    "parent_proofreader_decision"
                ],
            },
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
