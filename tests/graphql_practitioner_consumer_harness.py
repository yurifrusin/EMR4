from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PRACTITIONER_QUERY = """
query PractitionerDirectory($activeOnly: Boolean = true, $limit: Int = 50, $offset: Int = 0, $practiceId: ID = null) {
  practice(id: $practiceId) {
    practitioners(activeOnly: $activeOnly, limit: $limit, offset: $offset) {
      id
      displayName
      roleLabel
      active
      defaultLocation {
        id
        name
      }
    }
  }
}
"""

ALLOWED_PRACTITIONER_FIELDS = {
    "id",
    "displayName",
    "roleLabel",
    "active",
    "defaultLocation",
}

ALLOWED_LOCATION_FIELDS = {"id", "name"}


@dataclass(frozen=True)
class GraphQLConsumerResult:
    status_code: int
    body: dict[str, Any]

    @property
    def errors(self) -> list[dict[str, Any]]:
        errors = self.body.get("errors", [])
        return errors if isinstance(errors, list) else []

    @property
    def error_codes(self) -> set[str | None]:
        return {error.get("extensions", {}).get("code") for error in self.errors}

    @property
    def rows(self) -> list[dict[str, Any]]:
        practice = self.body.get("data", {}).get("practice")
        if not isinstance(practice, dict):
            return []
        rows = practice.get("practitioners", [])
        return rows if isinstance(rows, list) else []

    @property
    def practice_is_null(self) -> bool:
        return self.body.get("data", {}).get("practice") is None


class PractitionerGraphQLConsumerHarness:
    """Test-only consumer harness approved through 2026-08-06 for one field."""

    def __init__(self, client: Any):
        self._client = client

    def query_practitioners(
        self,
        *,
        token: str | None,
        active_only: bool | None = True,
        limit: int | None = 50,
        offset: int | None = 0,
        practice_id: str | None = None,
        query: str = PRACTITIONER_QUERY,
        variables: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> GraphQLConsumerResult:
        headers = {}
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        if extra_headers:
            headers.update(extra_headers)
        payload_variables = (
            variables
            if variables is not None
            else {
                "activeOnly": active_only,
                "limit": limit,
                "offset": offset,
                "practiceId": practice_id,
            }
        )
        response = self._client.post(
            "/api/v1/graphql",
            json={
                "query": query,
                "variables": payload_variables,
            },
            headers=headers,
        )
        return GraphQLConsumerResult(
            status_code=response.status_code,
            body=response.json(),
        )


def assert_approved_practitioner_projection(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        assert set(row) == ALLOWED_PRACTITIONER_FIELDS
        location = row.get("defaultLocation")
        if location is not None:
            assert set(location) == ALLOWED_LOCATION_FIELDS


def assert_graphql_error_code(result: GraphQLConsumerResult, code: str) -> None:
    assert result.status_code == 200
    assert code in result.error_codes


def assert_http_auth_failure(result: GraphQLConsumerResult) -> None:
    assert result.status_code == 401
