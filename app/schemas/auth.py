import uuid
from pydantic import BaseModel, Field, SecretStr


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: uuid.UUID
    account_id: uuid.UUID
    membership_id: uuid.UUID
    practice_id: uuid.UUID
    authority_generation: int
    role: str


class AccountBootstrapTokenData(BaseModel):
    account_id: uuid.UUID


class AccountRegistrationRequest(BaseModel):
    email: str = Field(min_length=1, max_length=255)
    password: SecretStr


class FirstPracticeRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class MembershipSelectionRequest(BaseModel):
    membership_id: uuid.UUID


class MembershipOut(BaseModel):
    membership_id: uuid.UUID
    practice_id: uuid.UUID
    practice_name: str
    role: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    practice_id: uuid.UUID

    model_config = {"from_attributes": True}
