from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime

from app.api.deps import get_current_user_payload
from app.db.session import get_session
from app.schemas.appointment_schema import AppointmentCreate, AppointmentPublic
from app.crud.appointment_crud import create_appointment
from app.models.appointment_model import Appointment, AppointmentStatus
from app.models.availability_model import DoctorAvailability

router = APIRouter()


def _map_py_weekday_to_spec(d: datetime) -> int:
    # Python: Monday=0..Sunday=6; Spec: Sunday=0..Saturday=6
    return (d.weekday() + 1) % 7


@router.post("/", response_model=AppointmentPublic, status_code=status.HTTP_201_CREATED)
async def create(
    payload: AppointmentCreate,
    db: AsyncSession = Depends(get_session),
    token_payload: dict = Depends(get_current_user_payload),
):
    # Basic sanity
    if payload.start_time >= payload.end_time:
        raise HTTPException(status_code=400, detail="start_time must be earlier than end_time")
    if payload.start_time.date() != payload.end_time.date():
        raise HTTPException(status_code=409, detail="Appointments must start and end on the same day")

    # Availability check
    dow = _map_py_weekday_to_spec(payload.start_time)
    start_t = payload.start_time.time()
    end_t = payload.end_time.time()

    res = await db.execute(
        select(DoctorAvailability).where(
            and_(
                DoctorAvailability.doctor_id == payload.doctor_id,
                DoctorAvailability.day_of_week == dow,
            )
        )
    )
    rules = list(res.scalars().all())

    within_any_rule = any((start_t >= r.start_time and end_t <= r.end_time) for r in rules)
    if not within_any_rule:
        raise HTTPException(
            status_code=409,
            detail="The requested time slot is outside the doctor's working hours.",
        )

    # Conflict check (exclude CANCELLED)
    overlap_q = select(Appointment).where(
        and_(
            Appointment.doctor_id == payload.doctor_id,
            Appointment.status != AppointmentStatus.CANCELLED,
            Appointment.start_time < payload.end_time,
            Appointment.end_time > payload.start_time,
        )
    )
    conflicts = (await db.execute(overlap_q)).scalars().first()
    if conflicts:
        raise HTTPException(
            status_code=409,
            detail="The requested time slot is already booked.",
        )

    # Passed checks -> create
    return await create_appointment(db, payload)
