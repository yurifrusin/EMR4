from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIARY_JS = ROOT / "docs" / "diary" / "diary.js"
EVIDENCE = ROOT / "docs" / "api-spine" / "practitioner-directory-office-addin-graphql-default-on-runtime.json"
TASKPANE_JS = ROOT / "EMR4 Sidebar" / "src" / "taskpane" / "taskpane.js"
SNAPSHOT = ROOT / "tests" / "fixtures" / "api_spine_external_readiness" / "blocked_readiness_status.json"


def _diary_source() -> str:
    return DIARY_JS.read_text(encoding="utf-8", errors="replace")


def _graphql_query_block() -> str:
    source = _diary_source()
    start = source.index("const PRACTITIONER_DIRECTORY_GRAPHQL_QUERY")
    end = source.index("const SLOT_HEIGHT_PX", start)
    return source[start:end]


def test_diary_graphql_practitioner_switch_defaults_on_after_approval_and_has_no_user_override():
    source = _diary_source()
    lowered = source.lower()

    assert "const ENABLE_GRAPHQL_PRACTITIONERS = true;" in source
    assert "const ENABLE_GRAPHQL_PRACTITIONERS = false;" not in source
    assert "emr4_flag_graphql_practitioners" not in lowered
    for line in lowered.splitlines():
        if "enable_graphql_practitioners" in line:
            assert "localstorage" not in line
            assert "urlsearchparams" not in line
            assert "office.context.document.settings" not in line


def test_diary_graphql_practitioner_query_uses_exact_approved_projection():
    source = _graphql_query_block()

    assert "const PRACTITIONER_DIRECTORY_GRAPHQL_QUERY" in source
    assert "query GetPractitioners($activeOnly: Boolean, $limit: Int, $offset: Int)" in source
    assert "practice {" in source
    assert "practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset)" in source
    for field in ("id", "displayName", "roleLabel", "active", "defaultLocation", "name"):
        assert field in source
    for forbidden in ("providerNumber", "prescriberNumber", "ahpraNumber", "hpiI", "email", "phone"):
        assert forbidden not in source


def test_diary_practitioner_loader_uses_rest_when_disabled_and_graphql_when_enabled():
    source = _diary_source()

    assert "async function fetchPractitionerDirectoryRest()" in source
    assert 'apiFetch("/practice/practitioners?activeOnly=true&limit=200")' in source
    assert "async function fetchPractitionerDirectoryGraphql()" in source
    assert 'apiFetch("/graphql", {' in source
    assert source.count('apiFetch("/graphql", {') == 1
    assert "if (!ENABLE_GRAPHQL_PRACTITIONERS) {" in source
    assert "return fetchPractitionerDirectoryRest();" in source


def test_diary_graphql_practitioner_fallback_and_error_contract_is_wired():
    source = _diary_source()

    assert 'reason: "transport"' in source
    assert 'code === "FORBIDDEN" || code === "BAD_USER_INPUT"' in source
    assert 'reason: "practice_null"' in source
    assert 'if (err && err.message === "401 Unauthorized") throw err;' in source
    assert "falling back to REST" in source
    assert "return await fetchPractitionerDirectoryRest();" in source


def test_diary_practitioner_normalizer_preserves_projection_and_drops_malformed_rows():
    source = _diary_source()

    assert "function normalizePractitionerDirectory(rows)" in source
    assert "const id = row && row.id ? String(row.id) : \"\";" in source
    assert "const displayName = row && row.displayName ? String(row.displayName).trim() : \"\";" in source
    assert "const roleLabel = row && row.roleLabel ? String(row.roleLabel).trim() : \"\";" in source
    assert "const active = typeof row?.active === \"boolean\" ? row.active : null;" in source
    assert "defaultLocationId" in source
    assert "defaultLocationName" in source
    assert ".filter(row => row.id && row.displayName);" in source


def test_no_unrelated_taskpane_graphql_path_or_readiness_flip():
    taskpane = TASKPANE_JS.read_text(encoding="utf-8", errors="replace").lower()
    snapshot = SNAPSHOT.read_text(encoding="utf-8")

    assert "/api/v1/graphql" not in taskpane
    assert "query getpractitioners" not in taskpane
    assert '"graphql_resolver_ready": false' in snapshot
    assert '"deployment_ready": false' not in snapshot


def test_runtime_evidence_records_approved_default_on_switch_boundaries():
    import json

    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    assert payload["schema_version"] == "api_spine.practitioner_directory_office_addin_graphql_default_on_runtime.v1"
    assert payload["sprint"] == 281
    assert payload["decision"] == "approved_default_on_office_addin_graphql_practitioner_selector_runtime"
    assert payload["runtime_posture"]["feature_gate_name"] == "ENABLE_GRAPHQL_PRACTITIONERS"
    assert payload["runtime_posture"]["feature_gate_default"] is True
    assert payload["runtime_posture"]["graphql_live_traffic_by_default"] is True
    assert payload["runtime_posture"]["single_consumer_only"] is True
    assert payload["runtime_posture"]["rest_fallback_retained"] is True
    assert "test_default_on_graphql_401_rethrows_without_rest_fallback_and_clears_token" in payload["browser_evidence"]["tests"]
    assert payload["browser_evidence"]["observed_default_on"]["graphql_401_rethrows_without_rest_fallback"] is True
    assert all(value is False for value in payload["must_remain_false"].values())
    assert payload["worker_reviews"]["antigravity_consumer_ux"]["verdict"] == "unavailable"
    assert payload["worker_reviews"]["deepseek_static_security"]["verdict"] == "PASS"
