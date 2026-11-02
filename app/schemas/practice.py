import uuid
from typing import Optional

from pydantic import BaseModel


class PractitionerDefaultLocationOut(BaseModel):
    id: uuid.UUID
    name: str


class PractitionerOut(BaseModel):
    id: uuid.UUID
    displayName: str
    roleLabel: Optional[str] = None
    active: bool
    defaultLocation: Optional[PractitionerDefaultLocationOut] = None

class PracticeContextOut(BaseModel):
    practice_id: uuid.UUID
    timezone: str