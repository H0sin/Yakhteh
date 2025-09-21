import uuid
from typing import Iterable, List
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.availability_model import DoctorAvailability
from app.schemas.availability_schema import AvailabilityRule


async def replace_doctor_availability(
    db: AsyncSession, *, doctor_id: uuid.UUID, rules: Iterable[AvailabilityRule]
) -> List[DoctorAvailability]:
    # Delete existing rules for doctor
    await db.execute(delete(DoctorAvailability).where(DoctorAvailability.doctor_id == doctor_id))

    # Insert new rules
    created: list[DoctorAvailability] = []
    for r in rules:
        created.append(
            DoctorAvailability(
                doctor_id=doctor_id,
                day_of_week=int(r.day_of_week),
                start_time=r.start_time,
                end_time=r.end_time,
            )
        )
    db.add_all(created)
    await db.commit()
    # refresh for completeness
    for ent in created:
        await db.refresh(ent)
    return created


async def get_doctor_availability(db: AsyncSession, *, doctor_id: uuid.UUID) -> List[DoctorAvailability]:
    res = await db.execute(
        select(DoctorAvailability)
        .where(DoctorAvailability.doctor_id == doctor_id)
        .order_by(DoctorAvailability.day_of_week, DoctorAvailability.start_time)
    )
    return list(res.scalars().all())

