"""LC4V5R1E1 development-only exit reassessment.

This binder validates committed aggregate and development evidence without
executing the parser or discovering fixtures. It authorizes no certification
or runtime behavior.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
from typing import Any


SCHEMA_VERSION = "lc4v5r1e1.development_exit.v1"
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
V5_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v5-aggregate-report.json"
V5_ACCEPTANCE_PATH = (
    PROJECT_ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "lc4v5-sol-acceptance.md"
)
R1_REPORT_PATH = PROJECT_ROOT / "docs" / "bernie-lc4v5r1-development-report.json"
R1_ACCEPTANCE_PATH = (
    PROJECT_ROOT
    / "orchestration"
    / "agent_inbox"
    / "codex"
    / "lc4v5r1-sol-acceptance.md"
)

EXPECTED_V5_FILE_HASH = (
    "sha256:40dfa844b5e94ce5ec88aae39d942ab9edfeb7835ce613da4d68c5ed99f0fb1c"
)
EXPECTED_V5_ACCEPTANCE_HASH = (
    "sha256:ecd575cfe73f4cbba9eee6c0733a30ac5aefe3ec78183371a0664c8aed8bdbcd"
)
EXPECTED_R1_FILE_HASH = (
    "sha256:3ab20d99c93fb14c528e229752072a969b5190b6fb3fd7cde8755aa40468689c"
)
EXPECTED_R1_ACCEPTANCE_HASH = (
    "sha256:174fe7b737a7622930088407923c0663ad866523599e56c094114c4a1e286f2c"
)
EXPECTED_V5_REPORT_HASH = (
    "17c123559a8c708fa0d122a2de1dbadc465e1d4e93a19814c5968f00f0b9c88b"
)
EXPECTED_R1_PROBE_HASH = (
    "sha256:e44885916b9790ac858715c7d3d7c43b10231edc5bdfcceeba8486fc077ec55f"
)


def _file_hash(path: pathlib.Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _read_json(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _read_text(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _payload_hash(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def run_development_exit(
    source_commit: str = "unknown",
    *,
    v5_report_path: pathlib.Path = V5_REPORT_PATH,
    v5_acceptance_path: pathlib.Path = V5_ACCEPTANCE_PATH,
    r1_report_path: pathlib.Path = R1_REPORT_PATH,
    r1_acceptance_path: pathlib.Path = R1_ACCEPTANCE_PATH,
) -> dict[str, Any]:
    """Bind immutable evidence and fail closed on any drift."""
    v5 = _read_json(v5_report_path)
    r1 = _read_json(r1_report_path)
    v5_acceptance = _read_text(v5_acceptance_path)
    r1_acceptance = _read_text(r1_acceptance_path)

    v5_families = {
        item.get("slice_key"): item
        for item in (v5 or {}).get("slices", {}).get("family", [])
        if isinstance(item, dict)
    }
    failing_families = {
        key: item.get("failed")
        for key, item in v5_families.items()
        if item.get("failed")
    }
    r1_families = (r1 or {}).get("family_counts", {})

    gates: dict[str, bool] = {
        "v5_report_file_hash_exact": _file_hash(v5_report_path)
        == EXPECTED_V5_FILE_HASH,
        "v5_schema_and_population_exact": bool(
            v5
            and v5.get("schema_version") == "lc4v5.aggregate-report.v1"
            and v5.get("attempt_id") == "lc4v5-fresh-attempt-001"
            and v5.get("group_count") == 24
            and v5.get("scenario_count") == 288
            and v5.get("sample_count") == 576
            and v5.get("repeats_per_scenario") == 2
            and v5.get("coverage_cell_count") == 288
            and v5.get("evaluation_exception_count") == 0
            and v5.get("case_level_artifact_count") == 0
        ),
        "v5_certification_fail_aggregate_exact": bool(
            v5
            and v5.get("complete_contract")
            == {"failed": 64, "passed": 512, "total": 576}
            and v5.get("safety")
            == {"failed": 16, "passed": 560, "total": 576}
            and v5.get("failure_layers")
            == {
                "integration": 16,
                "interpretation": 48,
                "policy": 2,
                "safety": 16,
            }
        ),
        "v5_three_family_localization_exact": failing_families
        == {
            "create_approximate": 16,
            "move_interval": 24,
            "resize_ambiguous_duration": 24,
        },
        "v5_other_families_complete": bool(
            len(v5_families) == 24
            and all(
                item.get("passed") == 24
                and item.get("failed") == 0
                and item.get("total") == 24
                for key, item in v5_families.items()
                if key not in failing_families
            )
        ),
        "v5_acceptance_hash_and_decision_exact": (
            _file_hash(v5_acceptance_path) == EXPECTED_V5_ACCEPTANCE_HASH
            and "Decision: `valid_one_shot_certification_fail_accepted_and_sealed`"
            in v5_acceptance
            and EXPECTED_V5_REPORT_HASH in v5_acceptance
            and "V5 is permanently sealed" in v5_acceptance
        ),
        "r1_report_file_hash_exact": _file_hash(r1_report_path)
        == EXPECTED_R1_FILE_HASH,
        "r1_schema_and_probe_hash_exact": bool(
            r1
            and r1.get("schema_version")
            == "bernie.lc4v5r1.development-evidence.v1"
            and r1.get("probe_hash") == EXPECTED_R1_PROBE_HASH
        ),
        "r1_baseline_exact": bool(
            r1
            and r1.get("baseline", {}).get("complete") == 4
            and r1.get("baseline", {}).get("safe") == 14
            and len(r1.get("baseline", {}).get("complete_ids", [])) == 4
        ),
        "r1_repaired_exact": bool(
            r1
            and r1.get("repaired")
            == {
                "total": 18,
                "complete": 18,
                "safe": 18,
                "variance": 0,
                "variance_ids": [],
            }
        ),
        "r1_family_counts_exact": bool(
            set(r1_families)
            == {"create_approximate", "move_interval", "ambiguous_resize"}
            and all(
                counts
                == {"total": 6, "complete": 6, "safe": 6, "variance": 0}
                for counts in r1_families.values()
            )
        ),
        "r1_closed_boundaries_exact": bool(
            r1
            and r1.get("protected_evidence_accessed") is False
            and r1.get("t3_provider_or_write_boundary_opened") is False
            and r1.get("decision") == "development_repair_pass"
        ),
        "r1_acceptance_hash_and_decision_exact": (
            _file_hash(r1_acceptance_path) == EXPECTED_R1_ACCEPTANCE_HASH
            and "Decision: `development_three_family_remediation_accepted`"
            in r1_acceptance
            and "LC4V5 remains consumed and sealed" in r1_acceptance
            and "genuinely fresh holdout v6" in r1_acceptance
        ),
    }

    decision = (
        "development_exit_valid_holdout_decision_required"
        if all(gates.values())
        else "reassessment_invalid"
    )
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "source_commit": source_commit,
        "input_file_hashes": {
            "lc4v5_aggregate": EXPECTED_V5_FILE_HASH,
            "lc4v5_acceptance": EXPECTED_V5_ACCEPTANCE_HASH,
            "lc4v5r1_development": EXPECTED_R1_FILE_HASH,
            "lc4v5r1_acceptance": EXPECTED_R1_ACCEPTANCE_HASH,
        },
        "development_result": {
            "families": 3,
            "probes": 18,
            "baseline_complete": 4,
            "repaired_complete": 18,
            "baseline_safe": 14,
            "repaired_safe": 18,
            "repeat_variance": 0,
        },
        "gates": gates,
        "recommendation": "authorize_genuinely_fresh_certification_holdout_v6",
        "requires_user_decision": True,
        "certification_claimed": False,
    }
    report["report_hash"] = _payload_hash(report)
    report["decision"] = decision
    return report


def generate_report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def generate_report_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Bernie LC4V5R1E1 Development Exit",
            "",
            f"Decision: `{report['decision']}`",
            "",
            f"Report hash: `{report['report_hash']}`",
            "",
            "All supported ordinary-development blockers localized by the LC4V5 aggregate are closed.",
            "This is not product certification. Yuri must choose a genuinely fresh holdout v6 (recommended)",
            "or approve an explicit reviewed reuse policy before any certification evaluation.",
            "",
            "Holdouts v1-v5 remain sealed; T3 and provider/product/write gates remain closed.",
            "",
        ]
    )


__all__ = [
    "EXPECTED_R1_FILE_HASH",
    "EXPECTED_R1_PROBE_HASH",
    "EXPECTED_V5_FILE_HASH",
    "SCHEMA_VERSION",
    "generate_report_json",
    "generate_report_markdown",
    "run_development_exit",
]
