"""Explicitly constructed GraphQL context for one application-auth read."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi import HTTPException, Request, Response, status
from graphql import GraphQLError, parse
from graphql.language.ast import FieldNode, OperationDefinitionNode
from strawberry.fastapi import GraphQLRouter

from app.graphql.schema import schema
from app.services.application_auth_product_read import (
    ApplicationSessionPractitionerDirectoryBridge,
    ProductReadAuthenticationFailed,
    ProductReadAuthorizationFailed,
    ProductReadRequestDenied,
    ProductReadUnavailable,
)
from app.services.application_auth_runtime import Surface
from app.services.application_auth_transport import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SESSION_COOKIE_NAME,
)


CORRELATION_HEADER_NAME = "X-EMR4-Correlation-ID"
_MAX_REQUEST_BYTES = 8192
_MAX_QUERY_CHARACTERS = 4096
_ROOT_ARGUMENTS = frozenset({"id"})
_DIRECTORY_ARGUMENTS = frozenset({"activeOnly", "limit", "offset"})
_DIRECTORY_FIELDS = frozenset(
    {"id", "displayName", "roleLabel", "active", "defaultLocation"}
)
_LOCATION_FIELDS = frozenset({"id", "name"})


async def _require_exact_directory_operation(request: Request) -> None:
    if request.method != "POST":
        raise ProductReadRequestDenied()
    content_type = request.headers.get("Content-Type", "").partition(";")[0]
    if content_type.strip().lower() != "application/json":
        raise ProductReadRequestDenied()
    raw_length = request.headers.get("Content-Length")
    if raw_length is not None:
        try:
            if int(raw_length) > _MAX_REQUEST_BYTES:
                raise ProductReadRequestDenied()
        except ValueError:
            raise ProductReadRequestDenied() from None
    body = await request.body()
    if not body or len(body) > _MAX_REQUEST_BYTES:
        raise ProductReadRequestDenied()
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProductReadRequestDenied() from None
    if not isinstance(payload, dict) or not set(payload) <= {
        "query",
        "variables",
        "operationName",
    }:
        raise ProductReadRequestDenied()
    query = payload.get("query")
    variables = payload.get("variables", {})
    if (
        not isinstance(query, str)
        or not query
        or len(query) > _MAX_QUERY_CHARACTERS
        or not isinstance(variables, dict)
        or not set(variables) <= {"practiceId", "activeOnly", "limit", "offset"}
    ):
        raise ProductReadRequestDenied()
    try:
        document = parse(query)
    except GraphQLError:
        raise ProductReadRequestDenied() from None
    if len(document.definitions) != 1:
        raise ProductReadRequestDenied()
    operation = document.definitions[0]
    if (
        not isinstance(operation, OperationDefinitionNode)
        or operation.operation.value != "query"
        or operation.directives
        or len(operation.selection_set.selections) != 1
    ):
        raise ProductReadRequestDenied()
    operation_name = payload.get("operationName")
    observed_name = operation.name.value if operation.name is not None else None
    if operation_name not in (None, observed_name):
        raise ProductReadRequestDenied()
    variable_names = {
        definition.variable.name.value
        for definition in (operation.variable_definitions or ())
    }
    if not variable_names <= {"practiceId", "activeOnly", "limit", "offset"}:
        raise ProductReadRequestDenied()

    practice = _require_field(
        operation.selection_set.selections[0],
        name="practice",
        allowed_arguments=_ROOT_ARGUMENTS,
    )
    if practice.selection_set is None or len(practice.selection_set.selections) != 1:
        raise ProductReadRequestDenied()
    directory = _require_field(
        practice.selection_set.selections[0],
        name="practitioners",
        allowed_arguments=_DIRECTORY_ARGUMENTS,
    )
    if directory.selection_set is None:
        raise ProductReadRequestDenied()
    fields = _require_unique_fields(
        directory.selection_set.selections,
        allowed=_DIRECTORY_FIELDS,
    )
    for field_name, field in fields.items():
        if field_name == "defaultLocation":
            if field.selection_set is None:
                raise ProductReadRequestDenied()
            location_fields = _require_unique_fields(
                field.selection_set.selections,
                allowed=_LOCATION_FIELDS,
            )
            if any(
                location_field.selection_set is not None
                for location_field in location_fields.values()
            ):
                raise ProductReadRequestDenied()
        elif field.selection_set is not None:
            raise ProductReadRequestDenied()


def _require_field(
    value: Any,
    *,
    name: str,
    allowed_arguments: frozenset[str],
) -> FieldNode:
    argument_names = (
        [argument.name.value for argument in value.arguments]
        if isinstance(value, FieldNode)
        else []
    )
    if (
        not isinstance(value, FieldNode)
        or value.name.value != name
        or value.alias is not None
        or value.directives
        or len(argument_names) != len(set(argument_names))
        or set(argument_names) - allowed_arguments
    ):
        raise ProductReadRequestDenied()
    return value


def _require_unique_fields(
    values: Any,
    *,
    allowed: frozenset[str],
) -> dict[str, FieldNode]:
    fields: dict[str, FieldNode] = {}
    for value in values:
        if not isinstance(value, FieldNode):
            raise ProductReadRequestDenied()
        field = _require_field(
            value,
            name=value.name.value,
            allowed_arguments=frozenset(),
        )
        name = field.name.value
        if name not in allowed or name in fields:
            raise ProductReadRequestDenied()
        fields[name] = field
    if not fields:
        raise ProductReadRequestDenied()
    return fields


def create_application_session_practitioner_directory_router(
    *,
    bridge: ApplicationSessionPractitionerDirectoryBridge,
    surface: Surface,
) -> GraphQLRouter:
    """Return an unmounted router bound to one server-selected surface."""

    async def context_getter(
        request: Request,
        response: Response,
    ) -> AsyncIterator[dict[str, object]]:
        try:
            await _require_exact_directory_operation(request)
            context = bridge.open_context(
                surface_session_value=(
                    request.cookies.get(SESSION_COOKIE_NAME) or ""
                ),
                csrf_cookie=request.cookies.get(CSRF_COOKIE_NAME),
                csrf_header=request.headers.get(CSRF_HEADER_NAME),
                surface=surface,
                origin=request.headers.get("Origin"),
                correlation_id=request.headers.get(CORRELATION_HEADER_NAME),
            )
        except ProductReadRequestDenied:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from None
        except ProductReadAuthenticationFailed:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from None
        except ProductReadUnavailable:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE
            ) from None

        response.headers["Cache-Control"] = "no-store"

        def authorize_practitioner_directory(
            *,
            active_only: bool,
            limit: int,
            offset: int,
        ) -> None:
            del limit, offset
            try:
                bridge.require_active_directory(
                    context,
                    active_only=active_only,
                )
            except ProductReadAuthorizationFailed:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN
                ) from None
            except ProductReadUnavailable:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE
                ) from None

        try:
            yield {
                "current_user": context.current_user,
                "db": context.db,
                "authorize_practitioner_directory": (
                    authorize_practitioner_directory
                ),
            }
        finally:
            context.db.close()

    return GraphQLRouter(
        schema,
        path="/api/v1/application-auth/product/graphql",
        context_getter=context_getter,
        graphql_ide=None,
        allow_queries_via_get=False,
        tags=["application-auth-product-read"],
    )


__all__ = [
    "CORRELATION_HEADER_NAME",
    "create_application_session_practitioner_directory_router",
]
