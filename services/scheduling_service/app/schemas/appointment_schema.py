import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.appointment_model import AppointmentStatus


class AppointmentBase(BaseModel):
    patient_name: str
    patient_contact_details: str
    doctor_id: uuid.UUID
    clinic_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentPublic(BaseModel):
    id: uuid.UUID
    patient_name: str
    patient_contact_details: str
    doctor_id: uuid.UUID
    clinic_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    notes: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

