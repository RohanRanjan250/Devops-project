from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Status = Literal["BOOKED", "CHECKED_IN", "COMPLETED", "CANCELLED"]


class DoctorCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    specialty: str = Field(min_length=2, max_length=80)
    room: str = Field(default="", max_length=20)


class DoctorOut(DoctorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AppointmentCreate(BaseModel):
    patient_name: str = Field(min_length=2, max_length=120)
    patient_phone: str = Field(pattern=r"^\+?[0-9 ]{7,15}$")
    doctor_id: int
    scheduled_at: datetime
    reason: str = Field(default="", max_length=500)


class AppointmentUpdate(BaseModel):
    patient_name: str | None = Field(default=None, min_length=2, max_length=120)
    patient_phone: str | None = Field(default=None, pattern=r"^\+?[0-9 ]{7,15}$")
    scheduled_at: datetime | None = None
    reason: str | None = Field(default=None, max_length=500)
    status: Status | None = None


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    patient_name: str
    patient_phone: str
    doctor_id: int
    doctor_name: str
    specialty: str
    scheduled_at: datetime
    reason: str
    status: Status
    created_at: datetime


class StatsOut(BaseModel):
    total: int
    booked: int
    checkedIn: int
    completed: int
    cancelled: int
    doctors: int
