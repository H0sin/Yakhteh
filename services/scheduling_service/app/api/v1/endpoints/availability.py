import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user_payload
from app.db.session import get_session
from app.schemas.availability_schema import AvailabilitySetRequest, DoctorAvailabilityPublic
from app.crud.availability_crud import replace_doctor_availability, get_doctor_availability

router = APIRouter()


def _validate_rules(req: AvailabilitySetRequest) -> None:
    for r in req.rules:
        if r.start_time >= r.end_time:
            raise HTTPException(status_code=400, detail="start_time must be earlier than end_time")
        if r.day_of_week < 0 or r.day_of_week > 6:
            raise HTTPException(status_code=400, detail="day_of_week must be in 0..6")


@router.post("/", response_model=List[DoctorAvailabilityPublic], status_code=status.HTTP_200_OK)
async def set_my_availability(
    payload: AvailabilitySetRequest,
    db: AsyncSession = Depends(get_session),
    token_payload: dict = Depends(get_current_user_payload),
):
    _validate_rules(payload)
    # Only allow doctor to set their own availability
    sub = token_payload.get("sub")
    try:
        doctor_id = uuid.UUID(str(sub))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    entities = await replace_doctor_availability(db, doctor_id=doctor_id, rules=payload.rules)
    return entities


@router.get("/doctors/{doctor_id}", response_model=List[DoctorAvailabilityPublic], status_code=status.HTTP_200_OK)
async def get_availability(doctor_id: uuid.UUID, db: AsyncSession = Depends(get_session)):
    return await get_doctor_availability(db, doctor_id=doctor_id)

