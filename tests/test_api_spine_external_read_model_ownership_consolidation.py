import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONSOLIDATION = (
    ROOT
    / "docs"
    / "api-spine"
    / "external-read-model-ownership-consolidation-preflight.md"
)
PRACTITIONER = (
    ROOT / "docs" / "api-spine" / "practitioner-directory-route-schema-ownership-candidate.md"
)
REMINDERS = ROOT / "docs" / "api-spine" / "patient-reminders-route-schema-ownership-candidate.md"
MESSAGES = ROOT / "docs" / "api-spine" / "patient-messages-route-schema-ownership-candidate.md"
SNAPSHOT = (
    ROOT
    / "tests"
    / "fixtures"
    / "api_spine_external_readiness"
    / "blocked_readiness_status.json"
)
PATIENTS_ROUTER = ROOT / "app" / "routers" / "patients.py"
DIARY_ROUTER = ROOT / "app" / "routers" / "diary.py"
CLINICAL_ROUTER = ROOT / "app" / "routers" / "clinical.py"
PATIENTS_SCHEMA = ROOT / "app" / "schemas" / "patients.py"
DIARY_SCHEMA = ROOT / "app" / "schemas" / "diary.py"

ALL_CANDIDATES = {
    "practice_practitioners": PRACTITIONER,
    "patient_reminders": REMINDERS,
    "patient_messages": MESSAGES,
}

EXPECTED_FIRST_CANDIDATE = "practice_practitioners"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _compact(path: Path) -> str:
    return " ".join(_read(path).split())


def _ownership_rows(path: Path) -> dict[str, str]:
    section = _read(path).split("## Candidate Ownership", 1)[1].split("\n## ", 1)[0]
    rows = {}
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows[cells[0].strip("`")] = cells[2].strip("`")
    return rows


def test_consolidation_references_all_three_candidate_packets_and_blocked_inputs():
    text = _read(CONSOLIDATION)
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

    for path in ALL_CANDIDATES.values():
        assert path.name in text
        assert path.exists()
    for artifact in [
        "external-read-model-implementation-planning-review.md",
        "external-read-model-combined-readiness-review.md",
        "external-read-model-readiness-dag.json",
        "blocked_readiness_status.json",
    ]:
        assert artifact in text

    assert snapshot["dag_decision"] == "blocked"
    assert snapshot["rest_route_ready"] is False
    assert snapshot["graphql_resolver_ready"] is False
    assert snapshot["external_read_model_runtime_ready"] is False


def test_ownership_matrix_matches_candidate_paths_and_homes():
    text = _read(CONSOLIDATION)

    expected_fragments = {
        "practice_practitioners": [
            "GET /api/v1/practice/practitioners",
            "new `app/routers/practice.py`",
            "new `app/schemas/practice.py::PractitionerOut`",
            "app/models/tenancy.py::Practitioner",
        ],
        "patient_reminders": [
            "GET /api/v1/patients/{patient_id}/reminders",
            "existing `app/routers/patients.py`",
            "existing `app/schemas/patients.py::PatientReminderOut`",
            "app/models/results.py::Reminder",
        ],
        "patient_messages": [
            "GET /api/v1/patients/{patient_id}/messages",
            "existing `app/routers/patients.py`",
            "existing `app/schemas/patients.py::PatientMessageSummaryOut`",
            "app/models/messaging.py::InternalMessage",
            "app/models/messaging.py::SmsLog",
        ],
    }

    for candidate, fragments in expected_fragments.items():
        assert f"`{candidate}`" in text
        for fragment in fragments:
            assert fragment in text


def test_all_candidate_ownership_rows_remain_unapproved():
    for name, path in ALL_CANDIDATES.items():
        rows = _ownership_rows(path)
        assert rows, f"{name} has no ownership rows"
        assert all(status in {"candidate_only", "evidence_only"} for status in rows.values())
        assert not any(status in {"approved", "implemented"} for status in rows.values())


def test_complexity_ranking_selects_practitioner_directory_first():
    compact = _compact(CONSOLIDATION)

    assert f"Recommended first go/no-go candidate: `{EXPECTED_FIRST_CANDIDATE}`" in compact
    assert "`1_lowest` | `practice_practitioners`" in _read(CONSOLIDATION)
    assert "`2_middle` | `patient_reminders`" in _read(CONSOLIDATION)
    assert "`3_highest` | `patient_messages`" in _read(CONSOLIDATION)
    for phrase in [
        "the only `route_gap`",
        "practice-scoped only",
        "avoids patient anti-enumeration handling",
        "no two-table union",
        "sensitive practitioner identifier exclusion",
    ]:
        assert phrase in compact


def test_preflight_keeps_current_runtime_code_negative():
    router_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [PATIENTS_ROUTER, DIARY_ROUTER, CLINICAL_ROUTER]
    )
    schema_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [PATIENTS_SCHEMA, DIARY_SCHEMA]
    )

    for fragment in [
        '@router.get("/practice/practitioners"',
        '@router.get("/{patient_id}/reminders"',
        '@router.get("/{patient_id}/messages"',
    ]:
        assert fragment not in router_text
    for fragment in [
        "class PractitionerOut",
        "class PatientReminderOut",
        "class PatientMessageSummaryOut",
    ]:
        assert fragment not in schema_text


def test_candidate_specific_preflight_emphasis_covers_each_gap_family():
    text = _read(CONSOLIDATION)

    for phrase in [
        "PractitionerOut` sensitive-field exclusions",
        "`displayName` derivation",
        "active-only default",
        "default-location join scope",
        "patient ownership `404`",
        "`dueAt` date-to-DateTime policy",
        "`COMPLETED` unavailable",
        "two-table union policy",
        "`internal-{id}`/`sms-{id}` namespace",
        "`EMAIL` blocked",
        "bulk SMS and inbound reply policy",
        "status union policy",
    ]:
        assert phrase in text


def test_closed_gates_are_preserved_in_consolidation():
    text = _read(CONSOLIDATION)
    compact = " ".join(text.split())

    for phrase in [
        "adding REST routes",
        "adding GraphQL resolvers or GraphQL mutations",
        "adding Pydantic runtime schemas",
        "changing the blocked readiness snapshot",
        "changing readiness flags to `true`",
        "provider calls or live provider gates",
        "provider dry-run wiring",
        "runtime FGA clients",
        "external patient clients",
        "H15/H-series runtime imports",
        "memory/RAG/GraphRAG runtime wiring",
        "broad historical diary trove mining",
        "Access AI invocation wiring",
        "source manifests as approved runtime configuration",
        "RACGP or Cochrane content ingestion, indexing, caching, embedding, scraping",
        "reminder, message, SMS, practitioner, directory, appointment, billing, result",
        "model-to-database writes outside REST command handlers",
        "raw compatibility deprecation mode changes",
    ]:
        assert phrase in compact
    assert "does not authorize" in text
    assert "does not prove runtime GraphQL resolver implementation" in compact
    assert "patient-facing client readiness" in text
