from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.db.session import get_session
from app.schemas.clinic_schema import ClinicCreate, ClinicUpdate, ClinicPublic
from app.crud.crud_clinic import get_clinic, list_clinics, create_clinic, update_clinic, delete_clinic

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# NOTE: In a real deployment, we'd share an auth library or call auth_service to validate tokens.
# Here, we just require the presence of a bearer token.
async def require_auth(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return token


@router.get("/", response_model=list[ClinicPublic])
async def list_all(db: AsyncSession = Depends(get_session), _: str = Depends(require_auth)):
    return await list_clinics(db)


@router.post("/", response_model=ClinicPublic, status_code=201)
async def create(payload: ClinicCreate, db: AsyncSession = Depends(get_session), _: str = Depends(require_auth)):
    return await create_clinic(db, payload)


@router.get("/{clinic_id}", response_model=ClinicPublic)
async def get_one(clinic_id: uuid.UUID, db: AsyncSession = Depends(get_session), _: str = Depends(require_auth)):
    clinic = await get_clinic(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


@router.put("/{clinic_id}", response_model=ClinicPublic)
async def update(clinic_id: uuid.UUID, payload: ClinicUpdate, db: AsyncSession = Depends(get_session), _: str = Depends(require_auth)):
    clinic = await get_clinic(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return await update_clinic(db, clinic, payload)


@router.delete("/{clinic_id}", status_code=204)
async def delete(clinic_id: uuid.UUID, db: AsyncSession = Depends(get_session), _: str = Depends(require_auth)):
    clinic = await get_clinic(db, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    await delete_clinic(db, clinic)
    return None
