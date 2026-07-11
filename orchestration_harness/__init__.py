"""Portable, advisory-only core for the Ariadne orchestration harness."""

from .models import ActionClassification, BoundaryClass, Evidence, Mandate
from .allocation import (
    AssignmentRecord,
    Availability,
    AvailabilityProbe,
    ConductorPlan,
    GeneralistProfile,
    Reachability,
    Role,
    RolePreference,
    Transport,
    UserOverride,
    VerifierDecision,
    VerifierResult,
    WorkerResource,
)
from .allocator import AllocationOutcome, allocate_roles

__all__ = [
    "ActionClassification", "AllocationOutcome", "AssignmentRecord", "Availability", "AvailabilityProbe",
    "BoundaryClass", "ConductorPlan", "Evidence", "GeneralistProfile", "Mandate",
    "Reachability", "Role", "RolePreference", "Transport", "UserOverride",
    "VerifierDecision", "VerifierResult", "WorkerResource", "allocate_roles",
]
