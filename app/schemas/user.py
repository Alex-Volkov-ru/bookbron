from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    tg_id: Optional[str] = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    tg_id: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)
    role: Optional[UserRole] = None
    active: Optional[bool] = None


class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: str


class UserResponse(UserBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

