from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time


class CafeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1)
    phone: Optional[str] = None
    description: Optional[str] = None
    photo_id: Optional[str] = None  # UUID изображения (соответствует OpenAPI)
    work_start_time: Optional[time] = None  # Время начала работы (например, 09:00)
    work_end_time: Optional[time] = None  # Время окончания работы (например, 22:00)
    slot_duration_minutes: Optional[int] = Field(None, ge=15, le=240)  # Длительность слота в минутах (15-240)


class CafeCreate(CafeBase):
    phone: str = Field(..., min_length=1)  # Обязательное поле по OpenAPI
    photo_id: str = Field(..., min_length=1)  # Обязательное поле по OpenAPI
    managers_id: List[int] = Field(default_factory=list)  # Соответствует OpenAPI (managers_id)


class CafeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=1)
    phone: Optional[str] = None
    description: Optional[str] = None
    photo: Optional[str] = None
    manager_ids: Optional[List[int]] = None
    active: Optional[bool] = None
    work_start_time: Optional[time] = None
    work_end_time: Optional[time] = None
    slot_duration_minutes: Optional[int] = Field(None, ge=15, le=240)


class CafeResponse(CafeBase):
    id: int
    is_active: bool  # Соответствует OpenAPI
    created_at: datetime
    updated_at: datetime
    managers: List[dict] = []  # Соответствует OpenAPI (список UserShortInfo)
    photo_id: Optional[str] = None  # Добавляем для соответствия OpenAPI

    class Config:
        from_attributes = True

