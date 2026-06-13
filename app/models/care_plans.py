import uuid
import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Date, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.models.base import Base


class CarePlanType(str, enum.Enum):
    GPCCMP = "GPCCMP"
    MHTP = "MHTP"
    HealthAssessment45 = "HealthAssessment45"
    HealthAssessment75 = "HealthAssessment75"
    ATSI_HA = "ATSI_HA"
    Antenatal = "Antenatal"


class CarePlanStatus(str, enum.Enum):
    Draft = "Draft"
    Active = "Active"
    Review_Due = "Review_Due"
    Completed = "Completed"


class CarePlan(Base):
    __tablename__ = "care_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    encounter_id = Column(UUID(as_uuid=True), ForeignKey("encounters.id"), nullable=True)
    plan_type = Column(Enum(CarePlanType), nullable=False)
    mbs_item = Column(String(20))
    status = Column(Enum(CarePlanStatus), default=CarePlanStatus.Draft)
    valid_until = Column(Date)
    review_date = Column(Date)
    plan_data = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_care_plans_patient_id", "patient_id"),
        Index("ix_care_plans_practice_id", "practice_id"),
    )
