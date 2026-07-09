from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


APPROVED_ROW_FIELDS = {"id", "displayName", "roleLabel", "active", "defaultLocation"}
APPROVED_LOCATION_FIELDS = {"id", "name"}

ErrorKind = Literal[
    "NONE",
    "HTTP_401",
    "GRAPHQL_FORBIDDEN",
    "GRAPHQL_BAD_USER_INPUT",
    "GRAPHQL_DISABLED",
    "NETWORK_OR_SYSTEM",
]


@dataclass(frozen=True)
class MockFetchResponse:
    status_code: int
    body: dict[str, Any]


@dataclass(frozen=True)
class MockPractitionerContractResult:
    rows: list[dict[str, Any]]
    error_kind: ErrorKind
    logout_requested: bool
    graphql_fetch_attempted: bool
    future_rest_fallback_requested: bool


def consume_mock_practitioner_graphql_response(
    response: MockFetchResponse | None,
    *,
    gate_disabled: bool = False,
) -> MockPractitionerContractResult:
    """Python-only contract reference for a future JS taskpane fetch wrapper.

    This deliberately consumes mocked response dictionaries instead of calling
    FastAPI, Strawberry, fetch, apiFetch, or taskpane code.
    """
    if gate_disabled:
        return MockPractitionerContractResult(
            rows=[],
            error_kind="GRAPHQL_DISABLED",
            logout_requested=False,
            graphql_fetch_attempted=False,
            future_rest_fallback_requested=False,
        )
    if response is None:
        return MockPractitionerContractResult(
            rows=[],
            error_kind="NETWORK_OR_SYSTEM",
            logout_requested=False,
            graphql_fetch_attempted=True,
            future_rest_fallback_requested=True,
        )
    if response.status_code == 401:
        return MockPractitionerContractResult(
            rows=[],
            error_kind="HTTP_401",
            logout_requested=True,
            graphql_fetch_attempted=True,
            future_rest_fallback_requested=False,
        )
    if response.status_code != 200:
        return MockPractitionerContractResult(
            rows=[],
            error_kind="NETWORK_OR_SYSTEM",
            logout_requested=False,
            graphql_fetch_attempted=True,
            future_rest_fallback_requested=True,
        )

    code = _first_graphql_error_code(response.body)
    if code == "FORBIDDEN":
        return MockPractitionerContractResult(
            rows=[],
            error_kind="GRAPHQL_FORBIDDEN",
            logout_requested=False,
            graphql_fetch_attempted=True,
            future_rest_fallback_requested=False,
        )
    if code == "BAD_USER_INPUT":
        return MockPractitionerContractResult(
            rows=[],
            error_kind="GRAPHQL_BAD_USER_INPUT",
            logout_requested=False,
            graphql_fetch_attempted=True,
            future_rest_fallback_requested=False,
        )

    practice = response.body.get("data", {}).get("practice")
    if not isinstance(practice, dict):
        return MockPractitionerContractResult(
            rows=[],
            error_kind="NONE",
            logout_requested=False,
            graphql_fetch_attempted=True,
            future_rest_fallback_requested=False,
        )
    rows = practice.get("practitioners", [])
    if not isinstance(rows, list):
        rows = []
    return MockPractitionerContractResult(
        rows=[_project_row(row) for row in rows if isinstance(row, dict)],
        error_kind="NONE",
        logout_requested=False,
        graphql_fetch_attempted=True,
        future_rest_fallback_requested=False,
    )


def _first_graphql_error_code(body: dict[str, Any]) -> str | None:
    errors = body.get("errors", [])
    if not isinstance(errors, list) or not errors:
        return None
    first = errors[0]
    if not isinstance(first, dict):
        return None
    extensions = first.get("extensions", {})
    if not isinstance(extensions, dict):
        return None
    code = extensions.get("code")
    return code if isinstance(code, str) else None


def _project_row(row: dict[str, Any]) -> dict[str, Any]:
    projected = {key: row.get(key) for key in ("id", "displayName", "roleLabel", "active")}
    location = row.get("defaultLocation")
    if isinstance(location, dict):
        projected["defaultLocation"] = {
            key: location.get(key)
            for key in ("id", "name")
            if key in location
        }
    else:
        projected["defaultLocation"] = None
    assert set(projected) == APPROVED_ROW_FIELDS
    if projected["defaultLocation"] is not None:
        assert set(projected["defaultLocation"]).issubset(APPROVED_LOCATION_FIELDS)
    return projected
