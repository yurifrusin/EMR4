from pathlib import Path

from scripts import (
    raisa_provider_free_read_only_status_confirm_route_mounting_readiness_rereview as review,
)


def test_frozen_contract_passes_text_only_review() -> None:
    contract = review.build_contract()
    schema = review.build_schema()
    evidence = review.build_evidence(contract, schema)

    assert review.validate(contract, schema) == []
    assert evidence["result"].endswith("_pass")
    assert evidence["verdict"] == "composition_accepted_route_mounting_not_ready"
    assert evidence["dimension_counts"] == {
        "satisfied": 4,
        "partial_gap": 2,
        "blocking_gap": 4,
    }


def test_all_hostile_mutations_fail_closed() -> None:
    contract = review.build_contract()
    schema = review.build_schema()
    mutations = review.hostile_mutations(contract)

    assert len(mutations) >= 50
    assert all(review.validate(candidate, schema) for _, candidate in mutations)


def test_dimension_order_and_blockers_are_exact() -> None:
    rows = review.build_contract()["dimensions"]

    assert [row["id"] for row in rows] == [
        "literal_route_mounting",
        "canonical_api_identity",
        "physical_seam_composition",
        "current_authority_and_session",
        "status_only_discrimination",
        "locked_policy_admission",
        "atomic_audit_private_receipt",
        "canonical_stored_delivery",
        "physical_outcome_mapping",
        "proved_physical_foundation",
    ]
    assert [row["id"] for row in rows if row["admission_blocker"]] == [
        "current_authority_and_session",
        "status_only_discrimination",
        "locked_policy_admission",
        "atomic_audit_private_receipt",
    ]
    assert all(row["unmounted_prerequisite_exists"] for row in rows)


def test_next_candidate_is_unmounted_and_provider_free() -> None:
    contract = review.build_contract()
    candidate = contract["next_candidate"]

    assert candidate["id"] == "provider_free_unmounted_status_confirm_product_adapter_rehearsal"
    assert candidate["route_mount_or_call"] is False
    assert candidate["database_execution"] is False
    assert all(value is False for value in contract["forbidden"].values())


def test_reviewer_never_imports_application_runtime() -> None:
    source = Path(review.__file__).read_text(encoding="utf-8")

    assert "from app" not in source
    assert "import app" not in source
    assert "sqlalchemy" not in source.lower()
