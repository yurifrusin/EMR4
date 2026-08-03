"""Provider-free unoccupied acceptance for the Davida advisory proofreader.

The harness composes only authored-synthetic in-memory context frames and runs
the deterministic proofreader. It opens no database, network, browser, model,
provider or clock. Evidence is written only to an explicit caller path after
all cases pass.
"""

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
from app.schemas.practice_administration import (  # noqa: E402
    ActivePracticeLocationOut,
)
from app.schemas.practice_administration_advisory import (  # noqa: E402
    APPLY_OPERATIONS,
    AdvisoryDraftAdapter,
    OPERATION_EXPLAIN,
    OPERATION_SUMMARIZE,
    PARENT_PROPOSAL_OPERATIONS,
    PracticeAdministrationAdvisoryResultAdapter,
    REJECTION_REASONS,
)
from app.services.practice.practice_administration_advisory_proofreader import (  # noqa: E402
    proofread_advisory_candidate,
)
from app.services.practice.practice_administration_context_desk import (  # noqa: E402
    ResourceReferenceBinding,
    ResourceReferenceRegistry,
    compose_practice_administration_context,
)


RESULT = "provider_free_practice_administration_advisory_proofreader_pass"
EVIDENCE_LABEL = "provider_free_unoccupied_authored_synthetic"
OBSERVED = datetime(2026, 8, 3, 12, 0, tzinfo=timezone.utc)
EVALUATED = OBSERVED + timedelta(minutes=1)
PRACTICE_REF = "practice_synth_advisory"
PRINCIPAL_REF = "principal_synth_advisory"
CORRELATION_ID = "correlation-davida-advisory-primary"
CONTRACT = ROOT / "orchestration/continuity/davida-provider-free-practice-administration-advisory/advisory-contract.json"
SCHEMA = ROOT / "orchestration/continuity/davida-provider-free-practice-administration-advisory/advisory-contract.schema.json"
SCHEMA_SOURCE = ROOT / "app/schemas/practice_administration_advisory.py"
PROOFREADER_SOURCE = ROOT / "app/services/practice/practice_administration_advisory_proofreader.py"


class AcceptanceFailure(RuntimeError):
    """One deterministic acceptance invariant failed."""


def _canonical(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _json_clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def _rehash_context(frame: dict[str, Any]) -> None:
    payload = {key: value for key, value in frame.items() if key != "content_revision"}
    frame["content_revision"] = _sha256_bytes(_canonical(payload).encode("utf-8"))


def _sample_context(*, empty: bool = False) -> dict[str, Any]:
    if empty:
        return compose_practice_administration_context(
            practitioners=[],
            active_locations=[],
            practice_ref=PRACTICE_REF,
            principal_ref=PRINCIPAL_REF,
            correlation_id=CORRELATION_ID,
            observed_at=OBSERVED,
            resource_references=ResourceReferenceRegistry.build(()),
        )

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
            defaultLocation=PractitionerDefaultLocationOut(
                id=location_one,
                name="Synthetic North",
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


def _candidate(
    context: dict[str, Any],
    *,
    operation: str = OPERATION_SUMMARIZE,
    evaluated_at: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": "emr4.davida.practice_administration_advisory.candidate.v1",
        "practice_ref": context["practice_ref"],
        "principal_ref": context["principal_ref"],
        "correlation_id": context["correlation_id"],
        "content_revision": context["content_revision"],
        "authority_class": "advisory",
        "writes_authorized": False,
        "proposal_authorized": False,
        "confirmation_authorized": False,
        "evaluated_at": evaluated_at or EVALUATED.isoformat().replace("+00:00", "Z"),
        "operation": operation,
    }
    result.update(extra)
    return result


def _released(candidate: Any, context: Any) -> dict[str, Any]:
    result = proofread_advisory_candidate(candidate=candidate, context_frame=context)
    parsed = PracticeAdministrationAdvisoryResultAdapter.validate_python(result)
    if parsed.verdict != "released":
        raise AcceptanceFailure(f"expected_released:{parsed.reason}")
    AdvisoryDraftAdapter.validate_python(result["draft"])
    return result


def _rejected(
    candidate: Any,
    context: Any,
    reason: str | None = None,
) -> dict[str, Any]:
    result = proofread_advisory_candidate(candidate=candidate, context_frame=context)
    parsed = PracticeAdministrationAdvisoryResultAdapter.validate_python(result)
    if parsed.verdict != "rejected":
        raise AcceptanceFailure("expected_rejected")
    if reason is not None and parsed.reason != reason:
        raise AcceptanceFailure(f"wrong_reason:{parsed.reason}:{reason}")
    if "draft" in result or "payload" in result:
        raise AcceptanceFailure("partial_release_on_rejection")
    return result


def _forbidden_effects_absent(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                calls.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                parts: list[str] = []
                current: ast.expr = node.func
                while isinstance(current, ast.Attribute):
                    parts.append(current.attr)
                    current = current.value
                if isinstance(current, ast.Name):
                    parts.append(current.id)
                calls.add(".".join(reversed(parts)))
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
    }
    forbidden_calls = {
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "open",
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
        verdict_counts[result["verdict"]] += 1
        cases.append(name)
        return result

    full = _sample_context()
    empty = _sample_context(empty=True)

    summary = record(
        "non_empty_summary",
        lambda: _released(_candidate(full), full),
    )
    if summary["draft"]["payload"] != {
        "practitioner_count": 2,
        "location_count": 2,
        "practitioners_with_role_count": 1,
        "practitioners_with_default_location_count": 1,
    }:
        raise AcceptanceFailure("summary_not_derived")
    record("empty_summary", lambda: _released(_candidate(empty), empty))

    explain_one = _candidate(
        full,
        operation=OPERATION_EXPLAIN,
        subject_kind="practitioner",
        subject_ref="prac_synth_0001",
    )
    explained_one = record(
        "practitioner_explain_with_role_and_location",
        lambda: _released(explain_one, full),
    )
    if explained_one["draft"]["payload"]["default_location_ref"] != "loc_synth_0001":
        raise AcceptanceFailure("default_location_not_grounded")

    explain_two = _candidate(
        full,
        operation=OPERATION_EXPLAIN,
        subject_kind="practitioner",
        subject_ref="prac_synth_0002",
    )
    explained_two = record(
        "practitioner_explain_without_role_or_location",
        lambda: _released(explain_two, full),
    )
    if explained_two["draft"]["payload"]["role_label"] is not None:
        raise AcceptanceFailure("nullable_role_not_preserved")

    location_candidate = _candidate(
        full,
        operation=OPERATION_EXPLAIN,
        subject_kind="location",
        subject_ref="loc_synth_0002",
    )
    record("location_explain", lambda: _released(location_candidate, full))

    repeat_one = _released(_json_clone(explain_one), _json_clone(full))
    repeat_two = _released(_json_clone(explain_one), _json_clone(full))
    if _canonical(repeat_one) != _canonical(repeat_two):
        raise AcceptanceFailure("repeat_bytes_differ")
    if repeat_one["candidate_hash"] != repeat_two["candidate_hash"]:
        raise AcceptanceFailure("repeat_candidate_hash_differs")
    if (
        repeat_one["draft"]["grounding"]["grounding_digest"]
        != repeat_two["draft"]["grounding"]["grounding_digest"]
    ):
        raise AcceptanceFailure("repeat_grounding_hash_differs")
    cases.append("repeated_byte_and_hash_determinism")

    excluded = sorted(
        PARENT_PROPOSAL_OPERATIONS
        | APPLY_OPERATIONS
        | {"CONFIRM_PRACTITIONER_DEACTIVATE", "WRITE_PRACTITIONER_PROFILE", "UNKNOWN"}
    )
    for operation in excluded:
        record(
            f"operation_blocked_{operation}",
            lambda operation=operation: _rejected(
                _candidate(full, operation=operation),
                full,
                "operation_not_allowed",
            ),
        )
    missing_operation = _candidate(full)
    missing_operation.pop("operation")
    record(
        "missing_operation",
        lambda: _rejected(missing_operation, full, "operation_not_allowed"),
    )

    for field, value in (
        ("free_text", "forbidden"),
        ("provider", "forbidden"),
        ("memory", {}),
        ("database", "forbidden"),
        ("network", True),
        ("clock", "now"),
        ("write", True),
        ("count", 2),
        ("claim", "forbidden"),
    ):
        record(
            f"extra_field_blocked_{field}",
            lambda field=field, value=value: _rejected(
                _candidate(full, **{field: value}),
                full,
                "candidate_schema_invalid",
            ),
        )

    for field in (
        "writes_authorized",
        "proposal_authorized",
        "confirmation_authorized",
    ):
        candidate = _candidate(full)
        candidate[field] = True
        record(
            f"authority_true_blocked_{field}",
            lambda candidate=candidate: _rejected(
                candidate, full, "candidate_schema_invalid"
            ),
        )
        coercible = _candidate(full)
        coercible[field] = 0
        record(
            f"authority_numeric_coercion_blocked_{field}",
            lambda coercible=coercible: _rejected(
                coercible, full, "candidate_noncanonical"
            ),
        )

    for field, value in (
        ("practice_ref", "other_practice"),
        ("principal_ref", "other_principal"),
        ("correlation_id", "correlation-other"),
        ("content_revision", "f" * 64),
    ):
        candidate = _candidate(full)
        candidate[field] = value
        record(
            f"scope_mismatch_{field}",
            lambda candidate=candidate: _rejected(candidate, full, "scope_mismatch"),
        )

    tampered_old_revision = _json_clone(full)
    tampered_old_revision["frames"]["locations"]["rows"][0]["name"] = "Tampered"
    record(
        "tampered_context_old_revision",
        lambda: _rejected(
            _candidate(full),
            tampered_old_revision,
            "context_revision_mismatch",
        ),
    )

    context_mutations: list[
        tuple[str, Callable[[dict[str, Any]], None], str]
    ] = [
        (
            "blocked_source",
            lambda frame: frame["blocked_sources"][0].update({"reason": "changed"}),
            "context_boundary_invalid",
        ),
        (
            "source_label",
            lambda frame: frame["frames"]["practitioners"].update({"label": "changed"}),
            "context_frame_invalid",
        ),
        (
            "active_only",
            lambda frame: frame["frames"]["locations"].update({"active_only": False}),
            "context_frame_invalid",
        ),
        (
            "authority_ceiling",
            lambda frame: frame["authority_ceiling"].update({"write": True}),
            "context_frame_invalid",
        ),
        (
            "count_row_drift",
            lambda frame: frame["frames"]["locations"].update({"count": 1}),
            "context_boundary_invalid",
        ),
        (
            "dangling_default_location",
            lambda frame: frame["frames"]["practitioners"]["rows"][0].update(
                {"default_location_ref": "loc_synth_9999"}
            ),
            "context_boundary_invalid",
        ),
        (
            "duplicate_target",
            lambda frame: (
                frame["frames"]["practitioners"]["rows"].append(
                    copy.deepcopy(frame["frames"]["practitioners"]["rows"][0])
                ),
                frame["frames"]["practitioners"].update({"count": 3}),
            ),
            "context_boundary_invalid",
        ),
    ]
    for name, mutate, expected_reason in context_mutations:
        changed = _json_clone(full)
        mutate(changed)
        _rehash_context(changed)
        candidate = _candidate(changed)
        record(
            f"context_boundary_blocked_{name}",
            lambda candidate=candidate, changed=changed, expected_reason=expected_reason: _rejected(
                candidate, changed, expected_reason
            ),
        )

    coercible_context = _json_clone(full)
    coercible_context["frames"]["practitioners"]["active_only"] = 1
    canonicalized = _json_clone(full)
    coercible_context["content_revision"] = canonicalized["content_revision"]
    record(
        "context_coercion_blocked",
        lambda: _rejected(
            _candidate(full), coercible_context, "context_frame_invalid"
        ),
    )

    for name, when, reason in (
        ("naive", "2026-08-03T12:01:00", "evaluated_at_naive"),
        ("before", "2026-08-03T11:59:59Z", "evaluated_at_out_of_range"),
        ("at_expiry", "2026-08-03T12:02:00Z", "evaluated_at_out_of_range"),
    ):
        record(
            f"freshness_blocked_{name}",
            lambda when=when, reason=reason: _rejected(
                _candidate(full, evaluated_at=when), full, reason
            ),
        )

    record(
        "missing_target",
        lambda: _rejected(
            _candidate(
                full,
                operation=OPERATION_EXPLAIN,
                subject_kind="practitioner",
                subject_ref="prac_synth_9999",
            ),
            full,
            "subject_not_resolved",
        ),
    )
    record(
        "wrong_kind_target",
        lambda: _rejected(
            _candidate(
                full,
                operation=OPERATION_EXPLAIN,
                subject_kind="location",
                subject_ref="prac_synth_0001",
            ),
            full,
            "wrong_subject_kind",
        ),
    )
    record(
        "summary_target_blocked",
        lambda: _rejected(
            _candidate(full, subject_kind="location", subject_ref="loc_synth_0001"),
            full,
            "candidate_schema_invalid",
        ),
    )
    record(
        "non_mapping_candidate",
        lambda: _rejected(["not", "a", "mapping"], full, "candidate_noncanonical"),
    )
    record(
        "non_json_candidate",
        lambda: _rejected({"operation": OPERATION_SUMMARIZE, "value": {1, 2}}, full, "candidate_noncanonical"),
    )
    over_bounded = _candidate(full)
    over_bounded["padding"] = "x" * 2100
    record(
        "over_bounded_candidate",
        lambda: _rejected(over_bounded, full, "input_over_bounded"),
    )

    if not _forbidden_effects_absent(SCHEMA_SOURCE):
        raise AcceptanceFailure("schema_effect_dependency")
    if not _forbidden_effects_absent(PROOFREADER_SOURCE):
        raise AcceptanceFailure("proofreader_effect_dependency")
    cases.append("static_effect_dependency_absence")

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    try:
        import jsonschema

        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema).validate(contract)
    except Exception as exc:  # pragma: no cover - evidence must fail closed
        raise AcceptanceFailure("contract_schema_validation_failed") from exc
    cases.append("machine_contract_schema_validation")

    return {
        "schema_version": "emr4.davida_practice_administration_advisory_evidence.v1",
        "result": RESULT,
        "evidence_label": EVIDENCE_LABEL,
        "data_class": "authored_synthetic",
        "case_count": len(cases),
        "passed_case_count": len(cases),
        "failed_case_count": 0,
        "verdict_counts": verdict_counts,
        "closed_rejection_reason_count": len(REJECTION_REASONS),
        "properties": {
            "provider_or_model_executed": False,
            "database_or_network_used": False,
            "clock_read": False,
            "repair_performed": False,
            "retry_authorized": False,
            "proposal_apply_confirmation_write_authority": False,
            "released_fields_context_derived": True,
            "rejection_partial_payload": False,
        },
        "hashes": {
            "contract_sha256": _sha256_bytes(CONTRACT.read_bytes()),
            "schema_sha256": _sha256_bytes(SCHEMA.read_bytes()),
            "proofreader_sha256": _sha256_bytes(PROOFREADER_SOURCE.read_bytes()),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = run_acceptance()
    serialized = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
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
        if forbidden in serialized:
            raise AcceptanceFailure("sensitive_value_in_evidence")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialized, encoding="utf-8")
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
