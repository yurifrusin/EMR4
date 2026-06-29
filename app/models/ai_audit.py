import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from app.models.base import Base


class AccessAiAuditLog(Base):
    __tablename__ = "access_ai_audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=True)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    event_type = Column(String(100), nullable=False)
    capability = Column(String(100), nullable=True)
    method = Column(String(50), nullable=True)
    decision = Column(String(50), nullable=False)
    reason_code = Column(String(100), nullable=True)
    source_surface = Column(String(50), nullable=False)
    target_resource_type = Column(String(100), nullable=True)
    target_resource_id = Column(String(100), nullable=True)
    correlation_id = Column(UUID(as_uuid=True), nullable=False)
    actor_roles = Column(JSONB, nullable=True)
    metadata_json = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    event_timestamp = Column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("ix_access_ai_audit_log_practice_created", "practice_id", "created_at"),
        Index("ix_access_ai_audit_log_correlation_id", "correlation_id"),
        Index("ix_access_ai_audit_log_event_type", "event_type"),
    )
