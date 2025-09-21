from datetime import time
import uuid
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class AvailabilityRule(BaseModel):
    day_of_week: int = Field(ge=0, le=6, description="0=Sunday ... 6=Saturday")
    start_time: time
    end_time: time


class AvailabilitySetRequest(BaseModel):
    rules: List[AvailabilityRule]


class DoctorAvailabilityPublic(BaseModel):
    id: uuid.UUID
    doctor_id: uuid.UUID
    day_of_week: int
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)

