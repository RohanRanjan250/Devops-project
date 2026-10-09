from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    specialty: Mapped[str] = mapped_column(String(80), nullable=False)
    room: Mapped[str] = mapped_column(String(20), nullable=False, default="")

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="doctor")


class Appointment(Base):
    __tablename__ = "appointments"
    # one doctor cannot have two appointments in the same slot
    __table_args__ = (UniqueConstraint("doctor_id", "scheduled_at", name="uq_doctor_slot"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_name: Mapped[str] = mapped_column(String(120), nullable=False)
    patient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="BOOKED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    doctor: Mapped[Doctor] = relationship(back_populates="appointments")
