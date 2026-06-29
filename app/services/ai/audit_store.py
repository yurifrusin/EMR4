"""Persistence helpers for typed Access AI audit events."""
from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.models.ai_audit import AccessAiAuditLog
from app.services.ai.audit_events import AccessAiAuditEvent


def persist_access_ai_audit_events(
    db: Session,
    events: Iterable[AccessAiAuditEvent],
) -> tuple[AccessAiAuditLog, ...]:
    rows: list[AccessAiAuditLog] = []
    for event in events:
        row = AccessAiAuditLog(
            event_id=event.event_id,
            practice_id=event.practice_id,
            actor_user_id=event.actor_user_id,
            event_type=event.event_type.value,
            capability=event.capability.value if event.capability else None,
            method=event.method.value if event.method else None,
            decision=event.decision.value,
            reason_code=event.reason_code,
            source_surface=event.source_surface.value,
            target_resource_type=event.target_resource_type,
            target_resource_id=(
                str(event.target_resource_id)
                if event.target_resource_id is not None
                else None
            ),
            correlation_id=event.correlation_id,
            actor_roles=list(event.actor_roles),
            metadata_json=dict(event.metadata),
            event_timestamp=event.timestamp,
        )
        db.add(row)
        rows.append(row)
    db.flush()
    return tuple(rows)
