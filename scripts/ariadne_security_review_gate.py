"""Fail-closed Ariadne Secure SDLC red/blue/purple gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SETTINGS = ROOT / "orchestration" / "harness_settings" / "security_review_protocol.yaml"


def _load_object(path: Path, *, yaml_input: bool = False) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    payload = yaml.safe_load(text) if yaml_input else json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain an object")
    return payload


def _has_value(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return value is not None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_normalized_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _valid_head(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _repo_artifact(value: Any) -> Path | None:
    if not _has_value(value):
        return None
    root = ROOT.resolve()
    path = (ROOT / str(value)).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path


def _artifact_reasons(
    role: str,
    review: dict[str, Any],
    *,
    expected_candidate: str,
    expected_decision: str,
) -> list[str]:
    artifact = review.get("artifact_path")
    if not _has_value(artifact):
        return [f"review_artifact_missing:{role}"]
    path = _repo_artifact(artifact)
    if path is None:
        return [f"review_artifact_outside_repository:{role}"]
    if not path.is_file():
        return [f"review_artifact_not_found:{role}"]
    reasons: list[str] = []
    if review.get("artifact_sha256") != _sha256_normalized_text(path):
        reasons.append(f"review_artifact_hash_mismatch:{role}")
    text = path.read_text(encoding="utf-8", errors="replace")
    if expected_candidate not in text:
        reasons.append(f"review_artifact_candidate_unbound:{role}")
    if f"DECISION: {expected_decision}" not in text:
        reasons.append(f"review_artifact_decision_unbound:{role}")
    return reasons


def _purple_cadence(
    manifest: dict[str, Any], settings: dict[str, Any]
) -> tuple[int, list[str]]:
    reasons: list[str] = []
    cadence = manifest.get("purple_cadence")
    if not isinstance(cadence, dict):
        return 0, ["purple_cadence_missing"]
    ledger_path = _repo_artifact(settings["purple_cadence"]["ledger_path"])
    if ledger_path is None or not ledger_path.is_file():
        return 0, ["purple_cadence_ledger_missing"]
    if cadence.get("ledger_sha256") != _sha256_normalized_text(ledger_path):
        reasons.append("purple_cadence_ledger_hash_mismatch")

    entries: list[dict[str, Any]] = []
    for index, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            reasons.append(f"purple_cadence_ledger_entry_invalid:{index}")
            continue
        if (
            not isinstance(entry, dict)
            or entry.get("schema_version") != settings["purple_cadence"]["entry_schema_version"]
            or not _has_value(entry.get("sprint_id"))
            or not isinstance(entry.get("material"), bool)
            or not isinstance(entry.get("purple_completed"), bool)
            or not _valid_head(entry.get("accepted_head"))
        ):
            reasons.append(f"purple_cadence_ledger_entry_invalid:{index}")
            continue
        entries.append(entry)

    last_purple = max(
        (index for index, entry in enumerate(entries) if entry["material"] and entry["purple_completed"]),
        default=None,
    )
    if last_purple is None:
        computed = int(settings["purple_cadence"]["no_prior_purple_count"])
    else:
        computed = sum(1 for entry in entries[last_purple + 1 :] if entry["material"])
    if cadence.get("declared_material_sprints_since_purple") != computed:
        reasons.append("purple_cadence_declared_count_mismatch")
    return computed, reasons


def _review_reasons(
    role: str,
    review: Any,
    role_settings: dict[str, Any],
    *,
    phase: str,
    require_fresh_red: bool,
    final_candidate_head: str,
    recovery_settings: dict[str, Any],
) -> tuple[list[str], bool, bool]:
    reasons: list[str] = []
    if not isinstance(review, dict):
        return [f"required_review_missing:{role}"], False, False
    if review.get("required") is not True:
        reasons.append(f"required_review_not_marked:{role}")
    if review.get("resource_id") != role_settings["preferred_resource_id"]:
        reasons.append(f"review_resource_mismatch:{role}")
    if not _has_value(review.get("packet_path")):
        reasons.append(f"review_packet_missing:{role}")
    else:
        packet_path = _repo_artifact(review.get("packet_path"))
        if packet_path is None:
            reasons.append(f"review_packet_outside_repository:{role}")
        elif not packet_path.is_file():
            reasons.append(f"review_packet_not_found:{role}")
    review_candidate = review.get("candidate_head")
    if not _valid_head(review_candidate):
        reasons.append(f"review_candidate_head_invalid:{role}")
    if role == "red" and require_fresh_red:
        for field in ("fresh_context", "candidate_only", "prior_review_artifacts_excluded"):
            if review.get(field) is not True:
                reasons.append(f"red_independence_missing:{field}")

    exact_pass = False
    recovered = False
    if (
        phase == "plan"
        and _valid_head(review_candidate)
        and review_candidate != final_candidate_head
        and review.get("disposition") != recovery_settings["allowed_disposition"]
    ):
        reasons.append(f"review_candidate_head_mismatch:{role}")
    if phase == "acceptance":
        if review.get("disposition") == recovery_settings["allowed_disposition"]:
            recovered = True
            worker_decision = review.get("decision")
            if worker_decision not in recovery_settings["allowed_worker_decisions"]:
                reasons.append(f"recovery_worker_decision_invalid:{role}")
                worker_decision = "revision_required"
            reasons.extend(
                _artifact_reasons(
                    role,
                    review,
                    expected_candidate=str(review_candidate),
                    expected_decision=str(worker_decision),
                )
            )
            recovery = review.get("recovery") if isinstance(review.get("recovery"), dict) else {}
            if recovery.get("owner_resource_id") != recovery_settings["recovery_owner_resource_id"]:
                reasons.append(f"recovery_owner_mismatch:{role}")
            recovery_value = recovery.get("artifact_path")
            if not _has_value(recovery_value):
                reasons.append(f"recovery_artifact_missing:{role}")
            else:
                recovery_path = _repo_artifact(recovery_value)
                if recovery_path is None:
                    reasons.append(f"recovery_artifact_outside_repository:{role}")
                elif not recovery_path.is_file():
                    reasons.append(f"recovery_artifact_not_found:{role}")
                else:
                    if recovery.get("artifact_sha256") != _sha256_normalized_text(recovery_path):
                        reasons.append(f"recovery_artifact_hash_mismatch:{role}")
                    recovery_text = recovery_path.read_text(encoding="utf-8", errors="replace")
                    if str(review_candidate) not in recovery_text or final_candidate_head not in recovery_text:
                        reasons.append(f"recovery_artifact_candidate_unbound:{role}")
        elif review.get("decision") == "pass":
            if review_candidate != final_candidate_head:
                reasons.append(f"review_candidate_head_mismatch:{role}")
            else:
                exact_pass = True
            reasons.extend(
                _artifact_reasons(
                    role,
                    review,
                    expected_candidate=str(review_candidate),
                    expected_decision="pass",
                )
            )
        else:
            reasons.append(f"review_not_passed_or_recovered:{role}")
    return reasons, exact_pass, recovered


def evaluate_security_review(
    manifest: dict[str, Any],
    settings: dict[str, Any],
    *,
    phase: str,
) -> dict[str, Any]:
    reasons: list[str] = []
    if phase not in settings["acceptance"]["gate_phases"]:
        raise ValueError(f"unsupported phase: {phase}")
    if manifest.get("schema_version") != "ariadne.sprint_security_review.v1":
        reasons.append("manifest_schema_invalid")

    material = manifest.get("material_sprint") is True
    materiality = manifest.get("materiality") if isinstance(manifest.get("materiality"), dict) else {}
    if materiality.get("classification") != ("material" if material else "non_material"):
        reasons.append("materiality_classification_mismatch")
    if materiality.get("owner_resource_id") != settings["material_sprint"]["classification_owner_resource_id"]:
        reasons.append("materiality_owner_mismatch")
    if not _has_value(materiality.get("rationale")):
        reasons.append("materiality_rationale_missing")
    if not material:
        non_material_triggers = manifest.get("triggers")
        if not isinstance(non_material_triggers, list):
            reasons.append("triggers_missing")
        elif non_material_triggers:
            reasons.append("non_material_has_security_triggers")
        return {
            "schema_version": "ariadne.security_review_gate_receipt.v1",
            "phase": phase,
            "status": "passed" if not reasons else "revision_required",
            "tier": "non_material",
            "required_reviews": [],
            "purple_required": False,
            "reasons": sorted(set(reasons)),
        }

    final_candidate_head = manifest.get("candidate_head")
    if not _valid_head(final_candidate_head):
        reasons.append("candidate_head_invalid")
        final_candidate_head = ""

    delta = manifest.get("security_delta")
    if not isinstance(delta, dict):
        reasons.append("security_delta_missing")
        delta = {}
    for field in settings["material_sprint"]["required_fields"]:
        if not _has_value(delta.get(field)):
            reasons.append(f"security_delta_field_missing:{field}")

    configured_triggers = set(settings["risk_classification"]["security_sensitive_triggers"])
    triggers = manifest.get("triggers")
    if not isinstance(triggers, list):
        reasons.append("triggers_missing")
        triggers = []
    unknown = sorted({str(item) for item in triggers} - configured_triggers)
    reasons.extend(f"unknown_security_trigger:{trigger}" for trigger in unknown)
    active = configured_triggers.intersection(str(item) for item in triggers)
    sensitive = bool(active)
    tier = (
        settings["risk_classification"]["security_sensitive_tier"]
        if sensitive
        else settings["risk_classification"]["default_tier"]
    )
    if manifest.get("declared_tier") != tier:
        reasons.append("declared_security_tier_mismatch")

    required_reviews: list[str] = []
    exact_independent_passes = 0
    recovered_reviews = 0
    reviews = manifest.get("reviews") if isinstance(manifest.get("reviews"), dict) else {}
    if sensitive:
        required_reviews = ["blue", "red"]
        for role in required_reviews:
            role_reasons, exact_pass, recovered = _review_reasons(
                role,
                reviews.get(role),
                settings["roles"][role],
                phase=phase,
                require_fresh_red=settings["independence"]["red_fresh_context_required"],
                final_candidate_head=final_candidate_head,
                recovery_settings=settings["recovery"],
            )
            reasons.extend(role_reasons)
            exact_independent_passes += int(exact_pass)
            recovered_reviews += int(recovered)
        blue = reviews.get("blue") if isinstance(reviews.get("blue"), dict) else {}
        red = reviews.get("red") if isinstance(reviews.get("red"), dict) else {}
        blue_packet = _repo_artifact(blue.get("packet_path"))
        red_packet = _repo_artifact(red.get("packet_path"))
        if blue_packet is not None and blue_packet == red_packet:
            reasons.append("asymmetric_review_packets_required")
        if phase == "acceptance":
            blue_artifact = _repo_artifact(blue.get("artifact_path"))
            red_artifact = _repo_artifact(red.get("artifact_path"))
            if blue_artifact is not None and blue_artifact == red_artifact:
                reasons.append("independent_review_artifacts_required")

    cadence, cadence_reasons = _purple_cadence(manifest, settings)
    reasons.extend(cadence_reasons)
    purple_triggers = set(settings["risk_classification"]["purple_review_triggers"])
    purple_required = bool(active.intersection(purple_triggers)) or cadence >= int(
        settings["risk_classification"]["maximum_material_sprints_between_purple"]
    )
    purple = reviews.get("purple") if isinstance(reviews.get("purple"), dict) else {}
    if purple_required:
        if purple.get("required") is not True:
            reasons.append("required_review_not_marked:purple")
        if purple.get("resource_id") != settings["roles"]["purple"]["owner_resource_id"]:
            reasons.append("review_resource_mismatch:purple")
        if phase == "acceptance":
            if purple.get("decision") != "pass":
                reasons.append("review_not_passed:purple")
            if purple.get("candidate_head") != final_candidate_head:
                reasons.append("review_candidate_head_mismatch:purple")
            reasons.extend(
                _artifact_reasons(
                    "purple",
                    purple,
                    expected_candidate=final_candidate_head,
                    expected_decision="pass",
                )
            )

    if phase == "acceptance":
        if recovered_reviews and exact_independent_passes < 1:
            reasons.append("recovery_exact_final_independent_pass_missing")
        unresolved = manifest.get("unresolved_findings")
        if not isinstance(unresolved, list):
            reasons.append("unresolved_findings_missing")
            unresolved = []
        blocking = set(settings["acceptance"]["blocking_unresolved_severities"])
        allowed = set(settings["acceptance"]["allowed_finding_severities"])
        for index, finding in enumerate(unresolved):
            if not isinstance(finding, dict):
                reasons.append(f"finding_schema_invalid:{index}")
                continue
            finding_id = finding.get("id") if _has_value(finding.get("id")) else f"unnamed-{index}"
            if not _has_value(finding.get("id")):
                reasons.append(f"finding_id_missing:{index}")
            raw_severity = finding.get("severity")
            if not isinstance(raw_severity, str):
                reasons.append(f"finding_severity_invalid:{finding_id}")
                continue
            severity = raw_severity.lower()
            if severity not in allowed:
                reasons.append(f"finding_severity_invalid:{finding_id}")
                continue
            if raw_severity != severity:
                reasons.append(f"finding_severity_not_canonical:{finding_id}")
            if severity in blocking:
                reasons.append(f"blocking_finding_unresolved:{finding_id}")

    return {
        "schema_version": "ariadne.security_review_gate_receipt.v1",
        "phase": phase,
        "status": "passed" if not reasons else "revision_required",
        "tier": tier,
        "required_reviews": required_reviews,
        "purple_required": purple_required,
        "reasons": sorted(set(reasons)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--phase", choices=("plan", "acceptance"), required=True)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = evaluate_security_review(
            _load_object(args.manifest),
            _load_object(args.settings, yaml_input=True),
            phase=args.phase,
        )
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError, KeyError) as error:
        print(f"ariadne security review gate failed: {error}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
