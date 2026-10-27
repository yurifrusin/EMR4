"""Account credential truth and the first, single-role membership bridge.

Tables alone do not enable Account login or grant tenant authority. This schema
must ship with the separately reviewed authentication/bootstrap transition.
"""
import uuid

from sqlalchemy import (
    BigInteger, Boolean, CheckConstraint, Column, DateTime, ForeignKey,
    ForeignKeyConstraint, Index, String, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    normalized_email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "normalized_email <> '' AND normalized_email = lower(btrim(normalized_email))",
            name="ck_accounts_normalized_email",
        ),
    )


class PracticeMembership(Base):
    __tablename__ = "practice_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False)
    practice_id = Column(UUID(as_uuid=True), ForeignKey("practices.id"), nullable=False)
    legacy_user_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    authority_generation = Column(BigInteger, nullable=False, server_default="1")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("account_id", "practice_id", name="uq_membership_account_practice"),
        ForeignKeyConstraint(
            ["practice_id", "legacy_user_id"], ["users.practice_id", "users.id"],
            name="fk_membership_practice_user",
        ),
        CheckConstraint("authority_generation >= 1", name="ck_membership_generation_positive"),
        Index("ix_memberships_practice_id", "practice_id"),
    )


class PracticeMembershipRole(Base):
    """Exactly one explicit existing UserRole value in this first slice.

    Composite roles require a later reviewed schema/authorization transition.
    The legacy User.role remains the compatibility role on untouched routes.
    """
    __tablename__ = "practice_membership_roles"

    membership_id = Column(
        UUID(as_uuid=True), ForeignKey("practice_memberships.id"), primary_key=True,
    )
    role = Column(String(32), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "role IN ('GP', 'Receptionist', 'Nurse', 'Admin', 'PracticeOwner')",
            name="ck_membership_role_existing_user_role",
        ),
    )
