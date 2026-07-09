import strawberry
from strawberry.extensions import MaxAliasesLimiter, MaxTokensLimiter, QueryDepthLimiter
from strawberry.types import Info


@strawberry.type
class GraphQLHealth:
    status: str
    service: str
    authenticated: bool


@strawberry.type
class Query:
    @strawberry.field
    def graphql_health(self, info: Info) -> GraphQLHealth:
        return GraphQLHealth(
            status="ok",
            service="emr4-graphql",
            authenticated=bool(info.context.get("current_user")),
        )


schema = strawberry.Schema(
    query=Query,
    extensions=[
        lambda: QueryDepthLimiter(max_depth=6),
        lambda: MaxAliasesLimiter(max_alias_count=500),
        lambda: MaxTokensLimiter(max_token_count=500),
    ],
)

