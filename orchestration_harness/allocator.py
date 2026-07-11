"""Pure, advisory-only Ariadne S4b worker allocation over supplied probes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .allocation import (
    AssignmentRecord,
    Availability,
    AvailabilityProbe,
    GeneralistProfile,
    Reachability,
    Role,
    RolePreference,
    WorkerResource,
)


@dataclass(frozen=True, slots=True)
class AllocationOutcome:
    assignments: tuple[AssignmentRecord, ...]
    unfilled_required_roles: tuple[Role, ...]


def _is_available(probe: AvailabilityProbe | None) -> bool:
    return probe is not None and (
        probe.reachability is Reachability.REACHABLE
        and probe.availability is Availability.AVAILABLE
    )


def allocate_roles(
    *,
    resources: Iterable[WorkerResource],
    preferences: Iterable[RolePreference],
    probes: Iterable[AvailabilityProbe],
    generalist: GeneralistProfile,
) -> AllocationOutcome:
    """Assign ranked roles from supplied observations, without any external action."""
    resource_by_id = {resource.resource_id: resource for resource in resources}
    probe_by_id = {probe.resource_id: probe for probe in probes}
    preference_by_role = {preference.role: preference for preference in preferences}
    assignments: list[AssignmentRecord] = []
    usage: dict[str, int] = {}
    unfilled: list[Role] = []

    for role, preference in preference_by_role.items():
        chosen: WorkerResource | None = None
        preferred_index = 0
        for index, resource_id in enumerate(preference.preferences):
            resource = resource_by_id.get(resource_id)
            if (
                resource is not None
                and role in resource.capabilities
                and _is_available(probe_by_id.get(resource_id))
                and usage.get(resource_id, 0) < resource.max_instances
            ):
                chosen = resource
                preferred_index = index
                break

        if chosen is None:
            generalist_resource = resource_by_id.get(generalist.resource_id)
            if (
                role in generalist.covers
                and generalist_resource is not None
                and _is_available(probe_by_id.get(generalist.resource_id))
            ):
                chosen = generalist_resource
                preferred_index = -1
            elif preference.required:
                unfilled.append(role)
                continue
            else:
                continue

        usage[chosen.resource_id] = usage.get(chosen.resource_id, 0) + 1
        fallback_reason = ""
        selection_basis = ["ranked_role_preference", "synthetic_available_probe"]
        independence_label = "declared_independent_resource"
        if preferred_index > 0:
            fallback_reason = "higher_ranked_preference_unavailable_or_ineligible"
            selection_basis.append("fallback")
        elif preferred_index == -1:
            fallback_reason = "generalist_fallback_required"
            selection_basis.extend(["generalist_fallback", "reduced_independence"])
            independence_label = generalist.independence

        assignments.append(
            AssignmentRecord(
                role=role,
                resource_id=chosen.resource_id,
                model=chosen.default_model,
                reasoning=chosen.default_reasoning,
                selection_basis=tuple(selection_basis),
                fallback_reason=fallback_reason,
                independence_label=independence_label,
                user_override_ref="",
                orchestrator_substituted=False,
                unfilled_obligations=(),
            )
        )

    unfilled_names = tuple(role.value for role in unfilled)
    if unfilled_names:
        assignments = [
            AssignmentRecord(
                role=assignment.role,
                resource_id=assignment.resource_id,
                model=assignment.model,
                reasoning=assignment.reasoning,
                selection_basis=assignment.selection_basis,
                fallback_reason=assignment.fallback_reason,
                independence_label=assignment.independence_label,
                user_override_ref=assignment.user_override_ref,
                orchestrator_substituted=False,
                unfilled_obligations=unfilled_names,
            )
            for assignment in assignments
        ]

    return AllocationOutcome(tuple(assignments), tuple(unfilled))
