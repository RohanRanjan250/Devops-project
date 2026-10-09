from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .config import settings
from .db import get_db
from .models import Appointment, Doctor
from .schemas import (
    AppointmentCreate,
    AppointmentOut,
    AppointmentUpdate,
    DoctorCreate,
    DoctorOut,
    StatsOut,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Schema is owned by Alembic (`alembic upgrade head` runs before uvicorn in the container).
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# business metric: what the clinic is actually doing, not just HTTP traffic
APPOINTMENT_EVENTS = Counter(
    "clinicflow_appointments_total",
    "Appointment lifecycle events",
    ["event", "specialty"],
)


def to_out(a: Appointment) -> AppointmentOut:
    return AppointmentOut(
        id=a.id,
        patient_name=a.patient_name,
        patient_phone=a.patient_phone,
        doctor_id=a.doctor_id,
        doctor_name=a.doctor.name,
        specialty=a.doctor.specialty,
        scheduled_at=a.scheduled_at,
        reason=a.reason,
        status=a.status,
        created_at=a.created_at,
    )


def get_appointment(db: Session, appointment_id: int) -> Appointment:
    appt = db.get(Appointment, appointment_id, options=[joinedload(Appointment.doctor)])
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appt


def commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        APPOINTMENT_EVENTS.labels(event="rejected_double_booking", specialty="any").inc()
        raise HTTPException(status_code=409, detail="Doctor already has an appointment in this slot")


@app.get("/")
def root():
    return {"service": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "UP"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(select(func.count(Doctor.id)))
    return {"status": "READY"}


# ---------- doctors ----------

@app.get("/api/doctors", response_model=list[DoctorOut])
def list_doctors(db: Session = Depends(get_db)):
    return list(db.scalars(select(Doctor).order_by(Doctor.name)))


@app.post("/api/doctors", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def create_doctor(payload: DoctorCreate, db: Session = Depends(get_db)):
    doctor = Doctor(**payload.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


# ---------- appointments ----------

@app.get("/api/appointments", response_model=list[AppointmentOut])
def list_appointments(status_filter: str | None = None, db: Session = Depends(get_db)):
    query = select(Appointment).options(joinedload(Appointment.doctor)).order_by(Appointment.scheduled_at)
    if status_filter:
        query = query.where(Appointment.status == status_filter.upper())
    return [to_out(a) for a in db.scalars(query)]


@app.get("/api/appointments/stats", response_model=StatsOut)
def appointment_stats(db: Session = Depends(get_db)):
    rows = db.execute(select(Appointment.status, func.count(Appointment.id)).group_by(Appointment.status)).all()
    counts = {s: c for s, c in rows}
    return StatsOut(
        total=sum(counts.values()),
        booked=counts.get("BOOKED", 0),
        checkedIn=counts.get("CHECKED_IN", 0),
        completed=counts.get("COMPLETED", 0),
        cancelled=counts.get("CANCELLED", 0),
        doctors=db.scalar(select(func.count(Doctor.id))) or 0,
    )


@app.get("/api/appointments/{appointment_id}", response_model=AppointmentOut)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    return to_out(get_appointment(db, appointment_id))


@app.post("/api/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def book_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    if not db.get(Doctor, payload.doctor_id):
        raise HTTPException(status_code=404, detail="Doctor not found")
    appt = Appointment(**payload.model_dump())
    db.add(appt)
    commit_or_conflict(db)
    booked = get_appointment(db, appt.id)
    APPOINTMENT_EVENTS.labels(event="booked", specialty=booked.doctor.specialty).inc()
    return to_out(booked)


@app.put("/api/appointments/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, payload: AppointmentUpdate, db: Session = Depends(get_db)):
    appt = get_appointment(db, appointment_id)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(appt, key, value)
    commit_or_conflict(db)
    updated = get_appointment(db, appointment_id)
    if "status" in changes:
        APPOINTMENT_EVENTS.labels(event=changes["status"].lower(), specialty=updated.doctor.specialty).inc()
    return to_out(updated)


@app.delete("/api/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db.delete(get_appointment(db, appointment_id))
    db.commit()
