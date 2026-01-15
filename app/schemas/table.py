from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TableBase(BaseModel):
    seats_count: int = Field(..., gt=0)
    description: Optional[str] = None


class TableCreate(TableBase):
    pass


class TableBulkCreate(BaseModel):
    """Схема для массового создания столов"""
    count: int = Field(..., ge=1, le=100, description="Количество столов для создания")
    seats_count: int = Field(..., ge=1, description="Количество мест за каждым столом")
    description: Optional[str] = Field(None, description="Описание для всех столов")


class TableUpdate(BaseModel):
    cafe_id: Optional[int] = None
    seats_count: Optional[int] = Field(None, gt=0)
    description: Optional[str] = None
    active: Optional[bool] = None


class TableResponse(BaseModel):
    id: int
    cafe_id: int
    seats_count: int
    description: Optional[str] = None
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
