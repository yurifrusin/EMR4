import uuid
from sqlalchemy import (
    Column, Date, String, Boolean, Integer, Time, ForeignKey, Index, UniqueConstraint, text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.models.base import Base


class DiaryTemplate(Base):
    """Per-practice diary template: slot defaults and footer labels."""
    __tablename__ = "diary_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=True)
    practice_name = Column(String(255))
    slot_start = Column(Time, nullable=False)
    slot_end = Column(Time, nullable=False)
    slot_interval_minutes = Column(Integer, nullable=False, default=15)
    footer = Column(JSONB, default=list)

    columns = relationship("DiaryColumn", back_populates="template",
                           order_by="DiaryColumn.display_order",
                           cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_diary_templates_practice_id", "practice_id"),
        # One practice-wide template per practice (location_id NULL)
        Index("uq_diary_templates_practice_no_loc", "practice_id", unique=True,
              postgresql_where=text("location_id IS NULL")),
        # One template per (practice, location) when location is set
        Index("uq_diary_templates_practice_loc", "practice_id", "location_id", unique=True,
              postgresql_where=text("location_id IS NOT NULL")),
    )


class DiaryColumn(Base):
    """An ordered room/column in the diary (maps to a practitioner or a free-text role)."""
    __tablename__ = "diary_columns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("diary_templates.id"), nullable=False)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    display_order = Column(Integer, nullable=False)
    room_label = Column(String(100), nullable=False)
    assignment = Column(String(255))
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    practitioner_ahpra = Column(String(50), nullable=True)
    tint_hex = Column(String(7), nullable=True)
    is_active = Column(Boolean, default=True)
    slot_interval_minutes = Column(Integer, nullable=True)

    template = relationship("DiaryTemplate", back_populates="columns")
    breaks = relationship("DiaryBreak", back_populates="column",
                          order_by="DiaryBreak.display_order",
                          cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_diary_columns_template_id", "template_id"),
        Index("ix_diary_columns_practice_id", "practice_id"),
        UniqueConstraint("template_id", "display_order", name="uq_diary_columns_template_order"),
    )


class DiaryBreak(Base):
    """A labelled break block within a diary column."""
    __tablename__ = "diary_breaks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    column_id = Column(UUID(as_uuid=True), ForeignKey("diary_columns.id"), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    label = Column(String(100), nullable=False)
    from_time = Column(Time, nullable=False)
    to_time = Column(Time, nullable=False)

    column = relationship("DiaryColumn", back_populates="breaks")

    __table_args__ = (Index("ix_diary_breaks_column_id", "column_id"),)


class WaitingArea(Base):
    """Named physical waiting area within a practice (e.g. 'Main Waiting Room')."""
    __tablename__ = "waiting_areas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=True)
    name = Column(String(100), nullable=False)
    display_order = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        Index("ix_waiting_areas_practice_id", "practice_id"),
        Index("ix_waiting_areas_location_id", "location_id"),
    )


class Room(Base):
    """A physical room in the practice, used for date-specific diary roster assignment."""
    __tablename__ = "rooms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    location_id = Column(UUID(as_uuid=True), ForeignKey("practice_locations.id"), nullable=True)
    name = Column(String(100), nullable=False)
    display_order = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    default_waiting_area_id = Column(UUID(as_uuid=True), ForeignKey("waiting_areas.id"), nullable=True)

    roster_entries = relationship("DiaryRoster", back_populates="room",
                                  cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_rooms_practice_id", "practice_id"),
        Index("ix_rooms_location_id", "location_id"),
        UniqueConstraint("practice_id", "display_order", name="uq_rooms_practice_order"),
    )


class DiaryRoster(Base):
    """Date-specific room assignment: maps (practice, room, date) → practitioner or label."""
    __tablename__ = "diary_roster"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    room_id = Column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    roster_date = Column(Date, nullable=False)
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("practitioners.id"), nullable=True)
    practitioner_ahpra = Column(String(50), nullable=True)
    label = Column(String(255), nullable=True)

    room = relationship("Room", back_populates="roster_entries")

    __table_args__ = (
        Index("ix_diary_roster_practice_date", "practice_id", "roster_date"),
        UniqueConstraint("practice_id", "room_id", "roster_date",
                         name="uq_diary_roster_practice_room_date"),
    )
