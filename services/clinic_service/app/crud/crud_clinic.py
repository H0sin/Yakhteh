from typing import Optional, Sequence
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.clinic_model import Clinic
from app.schemas.clinic_schema import ClinicCreate, ClinicUpdate


async def get_clinic(db: AsyncSession, clinic_id: uuid.UUID) -> Optional[Clinic]:
    res = await db.execute(select(Clinic).where(Clinic.id == clinic_id))
    return res.scalar_one_or_none()


async def list_clinics(db: AsyncSession) -> Sequence[Clinic]:
    res = await db.execute(select(Clinic))
    return res.scalars().all()


async def create_clinic(db: AsyncSession, payload: ClinicCreate) -> Clinic:
    clinic = Clinic(
        name=payload.name,
        address=payload.address,
        owner_id=payload.owner_id,
        subscription_status=payload.subscription_status,
    )
    db.add(clinic)
    await db.commit()
    await db.refresh(clinic)
    return clinic


async def update_clinic(db: AsyncSession, clinic: Clinic, payload: ClinicUpdate) -> Clinic:
    if payload.name is not None:
        clinic.name = payload.name
    if payload.address is not None:
        clinic.address = payload.address
    if payload.subscription_status is not None:
        clinic.subscription_status = payload.subscription_status
    await db.commit()
    await db.refresh(clinic)
    return clinic


async def delete_clinic(db: AsyncSession, clinic: Clinic) -> None:
    await db.delete(clinic)
    await db.commit()
