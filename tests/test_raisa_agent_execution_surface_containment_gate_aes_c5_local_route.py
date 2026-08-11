"""Provider-free tests for the AES-C5 disposable local-route harness."""

from __future__ import annotations

import copy
import json

import pytest

from scripts import (
    raisa_agent_execution_surface_containment_gate_aes_c5_local_route as local,
)
from scripts import (
    raisa_agent_execution_surface_containment_gate_aes_c5_product_runtime_admission as core,
)

SOURCE_HEAD = "ef0457067b9c2717c7b20dcd6f3bafeb9b275247"


def test_schema_name_is_exactly_bounded():
    value = "aes_c5_" + "a" * 32
    assert local.validate_schema_name(value) == value
    for invalid in (
        "public",
        "aes_c5_../public",
        "aes_c5_" + "a" * 31,
        "aes-c5-" + "a" * 32,
        "aes_c5_" + "G" * 32,
    ):
        with pytest.raises(local.LocalRouteError) as exc:
            local.validate_schema_name(invalid)
        assert exc.value.reason_code == "disposable_schema_name_invalid"


def test_core_local_mode_requires_both_bounded_adapters(tmp_path):
    with pytest.raises(core.AesC5Error) as exc:
        core.execute(
            mode="local-route-fake-provider",
            source_head=SOURCE_HEAD,
            evidence_output=tmp_path / "evidence.json",
            ledger_output=tmp_path / "ledgers",
        )
    assert exc.value.reason_code == "bounded_adapter_missing"


def test_local_mode_rejects_unproved_source_metadata(tmp_path):
    source = core.source_provider_free_fixture
    assert source().metadata.get("product_runtime_route_read") is not True
    evidence = core.execute(
        mode="local-route-fake-provider",
        source_head=SOURCE_HEAD,
        evidence_output=tmp_path / "evidence.json",
        ledger_output=tmp_path / "ledgers",
        source_adapter=source,
        provider_adapter=core.provider_provider_free_fixture,
    )
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["local_source_metadata_invalid"]


def test_local_fake_mode_rejects_provider_contact(tmp_path):
    observed_at = core.datetime(2026, 8, 11, tzinfo=core.timezone.utc)

    def source():
        result = core.source_provider_free_fixture()
        metadata = {
            "observed_at": observed_at,
            "product_runtime_route_read": True,
            "ordinary_bearer_auth_dependency_used": True,
            "token_user_practice_equality_observed": True,
            "counts_unchanged": True,
            "route_status": 200,
            "database_statement_count": 3,
        }
        return core.SourceResult(rows=result.rows, metadata=metadata)

    def contacted(request, frame):
        result = core.provider_provider_free_fixture(request, frame)
        metadata = copy.deepcopy(result.metadata)
        metadata["provider_contacted"] = True
        return core.ProviderResult(packet=result.packet, metadata=metadata)

    evidence = core.execute(
        mode="local-route-fake-provider",
        source_head=SOURCE_HEAD,
        evidence_output=tmp_path / "evidence.json",
        ledger_output=tmp_path / "ledgers",
        source_adapter=source,
        provider_adapter=contacted,
        now=observed_at,
    )
    assert evidence["result"] == "revision_required"
    assert evidence["reason_codes"] == ["provider_contact_forbidden"]


def test_lifecycle_evidence_contains_no_raw_schema_name_or_values(tmp_path):
    schema = "aes_c5_" + "b" * 32
    lifecycle = {
        "schema_version": "emr4.aes_c5.local_route_lifecycle_evidence.v1",
        "schema_name_digest": core.digest_of(schema),
        "schema_name_retained": False,
        "contains_sensitive_values": False,
    }
    path = tmp_path / "lifecycle.json"
    core.atomic_write(path, lifecycle)
    text_value = path.read_text(encoding="utf-8")
    assert schema not in text_value
    assert json.loads(text_value)["schema_name_retained"] is False
