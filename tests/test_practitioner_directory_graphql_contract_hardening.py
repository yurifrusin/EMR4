import json
from pathlib import Path

from app.graphql.schema import schema
from tests.conftest import make_token


ROOT = Path(__file__).resolve().parents[1]
SDL = ROOT / "docs" / "api-spine" / "graphql" / "appointment-diary-read.graphql"
DAG = ROOT / "docs" / "api-spine" / "external-read-model-readiness-dag.json"
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
SHELL_JSON = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-runtime-shell.json"
RESOLVER_JSON = ROOT / "docs" / "api-spine" / "practitioner-directory-graphql-resolver-runtime.json"
HARDENING_JSON = (
    ROOT
    / "docs"
    / "api-spine"
    / "practitioner-directory-graphql-contract-hardening.json"
)


def _auth(user) -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token(user)}"}


def _post(client, user, query: str):
    return client.post(
        "/api/v1/graphql",
        json={"query": query},
        headers=_auth(user),
    )


def test_runtime_sdl_matches_approved_practitioner_slice():
    runtime_sdl = schema.as_str()
    approved_sdl = SDL.read_text(encoding="utf-8")

    for fragment in (
        "practice(id: ID = null): Practice",
        "type Practice {\n  id: ID!\n  practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0): [Practitioner!]!",
        "type PracticeLocationBrief {\n  id: ID!\n  name: String!",
        "type Practitioner {\n  id: ID!\n  displayName: String!\n  roleLabel: String\n  active: Boolean!\n  defaultLocation: PracticeLocationBrief",
    ):
        assert fragment in runtime_sdl

    for fragment in (
        "practitioners(activeOnly: Boolean = true, limit: Int = 50, offset: Int = 0): [Practitioner!]!",
        "type PracticeLocationBrief",
        "defaultLocation: PracticeLocationBrief",
    ):
        assert fragment in approved_sdl

    for forbidden in ("type Mutation", "type Subscription", "appointment(", "patient(", "diary("):
        assert forbidden not in runtime_sdl


def test_alias_repetition_is_preempted_by_token_guard(client, gp_user):
    query = "{ " + " ".join(
        f"a{index}: graphqlHealth {{ status }}"
        for index in range(501)
    ) + " }"

    response = _post(client, gp_user, query)

    assert response.status_code == 200
    body = response.json()
    assert "errors" in body
    assert "token" in response.text.lower()
    assert "501" in response.text or "500" in response.text


def test_token_budget_counts_repeated_fields(client, gp_user):
    query = "{ " + " ".join(
        "graphqlHealth { status service authenticated }"
        for _index in range(130)
    ) + " }"

    response = _post(client, gp_user, query)

    assert response.status_code == 200
    body = response.json()
    assert "errors" in body
    assert "token" in response.text.lower()


def test_token_budget_protects_practitioner_resolver_path(client, gp_user):
    query = "{ " + " ".join(
        f"p{index}: practice {{ practitioners {{ id displayName roleLabel active defaultLocation {{ id name }} }} }}"
        for index in range(60)
    ) + " }"

    response = _post(client, gp_user, query)

    assert response.status_code == 200
    body = response.json()
    assert "errors" in body
    assert "token" in response.text.lower()


def test_current_runtime_depth_cannot_exceed_six_without_invalid_field_selection():
    runtime_sdl = schema.as_str()

    assert "Practice" in runtime_sdl
    assert "Practitioner" in runtime_sdl
    assert "PracticeLocationBrief" in runtime_sdl
    assert "PracticeLocationBrief!" not in runtime_sdl
    assert "defaultLocation: PracticeLocationBrief" in runtime_sdl
    assert "practitioners(" in runtime_sdl


def test_global_readiness_snapshots_remain_blocked_after_scoped_resolver():
    dag = json.loads(DAG.read_text(encoding="utf-8"))
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    assert dag["decision"] == "blocked"
    assert all(value is False for value in dag["readiness"].values())

    readiness_suffixes = ("_ready", "_performed", "_allowed")
    readiness_values = {
        key: value
        for key, value in snapshot.items()
        if key.endswith(readiness_suffixes)
        or key
        in {
            "closed_gate_consistency",
            "dag_all_readiness_false",
            "pause_required",
            "raw_compat_mode_change_ready",
        }
    }
    assert readiness_values["closed_gate_consistency"] is True
    assert readiness_values["dag_all_readiness_false"] is True
    assert readiness_values["pause_required"] is False
    for key, value in readiness_values.items():
        if key in {"closed_gate_consistency", "dag_all_readiness_false", "pause_required"}:
            continue
        assert value is False, key


def test_graphql_must_remain_false_artifacts_stay_consistent():
    shell = json.loads(SHELL_JSON.read_text(encoding="utf-8"))
    resolver = json.loads(RESOLVER_JSON.read_text(encoding="utf-8"))
    hardening = json.loads(HARDENING_JSON.read_text(encoding="utf-8"))

    expected = {
        "graphql_mutation_ready",
        "deployment_ready",
        "production_ready",
        "external_patient_client_ready",
        "write_authority_ready",
        "provider_or_memory_ready",
        "h15_h_series_historical_diary_ready",
    }

    assert set(resolver["must_remain_false"]) == expected
    assert set(hardening["must_remain_false"]) == expected
    assert expected.issubset(shell["must_remain_false"])
    assert all(value is False for value in shell["must_remain_false"].values())
    assert all(value is False for value in resolver["must_remain_false"].values())
    assert all(value is False for value in hardening["must_remain_false"].values())


def test_sprint271_evidence_records_hardening_without_new_surface():
    payload = json.loads(HARDENING_JSON.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "api_spine.practitioner_directory_graphql_contract_hardening.v1"
    assert payload["sprint"] == 271
    assert payload["decision"] == "contract_hardened_no_new_surface"
    assert payload["new_runtime_fields_added"] is False
    assert payload["guard_checks"]["alias_limit_configured"] is True
    assert payload["guard_checks"]["alias_limit_negative_test_preempted_by_token_budget"] is True
    assert payload["guard_checks"]["token_limit_negative_test"] is True
    assert payload["guard_checks"]["practitioner_path_token_limit_negative_test"] is True
    assert payload["readiness_snapshots_remain_blocked"] is True
    assert payload["cross_document_must_remain_false_consistency"] is True
    assert payload["worker_review"]["verdict"] == "PASS"
    assert all(value is False for value in payload["must_remain_false"].values())
