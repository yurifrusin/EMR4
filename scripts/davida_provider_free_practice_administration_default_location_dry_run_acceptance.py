"""Deterministic acceptance for Davida's default-location dry-run proposal."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.schemas.practice import (  # noqa: E402
    PractitionerDefaultLocationOut,
    PractitionerOut,
)
from app.schemas.practice_administration import ActivePracticeLocationOut  # noqa: E402
from app.schemas.practice_administration_default_location_proposal import (  # noqa: E402
    CANDIDATE_SCHEMA_VERSION,
    DefaultLocationProposalResultAdapter,
    OPERATION,
    REJECTION_REASONS,
)
from app.services.practice.practice_administration_context_desk import (  # noqa: E402
    ResourceReferenceBinding,
    ResourceReferenceRegistry,
    compose_practice_administration_context,
)
from app.services.practice.practice_administration_default_location_dry_run import (  # noqa: E402
    dry_run_default_location_proposal,
)

RESULT = "provider_free_practice_administration_default_location_dry_run_pass"
EVIDENCE_LABEL = "provider_free_unoccupied_default_location_dry_run"
OBSERVED = datetime(2026, 8, 3, 14, 0, tzinfo=timezone.utc)
EVALUATED = OBSERVED + timedelta(minutes=1)
PRACTICE_REF = "practice_synth_default_location"
PRINCIPAL_REF = "principal_synth_default_location"
CORRELATION_ID = "correlation-davida-default-location"
CONTRACT = ROOT / "orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.json"
SCHEMA = ROOT / "orchestration/continuity/davida-provider-free-practice-administration-default-location-dry-run/dry-run-contract.schema.json"
SCHEMA_SOURCE = ROOT / "app/schemas/practice_administration_default_location_proposal.py"
SERVICE_SOURCE = ROOT / "app/services/practice/practice_administration_default_location_dry_run.py"


class AcceptanceFailure(RuntimeError):
    """One deterministic invariant failed."""


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _rehash_context(frame: dict[str, Any]) -> None:
    frame["content_revision"] = _sha256(
        {key: value for key, value in frame.items() if key != "content_revision"}
    )


def _sample_context(*, current_null: bool = False) -> dict[str, Any]:
    practitioner_one = uuid.UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    practitioner_two = uuid.UUID("bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb")
    location_one = uuid.UUID("cccccccc-cccc-4ccc-8ccc-cccccccccccc")
    location_two = uuid.UUID("dddddddd-dddd-4ddd-8ddd-dddddddddddd")
    practitioners = [
        PractitionerOut(
            id=practitioner_one,
            displayName="Avery Authored Synthetic",
            roleLabel="GP",
            active=True,
            defaultLocation=(
                None
                if current_null
                else PractitionerDefaultLocationOut(
                    id=location_one, name="Synthetic North"
                )
            ),
        ),
        PractitionerOut(
            id=practitioner_two,
            displayName="Morgan Authored Synthetic",
            roleLabel=None,
            active=True,
            defaultLocation=None,
        ),
    ]
    locations = [
        ActivePracticeLocationOut(id=location_one, name="Synthetic North"),
        ActivePracticeLocationOut(id=location_two, name="Synthetic South"),
    ]
    bindings = (
        ResourceReferenceBinding(
            kind="practitioner",
            resource_id=practitioner_one,
            reference="prac_synth_0001",
            practice_ref=PRACTICE_REF,
        ),
        ResourceReferenceBinding(
            kind="practitioner",
            resource_id=practitioner_two,
            reference="prac_synth_0002",
            practice_ref=PRACTICE_REF,
        ),
        ResourceReferenceBinding(
            kind="location",
            resource_id=location_one,
            reference="loc_synth_0001",
            practice_ref=PRACTICE_REF,
        ),
        ResourceReferenceBinding(
            kind="location",
            resource_id=location_two,
            reference="loc_synth_0002",
            practice_ref=PRACTICE_REF,
        ),
    )
    return compose_practice_administration_context(
        practitioners=practitioners,
        active_locations=locations,
        practice_ref=PRACTICE_REF,
        principal_ref=PRINCIPAL_REF,
        correlation_id=CORRELATION_ID,
        observed_at=OBSERVED,
        resource_references=ResourceReferenceRegistry.build(bindings),
    )


def _candidate(context: dict[str, Any], **updates: Any) -> dict[str, Any]:
    candidate = {
        "schema_version": CANDIDATE_SCHEMA_VERSION,
        "operation": OPERATION,
        "practice_ref": context["practice_ref"],
        "principal_ref": context["principal_ref"],
        "correlation_id": context["correlation_id"],
        "content_revision": context["content_revision"],
        "evaluated_at": EVALUATED.isoformat().replace("+00:00", "Z"),
        "practitioner_ref": "prac_synth_0001",
        "location_ref": "loc_synth_0002",
        "reason_code": "PRACTICE_ASSIGNMENT_UPDATE",
        "risk_tier": "admin_proposal",
        "confirmation_authorized": False,
        "apply_authorized": False,
        "writes_authorized": False,
        "command_authorized": False,
        "provider_executed": False,
        "model_executed": False,
        "database_used": False,
        "network_used": False,
        "model_to_database": False,
    }
    candidate.update(updates)
    return candidate


def _run(candidate: Any, context: Any) -> dict[str, Any]:
    result = dry_run_default_location_proposal(
        candidate=candidate, context_frame=context
    )
    DefaultLocationProposalResultAdapter.validate_python(result)
    return result


def _expect_rejected(
    candidate: Any, context: Any, reason: str | None = None
) -> dict[str, Any]:
    result = _run(candidate, context)
    if result["verdict"] != "rejected":
        raise AcceptanceFailure("expected_rejected")
    if reason is not None and result["reason"] != reason:
        raise AcceptanceFailure(f"unexpected_reason:{result['reason']}:{reason}")
    if "proposal_candidate" in result:
        raise AcceptanceFailure("partial_proposal_on_rejection")
    return result


def _effect_dependencies_absent(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                calls.add(f"{node.func.value.id}.{node.func.attr}")
    forbidden_imports = {
        "sqlalchemy",
        "requests",
        "httpx",
        "socket",
        "urllib",
        "time",
        "psycopg",
        "openai",
        "google",
        "fastapi",
        "starlette",
        "strawberry",
    }
    forbidden_calls = {
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "requests.get",
        "requests.post",
        "httpx.get",
        "httpx.post",
    }
    return not (imports & forbidden_imports) and not (calls & forbidden_calls)


def run_acceptance() -> dict[str, Any]:
    cases: list[str] = []
    verdict_counts = {"released": 0, "rejected": 0}

    def record(name: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
        result = fn()
        cases.append(name)
        verdict_counts[result["verdict"]] += 1
        return result

    context = _sample_context()
    released = record("exact_valid_change", lambda: _run(_candidate(context), context))
    if released["verdict"] != "released":
        raise AcceptanceFailure("valid_change_not_released")
    proposal = released["proposal_candidate"]
    if proposal["before_state"]["default_location_ref"] != "loc_synth_0001":
        raise AcceptanceFailure("before_not_context_copied")
    if proposal["after_state"]["default_location_ref"] != "loc_synth_0002":
        raise AcceptanceFailure("after_not_target_copied")
    if proposal["changed_paths"] != ["practitioner.default_location_ref"]:
        raise AcceptanceFailure("changed_path_not_exact")

    current_null = _sample_context(current_null=True)
    null_result = record(
        "current_null_change", lambda: _run(_candidate(current_null), current_null)
    )
    if null_result["proposal_candidate"]["before_state"]["default_location_ref"] is not None:
        raise AcceptanceFailure("null_before_not_preserved")

    repeat = _run(_json_clone(_candidate(context)), _json_clone(context))
    if _canonical(released) != _canonical(repeat):
        raise AcceptanceFailure("repeat_output_not_deterministic")
    cases.append("deterministic_repeated_output")

    record(
        "same_location_no_change",
        lambda: _expect_rejected(
            _candidate(context, location_ref="loc_synth_0001"), context, "no_change"
        ),
    )
    for name, field, value, reason in (
        ("missing_practitioner", "practitioner_ref", "prac_synth_9999", "practitioner_not_resolved"),
        ("missing_location", "location_ref", "loc_synth_9999", "location_not_resolved"),
        ("wrong_kind_practitioner", "practitioner_ref", "loc_synth_0001", "wrong_resource_kind"),
        ("wrong_kind_location", "location_ref", "prac_synth_0002", "wrong_resource_kind"),
    ):
        record(
            name,
            lambda field=field, value=value, reason=reason: _expect_rejected(
                _candidate(context, **{field: value}), context, reason
            ),
        )

    for field, value in (
        ("practice_ref", "foreign_practice"),
        ("principal_ref", "foreign_principal"),
        ("correlation_id", "correlation-foreign"),
        ("content_revision", "f" * 64),
    ):
        record(
            f"scope_tamper_{field}",
            lambda field=field, value=value: _expect_rejected(
                _candidate(context, **{field: value}), context, "scope_mismatch"
            ),
        )

    for operation in (
        "ADVISORY_EXPLAIN_DIRECTORY",
        "ADVISORY_SUMMARIZE_DIRECTORY",
        "PROPOSE_DEACTIVATE_PRACTITIONER",
        "PROPOSE_REACTIVATE_PRACTITIONER",
        "PROPOSE_UPDATE_PRACTITIONER_PROFILE",
        "CONFIRM_UPDATE_PRACTITIONER_DEFAULT_LOCATION",
        "APPLY_PRACTITIONER_UPDATE_DEFAULT_LOCATION",
        "WRITE_PRACTITIONER_DEFAULT_LOCATION",
        "UNKNOWN",
    ):
        record(
            f"operation_blocked_{operation}",
            lambda operation=operation: _expect_rejected(
                _candidate(context, operation=operation),
                context,
                "operation_not_allowed",
            ),
        )

    for field, value in (
        ("free_text", "forbidden"),
        ("before_state", {}),
        ("after_state", {}),
        ("command_payload", {}),
        ("idempotency_key", "forbidden"),
        ("confirmation_evidence", {}),
        ("audit_event", {}),
        ("aggregate_version", 1),
        ("provider", "forbidden"),
        ("model", "forbidden"),
        ("database", "forbidden"),
        ("network", "forbidden"),
    ):
        record(
            f"extra_field_blocked_{field}",
            lambda field=field, value=value: _expect_rejected(
                _candidate(context, **{field: value}),
                context,
                "candidate_schema_invalid",
            ),
        )

    authority_fields = (
        "confirmation_authorized",
        "apply_authorized",
        "writes_authorized",
        "command_authorized",
        "provider_executed",
        "model_executed",
        "database_used",
        "network_used",
        "model_to_database",
    )
    for field in authority_fields:
        record(
            f"authority_true_blocked_{field}",
            lambda field=field: _expect_rejected(
                _candidate(context, **{field: True}),
                context,
                "candidate_schema_invalid",
            ),
        )
        record(
            f"authority_coercion_blocked_{field}",
            lambda field=field: _expect_rejected(
                _candidate(context, **{field: 0}), context, "candidate_noncanonical"
            ),
        )

    for name, value, reason in (
        ("naive", "2026-08-03T14:01:00", "evaluated_at_naive"),
        ("before", "2026-08-03T13:59:59Z", "evaluated_at_out_of_range"),
        ("expiry", "2026-08-03T14:02:00Z", "evaluated_at_out_of_range"),
    ):
        record(
            f"freshness_{name}",
            lambda value=value, reason=reason: _expect_rejected(
                _candidate(context, evaluated_at=value), context, reason
            ),
        )

    old_revision = _json_clone(context)
    old_revision["frames"]["locations"]["rows"][0]["name"] = "Tampered"
    record(
        "context_content_tamper",
        lambda: _expect_rejected(
            _candidate(context), old_revision, "context_revision_mismatch"
        ),
    )
    dangling = _json_clone(context)
    dangling["frames"]["practitioners"]["rows"][0]["default_location_ref"] = "loc_synth_9999"
    _rehash_context(dangling)
    record(
        "dangling_context_reference",
        lambda: _expect_rejected(
            _candidate(dangling), dangling, "context_boundary_invalid"
        ),
    )
    duplicate = _json_clone(context)
    duplicate["frames"]["locations"]["rows"].append(
        copy.deepcopy(duplicate["frames"]["locations"]["rows"][0])
    )
    duplicate["frames"]["locations"]["count"] = 3
    _rehash_context(duplicate)
    record(
        "duplicate_context_reference",
        lambda: _expect_rejected(
            _candidate(duplicate), duplicate, "context_boundary_invalid"
        ),
    )

    proposal_material = {
        "canonical_candidate": _candidate(context),
        "context_revision": context["content_revision"],
        "source_paths": proposal["source_paths"],
        "before_state": proposal["before_state"],
        "after_state": proposal["after_state"],
    }
    if proposal["proposal_hash"] != _sha256(proposal_material):
        raise AcceptanceFailure("proposal_hash_not_bound")
    grounding_material = {
        "canonical_candidate": _candidate(context),
        "context_revision": context["content_revision"],
        "source_paths": sorted(proposal["source_paths"]),
        "before_state": proposal["before_state"],
        "after_state": proposal["after_state"],
    }
    if proposal["grounding_hash"] != _sha256(grounding_material):
        raise AcceptanceFailure("grounding_hash_not_bound")
    cases.append("proposal_and_grounding_hashes_bound")

    if not _effect_dependencies_absent(SCHEMA_SOURCE):
        raise AcceptanceFailure("schema_effect_dependency")
    if not _effect_dependencies_absent(SERVICE_SOURCE):
        raise AcceptanceFailure("service_effect_dependency")
    cases.append("effect_dependencies_absent")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    try:
        import jsonschema

        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
    except Exception as error:
        raise AcceptanceFailure("contract_schema_validation_failed") from error
    cases.append("contract_schema_valid")

    return {
        "schema_version": "emr4.davida_default_location_dry_run_evidence.v1",
        "result": RESULT,
        "evidence_label": EVIDENCE_LABEL,
        "data_class": "authored_synthetic",
        "case_count": len(cases),
        "passed_case_count": len(cases),
        "failed_case_count": 0,
        "verdict_counts": verdict_counts,
        "closed_rejection_reason_count": len(REJECTION_REASONS),
        "properties": {
            "proposal_candidate_non_authoritative": True,
            "human_confirmation_required": True,
            "confirmation_apply_write_authority": False,
            "provider_or_model_executed": False,
            "database_or_network_used": False,
            "clock_read": False,
            "partial_proposal_on_rejection": False,
        },
        "hashes": {
            "contract_sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
            "schema_sha256": hashlib.sha256(SCHEMA.read_bytes()).hexdigest(),
            "service_sha256": hashlib.sha256(SERVICE_SOURCE.read_bytes()).hexdigest(),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = run_acceptance()
    rendered = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    for forbidden in (
        "Avery",
        "Morgan",
        "Synthetic North",
        "Synthetic South",
        "prac_synth",
        "loc_synth",
        PRACTICE_REF,
        PRINCIPAL_REF,
        CORRELATION_ID,
    ):
        if forbidden in rendered:
            raise AcceptanceFailure("sensitive_value_in_evidence")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(rendered)
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
