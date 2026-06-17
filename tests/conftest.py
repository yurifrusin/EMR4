"""
Shared fixtures for EMR4 regression tests.

Prerequisites (run once against the local Postgres server):
    CREATE DATABASE gp_pms_test;
    \\c gp_pms_test
    CREATE EXTENSION IF NOT EXISTS vector;

The conftest handles schema creation/drop around the test session and
truncates practice-scoped data before every test so tests are isolated.
"""

import os
from datetime import date, time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.dependencies import get_db
from app.main import app
from app.models.appointments import AppointmentType, PractitionerSchedule
from app.models.base import Base
from app.models.patients import Patient
from app.models.tenancy import Practice, Practitioner, User, UserRole
from app.services.auth_service import create_access_token, hash_password

TEST_DB_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5434/gp_pms_test",
)


# ─── Engine (session-scoped: create tables once, drop at end) ─────────────────

@pytest.fixture(scope="session")
def engine():
    eng = create_engine(TEST_DB_URL)
    with eng.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


# ─── Clean slate before every test ────────────────────────────────────────────

@pytest.fixture(autouse=True)
def clean_db(engine):
    """Truncate all practice-scoped tables before each test."""
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE practices RESTART IDENTITY CASCADE"))


# ─── Per-test session ─────────────────────────────────────────────────────────

@pytest.fixture()
def db(engine):
    Session_ = sessionmaker(bind=engine)
    session = Session_()
    yield session
    session.close()


# ─── TestClient with get_db overridden to use our session ────────────────────

@pytest.fixture()
def client(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Data fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture()
def practice(db):
    p = Practice(name="Test Practice")
    db.add(p)
    db.flush()
    return p


@pytest.fixture()
def practice_b(db):
    p = Practice(name="Other Practice")
    db.add(p)
    db.flush()
    return p


@pytest.fixture()
def practitioner(db, practice):
    pr = Practitioner(
        practice_id=practice.id,
        first_name="Alex",
        last_name="Shera",
        ahpra_number="MED0001234567",
    )
    db.add(pr)
    db.flush()
    return pr


@pytest.fixture()
def gp_user(db, practice, practitioner):
    u = User(
        practice_id=practice.id,
        email="gp@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.GP,
        practitioner_id=practitioner.id,
    )
    db.add(u)
    db.flush()
    return u


@pytest.fixture()
def receptionist_user(db, practice):
    u = User(
        practice_id=practice.id,
        email="rec@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.Receptionist,
    )
    db.add(u)
    db.flush()
    return u


@pytest.fixture()
def gp_user_b(db, practice_b):
    u = User(
        practice_id=practice_b.id,
        email="gp_b@test.local",
        password_hash=hash_password("Password1!"),
        role=UserRole.GP,
    )
    db.add(u)
    db.flush()
    return u


@pytest.fixture()
def patient(db, practice):
    p = Patient(
        practice_id=practice.id,
        first_name="Margaret",
        last_name="Thompson",
        date_of_birth=date(1955, 3, 20),
    )
    db.add(p)
    db.flush()
    return p


@pytest.fixture()
def patient_b(db, practice_b):
    p = Patient(
        practice_id=practice_b.id,
        first_name="Billy",
        last_name="Other",
        date_of_birth=date(2015, 10, 15),
    )
    db.add(p)
    db.flush()
    return p


@pytest.fixture()
def appt_type(db, practice):
    t = AppointmentType(
        practice_id=practice.id,
        name="Standard",
        default_duration=15,
    )
    db.add(t)
    db.flush()
    return t


@pytest.fixture()
def schedule(db, practitioner):
    """Mon–Fri 09:00–17:00, 15-min slots for the test practitioner."""
    for dow in range(5):
        db.add(PractitionerSchedule(
            practitioner_id=practitioner.id,
            day_of_week=dow,
            start_time=time(9, 0),
            end_time=time(17, 0),
            slot_duration_minutes=15,
        ))
    db.flush()


# ─── Token helper ─────────────────────────────────────────────────────────────

def make_token(user) -> str:
    return create_access_token({
        "sub": str(user.id),
        "practice_id": str(user.practice_id),
        "role": user.role.value,
    })
