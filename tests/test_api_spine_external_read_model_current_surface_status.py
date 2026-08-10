import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = (
    ROOT / "docs" / "api-spine" / "external-read-model-current-surface-status.json"
)
SCHEMA_PATH = STATUS_PATH.with_suffix(".schema.json")
HISTORICAL_PATH = (
    ROOT / "docs" / "api-spine" / "external-router-read-model-gap-inventory.md"
)

EXPECTED_SURFACES = {
    "Query.practice.practitioners",
    "Query.patient.reminders",
    "Query.patient.messages",
    "Query.directorySearch.RACGP_GUIDELINES",
    "Query.directorySearch.COCHRANE_LIBRARY",
}


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _rows() -> dict[str, dict]:
    value = _load(STATUS_PATH)
    return {row["surface"]: row for row in value["surfaces"]}


def test_current_surface_index_has_exact_closed_shape() -> None:
    value = _load(STATUS_PATH)
    schema = _load(SCHEMA_PATH)

    assert value["schema_version"] == (
        "api_spine.external_read_model_current_surface_status.v1"
    )
    assert set(value) == {
        "schema_version",
        "date",
        "historical_inventory",
        "current_status_authority",
        "surfaces",
        "claim_boundary",
    }
    assert {row["surface"] for row in value["surfaces"]} == EXPECTED_SURFACES
    assert len(value["surfaces"]) == 5
    assert value["historical_inventory"] == HISTORICAL_PATH.relative_to(ROOT).as_posix()
    assert schema["properties"]["surfaces"]["minItems"] == 5
    assert schema["properties"]["surfaces"]["maxItems"] == 5
    assert schema["$defs"]["surface"]["additionalProperties"] is False

    for row in value["surfaces"]:
        assert set(row) == {
            "surface",
            "authority_kind",
            "implementation_status",
            "rest",
            "graphql",
            "deployment_ready",
            "production_ready",
            "supersedes",
        }
        assert row["authority_kind"] == "read_only"
        assert row["deployment_ready"] is False
        assert row["production_ready"] is False
        for group in ("rest", "graphql"):
            for evidence in row[group]["evidence"]:
                assert (ROOT / evidence).is_file()
        for evidence in row["supersedes"]["evidence"]:
            assert (ROOT / evidence).is_file()


def test_practitioner_read_is_implemented_and_mounted_but_not_released() -> None:
    row = _rows()["Query.practice.practitioners"]
    main = (ROOT / "app/main.py").read_text(encoding="utf-8")
    rest = (ROOT / "app/routers/practice.py").read_text(encoding="utf-8")
    graphql = (ROOT / "app/graphql/schema.py").read_text(encoding="utf-8")

    assert row["implementation_status"] == "implemented_mounted"
    assert row["rest"] == {
        "status": "implemented",
        "mounted": True,
        "evidence": [
            "app/routers/practice.py",
            "app/main.py",
            "docs/api-spine/practitioner-directory-post-implementation-readiness-review.json",
        ],
    }
    assert row["graphql"]["status"] == "implemented"
    assert row["graphql"]["mounted"] is True
    assert row["supersedes"]["historical_posture"] == "route_gap"
    assert row["supersedes"]["current_posture"] == "implemented_mounted_read_only"
    assert '@router.get("/practitioners"' in rest
    assert "def practitioners(" in graphql
    assert "app.include_router(practice.router)" in main
    assert "app.include_router(graphql_router)" in main
    assert "class Mutation" not in graphql


def test_four_unimplemented_surfaces_remain_explicitly_closed() -> None:
    rows = _rows()
    for surface in EXPECTED_SURFACES - {"Query.practice.practitioners"}:
        row = rows[surface]
        assert row["implementation_status"] in {
            "route_and_shape_gap",
            "source_and_licensing_gap",
        }
        assert row["rest"]["status"] == "absent"
        assert row["rest"]["mounted"] is False
        assert row["graphql"]["status"] == "reserved_contract_only"
        assert row["graphql"]["mounted"] is False
        assert row["supersedes"]["current_posture"] == row["implementation_status"]


def test_current_index_separates_implementation_from_release_readiness() -> None:
    value = _load(STATUS_PATH)
    joined = " ".join(
        [value["current_status_authority"], value["claim_boundary"]]
    ).lower()
    assert "historical" in joined
    assert "provider" in joined
    assert "patient" in joined
    assert "write authority" in joined
    assert "deployment" in joined
    assert "production" in joined
    assert "grants no new resolver" in joined
