import strawberry
from fastapi import HTTPException, status
from strawberry.extensions import MaxAliasesLimiter, MaxTokensLimiter, QueryDepthLimiter
from strawberry.exceptions import StrawberryGraphQLError
from strawberry.types import Info

from app.services.practice.practitioner_directory_read import list_practitioner_directory


def _bad_user_input(message: str) -> StrawberryGraphQLError:
    return StrawberryGraphQLError(message, extensions={"code": "BAD_USER_INPUT"})


@strawberry.type
class GraphQLHealth:
    status: str
    service: str
    authenticated: bool


@strawberry.type
class PracticeLocationBrief:
    id: strawberry.ID
    name: str


@strawberry.type
class Practitioner:
    id: strawberry.ID
    display_name: str
    role_label: str | None
    active: bool
    default_location: PracticeLocationBrief | None


@strawberry.type(name="Practice")
class PracticeGraphQL:
    id: strawberry.ID

    @strawberry.field
    def practitioners(
        self,
        info: Info,
        active_only: bool | None = True,
        limit: int | None = 50,
        offset: int | None = 0,
    ) -> list[Practitioner]:
        if active_only is None:
            raise _bad_user_input("activeOnly must be true or false")
        if limit is None:
            raise _bad_user_input("limit must be between 1 and 200")
        if offset is None:
            raise _bad_user_input("offset must be greater than or equal to 0")
        if limit < 1 or limit > 200:
            raise _bad_user_input("limit must be between 1 and 200")
        if offset < 0:
            raise _bad_user_input("offset must be greater than or equal to 0")

        try:
            rows = list_practitioner_directory(
                db=info.context["db"],
                current_user=info.context["current_user"],
                active_only=active_only,
                limit=limit,
                offset=offset,
            )
        except HTTPException as exc:
            if exc.status_code == status.HTTP_403_FORBIDDEN:
                raise StrawberryGraphQLError(
                    "Forbidden",
                    extensions={"code": "FORBIDDEN"},
                ) from exc
            raise
        except Exception as exc:
            raise StrawberryGraphQLError(
                "Internal error",
                extensions={"code": "INTERNAL_ERROR"},
            ) from exc

        return [
            Practitioner(
                id=strawberry.ID(str(row.id)),
                display_name=row.displayName,
                role_label=row.roleLabel,
                active=row.active,
                default_location=(
                    PracticeLocationBrief(
                        id=strawberry.ID(str(row.defaultLocation.id)),
                        name=row.defaultLocation.name,
                    )
                    if row.defaultLocation is not None
                    else None
                ),
            )
            for row in rows
        ]


@strawberry.type
class Query:
    @strawberry.field
    def graphql_health(self, info: Info) -> GraphQLHealth:
        return GraphQLHealth(
            status="ok",
            service="emr4-graphql",
            authenticated=bool(info.context.get("current_user")),
        )

    @strawberry.field
    def practice(self, info: Info, id: strawberry.ID | None = None) -> PracticeGraphQL | None:
        viewer_practice_id = str(info.context["current_user"].practice_id)
        if id is not None and str(id) != viewer_practice_id:
            return None
        return PracticeGraphQL(id=strawberry.ID(viewer_practice_id))


schema = strawberry.Schema(
    query=Query,
    extensions=[
        lambda: QueryDepthLimiter(max_depth=6),
        lambda: MaxAliasesLimiter(max_alias_count=500),
        lambda: MaxTokensLimiter(max_token_count=500),
    ],
)
