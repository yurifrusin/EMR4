"""Exact display-safe schemas for the Davida pure-read projection."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class ActivePracticeLocationOut(BaseModel):
    """Exact active-location projection row.

    Strict extra-forbid: this schema contains only ``id`` and a bounded
    ``name``. Address, phone, ``waiting_rooms``, the active flag, foreign or
    inactive rows, administrative metadata and the prototype SDL
    ``displayOrder`` (the model has no such column) are never modelled here.
    """

    model_config = ConfigDict(extra="forbid")

    id: uuid.UUID
    name: str = Field(min_length=1, max_length=255)
