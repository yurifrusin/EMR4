from strawberry.fastapi import GraphQLRouter

from app.graphql.context import get_graphql_context
from app.graphql.schema import schema


graphql_router = GraphQLRouter(
    schema,
    path="/api/v1/graphql",
    context_getter=get_graphql_context,
    graphql_ide=None,
    tags=["graphql"],
)

