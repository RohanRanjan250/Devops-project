"""Test setup: every test gets a fresh, isolated SQLite database.

The production PostgreSQL is never touched - `get_db` is overridden to use a
throwaway in-memory SQLite engine, and the schema is created from the models.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import Doctor


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    session.add_all(
        [
            Doctor(name="Dr. Test Physician", specialty="General Medicine", room="1"),
            Doctor(name="Dr. Test Cardiologist", specialty="Cardiology", room="2"),
        ]
    )
    session.commit()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def booking():
    return {
        "patient_name": "Rohan Ranjan",
        "patient_phone": "+91 98765 43210",
        "doctor_id": 1,
        "scheduled_at": "2026-11-02T10:30:00+05:30",
        "reason": "Annual check-up",
    }
