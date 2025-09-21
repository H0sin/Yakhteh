from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_session
from app.schemas.clinic_schema import ClinicCreate, ClinicUpdate, ClinicPublic
from app.crud.crud_clinic import get_clinic, list_clinics, create_clinic, update_clinic, delete_clinic
from app.api.deps import get_current_user_payload

router = APIRouter()


@router.get("/", response_model=list[ClinicPublic])
async def list_all(db: AsyncSession = Depends(get_session), payload: dict = Depends(get_current_user_payload)):
    return await list_clinics(db)


@router.post("/", response_model=ClinicPublic, status_code=201)
async def create(payload: ClinicCreate, db: AsyncSession = Depends(get_session), token_payload: dict = Depends(get_current_user_payload)):
    # Extract user id from token subject (sub)
    sub = token_payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    try:
        owner_id = uuid.UUID(str(sub))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    # Create clinic using owner_id from token
    from app.models.clinic_model import Clinic
    clinic = Clinic(
        name=payload.name,
        address=payload.address,
        owner_id=owner_id,
        subscription_status=payload.subscription_status,
    )
    db.add(clinic)
    await db.commit()
    await db.refresh(clinic)
    return clinic


@router.get("/{clinic_id}", response_model=ClinicPublic)
async def get_one(clinic_id: uuid.UUID, db: AsyncSession = Depends(get_session), payload: dict = Depends(get_current_user_payload)):
    clinic = await get_clinic(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


@router.put("/{clinic_id}", response_model=ClinicPublic)
async def update(clinic_id: uuid.UUID, payload: ClinicUpdate, db: AsyncSession = Depends(get_session), token_payload: dict = Depends(get_current_user_payload)):
    clinic = await get_clinic(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return await update_clinic(db, clinic, payload)


@router.delete("/{clinic_id}", status_code=204)
async def delete(clinic_id: uuid.UUID, db: AsyncSession = Depends(get_session), payload: dict = Depends(get_current_user_payload)):
    clinic = await get_clinic(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    await delete_clinic(db, clinic)
    return None
