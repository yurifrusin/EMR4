import uuid
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: uuid.UUID
    practice_id: uuid.UUID
    role: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    practice_id: uuid.UUID

    model_config = {"from_attributes": True}
