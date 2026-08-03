"""Deterministic minimal context desk for the Davida pure-read tranche.

The composer is a pure, provider-free function outside any probabilistic cell.
It has no SQLAlchemy, model, database, network or provider import and never
reads a clock: ``observed_at`` is always caller-supplied and timezone-aware.
The ``datetime`` module is used only as a value type and for fixed two-minute
expiry arithmetic, never to obtain the current time. The composer receives
caller-supplied already-authorized exact ``list[PractitionerOut]`` and active
locations, bounded authored-synthetic practice/principal refs, a correlation
ID, a timezone-aware observed time and an immutable bounded backend
resource-reference registry, then returns one strict
``emr4.davida.practice_administration_context.v1`` frame that emits no internal
UUID. Database truth remains authoritative; context frames are minimal and
non-authoritative.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from types import MappingProxyType
from typing import Any, Iterable, Literal, Mapping

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.practice import PractitionerOut
from app.schemas.practice_administration import ActivePracticeLocationOut


SCHEMA_VERSION = "emr4.davida.practice_administration_context.v1"
DATA_CLASS = "authored_synthetic"
OBSERVED_EXPIRY_INTERVAL = timedelta(minutes=2)
MAX_FRAME_ROWS = 200

PRACTITIONER_SOURCE = (
    "app.services.practice.practitioner_directory_read.list_practitioner_directory"
)
LOCATION_SOURCE = (
    "app.services.practice.active_location_directory_read.list_active_location_directory"
)

_REF_PATTERN = re.compile(r"^[A-Za-z0-9._~-]{1,64}$")
_CORRELATION_PATTERN = re.compile(r"^correlation-[A-Za-z0-9._~-]{1,64}$")
_OPAQUE_PATTERN = re.compile(r"^[A-Za-z0-9._~-]{8,64}$")

RESOURCE_KINDS = frozenset({"practitioner", "location"})

BLOCKED_SOURCES = (
    {
        "name": "diary_rooms",
        "path": "GET /api/v1/diary/rooms",
        "reason": "normalizes_and_commits_during_nominal_read",
    },
    {
        "name": "diary_waiting_areas",
        "path": "GET /api/v1/diary/waiting-areas",
        "reason": "normalizes_and_commits_during_nominal_read",
    },
    {
        "name": "appointment_waiting_room_queue",
        "path": "GET /api/v1/appointments/waiting-room",
        "reason": "patient_linked_appointment_queue_closed_data",
    },
)

AUTHORITY_CEILING = {
    "command": False,
    "confirmation": False,
    "write": False,
    "proposal_apply": False,
    "provider": False,
    "event_actuator": False,
    "model_to_database": False,
}

FRAME_LABELS = {
    "minimal": True,
    "non_authoritative": True,
    "database_truth_authoritative": True,
}


@dataclass(frozen=True)
class ResourceReferenceBinding:
    """One backend-owned opaque reference for one internal resource UUID."""

    kind: str
    resource_id: uuid.UUID
    reference: str
    practice_ref: str

    def __post_init__(self) -> None:
        if self.kind not in RESOURCE_KINDS:
            raise ValueError("unsupported resource-reference kind")
        if not isinstance(self.resource_id, uuid.UUID):
            raise ValueError("resource-reference id must be a UUID")
        if not _OPAQUE_PATTERN.fullmatch(self.reference):
            raise ValueError("resource reference outside bounded opaque pattern")
        if not _REF_PATTERN.fullmatch(self.practice_ref):
            raise ValueError("practice reference outside bounded pattern")


@dataclass(frozen=True)
class ResourceReferenceRegistry:
    """Immutable bounded backend resource-reference registry.

    Maps each internal UUID to one opaque synthetic reference within one
    practice scope. Missing, duplicate, wrong-kind and cross-practice bindings
    all fail closed at construction or ``resolve`` time.
    """

    _by_id: Mapping[uuid.UUID, ResourceReferenceBinding] = field(
        default_factory=dict
    )

    @classmethod
    def build(
        cls,
        bindings: Iterable[ResourceReferenceBinding],
        *,
        max_entries: int = 500,
    ) -> "ResourceReferenceRegistry":
        materialized = tuple(bindings)
        if len(materialized) > max_entries:
            raise ValueError(
                "resource-reference registry exceeds bounded maximum"
            )
        by_id: dict[uuid.UUID, ResourceReferenceBinding] = {}
        seen_references: set[str] = set()
        for binding in materialized:
            if binding.resource_id in by_id:
                raise ValueError("duplicate resource-id binding")
            if binding.reference in seen_references:
                raise ValueError("duplicate opaque resource reference")
            by_id[binding.resource_id] = binding
            seen_references.add(binding.reference)
        return cls(_by_id=MappingProxyType(by_id))

    def resolve(
        self,
        *,
        kind: str,
        resource_id: uuid.UUID,
        practice_ref: str,
    ) -> str:
        binding = self._by_id.get(resource_id)
        if binding is None:
            raise ValueError("missing resource-reference binding")
        if binding.kind != kind:
            raise ValueError("wrong-kind resource-reference binding")
        if binding.practice_ref != practice_ref:
            raise ValueError("cross-practice resource-reference binding")
        return binding.reference


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _PractitionerRow(_StrictModel):
    resource_ref: str = Field(
        min_length=8, max_length=64, pattern=_OPAQUE_PATTERN.pattern
    )
    display_name: str = Field(min_length=1, max_length=255)
    role_label: str | None = Field(default=None, max_length=255)
    active: Literal[True]
    default_location_ref: str | None = Field(
        default=None, min_length=8, max_length=64, pattern=_OPAQUE_PATTERN.pattern
    )


class _PractitionerFrame(_StrictModel):
    label: Literal["live_api_fact"]
    source: Literal[
        "app.services.practice.practitioner_directory_read."
        "list_practitioner_directory"
    ]
    projection: Literal["pure"]
    active_only: Literal[True]
    count: int = Field(ge=0, le=200)
    rows: list[_PractitionerRow] = Field(max_length=200)


class _LocationRow(_StrictModel):
    resource_ref: str = Field(
        min_length=8, max_length=64, pattern=_OPAQUE_PATTERN.pattern
    )
    name: str = Field(min_length=1, max_length=255)


class _LocationFrame(_StrictModel):
    label: Literal["live_api_fact"]
    source: Literal[
        "app.services.practice.active_location_directory_read."
        "list_active_location_directory"
    ]
    projection: Literal["pure"]
    active_only: Literal[True]
    count: int = Field(ge=0, le=200)
    rows: list[_LocationRow] = Field(max_length=200)


class _Frames(_StrictModel):
    practitioners: _PractitionerFrame
    locations: _LocationFrame


class _BlockedSource(_StrictModel):
    name: str
    path: str
    reason: str


class _AuthorityCeiling(_StrictModel):
    command: Literal[False]
    confirmation: Literal[False]
    write: Literal[False]
    proposal_apply: Literal[False]
    provider: Literal[False]
    event_actuator: Literal[False]
    model_to_database: Literal[False]


class _Labels(_StrictModel):
    minimal: Literal[True]
    non_authoritative: Literal[True]
    database_truth_authoritative: Literal[True]


class PracticeAdministrationContextFrame(_StrictModel):
    schema_version: Literal["emr4.davida.practice_administration_context.v1"]
    data_class: Literal["authored_synthetic"]
    practice_ref: str = Field(
        min_length=1, max_length=64, pattern=_REF_PATTERN.pattern
    )
    principal_ref: str = Field(
        min_length=1, max_length=64, pattern=_REF_PATTERN.pattern
    )
    correlation_id: str = Field(
        min_length=1, max_length=100, pattern=_CORRELATION_PATTERN.pattern
    )
    observed_at: datetime
    expires_at: datetime
    content_revision: str = ""
    frames: _Frames
    blocked_sources: list[_BlockedSource]
    authority_ceiling: _AuthorityCeiling
    labels: _Labels


def compose_practice_administration_context(
    *,
    practitioners: list[PractitionerOut],
    active_locations: list[ActivePracticeLocationOut],
    practice_ref: str,
    principal_ref: str,
    correlation_id: str,
    observed_at: datetime,
    resource_references: ResourceReferenceRegistry,
) -> dict[str, Any]:
    """Compose one strict deterministic minimal context frame.

    Fail-closed rules: a naive ``observed_at``, unsupported reference or
    correlation values, unknown fields, over-bounded frames, and
    missing/duplicate/wrong-kind/cross-practice resource bindings are all
    rejected. Every internal UUID (including default-location IDs) is replaced
    with a registered opaque synthetic reference, so the returned frame emits no
    UUID. Fixed inputs produce identical frames and an identical SHA-256 content
    revision.
    """
    if observed_at.tzinfo is None:
        raise ValueError("observed_at must be timezone-aware")
    if not _REF_PATTERN.fullmatch(practice_ref):
        raise ValueError("practice_ref outside bounded pattern")
    if not _REF_PATTERN.fullmatch(principal_ref):
        raise ValueError("principal_ref outside bounded pattern")
    if not _CORRELATION_PATTERN.fullmatch(correlation_id):
        raise ValueError("correlation_id outside bounded pattern")

    practitioner_rows: list[dict[str, Any]] = []
    for practitioner in practitioners:
        resource_ref = resource_references.resolve(
            kind="practitioner",
            resource_id=practitioner.id,
            practice_ref=practice_ref,
        )
        if not practitioner.active:
            raise ValueError("inactive practitioner in active-only frame")
        default_location_ref = None
        if practitioner.defaultLocation is not None:
            default_location_ref = resource_references.resolve(
                kind="location",
                resource_id=practitioner.defaultLocation.id,
                practice_ref=practice_ref,
            )
        practitioner_rows.append(
            {
                "resource_ref": resource_ref,
                "display_name": practitioner.displayName,
                "role_label": practitioner.roleLabel,
                "active": practitioner.active,
                "default_location_ref": default_location_ref,
            }
        )
    if len(practitioner_rows) > MAX_FRAME_ROWS:
        raise ValueError("practitioner frame exceeds bounded maximum")

    location_rows: list[dict[str, Any]] = []
    for location in active_locations:
        resource_ref = resource_references.resolve(
            kind="location",
            resource_id=location.id,
            practice_ref=practice_ref,
        )
        location_rows.append(
            {
                "resource_ref": resource_ref,
                "name": location.name,
            }
        )
    if len(location_rows) > MAX_FRAME_ROWS:
        raise ValueError("location frame exceeds bounded maximum")

    expires_at = observed_at + OBSERVED_EXPIRY_INTERVAL

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "data_class": DATA_CLASS,
        "practice_ref": practice_ref,
        "principal_ref": principal_ref,
        "correlation_id": correlation_id,
        "observed_at": observed_at,
        "expires_at": expires_at,
        "frames": {
            "practitioners": {
                "label": "live_api_fact",
                "source": PRACTITIONER_SOURCE,
                "projection": "pure",
                "active_only": True,
                "count": len(practitioner_rows),
                "rows": practitioner_rows,
            },
            "locations": {
                "label": "live_api_fact",
                "source": LOCATION_SOURCE,
                "projection": "pure",
                "active_only": True,
                "count": len(location_rows),
                "rows": location_rows,
            },
        },
        "blocked_sources": list(BLOCKED_SOURCES),
        "authority_ceiling": dict(AUTHORITY_CEILING),
        "labels": dict(FRAME_LABELS),
    }

    provisional_json = PracticeAdministrationContextFrame(
        **payload
    ).model_dump(mode="json")
    provisional_json.pop("content_revision", None)
    canonical = json.dumps(
        provisional_json,
        sort_keys=True,
        separators=(",", ":"),
    )
    content_revision = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    final = PracticeAdministrationContextFrame(
        **payload,
        content_revision=content_revision,
    )
    return final.model_dump(mode="json")


__all__ = [
    "AUTHORITY_CEILING",
    "BLOCKED_SOURCES",
    "DATA_CLASS",
    "FRAME_LABELS",
    "LOCATION_SOURCE",
    "MAX_FRAME_ROWS",
    "OBSERVED_EXPIRY_INTERVAL",
    "PRACTITIONER_SOURCE",
    "PracticeAdministrationContextFrame",
    "ResourceReferenceBinding",
    "ResourceReferenceRegistry",
    "SCHEMA_VERSION",
    "compose_practice_administration_context",
]
