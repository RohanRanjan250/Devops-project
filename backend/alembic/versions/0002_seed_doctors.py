"""seed the clinic's doctors

Revision ID: 0002_seed_doctors
Revises: 0001_doctors_appointments
Create Date: 2026-10-09
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_seed_doctors"
down_revision = "0001_doctors_appointments"
branch_labels = None
depends_on = None

doctors = sa.table(
    "doctors",
    sa.column("name", sa.String),
    sa.column("specialty", sa.String),
    sa.column("room", sa.String),
)


def upgrade() -> None:
    op.bulk_insert(
        doctors,
        [
            {"name": "Dr. Ananya Sharma", "specialty": "General Medicine", "room": "101"},
            {"name": "Dr. Vikram Mehta", "specialty": "Cardiology", "room": "204"},
            {"name": "Dr. Priya Nair", "specialty": "Pediatrics", "room": "108"},
            {"name": "Dr. Arjun Rao", "specialty": "Orthopedics", "room": "310"},
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM doctors")
