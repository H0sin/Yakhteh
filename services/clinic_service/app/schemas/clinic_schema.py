import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.clinic_model import SubscriptionStatus


class ClinicBase(BaseModel):
    name: str
    address: Optional[str] = None
    subscription_status: SubscriptionStatus = SubscriptionStatus.free


class ClinicCreate(ClinicBase):
    pass


class ClinicUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    subscription_status: Optional[SubscriptionStatus] = None


class ClinicPublic(BaseModel):
    id: uuid.UUID
    name: str
    address: Optional[str]
    owner_id: uuid.UUID
    subscription_status: SubscriptionStatus
    model_config = ConfigDict(from_attributes=True)
