from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user_model import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.doctor


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(default=None, min_length=8)


class UserInDB(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class UserPublic(UserInDB):
    pass
