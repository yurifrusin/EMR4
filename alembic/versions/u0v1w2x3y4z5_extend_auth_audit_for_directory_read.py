"""Extend application-auth audit for the practitioner-directory read.

Revision ID: u0v1w2x3y4z5
Revises: t9u0v1w2x3y4
Create Date: 2026-08-02
"""

from typing import Sequence, Union

from alembic import op


revision: str = "u0v1w2x3y4z5"
down_revision: Union[str, Sequence[str], None] = "t9u0v1w2x3y4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_TABLE = "application_auth_audit_events"
_PRIOR_EVENTS = (
    "'auth.session_created', 'auth.session_refreshed', "
    "'auth.session_revoked', 'auth.surface_bound', "
    "'auth.exchange_issued', 'auth.exchange_redeemed', "
    "'auth.exchange_rejected', 'auth.authorization_denied'"
)
_CURRENT_EVENTS = _PRIOR_EVENTS + ", 'auth.authorization_allowed'"
_PRIOR_POLICY = "policy_version = 'clinician-workspace-read.v1'"
_CURRENT_POLICY = (
    "policy_version IN ('clinician-workspace-read.v1', "
    "'practice-practitioner-directory-read.v1')"
)


def _replace_constraints(*, event_expression: str, policy_expression: str) -> None:
    op.drop_constraint(
        "ck_app_auth_audit_event_type",
        _TABLE,
        type_="check",
    )
    op.drop_constraint(
        "ck_app_auth_audit_policy",
        _TABLE,
        type_="check",
    )
    op.create_check_constraint(
        "ck_app_auth_audit_event_type",
        _TABLE,
        f"event_type IN ({event_expression})",
    )
    op.create_check_constraint(
        "ck_app_auth_audit_policy",
        _TABLE,
        policy_expression,
    )


def upgrade() -> None:
    _replace_constraints(
        event_expression=_CURRENT_EVENTS,
        policy_expression=_CURRENT_POLICY,
    )


def downgrade() -> None:
    _replace_constraints(
        event_expression=_PRIOR_EVENTS,
        policy_expression=_PRIOR_POLICY,
    )
