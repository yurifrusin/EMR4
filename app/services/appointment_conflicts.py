"""Appointment collision classification and transaction-local practice binding."""
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import event, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

APPOINTMENT_OVERLAP_CONSTRAINT = "ex_appointments_practice_practitioner_no_overlap"


def is_appointment_overlap_error(error: BaseException) -> bool:
    """Classify a database rejection by its typed code and exact owned constraint."""
    if not isinstance(error, IntegrityError):
        return False
    original = error.orig
    sqlstate = getattr(original, "sqlstate", None) or getattr(original, "pgcode", None)
    diagnostic = getattr(original, "diag", None)
    return (
        sqlstate == "23P01"
        and getattr(diagnostic, "constraint_name", None) == APPOINTMENT_OVERLAP_CONSTRAINT
    )


def set_appointment_practice_context(db: Session, practice_id: UUID) -> None:
    """Rebind authenticated practice before reads in a new transaction."""
    db.execute(
        text("SELECT set_config('app.current_practice_id', :practice_id, true)"),
        {"practice_id": str(UUID(str(practice_id)))},
    )


@contextmanager
def appointment_practice_transaction(db, practice_id):
    """Bind a fresh status transaction before its first table read.

    The listener belongs only to this session and is removed on every exit.
    SET LOCAL is a utility statement, so the physical transaction can still set
    its isolation level before issuing its first query. No caller-supplied SQL
    is interpolated: the literal is a parsed and canonically formatted UUID.
    """
    if not isinstance(db, Session):
        # Explicit synthetic transaction doubles have no SQLAlchemy events.
        yield
        return
    practice = str(UUID(str(practice_id)))
    if db.in_transaction():
        raise ValueError("Status confirmation requires a fresh transaction")

    def bind_practice(session, transaction, connection):
        connection.exec_driver_sql("SET LOCAL app.current_practice_id = '" + practice + "'")

    event.listen(db, "after_begin", bind_practice)
    try:
        yield
    finally:
        event.remove(db, "after_begin", bind_practice)
