from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models.tenancy import User


def get_graphql_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return {
        "current_user": current_user,
        "db": db,
    }

