"""Add the narrow application-auth token bootstrap function.

Revision ID: p5q6r7s8t9u0
Revises: o4p5q6r7s8t9
Create Date: 2026-08-01
"""

from typing import Sequence, Union

from alembic import op


revision: str = "p5q6r7s8t9u0"
down_revision: Union[str, Sequence[str], None] = "o4p5q6r7s8t9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_RESOLVER = "public.emr4_resolve_application_auth_principal(text, text)"


def upgrade() -> None:
    op.execute(
        r"""
        CREATE FUNCTION public.emr4_resolve_application_auth_principal(
          reference_kind text,
          reference_hash text
        )
        RETURNS TABLE(user_ref text, practice_ref text)
        LANGUAGE plpgsql
        SECURITY DEFINER
        STABLE
        PARALLEL UNSAFE
        ROWS 1
        SET search_path = ''
        AS $$
        BEGIN
          IF reference_kind NOT IN ('parent', 'surface', 'exchange')
             OR reference_hash !~ '^sha256:[0-9a-f]{64}$' THEN
            RETURN;
          END IF;

          IF reference_kind = 'parent' THEN
            RETURN QUERY
              SELECT parent.user_ref::text, parent.practice_ref::text
              FROM public.application_auth_parent_sessions AS parent
              WHERE parent.session_reference_hash = reference_hash
              LIMIT 1;
          ELSIF reference_kind = 'surface' THEN
            RETURN QUERY
              SELECT parent.user_ref::text, parent.practice_ref::text
              FROM public.application_auth_surface_sessions AS surface_session
              JOIN public.application_auth_parent_sessions AS parent
                ON parent.practice_ref = surface_session.practice_ref
               AND parent.session_reference_hash =
                   surface_session.parent_session_reference_hash
              WHERE surface_session.surface_reference_hash = reference_hash
              LIMIT 1;
          ELSE
            RETURN QUERY
              SELECT parent.user_ref::text, parent.practice_ref::text
              FROM public.application_auth_exchange_grants AS exchange_grant
              JOIN public.application_auth_parent_sessions AS parent
                ON parent.practice_ref = exchange_grant.practice_ref
               AND parent.session_reference_hash =
                   exchange_grant.parent_session_reference_hash
              WHERE exchange_grant.grant_reference_hash = reference_hash
              LIMIT 1;
          END IF;
        END;
        $$
        """
    )
    op.execute(f"REVOKE ALL ON FUNCTION {_RESOLVER} FROM PUBLIC")


def downgrade() -> None:
    op.execute(f"DROP FUNCTION IF EXISTS {_RESOLVER}")
